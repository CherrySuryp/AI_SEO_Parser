from celery import Celery
from celery.result import AsyncResult
from fastapi import HTTPException, status

from app.config import redis_path

celery = Celery("app", broker=redis_path, backend=redis_path, include=["app.parser.tasks"])

celery.conf.worker_pool_restarts = True
celery.conf.broker_connection_retry_on_startup = True

celery.conf.task_queues = {"mpstats": {"exchange": "mpstats", "routing_key": "mpstats", "concurrency": 1}}
celery.conf.task_default_queue = "mpstats"

celery.conf.result_expires = 60


async def get_celery_result(task_id: str):
    task = AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "PENDING"}
    elif task.state == "SUCCESS":
        return {"status": "SUCCESS", "result": task.result}
    elif task.state == "FAILURE":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Task failed after 3 attempts",
        )
    elif task.state == "REVOKED":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Task was revoked",
        )
    else:
        return {"status": task.state}
