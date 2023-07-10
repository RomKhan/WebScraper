import re

import unidecode
from selenium.webdriver.common.by import By
from lxml import html

from abstract.ScrapeAll import ScrapeAll
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AvitoScrapeAll(ScrapeAll):
    def __init__(self, url_components, website_name, city, listing_type):
        ScrapeAll.__init__(self, By.CSS_SELECTOR, "span[class^='page-title-count']", url_components, 3500, 5000, 50, website_name, city, listing_type, 15)

    def parse_page(self, link, content):
        tree = html.fromstring(content)
        idx = set()
        try:
            offers = tree.xpath("//div[@data-marker='item' and parent::div[(contains(@class, 'items-items'))]]")
            corrupt_offers = 0
            for offer in offers:
                data, id = self.parse_offer(offer)
                if not data:
                    corrupt_offers += 1
                    self.count_of_corrupted += 1
                    continue
                idx.add(id)
                self.to_database(data)
            self.count_of_parsed += len(offers) - corrupt_offers
        except Exception as e:
            print(e, link)
            return None
        return idx

    def parse_offer(self, offer):
        residential_complex = None
        try:
            link = offer.xpath('.//a[@itemprop="url"]')[0].get('href')
            adress = offer.xpath(".//div[@data-marker='item-address']/*/p")
            if len(adress) > 2:
                residential_complex = adress[0].text
                adress = adress[1].xpath('.//span/text()')[0].replace('\'', '"')
            else:
                adress = adress[0].xpath('.//span/text()')[0].replace('\'', '"')
            id = list(filter(None, re.split('_|/', link)))[-1]
        except:
            return False, None
        price = None
        rooms_count = None
        house_type = None
        total_square = None
        description = None
        name = None
        flat_flour = None
        max_flours = None
        try:
            rooms_count, house_type, total_square, flat_flour, max_flours = self.parse_title(offer)
            price = offer.xpath('.//meta[@itemprop="price"]')[0].get('content')
            description_block = offer.xpath('.//div[contains(@class, "item-description")]/p/text()')
            if len(description_block) > 0:
                description = description_block[0].replace('\'', '"')
            user_atag = self.parse_if_exists(offer, './/div[contains(@class, "item-sellerInfo")]/div[contains(@class, "item-userInfo")]/*/a/p/text()')
            if user_atag is not None:
                name = user_atag[0].replace('\'', '"')
        except Exception as e:
            logging.warning(
                f'can\'t parse listing, link: {link}, error: {e}'
            )


        offer_data = {'id': id,
                      'Цена': price,
                      'Число комнат': rooms_count,
                      'Тип жилья': house_type,
                      'Общая площадь': total_square,
                      'Адресс': adress,
                      'Описание': description,
                      'Ссылка': link,
                      'Название продаца': name,
                      'Этаж квартиры': flat_flour,
                      'Этажей в доме': max_flours,
                      'Название ЖК': residential_complex}
        return offer_data, id



    def parse_title(self, offer):
        title = offer.xpath('.//h3[@itemprop="name"]/text()')[0].split(',')
        if len(title) == 4:
            temp = title.pop(1)
            title[1] = ','.join([temp, title[1]])
        if title[0][0].isdigit():
            rooms_count = title[0].split('-')
            house_type = title[0].split()[1]
        else:
            rooms_count = '0'
            house_type = title[0]
        total_square = title[1].split()[0]
        flat_flour, max_flours = title[2].split()[0].split('/')
        return rooms_count, house_type, total_square, flat_flour, max_flours


    def get_count_of_offers(self, content) -> int:
        tree = html.fromstring(content)
        try:
            offer_count_text = ''.join(unidecode.unidecode(tree.xpath("//span[starts-with(@class, 'page-title-count')]/text()")[0]).split())
        except:
             return -1
        return int(offer_count_text)

    def get_desk_link(self) -> str:
        if self.current_page < 2 and self.prev_price == 0:
            return f'{self.url_components[0]}&pmax={self.prev_price + self.step}&{self.url_components[1]}'
        elif self.current_page < 2:
            return f'{self.url_components[0]}&pmax={self.prev_price + self.step}&pmin={self.prev_price}&{self.url_components[1]}'
        elif self.prev_price == 0:
            return f'{self.url_components[0]}&pmax={self.prev_price + self.step}&p={self.current_page}&{self.url_components[1]}'
        return f'{self.url_components[0]}&pmax={self.prev_price + self.step}&pmin={self.prev_price}&p={self.current_page}&{self.url_components[1]}'

    @staticmethod
    def parse_link(url):
        data = url.split('&')
        first_part = []
        for i in range(len(data)):
            if data[i][0] == 'p':
                break
            first_part.append(data[i])

        first_part = '&'.join(first_part)
        second_part = data[-1]

        return [first_part, second_part]