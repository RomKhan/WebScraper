import random
import time

from bs4 import BeautifulSoup, SoupStrainer
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ScraperAbstract import ScraperAbstract


class ScrapeAll(ScraperAbstract):
    def __init__(self, by_settings, page_load_indicator, data_saver, url_components, min_offers, max_offers, offers_per_page, website_name, city, listing_type):
        ScraperAbstract.__init__(self, by_settings, page_load_indicator, data_saver, website_name, city, listing_type, 10)
        self.url_components = url_components
        self.prev_price = 0
        self.step = 1000000
        self.min_offers = min_offers
        self.max_offers = max_offers
        self.offers_per_page = offers_per_page
        self.last_offers_count = 0
        self.is_end = False

        self.count_of_parsed = 0
        self.count_of_requests = 0
        self.count_of_corrupted = 0

    def set_step(self, driver):
        issuie_count = 0
        while True:
            t1 = time.time()
            url = self.get_desk_link()
            self.run_driver_on_page(url, driver)
            self.count_of_requests += 1
            offers_count = self.get_count_of_offers(driver.page_source)
            if offers_count == -1:
                if issuie_count > 5:
                    break
                else:
                    issuie_count += 1
                    time.sleep(5)
                    continue
            if offers_count == 0 and self.last_offers_count != 0:
                self.is_end = True
                break
            if offers_count > self.min_offers and offers_count < self.max_offers:
                break
            elif offers_count <= self.min_offers:
                self.step = round(self.step + int(self.step/2), -3)
            elif offers_count >= self.max_offers:
                self.step = round(self.step - int(self.step/2), -3)
            t2 = time.time()
            if t2-t1 < 8:
                time.sleep(random.randint(5, 8))

        return offers_count

    def reset_iter(self):
        self.prev_price = 0
        self.step = 1000000

    def iter(self):
        self.current_page = 1
        driver = self.get_webdriver()
        offers_count = self.set_step(driver)
        if self.is_end:
            return

        url = self.get_desk_link()
        self.parse_page(url, content=driver.page_source)
        self.last_offers_count = offers_count
        self.current_page += 1
        offers_count -= self.offers_per_page

        while offers_count > 0:
            t1 = time.time()
            url = self.get_desk_link()
            print(f'Parse {url}')

            is_correct = False
            issue_count = 5
            while not is_correct or issue_count > 5:
                is_correct = self.run_driver_on_page(url, driver)
                issue_count -= 1
                self.count_of_requests += 1

            idx = self.parse_page(url, content=driver.page_source)
            self.current_page += 1
            offers_count -= self.offers_per_page
            idx_diff = len(idx - self.previous_idx)
            self.previous_idx = idx
            if not is_correct:
                idx_diff = 1

            t2 = time.time()
            if t2-t1 < 8:
                time.sleep(random.randint(5, 8))
            t2 = time.time()
            print(f'Parsed {self.count_of_parsed},'
                  f'taken {t2 - t1} seconds,'
                  f'send {self.count_of_requests} requests,'
                  f'Can\'t parse {self.count_of_corrupted} offers')

            if idx_diff == 0:
                break

        self.prev_price += self.step
        driver.close()
        driver.quit()

    def parse_page(self, link, content):
        pass

    def get_count_of_offers(self, content) -> int:
        pass

