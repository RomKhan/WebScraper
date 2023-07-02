from enum import Enum
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import datetime


class ListingMode(Enum):
    rent = 0
    sale = 1


class ScraperAbstract:
    def __init__(self, by_settings, page_load_indicator, data_saver, website_name, city, listing_type, page_load_timeout=150):
        self.by_settings = by_settings
        self.page_load_indicator = page_load_indicator
        self.page_load_timeout = page_load_timeout
        self.WINDOW_SIZE = "1920,1080"
        self.current_page = 1
        self.data_saver = data_saver
        self.website_db_id = self.data_saver.get_website_id(website_name)
        self.city_db_id = self.data_saver.get_city_id(city)
        self.listing_type_db_id = self.data_saver.get_listing_type_id(listing_type)
        self.previous_idx = set()

    def run_driver_on_page(self, url, driver):
        try:
            driver.get(url)
            WebDriverWait(driver, timeout=self.page_load_timeout).until(
                EC.presence_of_element_located((self.by_settings, self.page_load_indicator)))
        except Exception as e:
            print('i can\'t fully load this page', url)
            return False
        return True

    def parse_if_exists(self, tree, query):
        response = tree.xpath(query)
        if len(response) > 0:
            return response
        return None

    def get_webdriver(self):
        chrome_options = webdriver.ChromeOptions()
        # PROXY = "92.255.7.162:8080"
        # chrome_options.add_argument('--proxy-server=%s' % PROXY)
        chrome_options.add_argument('--headless')
        #chrome_options.add_argument('--no-sandbox')
        #chrome_options.add_argument('--disable-dev-shm-usage')

        #chrome_options.add_argument("enable-automation")
        #chrome_options.add_argument("--disable-dev-shm-usage")
        #chrome_options.add_argument("--disable-browser-side-navigation")
        #chrome_options.add_argument("--disable-gpu")

        chrome_options.add_argument("--window-size=%s" % self.WINDOW_SIZE)
        chrome_options.page_load_strategy = 'none'
        #chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        driver = uc.Chrome(options=chrome_options, user_multi_procs=True)
        #driver = webdriver.Chrome(options=chrome_options)
        return driver

    def get_desk_link(self) -> str:
        pass

    @staticmethod
    def parse_link(url):
        pass

    def get_soap(self, content):
        pass

    def to_database(self, data):
        data['Сайт id'] = self.website_db_id
        data['Город id'] = self.city_db_id
        data['Тип обьявления id'] = self.listing_type_db_id
        data['Дата публикации'] = datetime.date.today()
        data['Дата исчезновения'] = datetime.date.today()
        self.data_saver.data_to_save_queue.append(data)
