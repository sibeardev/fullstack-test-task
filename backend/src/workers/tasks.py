import asyncio

from src.application.use_cases.process_file import (
    extract_file_metadata,
    scan_file_for_threats,
    send_file_alert,
)
from src.infrastructure.queue.celery_app import celery_app

_worker_loop: asyncio.AbstractEventLoop | None = None


def run_in_worker_loop(coroutine):
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(coroutine)


@celery_app.task
def scan_file_for_threats_task(file_id: str) -> None:
    run_in_worker_loop(scan_file_for_threats(file_id))
    extract_file_metadata_task.delay(file_id)


@celery_app.task
def extract_file_metadata_task(file_id: str) -> None:
    run_in_worker_loop(extract_file_metadata(file_id))
    send_file_alert_task.delay(file_id)


@celery_app.task
def send_file_alert_task(file_id: str) -> None:
    run_in_worker_loop(send_file_alert(file_id))
