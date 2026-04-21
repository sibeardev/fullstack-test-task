from pathlib import Path

from .env import Settings

settings = Settings()

DEBUG = settings.DEBUG
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage" / "files"
MAX_UPLOAD_SIZE_MB = 10
PROHIBITED_EXTENSIONS = {".exe", ".bat", ".cmd", ".sh", ".js"}
VALID_PDF_MIME_TYPES = {"application/pdf", "application/octet-stream"}
DEFAULT_MIME_TYPE = "application/octet-stream"

DATABASE_URL = str(settings.POSTGRES.dsn)
REDIS_URL = str(settings.REDIS.DSN)
