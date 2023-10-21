import os
import pickle

from typing import Dict, List

from selenium import webdriver as selenium
from seleniumwire import webdriver as selwire
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.proxy import Proxy, ProxyType

from fake_useragent import UserAgent

import sentry_sdk

from app.config import Config


class Parser:
    def __init__(self, keywords_count: int = 30, headless: bool = True):
        self._settings = Config()
        self._cookies_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cookies")
        self._keywords_count = keywords_count

        chromedriver = os.path.join(os.path.dirname(os.path.realpath(__file__)), "chromedriver")
        user_agent = UserAgent().chrome
        print(user_agent)

        proxy_path = "195.190.12.57:8000"
        proxy_user = "6JN86b"
        proxy_pass = "3mTC0d"

        chrome_service = selenium.ChromeService(executable_path=chromedriver)
        options = selenium.ChromeOptions()
        options.add_argument(f"user-agent={user_agent}")
        options.add_argument("--headless") if headless else None
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        seleniumwire_options = {
            'proxy': {
                'http': f'https://{proxy_user}:{proxy_pass}@{proxy_path}',
                'verify_ssl': False,
            },
        }

        self._driver = selwire.Chrome(
            options=options,
            service=chrome_service,
            seleniumwire_options=seleniumwire_options
        )

        self._driver.maximize_window()
        # self._driver.set_window_size(1000, 600)

    def _check_cookies(self) -> bool:
        """
        Проверка наличия сохраненное сессии
        """
        return os.path.exists(self._cookies_path)

    def _inject_cookies(self) -> None:
        """
        Инъекция cookie для авторизации
        """
        for cookie in pickle.load(open(self._cookies_path, "rb")):
            self._driver.add_cookie(cookie)

    def _authorize(self, save_cookies: bool = False) -> None:
        """
        Авторизация на сайте с сохранением cookie в файл
        """
        self._driver.get("https://mpstats.io/login")
        email_input = self._driver.find_element(By.ID, "email")
        passwd_input = self._driver.find_element(By.NAME, "password")

        email_input.clear()
        email_input.send_keys(self._settings.MPSTATS_LOGIN)
        passwd_input.clear()
        passwd_input.send_keys(self._settings.MPSTATS_PASS)
        passwd_input.send_keys(Keys.ENTER)

        if save_cookies:
            pickle.dump(self._driver.get_cookies(), open("cookies", "wb"))
            print(f"Cookies saved to {self._cookies_path}")

    def _auth_pipeline(self):
        """
        Авторизации или инъекции cookie по условиям
        """
        if self._check_cookies():
            self._driver.get("https://mpstats.io/login")
            self._inject_cookies()
            self._driver.refresh()
            print("Cookies injected")

            if self._driver.current_url == "https://mpstats.io/doubleSession":
                print("Double Session")
                self._authorize()

        else:
            print("Getting cookies")
            self._authorize(save_cookies=False)
            WebDriverWait(self._driver, 10).until(
                ec.visibility_of_element_located(
                    (By.CLASS_NAME, "top-menu__desktop")
                )
            )
            print("Authorized")

    def _top_similar_item_by_sku(self, wb_sku: int) -> int:
        """
        Переход к ТОП-1 похожему товару
        """
        self._driver.get(f"https://mpstats.io/wb/item/{wb_sku}")
        elements = self._driver.find_elements(
            By.XPATH, "//a[@href and @title='Открыть в Wildberries' and " "@target='_blank']"
        )
        return int([i.text for i in elements][0])

    def _top_similar_item_by_item_name(self, item_name: str) -> int:
        item_name = "+".join(item_name.split(" "))
        self._driver.get(f"https://mpstats.io/wb/bysearch?query={item_name}")
        elements = WebDriverWait(self._driver, 10).until(
            ec.visibility_of_any_elements_located(
                (
                    By.XPATH,
                    "//a[@href and @title='Открыть в Wildberries' and " "@target='_blank']",
                )
            )
        )
        return int([i.text for i in elements][0])

    def _get_keywords(self, sku: int) -> Dict[str, int]:
        """
        Парсинг ключевых слов со страницы https://mpstats.io/wb/item/{sku}
        """
        self._driver.get(f"https://mpstats.io/wb/item/{sku}")
        self._driver.execute_script("document.body.style.zoom = '30%'")

        kw_json = {}
        while len(kw_json) <= self._keywords_count:
            scroll_table = WebDriverWait(self._driver, 10).until(
                ec.visibility_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="mp-stats-app"]/div[2]/div/section/div[5]'
                        "/div[2]/div[1]/div/div/div/div[2]/div[2]/div[3]",
                    )
                )
            )
            keywords = self._driver.find_elements(By.XPATH, '//a[@title="Информация по ключевому слову"]/span')
            count = self._driver.find_elements(By.XPATH, '//div[@col-id="wb_count"]')
            keywords = [i.text for i in keywords]
            count = [i.text for i in count][3:]

            for keyword, kw_count in zip(keywords, count):
                kw_json[keyword] = int(kw_count.replace(" ", ""))

            self._driver.execute_script("arguments[0].scrollTop += 100;", scroll_table)

        # json.dump(kw_json, open("keywords.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
        return kw_json

    def parse_mpstats_by_sku(self, wb_sku: int | str) -> List[str] | None:
        """
        Вызов бизнес логики
        """
        try:
            self._auth_pipeline()
            top_item_sku = self._top_similar_item_by_sku(wb_sku=wb_sku)
            result = self._get_keywords(top_item_sku)
            self._driver.quit()
            return list(result)

        except Exception as ex:
            self._driver.quit()
            sentry_sdk.capture_exception(ex)
            return None

    def parse_mpstats_by_name(self, item_name: str) -> List[str] | None:
        try:
            self._auth_pipeline()
            top_item_sku = self._top_similar_item_by_item_name(item_name)
            result = self._get_keywords(top_item_sku)
            self._driver.quit()
            return list(result)

        except Exception as ex:
            self._driver.quit()
            sentry_sdk.capture_exception(ex)
            return None

    def get_wb_item_name(self, sku: str | int) -> str:
        self._driver.get(f"https://www.wildberries.ru/catalog/{sku}/detail.aspx")
        product_name = WebDriverWait(self._driver, 10).until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, 'h1[data-link="text{:selectedNomenclature^goodsName}"]'))
        )
        return str(product_name.text)

    def get_wb_item_params(self, sku: str | int) -> Dict[str, str]:
        self._driver.get(f"https://www.wildberries.ru/catalog/{sku}/detail.aspx")

        button = WebDriverWait(self._driver, 10).until(
            ec.visibility_of_element_located((By.XPATH, "// button[text() = 'Развернуть характеристики']"))
        )
        self._driver.execute_script("arguments[0].scrollIntoView();", button)
        button.click()

        product_params_decor = self._driver.find_elements(By.CLASS_NAME, "product-params__cell-decor")
        product_params_info = self._driver.find_elements(By.CLASS_NAME, "product-params__cell")
        product_params_decor = [i.text for i in product_params_decor if i.text != ""]
        product_params_info = [
            i.text for i in product_params_info if i.text not in product_params_decor and i.text != ""
        ]
        result = {decor: info for decor, info in zip(product_params_decor, product_params_info)}
        return result

    def get_wb_item_desc(self, sku: str | int) -> str:
        self._driver.get(f"https://www.wildberries.ru/catalog/{sku}/detail.aspx")

        button = WebDriverWait(self._driver, 10).until(
            ec.visibility_of_element_located((By.XPATH, "// button[text() = 'Развернуть описание']"))
        )
        self._driver.execute_script("arguments[0].scrollIntoView();", button)
        button.click()

        return self._driver.find_element(By.CLASS_NAME, "collapsable__text").text

# print(Parser(headless=False).parse_mpstats_by_name("Подушка"))
