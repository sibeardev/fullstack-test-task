from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.alerts import alerts_router
from src.api.routes.files import files_router
from src.core.config import STORAGE_DIR, settings

STORAGE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS.ALLOW_ORIGINS,
    allow_credentials=settings.CORS.ALLOW_CREDENTIALS,
    allow_methods=settings.CORS.ALLOW_METHODS,
    allow_headers=settings.CORS.ALLOW_HEADERS,
)

app.include_router(alerts_router)
app.include_router(files_router)
