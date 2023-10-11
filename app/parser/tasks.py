from app.celery_app import celery
from app.parser.parser import Parser
from selenium.common.exceptions import TimeoutException


@celery.task(
    autoretry_for=(TimeoutException,),
    retry_kwargs={'max_retries': 3},
    soft_time_limit=60,
    time_limit=65
)
def get_info_v1(wb_sku: str | int):
    item_name = Parser().get_wb_item_name(wb_sku)
    item_params = Parser().get_wb_item_params(wb_sku)
    keywords = Parser().parse_mpstats_by_sku(wb_sku)
    result = {
        "name": item_name,
        "params": item_params,
        "desc": None,
        "keywords": keywords
    }

    return result


@celery.task(
    autoretry_for=(TimeoutException,),
    retry_kwargs={'max_retries': 3},
    soft_time_limit=60,
    time_limit=65
)
def get_info_v2(wb_sku: str | int):
    item_name = Parser().get_wb_item_name(wb_sku)
    item_params = Parser().get_wb_item_params(wb_sku)
    item_desc = Parser().get_wb_item_desc(wb_sku)
    keywords = Parser().parse_mpstats_by_sku(wb_sku)

    result = {
        "name": item_name,
        "params": item_params,
        "desc": item_desc,
        "keywords": keywords
    }
    return result
