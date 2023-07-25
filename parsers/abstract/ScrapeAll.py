import random
import threading
import time

from lxml import html

from KeysEnum import KeysEnum
from abstract.ScraperAbstract import ScraperAbstract
import logging


logging.basicConfig(level=logging.INFO, format='%(message)s')


class ScrapeAll(ScraperAbstract):
    def __init__(self,
                 url_components,
                 website_name,
                 city,
                 listing_type,
                 offers_xpath):
        ScraperAbstract.__init__(self, website_name, city, listing_type)
        self.url_components = url_components
        self.prev_price = 0
        self.current_price = 0
        self.last_offers_count = 0
        self.is_end = False

        self.count_of_parsed = 0
        self.count_of_corrupted = 0
        self.prev_count_of_lisitngs = -1
        self.offers_xpath = offers_xpath
        self.status = True
        self.url_queue = []

    def set_step(self):
        issuie_count = 0
        while True:
            url = self.get_desk_link()
            page_source = self.get_page(url)
            self.count_of_requests += 1
            offers_count = self.get_count_of_offers(page_source)
            if offers_count == -1 or self.prev_count_of_lisitngs == offers_count:
                if issuie_count > 5:
                    break
                else:
                    issuie_count += 1
                    continue
            if offers_count == 0 and self.last_offers_count != 0:
                self.is_end = True
                break
            break

        return offers_count, page_source

    def reset_iter(self):
        self.prev_price = 0

    def get_and_parse_page(self, url, attempts, page, pod, key):
        t1 = time.time()
        page_source, self.status = self.get_page(url, pod, key)
        if self.status:
            idx, last_price = self.parse_page(url, content=page_source)
            if len(self.previous_idx) == 0 and page == 1:
                self.previous_idx = idx

            if last_price is not None and last_price > self.current_price:
                self.current_price = last_price

            idx_diff = len(idx - self.previous_idx)
            if idx_diff == 0 and page > 1:
                self.prev_price = self.current_price
                offers_count = self.get_count_of_offers(page_source)
                if offers_count == 0 and self.last_offers_count != 0:
                    self.is_end = True
                if offers_count > -1:
                    self.last_offers_count = offers_count

            t2 = time.time()
            logging.info(
                f'Parsed {self.count_of_parsed},'
                f'taken {t2 - t1} seconds,'
                f'send {self.count_of_requests} requests,'
                f'Can\'t parse {self.count_of_corrupted} offers, '
                f'url: {url}'
            )
        else:
            self.url_queue.append([url, attempts + 1, page])



    def iter(self):
        self.current_page = 1
        start_price = self.prev_price
        while self.prev_price == start_price:
            pods = self.reserve_pods()
            if len(pods) == 0:
                time.sleep(5)
                continue
            for pod in pods:
                url = self.get_desk_link()
                attempts = 0
                page = self.current_page
                self.current_page += 1
                if len(self.url_queue) > 0:
                    url_temp, attempts_temp, page_temp = self.url_queue.pop(0)
                    if attempts < 5:
                        url = url_temp
                        attempts = attempts_temp
                        page = page_temp
                        self.current_page -= 1

                thread = threading.Thread(target=self.get_and_parse_page, args=(url, attempts, page, pod[0], pod[1]))
                thread.start()


    def update_prev_price(self, new_price):
        self.prev_price = int(new_price)

    def parse_page(self, link, content):
        t1_test = time.time()
        tree = html.fromstring(content)
        offers_dict = []
        idx = set()
        last_price = 0

        offers = tree.xpath(self.offers_xpath)
        corrupt_offers = 0
        for offer in offers:
            try:
                data, id = self.parse_offer(offer)
                if not data:
                    corrupt_offers += 1
                    self.count_of_corrupted += 1
                    continue
                idx.add(id)
                last_price = int(data[KeysEnum.PRICE.value])
                offers_dict.append(data)
            except Exception as e:
                print(e, link)

        self.count_of_parsed += len(offers) - corrupt_offers
        # threading.Thread(self.to_database, args=(offers_dict)).start()
        self.to_database(offers_dict)
        t2_test = time.time()
        logging.info(t2_test - t1_test)
        return idx, last_price

    def get_price_windows(self):
        pass

    def get_count_of_offers(self, content) -> int:
        pass

