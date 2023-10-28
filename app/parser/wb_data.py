import os

from typing import Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from fake_useragent import UserAgent
from selenium_stealth import stealth


class Parser:
    def __init__(self, headless: bool = True):
        chromedriver = os.path.join(os.path.dirname(os.path.realpath(__file__)), "chromedriver")
        chrome_service = webdriver.ChromeService(executable_path=chromedriver)

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={UserAgent().googlechrome}")
        options.add_argument("--headless") if headless else None
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self._driver = webdriver.Chrome(options=options, service=chrome_service)
        self._driver.maximize_window() if not headless else None

        stealth(
            self._driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            run_on_insecure_origins=True
        )

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

