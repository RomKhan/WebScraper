import random
import time

from lxml import html

from KeysEnum import KeysEnum
from abstract.ScraperAbstract import ScraperAbstract
import logging


logging.basicConfig(level=logging.INFO, format='%(message)s')


class ScrapeAll(ScraperAbstract):
    def __init__(self,
                 by_settings,
                 page_load_indicator,
                 url_components,
                 min_offers,
                 max_offers,
                 offers_per_page,
                 website_name,
                 city,
                 listing_type,
                 optimal_timeout,
                 offers_xpath):
        ScraperAbstract.__init__(self, by_settings, page_load_indicator, website_name, city, listing_type, 10)
        self.url_components = url_components
        self.prev_price = 0
        self.min_offers = min_offers
        self.max_offers = max_offers
        self.offers_per_page = offers_per_page
        self.last_offers_count = 0
        self.is_end = False

        self.count_of_parsed = 0
        self.count_of_requests = 0
        self.count_of_corrupted = 0
        self.prev_count_of_lisitngs = -1
        self.optimal_timeout = optimal_timeout
        self.offers_xpath = offers_xpath

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

    def iter(self):
        self.current_page = 1
        # driver = self.get_webdriver()
        offers_count, page_source = self.set_step()
        self.prev_count_of_lisitngs = offers_count
        if self.is_end:
            return

        url = self.get_desk_link()
        self.previous_idx, _ = self.parse_page(url, content=page_source)
        self.last_offers_count = offers_count
        self.current_page += 1
        prev_price = self.prev_price

        while offers_count > 0:
            url = self.get_desk_link()

            t1 = time.time()
            logging.info('Send Request')
            page_source = self.get_page(url)
            logging.info('Get page')
            self.count_of_requests += 1
            # t2 = time.time()
            # if t2 - t1 < self.optimal_timeout:
            #     time.sleep(random.randint(self.optimal_timeout - 3, self.optimal_timeout))

            idx, last_price = self.parse_page(url, content=page_source)
            # if last_price == 0:
            #     time.sleep(5)
            #     idx, last_price = self.parse_page(url, content=driver.page_source)

            idx_diff = len(idx - self.previous_idx)

            if last_price is not None and last_price > prev_price:
                prev_price = last_price

            if self.current_page < 3:
                idx_diff = 1

            self.current_page += 1

            t2 = time.time()
            logging.info(
                f'Parsed {self.count_of_parsed},'
                f'taken {t2 - t1} seconds,'
                f'send {self.count_of_requests} requests,'
                f'Can\'t parse {self.count_of_corrupted} offers, '
                f'url: {url}'
            )

            if idx_diff == 0:
                self.prev_price = prev_price
                break

        # self.delete_webdriver(driver)

    def update_prev_price(self, new_price):
        self.prev_price = int(new_price)

    def parse_page(self, link, content):
        t1_test = time.time()
        tree = html.fromstring(content)
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
                self.to_database(data)
            except Exception as e:
                print(e, link)

        self.count_of_parsed += len(offers) - corrupt_offers
        t2_test = time.time()
        logging.info(t2_test - t1_test)
        return idx, last_price

    def get_price_windows(self):
        pass

    def get_count_of_offers(self, content) -> int:
        pass

