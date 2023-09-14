import logging
import os
import re

from lxml import html
# from parsers.KeysEnum import KeysEnum
# from parsers.abstract.Scraper import Scraper
from KeysEnum import KeysEnum
from abstract.Scraper import Scraper


class DeepAvitoScraper(Scraper):
    def __init__(self, url, link_token, website_name, city, listing_type):
        Scraper.__init__(self,
                         url,
                         link_token,
                         website_name,
                         city,
                         listing_type,
                         offers_xpath="//div[@data-marker='item' and parent::div[(contains(@class, 'items-items'))]]",
                         max_page=100,
                         prev_address='https://www.avito.ru')

    def parse_offer_page(self, content, link, id):
        try:
            content = html.fromstring(content)
            address = f'{self.city}, ' + content.xpath('.//div[@itemprop="address"]/span/text()')[0]
            rooms_count, property_type, total_square, flat_flour, max_flours = self.parse_title(content)
            price = content.xpath('.//span[@itemprop="price"]')[0].get('content')
            description_block = content.xpath('.//div[@itemprop="description"]//p/text()')
            if len(description_block) == 0:
                description_block = content.xpath('.//div[@itemprop="description"]/text()')
            description = '\n'.join(description_block).replace('\'', '"')
            images = content.xpath('.//meta[@property="og:image"]')
            for i in range(len(images)):
                images[i] = images[i].get('content')
        except Exception as e:
            logging.info(f'Критическая ошибка: {e}, Обьявление: {link}')
            return False

        kitchen_area = None
        living_area = None
        rooms_type = None
        ceiling_height = None
        window_view = None
        separate_bathroom_count = None
        combined_bathroom_count = None
        renovation = None
        conditions = None
        is_mortgage_available = None
        balcony_count = None
        loggia_count = None
        furniture = None
        technique = None
        heated_floors = None
        decoration_finishing_type = None
        house_type = None
        passenger_elevator_count = None
        freight_elevator_count = None
        parking_type = None
        end_build_year = None
        is_chute = None
        gas_supply_type = None
        concierge = None
        residential_complex_name = None
        уard = None
        is_derelicted = None
        try:
            apartment_params_list = content.xpath(".//ul[starts-with(@class, 'params-paramsList')]/li")
            for param in apartment_params_list:
                name, value = param.text_content().replace('\xa0', ' ').split(': ')
                if name == 'Площадь кухни':
                    kitchen_area = value.split()[0]
                elif name == 'Жилая площадь':
                    living_area = value.split()[0]
                elif name == 'Тип комнат':
                    rooms_type = value
                elif name == 'Высота потолков':
                    ceiling_height = value.split()[0]
                elif name == 'Окна':
                    window_view = value
                elif name == 'Санузел':
                    types = value.split()
                    if len(types) == 2:
                        separate_bathroom_count = '1'
                        combined_bathroom_count = '1'
                    elif value == 'раздельный':
                        separate_bathroom_count = '1'
                    elif value == 'совмещенный':
                        combined_bathroom_count = '1'
                elif name == 'Ремонт':
                    renovation = value
                elif name == 'Способ продажи':
                    conditions = value
                elif name == 'Вид сделки' and value == 'возможна ипотека':
                    is_mortgage_available = True
                elif name == 'Балкон или лоджия':
                    types = value.split()
                    if len(types) == 2:
                        balcony_count = '1'
                        loggia_count = '1'
                    elif value == 'балкон':
                        balcony_count = '1'
                    elif value == 'лоджия':
                        loggia_count = '1'
                elif name == 'Мебель':
                    furniture = value
                elif name == 'Техника':
                    technique = value
                elif name == 'Тёплый пол':
                    heated_floors = value
                elif name == 'Отделка':
                    decoration_finishing_type = value
                elif name != 'Количество комнат' and name != 'Общая площадь' and name != 'Этаж' and name != 'Дополнительно':
                    logging.warning(f'НОВЫЙ ТАГ КВАРТИРЫ - {name}:{value}, ссылка: {link}')

            house_params_list = content.xpath(".//ul[starts-with(@class, 'style-item-params-list')]/li")
            for param in house_params_list:
                name, value = param.text_content().replace('\xa0', ' ').split(': ')
                if name == 'Тип дома':
                    house_type = value
                elif name == 'Пассажирский лифт':
                    if value.isdigit():
                        passenger_elevator_count = value
                    else:
                        passenger_elevator_count = 0
                elif name == 'Грузовой лифт':
                    if value.isdigit():
                        freight_elevator_count = value
                    else:
                        freight_elevator_count = 0
                elif name == 'Парковка':
                    parking_type = value
                elif name == 'Год постройки':
                    end_build_year = value
                elif name == 'В доме':
                    inside = value.split(', ')
                    for obj in inside:
                        if obj == 'мусоропровод':
                            is_chute = 'есть'
                        elif obj == 'газ':
                            gas_supply_type = 'есть'
                        elif obj == 'консьерж':
                            concierge = True
                        else:
                            logging.warning(f'НОВЫЙ ТАГ ВНУТРИ ДОМА - {obj}, ссылка: {link}')
                elif name == 'Название новостройки':
                    residential_complex_name = param.xpath('.//a/text()')[0].replace('\xa0', ' ')
                elif name == 'Срок сдачи':
                    end_build_year = value.split()[-1]
                elif name == 'Двор':
                    уard = value
                elif name == 'Запланирован снос':
                    is_derelicted = name + ': ' + value
                elif name != 'Этажей в доме' and name != 'Корпус, строение' and name != 'Тип участия':
                    logging.warning(f'НОВЫЙ ТАГ ДОМА - {name}:{value}, ссылка: {link}')
        except Exception as e:
            logging.info(f'Ошибка: {e}, Обьявление: {link}')

        offer_data = {KeysEnum.LISTING_ID.value: id,
                      KeysEnum.PRICE.value: price,
                      'Число комнат': rooms_count,
                      'Тип жилья': property_type,
                      'Общая площадь': total_square,
                      'Жилая площадь': living_area,
                      'Площадь кухни': kitchen_area,
                      'Адресс': address,
                      'Описание': description,
                      'Ссылка': link,
                      'Этаж квартиры': flat_flour,
                      'Высота потолков': ceiling_height,
                      'Вид из окон': window_view,
                      'Ремонт': renovation,
                      'Этажей в доме': max_flours,
                      'Название ЖК': residential_complex_name,
                      'Тип комнат': rooms_type,
                      'Балкон': balcony_count,
                      'Лоджия': loggia_count,
                      'Совмещенный санузел': combined_bathroom_count,
                      'Раздельный санузел': separate_bathroom_count,
                      'Мебель': furniture,
                      'Техника': technique,
                      'Теплый пол': heated_floors,
                      'Консьерж': concierge,
                      'Двор': уard,
                      'Условия сделки': conditions,
                      'Ипотека': is_mortgage_available,
                      'Пассажирский лифт': passenger_elevator_count,
                      'Грузовой лифт': freight_elevator_count,
                      'Парковка': parking_type,
                      'Газоснабжение': gas_supply_type,
                      'Мусоропровод': is_chute,
                      'Год постройки': end_build_year,
                      'Тип дома': house_type,
                      'Отделка': decoration_finishing_type,
                      'Аварийность': is_derelicted
                      }
        self.offers.append(offer_data)
        self.save_images(id, images)
        return True

    def parse_title(self, offer):
        title = offer.xpath('.//span[@class="title-info-title-text"]/text()')[0].split(',')
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

    def get_link(self, offer):
        link = offer.xpath('.//a[@itemprop="url"]')[0].get('href')
        id = list(filter(None, re.split('_|/', link)))[-1]
        return link, id

    def get_desk_link(self):
        if self.current_page < 2:
            return f'{self.url_components[0]}&{self.url_components[1]}'
        return f'{self.url_components[0]}&p={self.current_page}&{self.url_components[1]}'

    @staticmethod
    def parse_link(url):
        data = url.split('&')
        first_part = []
        for i in range(len(data)):
            if data[i][0] == 'p':
                break
            first_part.append(data[i])

        first_part = '&'.join(first_part)
        second_part = '&'.join(data[i+1:])

        return [first_part, second_part]