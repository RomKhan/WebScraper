import re

import unidecode
from selenium.webdriver.common.by import By
from lxml import html

from ScrapeAll import ScrapeAll

class CianScrapeAll(ScrapeAll):
    def __init__(self, url_components, data_saver, website_name, city, listing_type):
        ScrapeAll.__init__(self, By.XPATH, '//div[@data-name="SummaryHeader"]', data_saver, url_components, 1000, 1500, 28, website_name, city, listing_type)

    def parse_page(self, link, content):
        tree = html.fromstring(content)
        idx = set()
        try:
            offers = tree.xpath('//article[@data-name="CardComponent"]')
            corrupt_offers = 0
            for offer in offers:
                data, id = self.parse_offer(offer)
                if data == False:
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
        link_area = offer.xpath('.//div[@data-name="LinkArea"]')
        try:
            link = link_area[0].xpath('.//a')[0].get('href')
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
        try:
            rooms_count, house_type, total_square, flat_flour, max_flours = self.parse_title(link_area[0])
            adress = ' '.join(link_area[0].xpath(".//a[@data-name='GeoLabel']/text()")).replace('\'', '"')
            price = ''.join(unidecode.unidecode(link_area[0].xpath('.//span[@data-mark="MainPrice"]/span/text()')[0][:-2]).split())
            description_block = link_area[0].xpath('.//div[@data-name="Description"]/p/text()')
            if len(description_block) > 0:
                description = description_block[0]
            link_area[1] = link_area[1].xpath('.//div[@data-name="BrandingLevelWrapper"]')[0]
            trader_container = link_area[1].xpath('.//div[contains(@class, "content")]')[0]
            trader_data = trader_container.xpath('.//span/text()')
            if len(trader_data) == 1:
                name = trader_data[0]
            else:
                trader_type, name = trader_data[:2]
            # trader_id = trader_container.xpath('.//a')
            # if len(trader_id) > 0:
            #     trader_id = trader_id[0].get('href').split('/')[-1]
            # else:
            #     trader_id = name.split()[1]
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
                      'Этажей в доме': max_flours}
        return offer_data, id



    def parse_title(self, link_area):
        title = link_area.xpath('.//span[@data-mark="OfferTitle"]/span/text()')[0].split()
        if title[-1] != 'этаж':
            title = link_area.xpath('.//span[@data-mark="OfferSubtitle"]/text()')
        if len(title) == 0 or title[-1] != 'этаж':
            return None, None, None, None, None
        if len(title) < 6:
            rooms_count = '0'
            house_type = title[0][:-1]
            total_square = title[1]
            flat_flour, max_flours = title[3].split('/')
        else:
            rooms_count = title[0][0]
            house_type = title[1][:-1]
            total_square = title[2]
            flat_flour, max_flours = title[4].split('/')
        return rooms_count, house_type, total_square, flat_flour, max_flours


    def get_count_of_offers(self, content) -> int:
        tree = html.fromstring(content)
        try:
            offer_count_text = tree.xpath("//div[@data-name='SummaryHeader']/h5/text()")[0].split()
        except:
             return 0
        return int(''.join(offer_count_text[1:-1]))

    def get_desk_link(self) -> str:
        if self.current_page < 2 and self.prev_price == 0:
            return f'{self.url_components[0]}&maxprice={self.prev_price + self.step}&{self.url_components[1]}&{self.url_components[2]}'
        elif self.current_page < 2:
            return f'{self.url_components[0]}&maxprice={self.prev_price + self.step}&minprice={self.prev_price}&{self.url_components[1]}&{self.url_components[2]}'
        elif self.prev_price == 0:
            return f'{self.url_components[0]}&maxprice={self.prev_price + self.step}&{self.url_components[1]}&p={self.current_page}&{self.url_components[2]}'
        return f'{self.url_components[0]}&maxprice={self.prev_price + self.step}&minprice={self.prev_price}&{self.url_components[1]}&p={self.current_page}&{self.url_components[2]}'

    @staticmethod
    def parse_link(url):
        data = url.split('&')
        first_part = []
        for i in range(len(data)):
            if data[i][0] == 'p':
                break
            elif data[i][0:2] == 'ma':
                break
            elif data[i][0:2] == 'mi':
                break
            first_part.append(data[i])

        first_part = '&'.join(first_part)
        second_part = '&'.join(data[i + 2:i + 3])
        third_part = '&'.join(data[i + 4:])

        return [first_part, second_part, third_part]