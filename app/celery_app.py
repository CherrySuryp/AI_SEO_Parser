from celery import Celery
from app.config import redis_path

celery = Celery("app", broker=redis_path, include=["app.parser.tasks"])

celery.conf.worker_pool_restarts = True
celery.conf.broker_connection_retry_on_startup = True

celery.conf.task_queues = {"mpstats": {"exchange": "mpstats", "routing_key": "mpstats", "concurrency": 1}}
celery.conf.task_default_queue = "mpstats"

celery.conf.result_expires = 60
