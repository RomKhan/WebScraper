import logging
import os
import re

from lxml import html
# from parsers.KeysEnum import KeysEnum
# from parsers.abstract.Scraper import Scraper
from KeysEnum import KeysEnum
from abstract.Scraper import Scraper


class DeepDomclickScraper(Scraper):
    def __init__(self, url, link_token, website_name, city, listing_type):
        Scraper.__init__(self,
                         url,
                         link_token,
                         website_name,
                         city,
                         listing_type,
                         offers_xpath='//div[@data-e2e-id="offers-list__item"]',
                         max_page=100,
                         is_shallow_images=True)

    def parse_offer_page(self, content, link, id, images=None):
        description = None
        residential_complex_name = None
        try:
            content = html.fromstring(content)
            side_card = content.xpath(".//aside[@data-e2e-id='telephony-sidebar-block']")[0]
            main_block = content.xpath(".//section[@class='main_block__gallery']")[0]
            address = ' '.join(main_block.xpath('.//span[@itemprop="name"]/a/text()')).replace('\'', '"')
            rooms_count, property_type, total_square = self.parse_title(side_card)
            price = side_card.xpath('.//meta[@itemprop="price"]')[0].get('content')
            description_block = self.parse_if_exists(content, './/div[@itemprop="description"]/text()')
            if description_block is not None:
                description = description_block[0].replace('\'', '"')
            residential_complex_name_block = self.parse_if_exists(side_card, './/a[@class="offerShortSummary_complexLink"]/text()')
            if residential_complex_name_block is not None:
                residential_complex_name = residential_complex_name_block[0]
            images_inside = main_block.xpath('.//div[starts-with(@class, "dc-gallery__slot")]//img')
            if images is None:
                images = []
            for i in range(len(images_inside)):
                if images_inside[i].get('data-test') is not None:
                    continue
                images.append(images_inside[i].get('src'))
            images = list(set(images))
        except Exception as e:
            logging.info(f'Критическая ошибка: {e}, Обьявление: {link}')
            return False

        kitchen_area = None
        living_area = None
        ceiling_height = None
        window_view = None
        separate_bathroom_count = None
        combined_bathroom_count = None
        renovation = None
        conditions = None
        balcony_count = None
        decoration_finishing_type = None
        house_type = None
        parking_type = None
        end_build_year = None
        is_chute = None
        gas_supply_type = None
        concierge = None
        уard = None
        years_owned = None
        owners_count = None
        minor_owners = None
        registered_minors = None
        redevelopment = None
        flat_flour = None
        flooring_type = None
        house_serie = None
        heating_type = None
        apartments_number = None
        max_flours = None
        furniture = None
        try:
            apartment_params_list = content.xpath(".//ul[@data-e2e-id='О квартире-list']/li")
            apartment_params_list.extend(content.xpath(".//ul[@data-e2e-id='О квартире-list-spoiler']/li"))
            for param in apartment_params_list:
                name = param.get('data-e2e-id')
                value = param.xpath(".//span[@data-e2e-id='Значение']//text()")[0].replace('\xa0', ' ')
                if name == 'Кухня':
                    kitchen_area = value.split()[0]
                elif name == 'Жилая':
                    living_area = value.split()[0]
                elif name == 'Ремонт':
                    renovation = value
                elif name == 'Этаж':
                    flat_flour = value
                elif name == 'Тип сделки':
                    conditions = value
                elif name == 'Вид из окон':
                    window_view = value
                elif name == 'Балкон':
                    if value == 'нет':
                        balcony_count = '0'
                    else:
                        logging.warning(f'НОВЫЙ ТАГ КВАРТИРЫ - {name}:{value}, ссылка: {link}')
                elif name == 'Количество балконов':
                    balcony_count = value
                elif name == 'Газ':
                    gas_supply_type = value
                elif name == 'Мусоропровод':
                    is_chute = value
                elif name == 'Высота потолков':
                    ceiling_height = value
                elif name == 'Санузел':
                    if value == 'Раздельный':
                        separate_bathroom_count = '1'
                    elif value == 'Совмещенный':
                        combined_bathroom_count = '1'
                    elif value != 'Более одного':
                        logging.warning(f'НОВЫЙ ТАГ КВАРТИРЫ - {name}:{value}, ссылка: {link}')
                elif name == 'Лет в собственности':
                    years_owned = value
                elif name == 'Количество собственников':
                    owners_count = value
                elif name == 'Несовершеннолетние собственники':
                    minor_owners = False if value == 'Нет' else True
                elif name == 'Прописанные несовершеннолетние':
                    registered_minors = False if value == 'Нет' else True
                elif name == 'Перепланировка':
                    redevelopment = False if value == 'Нет' else True
                elif name == 'Отделка':
                    decoration_finishing_type = value
                elif name != 'Комнат' and name != 'Площадь' and name != 'Количество лифтов' and name != 'Грузовой лифт':
                    logging.warning(f'НОВЫЙ ТАГ КВАРТИРЫ - {name}:{value}, ссылка: {link}')

            additional_parms_list = content.xpath(".//div[@data-e2e-id='details-checkListByCategory']/div/div")
            for param in additional_parms_list:
                texts = param.xpath('.//text()')
                name = texts[0]
                values = texts[1:]
                if name == 'Благоустройство двора':
                    уard = ', '.join(values)
                elif name == 'Парковка':
                    parking_type = ', '.join(values)
                elif name == 'Безопасность' and 'Консьерж' in values:
                    concierge = True
                elif name == 'Удобства' and ('Мебель на кухне' in values or 'Мебель в комнатах' in values):
                    if furniture is not None:
                        furniture += f', {name} есть'
                    else:
                        furniture = f'{name} есть'
                elif name != 'Инфраструктура':
                    logging.warning(f'НОВЫЙ ТАГ ДОП ИНФЫ - {name}:{values}, ссылка: {link}')

            house_params_list = content.xpath(".//ul[@data-e2e-id='-list']/li")
            for param in house_params_list:
                name = param.get('data-e2e-id')
                value = param.xpath(".//span[@data-e2e-id='Значение']//text()")[0].replace('\xa0', ' ')
                if name == 'Год постройки':
                    end_build_year = value
                elif name == 'Материал стен':
                    house_type = value
                elif name == 'Количество этажей':
                    max_flours = value
                elif name == 'Тип перекрытий':
                    flooring_type = value
                elif name == 'Мусоропровод':
                    is_chute = value
                elif name == 'Газ':
                    is_chute = value
                elif name == 'Серия дома':
                    house_serie = value
                elif name == 'Горячее водоснабжение':
                    heating_type = value
                elif name == 'Количество квартир':
                    apartments_number = value
                elif 'ифт' not in name and name != 'Тип фундамента' and name != 'Детская площадка':
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
                      'Балкон': balcony_count,
                      'Совмещенный санузел': combined_bathroom_count,
                      'Раздельный санузел': separate_bathroom_count,
                      'Консьерж': concierge,
                      'Двор': уard,
                      'Условия сделки': conditions,
                      'Парковка': parking_type,
                      'Газоснабжение': gas_supply_type,
                      'Мусоропровод': is_chute,
                      'Год постройки': end_build_year,
                      'Тип дома': house_type,
                      'Отделка': decoration_finishing_type,
                      'Лет в собственности': years_owned,
                      'Количество собственников': owners_count,
                      'Несовершеннолетние собственники': minor_owners,
                      'Прописанные несовершеннолетние': registered_minors,
                      'Перепланировка': redevelopment,
                      'Тип перекрытий': flooring_type,
                      'Строительная серия': house_serie,
                      'Отопление': heating_type,
                      'Количество квартир': apartments_number,
                      'Путь к картинкам': f'{self.website_name}{os.sep}{id}' if len(images) > 0 else None
                      }
        self.offers.append(offer_data)
        self.save_images(id, images)
        return True

    def parse_title(self, title):
        title = title.xpath(".//h1/text()")[0].split(', ')
        title[0] = ' '.join(title[0].split()[1:])

        if title[0][0].isdigit():
            rooms_count = title[0].strip(',').split()[0].split('-')[0]
            house_type = title[0].strip(',').split()[0].split('-')[1]
        else:
            rooms_count = 0
            house_type = title[0].strip(',')
        total_square = title[1].strip(',').split()[0]
        return rooms_count, house_type, total_square

    def get_images(self, offer):
        images = offer.xpath('.//div[starts-with(@class, "dc-gallery__slot")]//img')
        for i in range(len(images)):
            images[i] = images[i].get('src')

        return images

    def get_link(self, offer):
        link = offer.xpath('.//a[@data-test="product-snippet-property-offer"]')[0].get('href')
        id = list(filter(None, re.split('_|/', link)))[-1]
        return link, id

    def get_desk_link(self):
        if self.current_page < 2:
            return f'{self.url_components[0]}&offset=0'
        return f'{self.url_components[0]}&offset={(self.current_page - 1)* 20}'

    @staticmethod
    def parse_link(url):
        data = url.split('&')
        first_part = []
        for i in range(len(data)):
            if data[i].startswith('offset'):
                break
            first_part.append(data[i])

        first_part = '&'.join(first_part)

        return [first_part]