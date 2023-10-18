from selenium.common.exceptions import TimeoutException

from app.celery_app import celery
from app.parser.parser import Parser
from app.parser.utils import Utils


class NoKeywordsException(Exception):
    def __init__(self, message):
        super().__init__(message)


@celery.task(
    autoretry_for=(
        TimeoutException,
        NoKeywordsException,
    ),
    retry_kwargs={"max_retries": 3},
    default_retry_delay=1,
    soft_time_limit=120,
    time_limit=125,
)
def get_info_v1(wb_sku: str | int):
    item_name = Parser().get_wb_item_name(wb_sku)
    item_params = Utils.exclude_dim_info(Parser().get_wb_item_params(wb_sku))
    keywords = Parser(headless=True).parse_mpstats_by_sku(wb_sku)
    if not keywords:
        raise NoKeywordsException("No keywords")
    result = {"name": item_name, "params": item_params, "desc": None, "keywords": keywords}
    return result


@celery.task(
    autoretry_for=(
        TimeoutException,
        NoKeywordsException,
    ),
    retry_kwargs={"max_retries": 3},
    default_retry_delay=1,
    soft_time_limit=120,
    time_limit=125,
)
def get_info_v2(wb_sku: str | int):
    item_name = Parser().get_wb_item_name(wb_sku)
    item_params = Utils.exclude_dim_info(Parser().get_wb_item_params(wb_sku))
    item_desc = Parser().get_wb_item_desc(wb_sku)
    keywords = Parser().parse_mpstats_by_sku(wb_sku)
    if not keywords:
        raise NoKeywordsException("No keywords")
    result = {"name": item_name, "params": item_params, "desc": item_desc, "keywords": keywords}
    return result


@celery.task(
    autoretry_for=(
        TimeoutException,
        NoKeywordsException,
    ),
    retry_kwargs={"max_retries": 3},
    default_retry_delay=1,
    soft_time_limit=120,
    time_limit=125,
)
def get_info_by_name(wb_sku: str | int):
    keywords = Parser(headless=False).parse_mpstats_by_name(wb_sku)
    if not keywords:
        raise NoKeywordsException("No keywords")
    result = {"name": None, "params": None, "desc": None, "keywords": keywords}
    return result
