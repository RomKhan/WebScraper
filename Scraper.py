import asyncio
import os
import random

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import undetected_chromedriver as uc
from bs4 import BeautifulSoup, SoupStrainer
import time
import re
from PIL import Image
from io import BytesIO
from lxml import etree
import threading


class Scraper:
    def __init__(self, url_components, link_token, pics_folder, image_loader, data_saver, prev_address = None):
        self.url_components = url_components
        self.WINDOW_SIZE = "1920,1080"
        self.link_token = link_token
        self.prev_address = prev_address
        self.pics_folder = pics_folder
        self.image_loader = image_loader
        self.data_saver = data_saver
        self.links = {}
        self.previous_idx = set()
        self.main_page_load_indicator = ''
        self.by_settings = By.XPATH
        self.current_page = 1
        self.is_first_run = True

    def run(self):
        driver = self.get_webdriver()

        future_previous_idx = set()
        for i in range(10):
            if self.is_first_run and i > 1:
                self.is_first_run = False
                break
            url = self.get_link_by_page()
            self.run_driver_on_main_page(url, driver)
            soup = self.get_soap(driver.page_source)
            links = self.get_offer_links(soup)
            idx = set(links.keys())

            if i == 0:
                future_previous_idx = idx

            idx = idx.difference(self.previous_idx)
            for id in idx:
                self.links[id] = links[id]

            self.current_page += 1
            if i == 9:
                print('Я взял обявления с 10 страниц')
            if len(idx) != len(set(links.keys())):
                break

        print(f'Пытаюсь спарсить {len(self.links)} обявлений')
        self.current_page = 1
        self.previous_idx = future_previous_idx
        self.get_offers_data(driver)

        driver.close()
        driver.quit()

    def run_driver_on_main_page(self, url, driver):
        try:
            driver.get(url)
            WebDriverWait(driver, timeout=150).until(
                EC.presence_of_element_located((self.by_settings, self.main_page_load_indicator)))
        except Exception as e:
            print('error here', url)

    def get_link_by_page(self) -> str:
        pass

    def parse_if_exists(self, tree, query):
        response = tree.xpath(query)
        if len(response) > 0:
            return response
        return None

    def screenshots_merge(self, sceenshot_1, sceenshot_2, sceenshot_3, name):
        sceenshot_1 = Image.open(BytesIO(sceenshot_1))
        sceenshot_2 = Image.open(BytesIO(sceenshot_2))
        sceenshot_3 = Image.open(BytesIO(sceenshot_3))

        new_im = Image.new('RGB', (sceenshot_1.size[0], sceenshot_1.size[1] * 3), (250, 250, 250))
        new_im.paste(sceenshot_1, (0, 0))
        new_im.paste(sceenshot_2, (0, sceenshot_1.size[1]))
        new_im.paste(sceenshot_3, (0, sceenshot_1.size[1] * 2))
        new_im.save(f"{self.pics_folder}{os.sep}{name}.png", "PNG")

    def save_screenshot(self, link, id, driver):
        #driver = self.get_webdriver()
        driver.get(link)
        sceenshot_1 = driver.get_screenshot_as_png()
        driver.execute_script("window.scrollTo(0, 1080)")
        sceenshot_2 = driver.get_screenshot_as_png()
        driver.execute_script("window.scrollTo(0, 2160)")
        sceenshot_3 = driver.get_screenshot_as_png()
        driver.execute_script("window.scrollTo(0, 0)")
        self.screenshots_merge(sceenshot_1, sceenshot_2, sceenshot_3, id)
        #driver.close()
        #driver.quit()

    def get_offer_data(self, link, id, driver):
        pass

    def get_offers_data(self, driver):
        idx = list(self.links.keys())
        for id in idx:
            t1 = time.time()
            link, errors = self.links.pop(id)
            if not self.get_offer_data(link, id, driver) and errors < 10:
                self.links[id] = (link, errors + 1)
            t2 = time.time()
            if t2-t1 < 8:
                time.sleep(random.randint(5, 8))
            t2 = time.time()
            print(f'Парсинг обьявления {link} занял {t2-t1} секунд')

            #driver.switch_to.new_window('tab')
            #thread = threading.Thread(target=self.save_screenshot, args=(links[i], idx[i], driver))
            #thread.start()
            #asyncio.run(self.save_screenshot(links[i], idx[i], driver))
            #self.save_screenshot(links[i], idx[i], driver)
            #driver.get(links[i])
            #time.sleep(5)
            #WebDriverWait(driver, timeout=100).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-page')))
            #content = driver.page_source
            #soup = BeautifulSoup(content, features="html.parser")
            #dom = etree.HTML(str(soup))
            #print(dom.xpath("//div[@class='l2ytJ']/span")[0].text)
            #driver.get_screenshot_as_file(f"{self.pics_folder}{os.sep}{idx[i]}.png")

    def get_offer_links(self, soup):
        links = {}
        for link in soup:
            if link.has_attr('href') and self.link_token in link['href']:
                id = list(filter(None, re.split('_|/', link['href'])))[-1]
                if re.match('^[0-9]{5,}', id):
                    if self.prev_address is not None:
                        links[id] = (self.prev_address + link['href'], 0)
                    else:
                        links[id] = (link['href'], 0)
        return links

    def get_soap(self, content):
        soup = BeautifulSoup(content, parse_only=SoupStrainer('a'), features="html.parser")
        return soup

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
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        driver = uc.Chrome(options=chrome_options, user_multi_procs=True)
        #driver = webdriver.Chrome(options=chrome_options)
        return driver

    async def parse_offer_page(self, content, link, id):
        pass

    @staticmethod
    def parse_link(url):
        pass