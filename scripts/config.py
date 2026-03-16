import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GITEA_URL = os.getenv("GITEA_URL", "https://gitea.alithya.com").rstrip("/")
GITEA_READ_TOKEN = os.getenv("GITEA_READ_TOKEN", os.getenv("GITEA_TOKEN"))
GITEA_WRITE_TOKEN = os.getenv("GITEA_WRITE_TOKEN")
GITEA_ALLOW_WRITES = str(os.getenv("GITEA_ALLOW_WRITES", "false")).lower() in ["true", "1", "yes"]

HEADERS = {
    "Accept": "application/json"
}

WRITE_HEADERS = {
    "Accept": "application/json"
}

if GITEA_READ_TOKEN:
    HEADERS["Authorization"] = f"token {GITEA_READ_TOKEN}"
else:
    print("WARNING: GITEA_READ_TOKEN is not set. Read operations will fail.")
    
if GITEA_WRITE_TOKEN:
    WRITE_HEADERS["Authorization"] = f"token {GITEA_WRITE_TOKEN}"
else:
    pass # Optional warning, writes are blocked by default anyway if ALLOW_WRITES is false
