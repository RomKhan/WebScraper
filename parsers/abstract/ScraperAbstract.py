import logging
import time
from enum import Enum
import requests
from KeysEnum import KeysEnum
# from parsers.KeysEnum import KeysEnum


class ScraperAbstract:
    def __init__(self, website_name, city, listing_type, max_page):
        self.current_page = 1
        self.max_page = max_page
        self.db_flow_url = 'http://db-api-service:8080/db'
        self.chrome_service = 'http://api-getaway-service:8083'
        # self.db_flow_url = 'http://localhost:30006/db'
        # self.chrome_service = 'http://localhost:30731'
        self.website_name = website_name
        self.listing_type = listing_type
        self.city = city
        self.website_db_id = int(requests.get(self.db_flow_url+'/getWebsiteId', params={'website': website_name}).text.strip('"'))
        self.city_db_id = int(requests.get(self.db_flow_url+'/getCityId', params={'city': city}).text.strip('"'))
        self.listing_type_db_id = int(requests.get(self.db_flow_url+'/getListingTypeId', params={'listing_type': listing_type}).text.strip('"'))
        self.count_of_requests = 0

    def reserve_pods(self, count):
        pods = []
        while True:
            try:
                response = requests.get(f"{self.chrome_service}/reservePod", json={'website': self.website_name, 'count': count})
                if response.status_code == 200:
                    data = response.json()
                    for i in range(len(data['pods'])):
                        pods.append((data['pods'][i], data['keys'][i]))
            except:
                pass

            if len(pods) == 0:
                time.sleep(2)
            else:
                break
        return pods


    def get_page(self, url, pod, key):
        status = False
        page_source = None
        try:
            response = requests.get(f"{self.chrome_service}/getPage", json={
                'url': url, 'website': self.website_name, 'pod_id': pod, 'key': key})
            self.count_of_requests += 1
            if response.status_code == 200 or 201:
                response.encoding = "utf-8"
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

    def to_database(self, offers):
        if len(offers) == 0:
            return 0
        for offer in offers:
            offer[KeysEnum.LISTING_ID.value] = f'{offer[KeysEnum.LISTING_ID.value]}_{self.website_db_id}_{self.listing_type_db_id}_{self.city_db_id}'
            offer[KeysEnum.WEBSITE_ID.value] = self.website_db_id
            offer[KeysEnum.CITY_ID.value] = self.city_db_id
            offer[KeysEnum.LISTING_TYPE_ID.value] = self.listing_type_db_id

        try:
            request_text = requests.post(self.db_flow_url+'/saveListing', json={'offers': offers}).text
            inserted_rows = int(request_text.strip('"'))
        except:
            inserted_rows = -1
        return inserted_rows

    def save_images(self, id, urls):
        try:
            requests.post(self.db_flow_url+'/saveImages',
                          json={
                              'website_name': self.website_name,
                              'id': id,
                              'urls': urls
                          })
        except:
            logging.info('Произошла ошибка при сохранении картинок')

    def parse_offer(self, offer):
        pass

    def get_desk_link(self) -> str:
        pass

    @staticmethod
    def parse_link(url):
        pass

    def get_soap(self, content):
        pass


