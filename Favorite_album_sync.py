import requests

# --- Configuration ---
IMMICH_URL = "http://localhost:2283"
API_KEY = "yaWLQ6BYtcvsKpJH29H2pQ9HMSzXDTGTGRi27NGoA"
ALBUM_NAME = "Favorites"
# ---------------------

HEADERS = {"x-api-key": API_KEY, "Accept": "application/json"}


def get_all_favorite_asset_ids():
    all_favorite_ids = []
    page = 1
    page_size = 250
    while True:
        payload = {
            "isFavorite": True,
            "page": page,
            "size": page_size,
            }
        response = requests.post(f"{IMMICH_URL}/api/search/metadata", headers=HEADERS, json=payload, verify=False)
        response.raise_for_status()
        # Access the nested 'assets' -> 'items' path
        items = response.json().get('assets', {}).get('items', [])
        if not items:
            break
        all_favorite_ids.extend([a['id'] for a in items])
        if len(items) < page_size:
            break
        page += 1
    return set(all_favorite_ids)


def get_or_create_album(name):
    """Finds an existing album by name or creates a new one."""
    # 1. Search for existing album
    response = requests.get(f"{IMMICH_URL}/api/albums", headers=HEADERS)
    response.raise_for_status()
    albums = response.json()

    for album in albums:
        if album['albumName'] == name:
            print(f"Found existing album: '{name}' (ID: {album['id']})")
            return album['id']

    # 2. Create if not found
    print(f"Album '{name}' not found. Creating it...")
    payload = {"albumName": name}
    response = requests.post(f"{IMMICH_URL}/api/albums", headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()['id']


def add_assets_to_album(album_id, asset_ids):
    """Adds a list of asset IDs to the specified album."""
    # Convert set to list for JSON serialization
    payload = {"ids": list(asset_ids)}

    # PUT /api/albums/{id}/assets is the standard endpoint
    url = f"{IMMICH_URL}/api/albums/{album_id}/assets"
    response = requests.put(url, headers=HEADERS, json=payload)
    response.raise_for_status()

    result = response.json()
    # The API typically returns a list of results for each ID
    success_count = sum(1 for item in result if item.get('success', True))
    print(f"Successfully added {success_count} assets to the album.")


def get_assets_in_album(album_id):
    """Fetches all asset IDs currently in the specified album."""
    response = requests.get(f"{IMMICH_URL}/api/albums/{album_id}", headers=HEADERS)
    response.raise_for_status()
    return set(asset['id'] for asset in response.json().get('assets', []))


def remove_assets_from_album(album_id, asset_ids):
    """Removes a list of asset IDs from the specified album."""
    payload = {"ids": list(asset_ids)}
    url = f"{IMMICH_URL}/api/albums/{album_id}/assets"
    response = requests.delete(url, headers=HEADERS, json=payload)
    response.raise_for_status()

    result = response.json()
    success_count = sum(1 for item in result if item.get('success', True))
    print(f"Successfully removed {success_count} assets from the album.")


def main():
    print("Fetching favorite asset IDs...")
    favorites = get_all_favorite_asset_ids()

    album_id = get_or_create_album(ALBUM_NAME)

    print("Fetching current album assets...")
    current_album_assets = get_assets_in_album(album_id)

    ids_to_add = favorites - current_album_assets
    ids_to_remove = current_album_assets - favorites

    if ids_to_add:
        add_assets_to_album(album_id, ids_to_add)
    if ids_to_remove:
        remove_assets_from_album(album_id, ids_to_remove)

if __name__ == "__main__":
    main()
