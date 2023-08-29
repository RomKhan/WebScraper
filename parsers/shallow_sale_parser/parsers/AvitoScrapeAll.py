import re

import unidecode
from lxml import html

from KeysEnum import KeysEnum
from abstract.ScrapeAll import ScrapeAll
# from parsers.KeysEnum import KeysEnum
# from parsers.abstract.ScrapeAll import ScrapeAll
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AvitoScrapeAll(ScrapeAll):
    def __init__(self, url_components, city, website, listing_type, min_price):
        ScrapeAll.__init__(self,
                           url_components,
                           website,
                           city,
                           listing_type,
                           min_price,
                           offers_xpath="//div[@data-marker='item' and parent::div[(contains(@class, 'items-items'))]]",
                           max_page=100,
                           offers_per_page=50)

    def parse_offer(self, offer):
        residential_complex = None
        try:
            link = offer.xpath('.//a[@itemprop="url"]')[0].get('href')
            residential_complex_data = offer.xpath(".//div[@data-marker='item-address']/p")
            if len(residential_complex_data) > 0:
                residential_complex = residential_complex_data[0].text
            adress = f'{self.city}, ' + offer.xpath(".//div[@data-marker='item-address']/div//span/text()")[0].replace('\'', '"')
            # if not adress.startswith('Москва'):
            #     logging.info(f'{adress}, ЖК: {residential_complex}')
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
        commission = None
        pledge = None
        rooms_type = None
        balcony_count = None
        loggia_count = None
        combined_bathroom_count = None
        separate_bathroom_count = None
        try:
            rooms_count, house_type, total_square, flat_flour, max_flours = self.parse_title(offer)
            price = offer.xpath('.//meta[@itemprop="price"]')[0].get('content')
            description_block = offer.xpath('.//div[contains(@class, "item-description")]/p/text()')
            if len(description_block) > 0:
                description = description_block[0].replace('\'', '"')
            user_atag = self.parse_if_exists(offer, './/div[contains(@class, "item-sellerInfo")]/div[contains(@class, "item-userInfo")]/*/a/p/text()')
            if user_atag is not None:
                name = user_atag[0].replace('\'', '"')
            tags = self.parse_if_exists(offer, './/div[contains(@class, "item-autoParamsStep")]/p/text()')
            if tags is not None:
                tags = tags[0].lower().replace('\xa0', ' ').split(', ')
                for tag in tags:
                    tag = tag.strip()
                    if tag == 'балкон':
                        balcony_count = '1'
                    elif tag == 'лоджия':
                        loggia_count = '1'
                    elif tag == 'без комиссии':
                        commission = 0
                    elif tag.startswith('комиссия'):
                        commission = int(tag.split()[1][:-1])
                    elif tag == 'без залога':
                        pledge = 0
                    elif tag.endswith('залог'):
                        pledge = int(''.join(filter(str.isdigit, tag)))
                    elif tag.startswith('комнаты'):
                        rooms_type = tag.split()[1]
                    elif tag == 'смежные' or tag == 'изолированные':
                        rooms_type += f', {tag}'
                    elif tag.startswith('санузел'):
                        tag = tag.split()[1]
                        if tag == 'раздельный':
                            separate_bathroom_count = '1'
                        elif tag == 'совмещённый':
                            combined_bathroom_count = '1'
                    elif tag == 'раздельный':
                        separate_bathroom_count = '1'
                    elif tag == 'совмещённый':
                        combined_bathroom_count = '1'
                    else:
                        logging.warning(f'НОВЫЙ ТАГ - {tag}, ссылка: {link}, все таги: {", ".join(tags)}')


        except Exception as e:
            logging.warning(
                f'can\'t parse listing, link: {link}, error: {e}'
            )


        offer_data = {KeysEnum.LISTING_ID.value: id,
                      KeysEnum.PRICE.value: price,
                      'Число комнат': rooms_count,
                      'Тип жилья': house_type,
                      'Общая площадь': total_square,
                      'Адресс': adress,
                      'Описание': description,
                      'Ссылка': link,
                      'Название продаца': name,
                      'Этаж квартиры': flat_flour,
                      'Этажей в доме': max_flours,
                      'Название ЖК': residential_complex,
                      'Комиссия': commission,
                      'Залог': pledge,
                      'Тип комнат': rooms_type,
                      'Балкон': balcony_count,
                      'Лоджия': loggia_count,
                      'Совмещенный санузел': combined_bathroom_count,
                      'Раздельный санузел': separate_bathroom_count,
                      }
        return offer_data, id



    def parse_title(self, offer):
        title = offer.xpath('.//h3[@itemprop="name"]/text()')[0].split(',')
        if len(title) == 4:
            temp = title.pop(1)
            title[1] = ','.join([temp, title[1]])
        if title[0][0].isdigit():
            rooms_count = title[0].split('-')[0]
            house_type = title[0].split()[1]
        elif title[0].startswith('Доля') or title[0].startswith('Аукцион'):
            rooms_count = '-1'
            house_type = title[0]
        else:
            rooms_count = '0'
            house_type = title[0]
        total_square = title[1].split()[0]
        flat_flour, max_flours = title[2].split()[0].split('/')
        return rooms_count, house_type, total_square, flat_flour, max_flours


    def get_count_of_offers(self, content) -> int:
        tree = html.fromstring(content)
        try:
            if self.parse_if_exists(content, "//div[starts-with(@class, 'no-results-root')]") is not None:
                return 0
            offer_count_text = ''.join(unidecode.unidecode(tree.xpath("//span[starts-with(@class, 'page-title-count')]/text()")[0]).split())
        except:
            return -1
        return int(offer_count_text)

    def get_desk_link(self) -> str:
        if self.current_page < 2 and self.prev_price == 0:
            return f'{self.url_components[0]}&{self.url_components[1]}'
        elif self.current_page < 2:
            return f'{self.url_components[0]}&pmin={self.prev_price}&{self.url_components[1]}'
        elif self.prev_price == 0:
            return f'{self.url_components[0]}&p={self.current_page}&{self.url_components[1]}'
        return f'{self.url_components[0]}&pmin={self.prev_price}&p={self.current_page}&{self.url_components[1]}'

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