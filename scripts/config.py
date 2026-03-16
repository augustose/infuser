import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GITEA_URL = os.getenv("GITEA_URL", "https://gitea.alithya.com").rstrip("/")
GITEA_TOKEN = os.getenv("GITEA_TOKEN")

HEADERS = {
    "Accept": "application/json"
}

if GITEA_TOKEN:
    HEADERS["Authorization"] = f"token {GITEA_TOKEN}"
else:
    print("WARNING: GITEA_TOKEN is not set in the .env file. API calls requiring authentication will fail.")
