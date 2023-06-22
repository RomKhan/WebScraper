import asyncio

from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Scraper import Scraper


class AvitoScraper(Scraper):
    def __init__(self, url, link_token, pics_folder, image_loader, data_saver, prev_address = None):
        Scraper.__init__(self, url, link_token, pics_folder, image_loader, data_saver, prev_address)
        self.offer_load_indicator = "span[class^='style-price-value-main']"
        self.main_page_load_indicator = "span[class^='page-title-count']"
        self.by_settings = By.CSS_SELECTOR

    def get_offer_data(self, link, id, driver):
        try:
            driver.get(link)
            WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.offer_load_indicator)))
        except Exception as e:
            print('error here', link)
        asyncio.run(self.parse_offer_page(driver.page_source, link))

    async def parse_offer_page(self, content, link, id):
        tree = html.fromstring(content)
        #price = tree.xpath("//div[class*='style-item-view-price-content']/div/div/div/div/span")[1].text
        try:
            price = tree.xpath("//span[starts-with(@class, 'style-price-value-main')]/span")[0].text
            print(link, price)
        except:
            print('cant find price')

    # def run_driver_on_main_page(self, driver):
    #     try:
    #         driver.get(self.url)
    #         WebDriverWait(driver, timeout=100).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.main_page_load_indicator)))
    #         driver.execute_script("window.stop();")
    #     except Exception as e:
    #         print('error here', self.url)

    def get_link_by_page(self):
        pass

    @staticmethod
    def parse_link(url):
        pass