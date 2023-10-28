import requests
from datetime import date, timedelta
from app.config import config


class Keywords:
    def __init__(self):
        self._token = config.WILDBOX_TOKEN

    def get_top_sku_by_name(self, item_name: str) -> str:
        endpoint = "https://wildbox.ru/api/wb_dynamic/products/"
        req = requests.get(
            endpoint,
            params={
                "city": "Москва",
                "wb_search": item_name,
                "period": 30,
                "limit": 1,
                "ordering": "-proceeds",
                "extra_fields": "id,product,brand"
            },
            headers={"Authorization": f"Token {self._token}"}
        )
        top_sku = str(req.json()["results"][-1]["id"])
        return top_sku

    def get_keywords(self, sku: str):
        endpoint = f'https://wildbox.ru/api/wb_dynamic/products/{sku}/keywords/'
        date_from = date.today() - timedelta(days=30)

        data = requests.get(
            endpoint,
            params={"date_from": date_from, "limit": 25, "ordering": "-frequency"},
            headers={
                "Authorization": f"Token {self._token}",
            }
        )
        keywords = data.json()["results"]
        return [keyword["keyword"]["name"] for keyword in keywords]
