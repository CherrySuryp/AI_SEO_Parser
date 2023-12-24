from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.queue import get_celery_result
from app.parser.tasks import get_info_v1, get_info_v2, get_info_by_name, get_info_only_keywords

router = APIRouter(tags=["Parser"])


class TaskStatus(BaseModel):
    task_id: str


class ResultSchema(BaseModel):
    name: Optional[str] = None
    params: Optional[dict] = {}
    desc: Optional[str] = None
    keywords: Optional[list] = None


class TaskResult(BaseModel):
    status: Literal["PENDING", "SUCCESS", "RETRY"] = "SUCCESS"
    result: Optional[ResultSchema] = None


@router.post("/{wb_sku}", response_model=TaskStatus)
async def parse_data(wb_sku: str | int, mode: Literal["only_keywords", "v1", "v1.2", "by_name"]):
    try:
        if mode == "only_keywords":
            task = get_info_only_keywords.delay(wb_sku=wb_sku)
        elif mode == "v1":
            task = get_info_v1.delay(wb_sku=wb_sku)
        elif mode == "v1.2":
            task = get_info_v2.delay(wb_sku=wb_sku)
        else:
            task = get_info_by_name.delay(wb_sku=wb_sku)

        return TaskStatus.model_validate({"task_id": task.id})
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't initiate the task.")


@router.get("/{task_id}/result")
async def get_task_result(task_id: str) -> TaskResult:
    result = await get_celery_result(task_id)
    return result
