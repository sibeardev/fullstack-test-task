from celery import Celery

from src.core.config import REDIS_URL

celery_app = Celery("file_tasks", broker=REDIS_URL, backend=REDIS_URL)
celery_app.autodiscover_tasks(["src.workers"])
