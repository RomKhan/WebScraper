import logging
import random
import threading

from bs4 import BeautifulSoup, SoupStrainer
import time
import re

from abstract.ScraperAbstract import ScraperAbstract
# from parsers.abstract.ScraperAbstract import ScraperAbstract


class Scraper(ScraperAbstract):
    def __init__(self, url_components, link_token, website_name, city, listing_type, max_page, prev_address = None):
        ScraperAbstract.__init__(self, website_name, city, listing_type, max_page)
        self.url_components = url_components
        self.link_token = link_token
        self.prev_address = prev_address
        self.url_queue = []
        self.is_first_run = True
        self.previous_idx = set()
        self.offers = []
        self.parsed_count = 0

    def run(self):
        start_page_number = 1
        self.current_page = start_page_number
        current_idx = set()
        errors = 0
        while self.current_page <= self.max_page and len(self.previous_idx & current_idx) == 0:
            if self.is_first_run and self.current_page > start_page_number:
                self.is_first_run = False
                break
            pod, key = self.reserve_pods()[0]
            url = self.get_desk_link()
            page_source, self.status = self.get_page(url, pod, key)

            if self.status:
                links = self.get_offer_links(page_source)
                idx = set(links.keys())
                if len(links) == 0:
                    errors += 1
                    continue
                errors = 0
                if self.current_page == start_page_number:
                    current_idx = idx
                idx = idx - self.previous_idx
                for id in idx:
                    self.url_queue.append(links[id])
                self.current_page += 1
                if len(idx) != len(set(links.keys())):
                    break
            elif errors < 5:
                errors += 1
                continue
            else:
                break

        logging.info(f'Собираюсь спарсить {len(self.url_queue)} обьявлений')
        if len(current_idx) > 0:
            self.previous_idx = current_idx
        # thread = threading.Thread(target=self.get_offers_data)
        # thread.start()
        self.get_offers_data()

    def get_offer_data(self, url, id, attempts, pod, key):
        page_source, self.status = self.get_page(url, pod, key)
        if self.status:
            is_parsed = self.parse_offer_page(page_source, url, id)
            if not is_parsed:
                self.url_queue.append([url, id, attempts + 1])
        else:
            self.url_queue.append([url, id, attempts + 1])

    def get_offers_data(self):
        while len(self.url_queue) > 0:
            pods = self.reserve_pods()
            for pod in pods:
                url, id, attempts = self.url_queue.pop(0)
                if attempts < 5:
                    thread = threading.Thread(target=self.get_offer_data, args=(url, id, attempts, pod[0], pod[1]))
                    thread.start()
        offers = self.offers
        self.offers = []
        self.to_database(offers)
        self.parsed_count += len(offers)
        logging.info(f'Отправил в бд {len(offers)} обьявлений, всего отправил - {self.parsed_count}')

    def get_offer_links(self, content):
        links = {}
        soup = BeautifulSoup(content, parse_only=SoupStrainer('a'), features="html.parser")
        for link in soup:
            if link.has_attr('href') and self.link_token in link['href']:
                id = list(filter(None, re.split('_|/', link['href'])))[-1]
                if re.match('^[0-9]{5,}', id):
                    if self.prev_address is not None:
                        links[id] = (self.prev_address + link['href'], id, 0)
                    else:
                        links[id] = (link['href'], id, 0)
        return links

    async def parse_offer_page(self, content, link, id):
        pass