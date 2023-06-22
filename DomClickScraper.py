import asyncio

from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Scraper import Scraper


class DomClickScraper(Scraper):
    def __init__(self, url, link_token, pics_folder, image_loader, data_saver, prev_address = None):
        Scraper.__init__(self, url, link_token, pics_folder, image_loader, data_saver, prev_address)
        self.offer_load_indicator = 'product-page'
        self.main_page_load_indicator = 'content-wrap'
        self.by_settings = By.CLASS_NAME

    def get_offer_data(self, link, id, driver):
        try:
            driver.get(link)
            WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.CLASS_NAME, self.offer_load_indicator)))
        except Exception as e:
            print('error here', link)
        asyncio.run(self.parse_offer_page(driver.page_source, link))

    async def parse_offer_page(self, content, link, id):
        tree = html.fromstring(content)
        try:
            price = tree.xpath("//div[@class='l2ytJ']/span")[0].text
            print(link, price)
        except:
            print('cant find price')

    # def run_driver_on_main_page(self, driver):
    #     try:
    #         driver.get(self.url)
    #         WebDriverWait(driver, timeout=150).until(EC.presence_of_element_located((By.CLASS_NAME, self.main_page_load_indicator)))
    #     except Exception as e:
    #         print('error here', self.url)

    def get_link_by_page(self):
        pass

    @staticmethod
    def parse_link(url):
        pass
