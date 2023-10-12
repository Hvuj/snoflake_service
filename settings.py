from imports import Final
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import secretmanager
import os
import google_crc32c
import json

try:
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()
    # Load environment variables from the '.env' file
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
except FileNotFoundError:
    print("Could not find .env file")
    raise

PROJECT_ID: Final[str] = os.environ.get("PROJECT_ID")
SECRET_ID: Final[str] = os.environ.get("SECRET_ID")
name = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/latest"

try:
    response = client.access_secret_version(request={"name": name})
    # Verify payload checksum.
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        print("Data corruption detected.")
        print(response)
    payload = json.loads(response.payload.data.decode("utf-8"))
except Exception as e:
    raise f"An error occurred while accessing the secret: {e}" from e

# Assign the environment variables to constants
PROJECT_NAME = payload["project_id"]
ACCESS_TOKEN = payload["access_token"]

if None in PROJECT_NAME:
    raise ValueError(
        "Missing environment variables." "Make sure to set:" "PROJECT_NAME."
    )
