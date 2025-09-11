#!/usr/bin/env bash
# tunnelctl — manage an Azure Bastion TCP tunnel as a long-lived background process.
# Usage:
#   LOCAL_PORT=5432 NAME=your-bastion-name AZURE_RESOURCE_GROUP_NAME=your-rg \
#     VM_NAME=your-vm RESOURCE_PORT=5432 STATE_DIR=/tmp/bastion VM_NAME=your-vm \
#     tunnelctl {start|status|stop}
#
# Env vars:
#   LOCAL_PORT                  Local TCP port to bind (default: 5432)
#   NAME                        Bastion name                       (required)
#   AZURE_SUBSCRIPTION_ID       Azure subscription ID              (required) 
#   AZURE_RESOURCE_GROUP_NAME   Azure resource group               (required)
#   VM_NAME                     Azure VM name                      (required)
#   RESOURCE_PORT               Target resource port (default: 5432)
#   STATE_DIR                   Where to keep pid/port/logs (default: /tmp/bastion-tunnel-$USER_ID)

set -euo pipefail

# Get user ID
USER_ID="$(id -un)"

# Prepare env vars
LOCAL_PORT="${LOCAL_PORT:-5432}"
NAME="${NAME:-bastion-host}"
AZURE_SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID}"
AZURE_RESOURCE_GROUP_NAME="${AZURE_RESOURCE_GROUP_NAME}"
VM_NAME="${VM_NAME:-my-vm}"
RESOURCE_PORT="${RESOURCE_PORT:-5432}"
STATE_DIR="${STATE_DIR:-/tmp/bastion-tunnel-$USER_ID}"
PID_FILE="$STATE_DIR/pid"
PORT_FILE="$STATE_DIR/port"
LOG_FILE="$STATE_DIR/tunnel.log"
AZURE_RESOURCE_GROUP_NAME="${AZURE_RESOURCE_GROUP_NAME}"
TARGET_ID="/subscriptions/${AZURE_SUBSCRIPTION_ID}/resourceGroups/${AZURE_RESOURCE_GROUP_NAME}/providers/Microsoft.Compute/virtualMachines/${VM_NAME}"

# --- helpers -----------------------------------------------------------------

log() { printf "[%(%Y-%m-%d %H:%M:%S)T] %s\n" -1 "$*" | tee -a "$LOG_FILE" >&2; }

require_env() {
  local missing=0
  for v in NAME AZURE_SUBSCRIPTION_ID AZURE_RESOURCE_GROUP_NAME VM_NAME; do
    if [[ -z "${!v:-}" ]]; then
      echo "Missing required env var: $v" >&2; missing=1
    fi
  done
  [[ $missing -eq 0 ]] || exit 2
}

have_pid() { [[ -f "$PID_FILE" ]] && ps -p "$(cat "$PID_FILE")" >/dev/null 2>&1; }

# True if any other process is listening on TCP $1 (localhost)
port_up() {
  local p="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -ltn "( sport = :$p )" | grep -q LISTEN
    return $?
  elif command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"$p" -sTCP:LISTEN -n -P >/dev/null 2>&1
    return $?
  else
    # bash /dev/tcp fallback
    (echo > /dev/tcp/127.0.0.1/"$p") >/dev/null 2>&1
    return $?
  fi
}

wait_for_port() {
  local p="$1" timeout="${2:-30}" t0 now
  t0=$(date +%s)
  while true; do
    if port_up "$p"; then return 0; fi
    now=$(date +%s)
    if (( now - t0 >= timeout )); then
      return 1
    fi
    sleep 0.25
  done
}

# Kill by PID if known; otherwise kill by port/command as a safety net
kill_tunnel() {
  local killed=0
  if have_pid; then
    local pid; pid="$(cat "$PID_FILE")"
    # Kill the process group in case az spawned children (setsid makes PID==PGID)
    if kill -- -"$pid" 2>/dev/null; then killed=1; fi
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 -- -"$pid" 2>/dev/null || true
    fi
  fi

  # If still listening, kill by port (exact) — Linux path
  if port_up "$LOCAL_PORT"; then
    if command -v lsof >/dev/null 2>&1; then
      while read -r pid; do
        kill "$pid" 2>/dev/null || true
      done < <(lsof -t -iTCP:"$LOCAL_PORT" -sTCP:LISTEN -n -P || true)
      sleep 1
      # Escalate if needed
      while read -r pid; do
        kill -9 "$pid" 2>/dev/null || true
      done < <(lsof -t -iTCP:"$LOCAL_PORT" -sTCP:LISTEN -n -P || true)
    elif command -v ss >/dev/null 2>&1; then
      # Extract pid=NNN from ss output
      local pid
      pid=$(ss -lptn "( sport = :$LOCAL_PORT )" | awk -F'[=, ]+' '/pid=/ {print $6; exit}')
      if [[ -n "${pid:-}" ]]; then
        kill "$pid" 2>/dev/null || true
        sleep 1
        kill -9 "$pid" 2>/dev/null || true
      fi
    fi
  fi

  # Fallback: pattern kill
  pkill -f "az network bastion tunnel --name ${NAME:-}" 2>/dev/null || true
  sleep 1
  killed=1

  # Cleanup files if port is down
  if ! port_up "$LOCAL_PORT"; then
    rm -f "$PID_FILE" "$PORT_FILE"
  fi

  return $killed
}

# --- commands ----------------------------------------------------------------

start() {
  require_env
  mkdir -p "$STATE_DIR"
  touch "$LOG_FILE"

  # If already running on same port, be idempotent
  if port_up "$LOCAL_PORT"; then
    log "Tunnel already UP on 127.0.0.1:$LOCAL_PORT"
    echo "$LOCAL_PORT" > "$PORT_FILE"
    exit 0
  fi

  # If we have a stale PID (file exists but port is down), clean it
  if [[ -f "$PID_FILE" ]] && ! have_pid; then
    rm -f "$PID_FILE"
  fi

  log "Starting Bastion tunnel: name=$NAME rg=$AZURE_RESOURCE_GROUP_NAME target=$TARGET_ID -> 127.0.0.1:$LOCAL_PORT (target $RESOURCE_PORT)"
  # Start in a fresh session so we can kill the whole group later; exec replaces shell with az
  setsid bash -c 'exec az network bastion tunnel \
    --name "'"$NAME"'" \
    --resource-group "'"$AZURE_RESOURCE_GROUP_NAME"'" \
    --target-resource-id "'"$TARGET_ID"'" \
    --resource-port "'"$RESOURCE_PORT"'" \
    --port "'"$LOCAL_PORT"'"' >>"$LOG_FILE" 2>&1 &

  # $! is the PID of the setsid bash; because we exec az inside it, az inherits the same PGID
  echo $! > "$PID_FILE"
  echo "$LOCAL_PORT" > "$PORT_FILE"

  if ! wait_for_port "$LOCAL_PORT" 60; then
    log "ERROR: Port $LOCAL_PORT did not open in time."
    # cleanup
    kill -- -$(cat "$PID_FILE") 2>/dev/null || true
    rm -f "$PID_FILE"
    exit 1
  fi

  log "Bastion tunnel UP: 127.0.0.1:$LOCAL_PORT"
}

status() {
  local up_port="down" up_pid="down"
  if port_up "$LOCAL_PORT"; then up_port="up"; fi
  if have_pid; then up_pid="up"; fi

  echo "port: 127.0.0.1:$LOCAL_PORT is $up_port"
  if [[ -f "$PID_FILE" ]]; then
    echo "pid:  $(cat "$PID_FILE") is $up_pid"
  else
    echo "pid:  (none)"
  fi

  if [[ "$up_port" == "up" ]]; then
    exit 0
  else
    exit 3
  fi
}

stop() {
  require_env
  if ! port_up "$LOCAL_PORT" && ! have_pid; then
    echo "already stopped"
    exit 0
  fi
  log "Stopping Bastion tunnel..."
  kill_tunnel || true

  if port_up "$LOCAL_PORT"; then
    log "WARNING: Port $LOCAL_PORT still listening. Manual cleanup may be required."
    exit 1
  fi
  log "Stopped."
}

# --- main --------------------------------------------------------------------

case "${1:-}" in
  start)  start ;;
  status) status ;;
  stop)   stop ;;
  *)
    cat >&2 <<EOF
Usage: tunnelctl {start|status|stop}
  Env: LOCAL_PORT (default 5432), RESOURCE_PORT (default 5432),
       NAME (required), AZURE_RESOURCE_GROUP_NAME (required), VM_NAME (required), 
       STATE_DIR (default /tmp/bastion-tunnel-$USER_ID)
Examples:
  LOCAL_PORT=5432 NAME=bastion-host AZURE_RESOURCE_GROUP_NAME=my-rg VM_NAME=my-vm \\
    tunnelctl start
EOF
    exit 2
    ;;
esac
