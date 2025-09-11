import os
import shutil
import signal
import socket
import subprocess
import time
from typing import Optional
from dotenv import load_dotenv

from typing import List, Optional
from contextlib import contextmanager
from dagster import ConfigurableResource, InitResourceContext


load_dotenv()

def _wait_for_port(host: str, port: int, timeout_s: int = 60) -> None:
    end = time.time() + timeout_s
    while time.time() < end:
        with socket.socket() as s:
            s.settimeout(1.0)
            if s.connect_ex((host, port)) == 0:
                return
        time.sleep(0.25)
    raise RuntimeError(f"Local port {host}:{port} did not open within {timeout_s}s")


class BastionTunnelResource(ConfigurableResource):
    """Starts `az network bastion tunnel` before ops and tears it down afterwards."""
    bastion_name: str = "bastion-host"
    resource_group: str = os.environ.get('AZURE_RESOURCE_GROUP_NAME')
    target_resource_id: str = f"/subscriptions/{os.environ.get('AZURE_SUBSCRIPTION_ID')}/resourceGroups/{os.environ.get('AZURE_RESOURCE_GROUP_NAME')}/providers/Microsoft.Compute/virtualMachines/{os.environ.get('VM_NAME')}"        # VM resource ID
    resource_port: int = 5432
    local_port: int = int(os.environ.get("DB_PORT", 5438))
    local_host: str = "127.0.0.1"
    startup_timeout_s: int = 60
    extra_args: list[str] = []

    # Runtime handle (not in config)
    _proc: Optional[subprocess.Popen] = None

    def _build_cmd(self) -> List[str]:
        return [
            "az", "network", "bastion", "tunnel",
            "--name", self.bastion_name,
            "--resource-group", self.resource_group,
            "--target-resource-id", self.target_resource_id,
            "--resource-port", str(self.resource_port),
            "--port", str(self.local_port),
            *self.extra_args,
        ]

    def _start(self, context: InitResourceContext) -> None:
        if shutil.which("az") is None:
            raise RuntimeError("Azure CLI 'az' not found in PATH (required).")

        cmd = self._build_cmd()
        context.log.info(f"Starting Bastion tunnel: {' '.join(cmd)}")

        # separate process group for clean termination
        creationflags = 0
        preexec = os.setsid

        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            preexec_fn=preexec,
            creationflags=creationflags,
        )

        # brief non-blocking read for early errors
        start = time.time()
        while time.time() - start < 2 and self._proc.poll() is None:
            if self._proc.stdout:
                line = self._proc.stdout.readline()
                if not line:
                    break
                context.log.debug(f"[bastion] {line.rstrip()}")

        _wait_for_port(self.local_host, self.local_port, self.startup_timeout_s)
        context.log.info(
            f"Bastion tunnel up: {self.local_host}:{self.local_port} "
            f" {self.target_resource_id}:{self.resource_port}"
        )


    def _stop(self, context: InitResourceContext) -> None:
        proc = self._proc
        if not proc:
            return
        context.log.info("Stopping Bastion tunnel...")
        try:
            # try to terminate the whole process group first
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                # Fallback: terminate just the child
                proc.terminate()

            # give it a moment to exit cleanly
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                # escalate to SIGKILL on the process group
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except Exception:
                    proc.kill()

        finally:
            self._proc = None

    @contextmanager
    def yield_for_execution(self, context: InitResourceContext):
        self._start(context)
        try:
            yield self
        finally:
            self._stop(context)


    @property
    def host(self) -> str:
        return self.local_host

    @property
    def port(self) -> int:
        return self.local_port
