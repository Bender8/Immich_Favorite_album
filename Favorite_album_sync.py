import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Set

import requests

# --- Configuration ---
IMMICH_URL: str = "http://localhost:2283"  # IF RUNNING ON HOST WITH DEFAULT PORT NO CHANGE NEEDE, ELSE SET YOUR IMMICH IP
API_KEY: str = "YOUR-API-KEY"  # REPLACE WITH YOUR API KEY
ALBUM_NAME: str = "Favorites"
LOG_FILE_PATH: str = "favorite_album_sync.log"
# ---------------------

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(LOG_FILE_PATH, maxBytes=5 * 1024 * 1024, backupCount=3),
        logging.StreamHandler(sys.stdout),
    ],
)

HEADERS: dict[str, str] = {"x-api-key": API_KEY, "Accept": "application/json"}


def get_all_favorite_asset_ids() -> set[str]:
    all_favorite_ids: list[str] = []
    page = 1
    page_size = 250
    while True:
        payload = {
            "isFavorite": True,
            "page": page,
            "size": page_size,
        }
        response = requests.post(
            f"{IMMICH_URL}/api/search/metadata",
            headers=HEADERS,
            json=payload,
            verify=False,
        )
        response.raise_for_status()
        # Access the nested 'assets' -> 'items' path
        items = response.json().get("assets", {}).get("items", [])
        if not items:
            break
        all_favorite_ids.extend([a["id"] for a in items])
        if len(items) < page_size:
            break
        page += 1
    return set(all_favorite_ids)


def get_or_create_album(name: str) -> str:
    """Finds an existing album by name or creates a new one."""
    # 1. Search for existing album
    response = requests.get(f"{IMMICH_URL}/api/albums", headers=HEADERS)
    response.raise_for_status()
    albums = response.json()

    for album in albums:
        if album["albumName"] == name:
            logging.info(f"Found existing album: {name}")
            return album["id"]

    # 2. Create if not found
    logging.info(f"Album '{name}' not found. Creating it...")
    payload = {"albumName": name}
    response = requests.post(f"{IMMICH_URL}/api/albums", headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["id"]


def add_assets_to_album(album_id: str, asset_ids: set[str]) -> None:
    """Adds a list of asset IDs to the specified album."""
    # Convert set to list for JSON serialization
    payload = {"ids": list(asset_ids)}

    # PUT /api/albums/{id}/assets is the standard endpoint
    url = f"{IMMICH_URL}/api/albums/{album_id}/assets"
    response = requests.put(url, headers=HEADERS, json=payload)
    response.raise_for_status()

    result = response.json()
    # The API typically returns a list of results for each ID
    success_count = sum(1 for item in result if item.get("success", True))
    logging.info(f"Successfully added {success_count} assets to the album.")


def get_assets_in_album(album_id: str) -> set[str]:
    """Fetches all asset IDs currently in the specified album."""
    response = requests.get(f"{IMMICH_URL}/api/albums/{album_id}", headers=HEADERS)
    response.raise_for_status()
    return set(asset["id"] for asset in response.json().get("assets", []))


def remove_assets_from_album(album_id: str, asset_ids: set[str]) -> None:
    """Removes a list of asset IDs from the specified album."""
    payload = {"ids": list(asset_ids)}
    url = f"{IMMICH_URL}/api/albums/{album_id}/assets"
    response = requests.delete(url, headers=HEADERS, json=payload)
    response.raise_for_status()

    result = response.json()
    success_count = sum(1 for item in result if item.get("success", True))
    logging.info(f"Successfully removed {success_count} assets from the album.")


def main() -> None:
    try:
        logging.info("Starting sync process...")
        logging.info("Fetching favorite asset IDs...")
        favorites = get_all_favorite_asset_ids()

        album_id = get_or_create_album(ALBUM_NAME)

        logging.info("Fetching current album assets...")
        current_album_assets = get_assets_in_album(album_id)

        ids_to_add = favorites - current_album_assets
        ids_to_remove = current_album_assets - favorites

        if ids_to_add:
            add_assets_to_album(album_id, ids_to_add)
        else:
            logging.info("No new assets to add.")

        if ids_to_remove:
            remove_assets_from_album(album_id, ids_to_remove)
        else:
            logging.info("No assets to remove.")

        logging.info("Sync process completed.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
