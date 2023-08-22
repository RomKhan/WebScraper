import re

import unidecode
from lxml import html

# from KeysEnum import KeysEnum
# from abstract.ScrapeAll import ScrapeAll
from parsers.KeysEnum import KeysEnum
from parsers.abstract.ScrapeAll import ScrapeAll
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CianScrapeAll(ScrapeAll):
    def __init__(self, url_components, city, website, listing_type, min_price):
        ScrapeAll.__init__(self,
                           url_components,
                           website,
                           city,
                           listing_type,
                           min_price,
                           offers_xpath='//article[@data-name="CardComponent"]',
                           max_page=54,
                           offers_per_page=28)

    def parse_offer(self, offer):
        link_area = offer.xpath('.//div[@data-name="LinkArea"]')
        try:
            link = link_area[0].xpath('.//a')[0].get('href')
            geo_data = link_area[0].xpath(".//a[@data-name='GeoLabel']/text()")
            address = ''
            for i in range(len(geo_data)-1):
                if geo_data[i].startswith("м. ") or geo_data[i].split()[0].isupper() or geo_data[i] == 'ЗелАО':
                    continue
                else:
                    address += geo_data[i].replace('\'', '"') + ', '
            address = address + geo_data[-1]
            # if not address.startswith('Москва'):
            #     logging.info(f'{address}')
            id = list(filter(None, re.split('_|/', link)))[-1]
        except:
            return False, None
        price = None
        rooms_count = None
        house_type = None
        total_square = None
        description = None
        trader_type = None
        name = None
        flat_flour = None
        max_flours = None
        residential_complex = None
        try:
            rooms_count, house_type, total_square, flat_flour, max_flours = self.parse_title(link_area[0])
            price = ''.join(unidecode.unidecode(link_area[0].xpath('.//span[@data-mark="MainPrice"]/span/text()')[0][:-2]).split())
            residential_complex = self.parse_if_exists(link_area[0], './/div[@data-name="ContentRow"]/a/text()')
            if residential_complex is not None:
                residential_complex = residential_complex[0].replace('\'', '"')
            description_block = link_area[0].xpath('.//div[@data-name="Description"]/p/text()')
            if len(description_block) > 0:
                description = description_block[0].replace('\'', '"')
            link_area[1] = link_area[1].xpath('.//div[@data-name="BrandingLevelWrapper"]')[0]
            trader_container = link_area[1].xpath('.//div[contains(@class, "content")]')[0]
            trader_data = trader_container.xpath('.//span/text()')
            if len(trader_data) == 1:
                name = trader_data[0].replace('\'', '"')
            else:
                trader_type, name = trader_data[:2]
                name = name.replace('\'', '"')
        except Exception as e:
            logging.warning(
                f'can\'t parse listing, link: {link}, error: {e}'
            )


        offer_data = {KeysEnum.LISTING_ID.value: id,
                      KeysEnum.PRICE.value: price,
                      'Число комнат': rooms_count,
                      'Тип жилья': house_type,
                      'Общая площадь': total_square,
                      'Адресс': address,
                      'Описание': description,
                      'Ссылка': link,
                      'Тип продаца': trader_type,
                      'Название продаца': name,
                      'Этаж квартиры': flat_flour,
                      'Этажей в доме': max_flours,
                      'Название ЖК': residential_complex}
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
            is_zero = tree.xpath("//h3[@data-name='EmptySearchContent']")
            if len(is_zero) > 0:
                return 0
            else:
                return -1

        return int(''.join(offer_count_text[1:-1]))

    def get_desk_link(self) -> str:
        if self.current_page < 2 and self.prev_price == 0:
            return f'{self.url_components[0]}&{self.url_components[1]}&{self.url_components[2]}'
        elif self.current_page < 2:
            return f'{self.url_components[0]}&minprice={self.prev_price}&{self.url_components[1]}&{self.url_components[2]}'
        elif self.prev_price == 0:
            return f'{self.url_components[0]}&{self.url_components[1]}&p={self.current_page}&{self.url_components[2]}'
        return f'{self.url_components[0]}&minprice={self.prev_price}&{self.url_components[1]}&p={self.current_page}&{self.url_components[2]}'

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