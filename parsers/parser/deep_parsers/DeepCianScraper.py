import asyncio
import logging
import os
import re
import time

from lxml import html
# from parsers.KeysEnum import KeysEnum
# from parsers.abstract.Scraper import Scraper
from KeysEnum import KeysEnum
from abstract.Scraper import Scraper


class DeepCianScraper(Scraper):
    def __init__(self, url, link_token, website_name, city, listing_type):
        Scraper.__init__(self,
                         url,
                         link_token,
                         website_name,
                         city,
                         listing_type,
                         offers_xpath='//article[@data-name="CardComponent"]',
                         max_page=54)

    def parse_offer_page(self, content, link, id):
        try:
            tree = html.fromstring(content)
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
            return True
        except Exception as e:
            logging.info(f'Ошибка: {e}, Обьявление: {link}')
            return False

    def parse_aside_main_info(self, tree):
        asideMainInfo = tree.xpath("//div[@data-name='AsideMainInfo']")[0]
        price = ''.join(filter(str.isdigit, asideMainInfo.xpath(".//div[@data-name='PriceInfo']/div/span/text()")[0]))
        offerFacts = asideMainInfo.xpath(".//div[@data-name='OfferFactItem']/span/text()")
        conditions, is_mortgage_available = None, None
        for i in range(0, len(offerFacts), 2):
            offerFacts[i] = offerFacts[i].replace('\xa0', ' ')
            if offerFacts[i] == 'Ипотека' and offerFacts[i + 1] == 'возможна':
                is_mortgage_available = True
            elif offerFacts[i] == 'Условия сделки':
                conditions = offerFacts[i + 1].replace('\xa0', ' ')
            elif offerFacts[i] != 'Цена за метр':
                logging.info(f'Новый параметр квартиры - {offerFacts[i]}: {offerFacts[i + 1]}')
        return price, conditions, is_mortgage_available

    def parse_main_title(self, tree):
        mainNew = tree.xpath("//section[@data-name='MainNew']")[0]
        title = mainNew.xpath(".//div[@data-name='OfferTitleNew']/h1/text()")[0].split()
        if len(title) < 4:
            rooms_count = 0
            house_type = title[0][:-1]
            total_square = title[1]
        else:
            rooms_count = title[0][0]
            house_type = title[1][:-1]
            total_square = title[2]
        geo_data = mainNew.xpath(".//div[@data-name='AddressContainer']/a/text()")
        address = ''
        for i in range(len(geo_data) - 1):
            if geo_data[i].startswith("м. ") or geo_data[i].split()[0].isupper() or geo_data[i] == 'ЗелАО':
                continue
            else:
                address += geo_data[i].replace('\'', '"') + ', '
        address = address + geo_data[-1]
        residential_complex = self.parse_if_exists(mainNew, ".//div[@data-name='ParentNew']/a/text()")
        if residential_complex is not None:
            residential_complex = residential_complex[0]

        return rooms_count, house_type, total_square, address, residential_complex

    def parse_object_factors(self, tree):
        objectFactoids = tree.xpath("//div[@data-name='ObjectFactoids']")[0]
        object_data = objectFactoids.xpath(".//div[@data-name='ObjectFactoidsItem']/div[2]/span/text()")
        object_data_dict = {}
        for i in range(0, len(object_data), 2):
            object_data_dict[object_data[i]] = object_data[i + 1].rstrip('\xa0м²')
        object_data_dict['Этаж квартиры'] = object_data_dict['Этаж'].split()[0]
        object_data_dict['Этажей в доме'] = object_data_dict['Этаж'].split()[2]
        object_data_dict.pop('Этаж', None)

        return object_data_dict

    def parse_description(self, tree):
        description = tree.xpath("//div[@data-name='Description']/div/div/*/span")[0].text
        return description

    def parse_flat_and_house_additional_data(self, tree):
        add_info = [x.xpath('.//text()') for x in tree.xpath("//div[@data-name='OfferSummaryInfoItem']")]
        add_info = [item for sublist in add_info for item in sublist]
        add_dict = {}
        for i in range(0, len(add_info), 2):
            add_dict[add_info[i]] = add_info[i + 1].rstrip('\xa0м')

        if 'Количество лифтов' in add_dict.keys():
            elevators = add_dict.pop('Количество лифтов').split(',')
            if len(elevators) == 2:
                add_dict['Пассажирский лифт'] = elevators[0].split()[0]
                add_dict['Грузовой лифт'] = elevators[1].split()[0]
            elif len(elevators) == 1:
                components = elevators[0].split()
                if 'пассаж' in components[1]:
                    add_dict['Пассажирский лифт'] = components[0]
                elif 'груз' in components[1]:
                    add_dict['Грузовой лифт'] = components[0]
                else:
                    logging.info(f'Аномальный  тип лифта - {elevators}', elevators)
            else:
                logging.info(f'Аномальное количество типов лифтов - {elevators}')

        if 'Санузел' in add_dict.keys():
            bathrooms = add_dict.pop('Санузел').split(',')
            if len(bathrooms) == 2:
                add_dict['Совмещенный санузел'] = bathrooms[0].split()[0]
                add_dict['Раздельный санузел'] = bathrooms[1].split()[0]
            elif len(bathrooms) == 1:
                components = bathrooms[0].split()
                if 'раздел' in components[1]:
                    add_dict['Раздельный санузел'] = components[0]
                elif 'совмещ' in components[1]:
                    add_dict['Совмещенный санузел'] = components[0]
                else:
                    logging.info(f'Аномальный  тип туалета - {bathrooms}', bathrooms)
            else:
                logging.info(f'Аномальное количество типов туалетов - {bathrooms}')

        if 'Балкон/лоджия' in add_dict.keys():
            louge_and_balcony = add_dict.pop('Балкон/лоджия').split(',')
            if len(louge_and_balcony) == 2:
                add_dict['Лоджия'] = louge_and_balcony[0].split()[0]
                add_dict['Балкон'] = louge_and_balcony[1].split()[0]
            elif len(louge_and_balcony) == 1:
                components = louge_and_balcony[0].split()
                if 'лод' in components[1]:
                    add_dict['Лоджия'] = components[0]
                elif 'балк' in components[1]:
                    add_dict['Балкон'] = components[0]
                else:
                    logging.info(f'Аномальный  тип баллкона - {louge_and_balcony}')
            else:
                logging.info(f'Аномальное количество типов балконов - {louge_and_balcony}')

        return add_dict

    def parse_photos_urls(self, tree):
        images = tree.xpath("//div[@data-name='GalleryInnerComponent']/div/div")[0].xpath('.//img')
        images_urls = []
        for image in images:
            images_urls.append(image.get('src'))

        return images_urls

    def get_link(self, offer):
        link = offer.xpath('.//div[@data-name="LinkArea"]/a')[0].get('href')
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

            # def run_driver_on_main_page(self, driver):
    #     try:
    #         driver.get(self.url)
    #         WebDriverWait(driver, timeout=150).until(EC.presence_of_element_located((By.XPATH, self.main_page_load_indicator)))
    #         # driver.execute_script("window.stop();")
    #     except Exception as e:
    #         print('error here', self.url)
