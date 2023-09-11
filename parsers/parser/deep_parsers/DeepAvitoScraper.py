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
                         max_page=100)

    def parse_offer_page(self, content, link, id):
        try:
            tree = html.fromstring(content)
            id = list(filter(None, re.split('_|/', link)))[-1]
            address = f'{self.city}, ' + content.xpath('.//div[@itemprop="address"]/span/text()')[0]
            rooms_count, house_type, total_square, flat_flour, max_flours = self.parse_title(content)
            price = content.xpath('.//span[@itemprop="price"]')[0].get('content')
            description_block = content.xpath('.//div[@itemprop="description"]/p/text')
            if len(description_block) > 0:
                description = description_block[0].replace('\'', '"')
            else:
                description = None
        except:
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
        try:
            apartment_params_list = content.xpath(".//ul[starts-with(@class, 'params-paramsList')]/li")
            for param in apartment_params_list:
                name = param.xpath('.//span/text()')[0].replace('\xa0', ' ')
                value = param.text.replace('\xa0', ' ')
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
                    types = name.split()
                    if len(types) == 2:
                        separate_bathroom_count = '1'
                        combined_bathroom_count = '1'
                    elif value == 'раздельный':
                        separate_bathroom_count = '1'
                    elif value == 'совмещённый':
                        combined_bathroom_count = '1'
                elif name == 'Ремонт':
                    renovation = value
                elif name == 'Способ продажи':
                    conditions = value
                elif name == 'Вид сделки' and value == 'возможна ипотека':
                    is_mortgage_available = True
                elif name == 'Балкон или лоджия':
                    types = name.split()
                    if len(types) == 2:
                        balcony_count = '1'
                        loggia_count = '1'
                    elif value == 'балкон':
                        balcony_count = '1'
                    elif value == 'лоджия':
                        loggia_count = '1'
                elif name == 'Мебель':
                    living_area = value
                elif name == 'Техника':
                    living_area = value
            price, conditions, is_mortgage_available = self.parse_aside_main_info(tree)
            rooms_count, house_type, total_square, address, residential_complex = self.parse_main_title(tree)
            object_data_dict = self.parse_object_factors(tree)
            description = self.parse_description(tree)
            add_dict_info = self.parse_flat_and_house_additional_data(tree)
            image_urls = self.parse_photos_urls(tree)
            if image_urls == False:
                image_path = False
            else:
                image_path = f'{self.website_name}{os.sep}{id}'
                self.save_images(id, image_urls)
            offer_data = {KeysEnum.LISTING_ID.value: id,
                          KeysEnum.PRICE.value: price,
                          'Условия cделки': conditions,
                          'Ипотека': is_mortgage_available,
                          'Число комнат': rooms_count,
                          'Тип жилья': house_type,
                          'Общая площадь': total_square,
                          'Адресс': address,
                          'Название ЖК': residential_complex,
                          'Описание': description,
                          'Ссылка': link,
                          'Путь к картинкам': image_path
                          }
            offer_data.update(object_data_dict)
            offer_data.update(add_dict_info)
            #offer_data.update(house_info_dict)
            self.offers.append(offer_data)
        except Exception as e:
            logging.info(f'Ошибка: {e}, Обьявление: {link}')

        offer_data = {KeysEnum.LISTING_ID.value: id,
                      KeysEnum.PRICE.value: price,
                      'Число комнат': rooms_count,
                      'Тип жилья': house_type,
                      'Общая площадь': total_square,
                      'Адресс': address,
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
        self.offers.append(offer_data)
        return True

    def parse_title(self, offer):
        title = offer.xpath('.//span[@itemprop="name"]/text()')[0].split(',')
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