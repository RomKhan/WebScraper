import logging
import os
import random
from enum import Enum
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import undetected_chromedriver as uc
import requests

from KeysEnum import KeysEnum


class ListingMode(Enum):
    rent = 0
    sale = 1


class ScraperAbstract:
    def __init__(self, by_settings, page_load_indicator, website_name, city, listing_type, page_load_timeout=150):
        self.by_settings = by_settings
        self.page_load_indicator = page_load_indicator
        self.page_load_timeout = page_load_timeout
        self.WINDOW_SIZE = "1920,1080"
        self.current_page = 1
        self.db_flow_url = 'http://app:8080/db'
        self.website_db_id = requests.get(self.db_flow_url+'/getWebsiteId', params={'website': website_name}).text
        self.city_db_id = requests.get(self.db_flow_url+'/getCityId', params={'city': city}).text
        self.listing_type_db_id = requests.get(self.db_flow_url+'/getListingTypeId', params={'listing_type': listing_type}).text
        self.previous_idx = set()
        self.useragents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.3',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.3',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.2.625 Yowser/2.5 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 YaBrowser/20.12.2.105 Yowser/2.5 Safari/537.36'
        ]

    def run_driver_on_page(self, url, driver):
        status = True
        try:
            driver.get(url)
            WebDriverWait(driver, timeout=self.page_load_timeout).until(
                EC.presence_of_element_located((self.by_settings, self.page_load_indicator)))
        except Exception as e:
            #print('i can\'t fully load this page', url)
            status = False

        try:
            driver.execute_script("window.stop();")
        except:
            logging.info('Can\'t execute window.stop();')
        return status

    def parse_if_exists(self, tree, query):
        response = tree.xpath(query)
        if len(response) > 0:
            return response
        return None

    def get_webdriver(self):
        options = webdriver.ChromeOptions()
        # PROXY = "92.255.7.162:8080"
        # chrome_options.add_argument('--proxy-server=%s' % PROXY)
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-infobars')
        #options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument("--incognito")
        options.add_argument(f"--user-agent={random.choice(self.useragents)}")
        #chrome_options.add_argument('--disable-dev-shm-usage')

        #chrome_options.add_argument("enable-automation")
        #chrome_options.add_argument("--disable-dev-shm-usage")
        #chrome_options.add_argument("--disable-browser-side-navigation")

        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--window-size=%s" % self.WINDOW_SIZE)
        options.page_load_strategy = 'none'
        #chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        driver = uc.Chrome(options=options,
                           user_multi_procs=True,
                           driver_executable_path=os.environ['CHROMEDRIVER_PATH']
                           )
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
        data[KeysEnum.WEBSITE_ID.value] = self.website_db_id
        data[KeysEnum.CITY_ID.value] = self.city_db_id
        data[KeysEnum.LISTING_TYPE_ID.value] = self.listing_type_db_id
        requests.post(self.db_flow_url+'/saveListing', json=data)

    def delete_webdriver(self, driver):
        driver.close()
        # driver.delete_all_cookies()
        # driver.execute_script("window.localStorage.clear();")
        # driver.execute_script("window.sessionStorage.clear();")
        driver.quit()
        if hasattr(driver, "service") and getattr(driver.service, "process", None):
            driver.service.process.wait(3)
        os.waitpid(driver.browser_pid, 0)

    def parse_offer(self, offer):
        pass
