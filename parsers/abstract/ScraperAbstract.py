import logging
from enum import Enum

import aiohttp
import requests
from KeysEnum import KeysEnum


class ListingMode(Enum):
    rent = 0
    sale = 1


class ScraperAbstract:
    def __init__(self, website_name, city, listing_type):
        self.WINDOW_SIZE = "1920,1080"
        self.current_page = 1
        self.db_flow_url = 'http://db-api-service:8080/db'
        self.chrome_service = 'http://api-getaway-service:8083/'
        self.website_name = website_name
        self.website_db_id = requests.get(self.db_flow_url+'/getWebsiteId', params={'website': website_name}).text
        self.city_db_id = requests.get(self.db_flow_url+'/getCityId', params={'city': city}).text
        self.listing_type_db_id = requests.get(self.db_flow_url+'/getListingTypeId', params={'listing_type': listing_type}).text
        # self.previous_idx = set()
        self.count_of_requests = 0

    def reserve_pods(self):
        pods = []
        try:
            response = requests.get(f"{self.chrome_service}/reservePod", json={'website': self.website_name})
            if response.status_code == 200:
                data = response.json()
                for i in range(len(data['pods'])):
                    pods.append((data['pods'][i], data['keys'][i]))
        except:
            pass
        return pods


    def get_page(self, url, pod, key):
        status = False
        page_source = None
        try:
            response = requests.get(f"{self.chrome_service}/getPage", json={
                'url': url, 'website': self.website_name, 'pod_id': pod, 'key': key})
            self.count_of_requests += 1
            if response.status_code == 200 or 201:
                page_source = response.text
                status = True
        except:
            pass

        return page_source, status

    def parse_if_exists(self, tree, query):
        response = tree.xpath(query)
        if len(response) > 0:
            return response
        return None

    # def get_webdriver(self):
    #     options = webdriver.ChromeOptions()
    #     # PROXY = "92.255.7.162:8080"
    #     # chrome_options.add_argument('--proxy-server=%s' % PROXY)
    #     options.add_argument('--headless')
    #     options.add_argument('--no-sandbox')
    #     options.add_argument('--disable-gpu')
    #     options.add_argument('--disable-dev-shm-usage')
    #     options.add_argument('--disable-infobars')
    #     #options.add_argument('--disable-features=VizDisplayCompositor')
    #     options.add_argument("--incognito")
    #     options.add_argument(f"--user-agent={random.choice(self.useragents)}")
    #     #chrome_options.add_argument('--disable-dev-shm-usage')
    #
    #     #chrome_options.add_argument("enable-automation")
    #     #chrome_options.add_argument("--disable-dev-shm-usage")
    #     #chrome_options.add_argument("--disable-browser-side-navigation")
    #
    #     options.add_argument('--disable-blink-features=AutomationControlled')
    #     options.add_argument("--window-size=%s" % self.WINDOW_SIZE)
    #     options.page_load_strategy = 'none'
    #     #chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    #     driver = uc.Chrome(options=options,
    #                        user_multi_procs=True,
    #                        driver_executable_path=os.environ['CHROMEDRIVER_PATH']
    #                        )
    #     #driver = webdriver.Chrome(options=chrome_options)
    #     return driver

    def get_desk_link(self) -> str:
        pass

    @staticmethod
    def parse_link(url):
        pass

    def get_soap(self, content):
        pass

    def to_database(self, offers):
        for offer in offers:
            offer[KeysEnum.WEBSITE_ID.value] = self.website_db_id
            offer[KeysEnum.CITY_ID.value] = self.city_db_id
            offer[KeysEnum.LISTING_TYPE_ID.value] = self.listing_type_db_id

        try:
            request_text = requests.post(self.db_flow_url+'/saveListing', json={'offers': offers}).text
            inserted_rows = int(request_text)
        except:
            inserted_rows = -1
        return inserted_rows

    # def delete_webdriver(self, driver):
    #     driver.close()
    #     # driver.delete_all_cookies()
    #     # driver.execute_script("window.localStorage.clear();")
    #     # driver.execute_script("window.sessionStorage.clear();")
    #     driver.quit()
    #     if hasattr(driver, "service") and getattr(driver.service, "process", None):
    #         driver.service.process.wait(3)
    #     os.waitpid(driver.browser_pid, 0)

    def parse_offer(self, offer):
        pass

