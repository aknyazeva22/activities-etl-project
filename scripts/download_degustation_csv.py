import sys
from pathlib import Path

import requests


def download_csv(url: str, destination: Path, chunk_size: int = 8192) -> None:
    """Stream–download *url* to *destination*."""
    destination.parent.mkdir(parents=True, exist_ok=True)  # Ensure folders exist

    print(f"Downloading {url} -> {destination}")
    with requests.get(url, stream=True, timeout=30) as resp:
        resp.raise_for_status()  # Raises if the request failed

        with destination.open("wb") as f:
            for chunk in resp.iter_content(chunk_size):
                if chunk:  # filter out keep-alive chunks
                    f.write(chunk)

    print(f"Saved {destination.absolute()}")


if __name__ == "__main__":
    DOWNLOAD_URL = "https://data.paysdelaloire.fr/api/explore/v2.1/catalog/datasets/234400034_070-010_offre-touristique-degustations-rpdl/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    OUTPUT_FILE = "data/degustations.csv"

    try:
        download_csv(DOWNLOAD_URL, Path(OUTPUT_FILE))
    except requests.exceptions.RequestException as exc:
        print(f"Download failed: {exc}")
        sys.exit(1)
