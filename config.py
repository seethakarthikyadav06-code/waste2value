import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "crop-waste-dev-secret-key-2026")
    DATABASE_PATH = BASE_DIR / "database" / "database.db"
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB max file upload size
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    
    # AI configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    
    # App Settings
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
    PORT = int(os.getenv("PORT", 5000))
