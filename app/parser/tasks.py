from selenium.common.exceptions import TimeoutException
from requests.exceptions import ConnectionError

from app.celery_app import celery
from app.parser.wb_data import Parser
from app.parser.keywords_data import Keywords
from app.parser.utils import Utils


parser_service = Parser()
keywords_service = Keywords()


class NoKeywordsException(Exception):
    def __init__(self, message):
        super().__init__(message)


@celery.task(
    autoretry_for=(
        TimeoutException,
        NoKeywordsException,
        ConnectionError
    ),
    retry_kwargs={"max_retries": 3},
    default_retry_delay=1,
    soft_time_limit=120,
    time_limit=125,
)
def get_info_v1(wb_sku: str | int):
    item_name = parser_service.get_wb_item_name(wb_sku)
    item_params = Utils.exclude_dim_info(Parser().get_wb_item_params(wb_sku))
    keywords = keywords_service.get_keywords(wb_sku)
    if not keywords:
        raise NoKeywordsException("No keywords")
    result = {"name": item_name, "params": item_params, "desc": None, "keywords": keywords}
    return result


@celery.task(
    autoretry_for=(
        TimeoutException,
        NoKeywordsException,
        ConnectionError
    ),
    retry_kwargs={"max_retries": 3},
    default_retry_delay=1,
    soft_time_limit=120,
    time_limit=125,
)
def get_info_v2(wb_sku: str | int):
    item_name = parser_service.get_wb_item_name(wb_sku)
    item_params = Utils.exclude_dim_info(Parser().get_wb_item_params(wb_sku))
    item_desc = parser_service.get_wb_item_desc(wb_sku)
    keywords = keywords_service.get_keywords(wb_sku)
    if not keywords:
        raise NoKeywordsException("No keywords")
    result = {"name": item_name, "params": item_params, "desc": item_desc, "keywords": keywords}
    return result


@celery.task(
    autoretry_for=(
        TimeoutException,
        NoKeywordsException,
        ConnectionError
    ),
    retry_kwargs={"max_retries": 3},
    default_retry_delay=1,
    soft_time_limit=120,
    time_limit=125,
)
def get_info_by_name(wb_sku: str | int):
    keywords = keywords_service.get_keywords(keywords_service.get_top_sku_by_name(wb_sku))
    if not keywords:
        raise NoKeywordsException("No keywords")
    result = {"name": None, "params": None, "desc": None, "keywords": keywords}
    return result
