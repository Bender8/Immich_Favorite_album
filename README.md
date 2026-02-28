# DEPRECATED USE Bender8/immich_auto_album INSTEAD!!!
# THIS FUNCTIONALITY IS NOW INCLUDED IN Bender8/immich_auto_album

## Immich Favorite Album Sync

This tool automatically synchronizes your "Favorite" assets in Immich to a specific album (default: "Favorites"). It ensures that the album always reflects your current favorites by adding new ones and removing those you've unfavorited.

## Features

- **Auto-Sync:** Adds all assets marked as "Favorite" to a target album.
- **Cleanup:** Removes assets from the target album if they are no longer marked as "Favorite".
- **Album Creation:** Automatically creates the target album if it doesn't exist.
- **Error Notifications:** Optional email notifications when the script encounters an unhandled exception.
- **Logging:** Detailed logs are written to `favorite_album_sync.log`.

## Prerequisites

- Python 3.x
- `requests` library

## Installation

1. Clone this repository or download `Favorite_album_sync.py`.
2. Install the required Python dependency:

   - **Debian/Ubuntu:**
     ```bash
     sudo apt update && sudo apt install python3-requests
     ```

   - **Other Systems (using pip):**
     ```bash
     pip install requests
     ```

## Configuration

Open `Favorite_album_sync.py` in a text editor and update the **Configuration** section at the top of the file:

### Immich Settings
- `IMMICH_URL`: Your Immich server URL (e.g., `http://localhost:2283` or `http://192.168.1.100:2283`).
- `API_KEY`: Your Immich API Key. You can generate this in the Immich Web UI under **Account Settings > API Keys**.
- `ALBUM_NAME`: The name of the album to sync favorites to (default: `"Favorites"`).
- `LOG_FILE_PATH`: Set the file path and name for your log file (default: "favorite_album_sync.log" in same directory as the script)

### Email Notifications (Optional)
To receive emails if the script fails, configure the following:
- `ENABLE_EMAIL_ON_ERROR`: Set to `True`. Change to `False` to disable
- `EMAIL_SMTP_SERVER`: Your SMTP server (default is configured for Gmail: `smtp.gmail.com`).
- `EMAIL_SMTP_PORT`: SMTP port (default `465` for SSL).
- `EMAIL_USERNAME`: Your email address.
- `EMAIL_PASSWORD`: Your email password or App Password (recommended for Gmail).
- `EMAIL_TO`: The recipient email address.

## Usage

Run the script manually:

```bash
python3 Favorite_album_sync.py
```

### Scheduling
To keep your album in sync automatically, you can schedule the script to run periodically.

- **Linux/macOS:** Use `cron` (e.g., run every hour).
- **Windows:** Use Task Scheduler.

## Logging
The script outputs logs to the console. It also writes to `favorite_album_sync.log` in the same directory or a file path spcified in the config section.
