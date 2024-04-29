import logging
import threading

import time
from lxml import html

from abstract.ScraperAbstract import ScraperAbstract
# from parsers.abstract.ScraperAbstract import ScraperAbstract

url_queue = []

class Scraper(ScraperAbstract):
    def __init__(self, url_components, link_token, website_name, city, listing_type, offers_xpath, max_page, prev_address = None, is_shallow_images=False):
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
        self.is_shallow_images = is_shallow_images

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

            if self.status and page_source:
                links = self.get_offer_links(page_source)
                idx = set(links.keys())
                if len(links) == 0:
                    errors += 1
                    continue
                errors = 0
                current_idx |= idx
                idx = idx - self.previous_idx
                for id in idx:
                    if links[id] not in url_queue:
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

    def get_offer_data(self, url, id, images, attempts, pod, key):
        page_source, self.status = self.get_page(url, pod, key)
        if self.status:
            is_parsed = self.parse_offer_page(page_source, url, id, images)
            if not is_parsed:
                url_queue.append([self, url, id, images, attempts + 1])
        else:
            url_queue.append([self, url, id, images, attempts + 1])

    @staticmethod
    def get_offers_data():
        count = 0
        while True:
            if count >= 100:
                logging.info(f'Количество обьявлений в очереди: {len(url_queue)}')
                count = 0
            else:
                count += 1
            if len(url_queue) > 0:
                parser, url, id, images, attempts = url_queue.pop(0)
                pod = parser.reserve_pods(count=1)[0]
                if attempts < 5:
                    thread = threading.Thread(target=parser.get_offer_data, args=(url, id, images, attempts, pod[0], pod[1]))
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
                images = None
                link, id = self.get_link(offer)
                if self.is_shallow_images:
                    images = self.get_images(offer)
            except Exception as e:
                logging.info(f'Can\'t parse offer due this error: {e}')
                continue
            if self.prev_address is not None:
                links[id] = (self, self.prev_address + link, id, images, 0)
            else:
                links[id] = (self, link, id, images, 0)
        return links

    def get_link(self, offer):
        pass

    def get_images(self, offer):
        pass

    def parse_offer_page(self, content, link, id, images=None):
        pass