import logging
import os
import re

from lxml import html
# from parsers.KeysEnum import KeysEnum
# from parsers.abstract.Scraper import Scraper
from KeysEnum import KeysEnum
from abstract.Scraper import Scraper


class DeepYandexScraper(Scraper):
    def __init__(self, url, link_token, website_name, city, listing_type):
        Scraper.__init__(self,
                         url,
                         link_token,
                         website_name,
                         city,
                         listing_type,
                         offers_xpath="//ol/li[starts-with(@class, 'OffersSerpItem')]",
                         max_page=25,
                         is_shallow_images=True,
                         prev_address='https://realty.ya.ru')

    def parse_offer_page(self, content, link, id, images=None):
        try:
            content = html.fromstring(content)
            aside_card = content.xpath('.//div[@data-test="OfferCardSummary"]')[0]
            address = aside_card.xpath(".//div[starts-with(@class, 'CardLocation__addressItem')]/text()")[0]
            rooms_count, property_type, total_square = self.parse_title(aside_card)
            price = ''.join(filter(str.isdigit, aside_card.xpath(".//span[starts-with(@class, 'OfferCardSummaryInfo__price')]/text()")[0]))
            description_block = content.xpath('.//div[starts-with(@class, "OfferCard__textDescription")]/div//text()')
            if len(description_block) == 0:
                description_block = None
            elif description_block[-1] == 'Подробнее':
                description_block = description_block[:-1]
            description = '\n'.join(description_block).replace('\'', '"')
            images_inside = ['https:' + url.get('src') for url in content.xpath('.//div[starts-with(@class, "GalleryV2__slides")]//img') if url.get('src')[0] == '/']
            if images is not None:
                images = list(set(images) | set(images_inside))
            else:
                images = images_inside
        except Exception as e:
            logging.info(f'Критическая ошибка: {e}, Обьявление: {link}')
            return False

        kitchen_area = None
        living_area = None
        flat_flour = None
        max_flours = None
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
        house_type = None
        parking_type = None
        end_build_year = None
        is_chute = None
        concierge = None
        residential_complex_name = None
        negotiation = None
        house_status = None
        online_view = None
        house_serie = None
        apartments_number = None
        entrance_count = None
        heating_type = None
        try:
            main_params = content.xpath(".//div[starts-with(@class, 'OfferCard__techFeatures')]/div")
            for param in main_params:
                value, name = param.xpath('.//text()')
                value = value.replace('\xa0', ' ')
                name = name.replace('\xa0', ' ')
                if name == 'кухня':
                    kitchen_area = value.split()[0]
                elif name == 'жилая':
                    living_area = value.split()[0]
                elif name.startswith('из'):
                    flat_flour = value.split()[0]
                    max_flours = name.split()[1]
                elif name == 'потолки':
                    ceiling_height = value.split()[0]
                elif name == 'год постройки' or name == 'срок сдачи':
                    end_build_year = value.split()[0]
                elif name != 'общая':
                    logging.warning(f'НОВЫЙ ТАГ ОСНОВНОЙ ИНФЫ - {name}:{value}, ссылка: {link}')

            tags_params = aside_card.xpath(".//div[starts-with(@class, 'OfferCardSummaryTags__tags')]//text()")
            for tag in tags_params:
                tag = tag.replace('\xa0', ' ')
                if tag == 'ипотека':
                    is_mortgage_available = True
                elif 'продаж' in tag or tag == 'альтернатива' or tag == 'переуступка':
                    conditions = tag
                elif tag == 'торг':
                    negotiation = True
                elif tag.startswith('срок сдачи'):
                    house_status = 'не сдан'
                elif tag.startswith('сдан в'):
                    house_status = 'сдан'
                elif tag == 'без торга':
                    negotiation = False
                elif tag == 'онлайн показ':
                    online_view = True
                elif tag != 'хорошая цена' and 'сдан' not in tag and tag != 'апартаменты':
                    logging.warning(f'НОВЫЙ ТАГ БОКОВОЙ КАРТОЧКИ - {tag}, ссылка: {link}')

            apart_params = content.xpath(".//div[starts-with(@class, 'OfferCardDetailsFeatures__container')]//text()")
            for name in apart_params:
                name = name.replace('\xa0', ' ')
                if name.startswith('Вид из окон'):
                    window_view = ' '.join(name.split()[3:])
                elif name.startswith('Отделка'):
                    renovation = ' '.join(name.split()[2:])
                elif name == 'Балкон':
                    balcony_count = '1'
                elif name == 'Два балкона':
                    balcony_count = '2'
                elif name == 'Лоджия':
                    loggia_count = '1'
                elif name == 'Две лоджии':
                    loggia_count = '2'
                elif name.startswith('Санузел'):
                    bathroom_type = name.split()[1]
                    if bathroom_type == 'раздельный':
                        separate_bathroom_count = '1'
                    elif bathroom_type == 'совмещённый':
                        combined_bathroom_count = '1'
                    else:
                        logging.warning(f'НОВЫЙ ТИП САНУЗЛА - {bathroom_type}, ссылка: {link}')
                elif name == 'Мебель' or name == 'Мебель на кухне':
                    if furniture is not None:
                        furniture += f', {name} есть'
                    else:
                        furniture = f'{name} есть'
                elif name == 'Холодильник' or name == 'Стиральная машина' or name == 'Кондиционер' or name == 'Телефон':
                    if technique is not None:
                        technique += f', {name}'
                    else:
                        technique = f'{name}'
                elif name != 'Несколько санузлов' and name != 'Интернет' and name != 'Телефона нет'\
                        and 'м²' not in name and not name.startswith('ещё') and 'пол' not in name\
                        and name != 'Мебели нет' and name != 'Холодильника нет' and name != 'Стиральной машины нет':
                    logging.warning(f'НОВЫЙ ТАГ КВАРТИРЫ - {name}, ссылка: {link}')

            house_params_list = content.xpath(".//div[starts-with(@class, 'OfferCardBuildingFeatures__featuresContainer')]//text()")
            for name in house_params_list:
                name = name.replace('\xa0', ' ')
                if name.endswith('здание'):
                    house_type = name.split()[0]
                elif name.startswith('Серия'):
                    house_serie = name.split()[1]
                elif name == 'Индивидуальный проект':
                    house_serie = name
                elif 'квартир' in name:
                    apartments_number = name.split()[0]
                elif 'парковка' in name:
                    parking_type = name
                elif name == 'Мусоропровод':
                    is_chute = 'есть'
                elif name == 'Мусоропровода нет':
                    is_chute = 'нет'
                elif 'подъезд' in name:
                    entrance_count = name.split()[0]
                elif name.endswith('отопление'):
                    heating_type = name.split()[0]
                elif name == 'Охрана/консьерж':
                    concierge = True
                elif 'этаж' not in name and not name.startswith('Застройщик') and not name.endswith('потолки')\
                        and not name.startswith('Дом') and name != 'Лифт' and not name.startswith('ещё')\
                        and not name.startswith('Закрыт') and not name.startswith('Реконструкция') and not name.startswith('Охраны или консьержа'):
                    logging.warning(f'НОВЫЙ ТАГ ДОМА - {name}, ссылка: {link}')

            residential_complex_name = self.parse_if_exists(content, './/div[starts-with(@class, "OfferCardSitePreview__title")]/text()')
            if residential_complex_name is not None:
                residential_complex_name = residential_complex_name[0].split('«')[-1][:-1]
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
                      'Лоджия': loggia_count,
                      'Совмещенный санузел': combined_bathroom_count,
                      'Раздельный санузел': separate_bathroom_count,
                      'Мебель': furniture,
                      'Техника': technique,
                      'Консьерж': concierge,
                      'Условия сделки': conditions,
                      'Ипотека': is_mortgage_available,
                      'Парковка': parking_type,
                      'Мусоропровод': is_chute,
                      'Год постройки': end_build_year,
                      'Тип дома': house_type,
                      'Путь к картинкам': f'{self.website_name}{os.sep}{id}' if len(images) > 0 else None,
                      'Торг': negotiation,
                      'Дом': house_status,
                      'Онлайн показ': online_view,
                      'Строительная серия': house_serie,
                      'Количество квартир': apartments_number,
                      'Подъезды': entrance_count,
                      'Отопление': heating_type
                      }
        self.offers.append(offer_data)
        self.save_images(id, images)
        return True

    def parse_title(self, offer):
        title = offer.xpath(".//div[starts-with(@class, 'OfferCardSummaryInfo__description')]/text()")[0].split()
        if len(title) > 3:
            title[2] = ' '.join(title[2:])
        if title[2][0].isdigit():
            rooms_count, house_type = title[2].split('-')
        else:
            rooms_count = '0'
            house_type = title[2]
        total_square = title[0]
        return rooms_count, house_type, total_square

    def get_images(self, offer):
        images = offer.xpath('.//div[@class="Gallery__items"]/span/img')
        image_urls = []
        for i in range(len(images)):
            srcset = images[i].get('srcset')
            if srcset is None:
                continue
            image_urls.append('https:' + '/'.join(srcset.split(', ')[-1].split()[0].split('/')[:-1]) + '/app_large')
        if len(image_urls) == 0:
            return None

        return image_urls

    def get_link(self, offer):
        general_block = offer.xpath(".//div[@class='OffersSerpItem__generalInfoInnerContainer']")[0]
        link = general_block.xpath("./a")[0].get('href')
        id = list(filter(None, re.split('_|/', link)))[-1]
        return link, id

    def get_desk_link(self):
        if self.current_page < 2:
            return f'{self.url_components[0]}'
        return f'{self.url_components[0]}&page={self.current_page-1}'

    @staticmethod
    def parse_link(url):
        data = url.split('&')
        first_part = []
        for i in range(len(data)):
            if data[i][0] == 'p':
                break
            first_part.append(data[i])

        first_part = '&'.join(first_part)

        return [first_part]