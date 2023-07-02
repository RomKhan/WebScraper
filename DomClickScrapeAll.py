import re

import unidecode
from selenium.webdriver.common.by import By
from lxml import html

from ScrapeAll import ScrapeAll


class DomClickScrapeAll(ScrapeAll):
    def __init__(self, url_components, data_saver, website_name, city, listing_type):
        ScrapeAll.__init__(self, By.CLASS_NAME, 'app main-content', data_saver, url_components, 1500, 2000, 20, website_name, city, listing_type, 8)

    def parse_page(self, link, content):
        tree = html.fromstring(content)
        idx = set()
        try:
            offers = tree.xpath('//div[@data-e2e-id="offers-list__item"]')
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
        try:
            title = offer.xpath('.//a[@data-test="product-snippet-property-offer"]')[0]
            link = title.get('href')
            id = list(filter(None, re.split('_|/', link)))[-1]
        except:
            return False, None
        price = None
        rooms_count = None
        house_type = None
        total_square = None
        adress = None
        description = None
        trader_type = None
        name = None
        flat_flour = None
        max_flours = None
        residential_complex = None
        build_date = None
        try:
            rooms_count, house_type, total_square, flat_flour, max_flours = self.parse_title(title)
            adress = ' '.join(offer.xpath(".//span[@data-e2-id='product-snippet-address']/text()")).replace('\'', '"')
            price = ''.join(unidecode.unidecode(offer.xpath('.//div[@data-e2e-id="product-snippet-price-sale"]/p/text()')[0][:-2]).split())
            description_block = self.parse_if_exists(offer, './/a[@data-test="product-snippet-property-offer"]/../../div/div/text()')
            if description_block is not None:
                description = description_block[0]
            residential_data = self.parse_if_exists(offer, ".//div[@data-e2e-id='flat-complex-icon']/../../..")
            if residential_data is not None:
                residential_complex = residential_data[0].xpath('.//span/text()')[0]
                build_date_info = self.parse_if_exists(residential_data[0], './/div//div/text()')
                if build_date_info is not None and len(build_date_info[0].split()) > 1:
                    build_date = build_date_info[0].split()[-2]
            developer_info = self.parse_if_exists(offer, ".//div[@data-e2e-id='product-snippet-developer']/span/text()")
            if developer_info is not None:
                trader_type = 'Застройщик'
                name = developer_info[0]
        except Exception as e:
            print(e)
            print('не получилось полностью спарсить обьявление')


        offer_data = {'id': id,
                      'Цена': price,
                      'Число комнат': rooms_count,
                      'Тип жилья': house_type,
                      'Общая площадь': total_square,
                      'Адресс': adress,
                      'Описание': description,
                      'Ссылка': link,
                      'Тип продаца': trader_type,
                      'Название продаца': name,
                      'Этаж квартиры': flat_flour,
                      'Этажей в доме': max_flours,
                      'Название ЖК': residential_complex,
                      'Год сдачи': build_date}
        return offer_data, id



    def parse_title(self, title):
        title = title.xpath('.//span/text()')
        if title[0][0].isdigit():
            rooms_count = title[0].split()[0].split('-')[0]
            house_type = title[0].split()[0].split('-')[1]
        else:
            rooms_count = 0
            house_type = title[0]
        total_square = title[1].split()[0]
        flat_flour, max_flours = title[2].split()[0].split('/')
        return rooms_count, house_type, total_square, flat_flour, max_flours


    def get_count_of_offers(self, content) -> int:
        tree = html.fromstring(content)
        try:
            offer_count_text = tree.xpath("//div[@data-e2e-id='offers-count']/text()")[0].split()
        except:
             return -1
        return int(''.join(offer_count_text[:-1]))

    def get_desk_link(self) -> str:
        if self.current_page < 2 and self.prev_price == 0:
            return f'{self.url_components[0]}&sale_price__lte={self.prev_price + self.step}&{self.url_components[1]}&offset=0'
        elif self.current_page < 2:
            return f'{self.url_components[0]}&sale_price__lte={self.prev_price + self.step}&{self.url_components[1]}&sale_price__gte={self.prev_price}&offset=0'
        elif self.prev_price == 0:
            return f'{self.url_components[0]}&sale_price__lte={self.prev_price + self.step}&{self.url_components[1]}&offset={(self.current_page - 1) * 20}'
        return f'{self.url_components[0]}&sale_price__lte={self.prev_price + self.step}&{self.url_components[1]}&sale_price__gte={self.prev_price}&offset={(self.current_page - 1)* 20}'

    @staticmethod
    def parse_link(url):
        data = url.split('&')
        first_part = []
        for i in range(len(data)):
            if data[i].startswith('offset'):
                break
            elif data[i].startswith('sale_price__gte'):
                break
            elif data[i].startswith('sale_price__lte'):
                break
            first_part.append(data[i])

        first_part = '&'.join(first_part)
        second_part = '&'.join(data[i + 1:i + 3])

        return [first_part, second_part]
