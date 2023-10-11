from app.celery_app import celery
from app.parser.parser import Parser


@celery.task()
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


@celery.task()
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
