import re

import unidecode
from lxml import html
from KeysEnum import KeysEnum
from abstract.ScrapeAll import ScrapeAll
# from parsers.KeysEnum import KeysEnum
# from parsers.abstract.ScrapeAll import ScrapeAll
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YandexScrapeAll(ScrapeAll):
    def __init__(self, url_components, city, website, listing_type, min_price):
        ScrapeAll.__init__(self,
                           url_components,
                           website,
                           city,
                           listing_type,
                           min_price,
                           offers_xpath="//ol/li[starts-with(@class, 'OffersSerpItem')]",
                           max_page=25,
                           offers_per_page=20)

    def parse_offer(self, offer):
        try:
            offer = offer.xpath(".//div[@class='OffersSerpItem__info-inner']")[0]
            general_block = offer.xpath(".//div[@class='OffersSerpItem__generalInfoInnerContainer']")[0]
            link = general_block.xpath("./a")[0].get('href')
            id = list(filter(None, re.split('_|/', link)))[-1]
            adress = f'{self.city}, ' + ' '.join(general_block.xpath("./div")[0].xpath(".//text()"))
            # if not adress.startswith('Москва'):
            #     logging.info(f'{adress}')
        except:
            print(id, link)
            return False, None
        residential_complex = None
        price = None
        rooms_count = None
        house_type = None
        total_square = None
        description = None
        flat_flour = None
        max_flours = None
        is_mortgage_available = None
        negotiation = None
        online_view = None
        is_communal_payments_included = None
        commission = None
        prepayment = None
        pledge = None
        try:
            rooms_count, house_type, total_square, flat_flour, max_flours = self.parse_title(general_block)
            price = ''.join(unidecode.unidecode(offer.xpath('.//span[@class="price"]//text()')[0][:-2]).split())
            description_block = offer.xpath('.//p[@class="OffersSerpItem__description"]/text()')
            if len(description_block) > 0:
                description = description_block[0].replace('\'', '"')

            residential_complex = self.parse_if_exists(general_block, "./span/*/a/text()")
            if residential_complex is not None:
                residential_complex = residential_complex[0]

            tags = self.parse_if_exists(offer, './/div[@class="OffersSerpItem__tagsContainer"]/div//text()')
            if tags is not None:
                for tag in tags:
                    tag = str(tag).replace('\xa0', ' ')
                    if tag == 'ипотека':
                        is_mortgage_available = True
                    elif tag == 'торг':
                        negotiation = True
                    elif tag == 'без торга':
                        negotiation = False
                    elif tag == 'онлайн показ':
                        online_view = True
                    elif tag == 'цена с КУ':
                        is_communal_payments_included = True
                    elif tag == 'цена без КУ':
                        is_communal_payments_included = True
                    elif tag == 'залог':
                        pledge = -1
                    elif tag == 'без залога':
                        pledge = 0
                    elif tag == 'без комиссии':
                        commission = 0
                    elif tag.startswith('комиссия'):
                        commission = int(tag.split()[1][:-1])
                    elif tag.startswith('предоплата'):
                        prepayment = int(tag.split()[1][:-1])
                    elif tag != 'хорошая цена' and 'кешбэк' not in tag:
                        logging.warning(f'НОВЫЙ ТАГ - {tag}')


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
                      'Этаж квартиры': flat_flour,
                      'Этажей в доме': max_flours,
                      'Название ЖК': residential_complex,
                      'Ипотека': is_mortgage_available,
                      'Торг': negotiation,
                      'Онлайн показ': online_view,
                      'Коммуналньые платежи': is_communal_payments_included,
                      'Комиссия': commission,
                      'Предоплата': prepayment,
                      'Залог': pledge
                      }
        return offer_data, id



    def parse_title(self, offer):
        title = offer.xpath('./a/span/text()')[0].split()
        additional = offer.xpath('.//div[@class="OffersSerpItem__building"]/text()')
        if len(title) > 3:
            title[2] = ' '.join(title[2:])
        if title[2][0].isdigit():
            rooms_count, house_type = title[2].split('-')
        else:
            rooms_count = '0'
            house_type = title[2]
        total_square = title[0]
        floor_data = additional[-1].split()
        flat_flour, max_flours = floor_data[0], floor_data[-1]
        return rooms_count, house_type, total_square, flat_flour, max_flours


    def get_count_of_offers(self, content) -> int:
        tree = html.fromstring(content)
        try:
            offer_count_text = tree.xpath("//div[@itemprop='offers']/meta[@itemprop='offerCount']")[0].get('content')
            # offer_count_text = []
            # for part in text:
            #     if part.isnumeric():
            #         offer_count_text.append(part)
            # offer_count_text = ''.join(offer_count_text)
            # print(offer_count_text)
        except:
             return -1
        return int(offer_count_text)

    def get_desk_link(self) -> str:
        if self.current_page < 2 and self.prev_price == 0:
            return f'{self.url_components[0]}&{self.url_components[1]}'
        elif self.current_page < 2:
            return f'{self.url_components[0]}&priceMin={self.prev_price}&{self.url_components[1]}'
        elif self.prev_price == 0:
            return f'{self.url_components[0]}&{self.url_components[1]}&page={self.current_page-1}'
        return f'{self.url_components[0]}&priceMin={self.prev_price}&{self.url_components[1]}&page={self.current_page-1}'

    @staticmethod
    def parse_link(url):
        data = url.split('&')
        first_part = data[0]
        second_part = data[2]

        return [first_part, second_part]
