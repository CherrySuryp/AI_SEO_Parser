import asyncio
from typing import Literal, Optional

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from selenium.common.exceptions import TimeoutException

from app.celery_app import get_celery_result
from app.parser.tasks import get_info_v1, get_info_v2

router = APIRouter(tags=["Parser"])


class TaskStatus(BaseModel):
    task_id: str


class ResultSchema(BaseModel):
    params: dict
    desc: Optional[str] = None
    keywords: Optional[list] = None


class TaskResult(BaseModel):
    status: Literal["PENDING", "SUCCESS", "RETRY"] = "SUCCESS"
    result: Optional[ResultSchema] = None


@router.post("/{wb_sku}", response_model=TaskStatus)
async def parse_data(wb_sku: str | int, mode: Literal["v1", "v2"]):
    try:
        task = get_info_v1.delay(wb_sku=wb_sku) if mode == "v1" else get_info_v2.delay(wb_sku=wb_sku)
        return TaskStatus.model_validate({"task_id": task.id})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Couldn't initiate the task."
        )


@router.get("/{task_id}/result")
async def get_task_result(task_id: str) -> TaskResult:
    result = await get_celery_result(task_id)
    return result
