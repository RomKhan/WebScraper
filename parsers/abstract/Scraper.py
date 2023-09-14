import logging
import random
import threading

from bs4 import BeautifulSoup, SoupStrainer
import time
import re
from lxml import html

# from abstract.ScraperAbstract import ScraperAbstract
from parsers.abstract.ScraperAbstract import ScraperAbstract

url_queue = []

class Scraper(ScraperAbstract):
    def __init__(self, url_components, link_token, website_name, city, listing_type, offers_xpath, max_page, prev_address = None):
        ScraperAbstract.__init__(self, website_name, city, listing_type, max_page)
        self.url_components = url_components
        self.link_token = link_token
        self.prev_address = prev_address
        self.is_first_run = True
        self.previous_idx = set()
        self.offers = []
        self.parsed_count = 0
        self.offers_xpath = offers_xpath
        self.last_idx = []

    def run(self):
        start_page_number = 3
        self.current_page = start_page_number
        current_idx = set()
        errors = 0
        offers_count = 0
        while self.current_page <= self.max_page and len(self.previous_idx & current_idx) == 0:
            if self.current_page > 20:
                logging.info(f'Больше {self.current_page-1} стр парсим. previous_idx: {self.previous_idx}, last idx: {idx}')
            if self.is_first_run and self.current_page > start_page_number:
                self.is_first_run = False
                break
            pod, key = self.reserve_pods(count=1)[0]
            url = self.get_desk_link()
            page_source, self.status = self.get_page(url, pod, key)

            if self.status:
                links = self.get_offer_links(page_source)
                idx = set(links.keys())
                if len(links) == 0:
                    errors += 1
                    continue
                errors = 0
                current_idx |= idx
                idx = idx - self.previous_idx
                for id in idx:
                    url_queue.append(links[id])
                    offers_count += 1
                self.current_page += 1
                if len(idx) != len(set(links.keys())):
                    break
            elif errors < 5:
                errors += 1
                continue
            elif not self.status:
                break

        logging.info(f'Собираюсь спарсить {offers_count} обьявлений')
        if len(current_idx) > 0:
            self.last_idx.append(current_idx)
            if len(self.last_idx) > 10:
                self.last_idx.pop(0)
            self.previous_idx = set([x for idx in self.last_idx for x in idx])

    def get_offer_data(self, url, id, attempts, pod, key):
        page_source, self.status = self.get_page(url, pod, key)
        if self.status:
            is_parsed = self.parse_offer_page(page_source, url, id)
            if not is_parsed:
                url_queue.append([self, url, id, attempts + 1])
        else:
            url_queue.append([self, url, id, attempts + 1])

    @staticmethod
    def get_offers_data():
        while True:
            if len(url_queue) > 0:
                parser, url, id, attempts = url_queue.pop(0)
                pod = parser.reserve_pods(count=1)[0]
                if attempts < 5:
                    thread = threading.Thread(target=parser.get_offer_data, args=(url, id, attempts, pod[0], pod[1]))
                    thread.start()
                if len(parser.offers) > 50:
                    offers = parser.offers
                    parser.offers = []
                    parser.to_database(offers)
                    parser.parsed_count += len(offers)
                    logging.info(f'Отправил в бд {len(offers)} обьявлений, всего отправил - {parser.parsed_count}')
            else:
                time.sleep(60)


    def get_offer_links(self, content):
        links = {}
        tree = html.fromstring(content)
        offers = tree.xpath(self.offers_xpath)
        for offer in offers:
            try:
                link, id = self.get_link(offer)
            except:
                continue
            if self.prev_address is not None:
                links[id] = (self, self.prev_address + link, id, 0)
            else:
                links[id] = (self, link, id, 0)
        return links
        # links = {}
        # soup = BeautifulSoup(content, parse_only=SoupStrainer('a'), features="html.parser")
        # for link in soup:
        #     if link.has_attr('href') and self.link_token in link['href']:
        #         id = list(filter(None, re.split('_|/', link['href'])))[-1]
        #         if re.match('^[0-9]{5,}', id):
        #             if self.prev_address is not None:
        #                 links[id] = (self.prev_address + link['href'], id, 0)
        #             else:
        #                 links[id] = (link['href'], id, 0)
        # return links

    def get_link(self, offer):
        pass

    def parse_offer_page(self, content, link, id):
        pass