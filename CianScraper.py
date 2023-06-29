import asyncio
import os
import time

from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unidecode

from Scraper import Scraper


class CianScraper(Scraper):
    def __init__(self, url, link_token, image_loader, data_saver, website_name, city, listing_type, prev_address=None):
        Scraper.__init__(self,
                         url,
                         link_token,
                         image_loader,
                         data_saver,
                         By.XPATH,
                         "//div[@data-name='SummaryHeader']",
                         website_name,
                         city,
                         listing_type,
                         prev_address)
        self.offer_load_indicator = "//div[@data-name='PriceInfo']"

    def get_offer_data(self, link, id, driver):
        try:
            driver.get(link)
            WebDriverWait(driver, timeout=30).until(
                EC.presence_of_element_located((By.XPATH, self.offer_load_indicator)))
            driver.execute_script("window.stop();")
            asyncio.run(self.parse_offer_page(driver.page_source, link, id))
            return True
        except:
            print('не смог полностью загрузить', link)

        return False

    async def parse_offer_page(self, content, link, id):
        try:
            tree = html.fromstring(content)
            price, offer_facts = self.parse_aside_main_info(tree)
            rooms_count, house_type, total_square, adress, residential_complex = self.parse_main_title(tree)
            total_square = total_square
            object_data_dict = self.parse_object_factors(tree)
            description = self.parse_description(tree)
            add_dict_info = self.parse_flat_and_house_additional_data(tree)
            image_url_data = ('cian', id, self.parse_photos_urls(tree))
            if image_url_data == False:
                image_path = False
            else:
                image_path = f'cian{os.sep}{id}'
            offer_data = {'id': id,
                          'Цена': price,
                          'Факты о сделке': offer_facts,
                          'Число комнат': rooms_count,
                          'Тип жилья': house_type,
                          'Общая площадь': total_square,
                          'Адресс': adress,
                          'Название ЖК': residential_complex,
                          'Описание': description,
                          'Ссылка': link,
                          'Путь к картинкам': image_path
                          }
            offer_data.update(object_data_dict)
            offer_data.update(add_dict_info)
            #offer_data.update(house_info_dict)
            if image_url_data[2] != False:
                self.image_loader.image_to_disk_queue.append(image_url_data)
            self.to_database(offer_data)
        except Exception as e:
            print(e, link)

    def parse_aside_main_info(self, tree):
        try:
            asideMainInfo = tree.xpath("//div[@data-name='AsideMainInfo']")[0]
            price = ''.join(unidecode.unidecode(asideMainInfo.xpath(".//div[@data-name='PriceInfo']/div/span")[0].text[:-2]).split())
            offerFacts = asideMainInfo.xpath(".//div[@data-name='OfferFactItem']/p/text()")
            offerFacts_dict = {}
            for i in range(0, len(offerFacts), 2):
                offerFacts_dict[offerFacts[i]] = offerFacts[i + 1]
            # transaction_terms = offerFacts[1].xpath(".//p")[1].text
            # mortgage = self.parse_if_exists(offerFacts[2], ".//p")[1].text
        except:
            raise Exception("Ошибка парсинга основной инфы с карточки сбоку")
        return price, offerFacts_dict

    def parse_main_title(self, tree):
        try:
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
            adress = ', '.join(mainNew.xpath(".//div[@data-name='AddressContainer']/a/text()"))
            # city = adress_items[0]
            # street = adress_items[3]
            # house_id = adress_items[4]
            residential_complex = self.parse_if_exists(mainNew, ".//div[@data-name='ParentNew']/a/text()")
            if residential_complex is not None:
                residential_complex = residential_complex[0]
        except Exception as e:
            print(e)
            raise Exception("Ошибка парсинга названия обьявления")
        return rooms_count, house_type, total_square, adress, residential_complex

    def parse_object_factors(self, tree):
        try:
            objectFactoids = tree.xpath("//div[@data-name='ObjectFactoids']")[0]
            object_data = objectFactoids.xpath(".//div[@data-name='ObjectFactoidsItem']/div[2]/span/text()")
            object_data_dict = {}
            for i in range(0, len(object_data), 2):
                object_data_dict[object_data[i]] = object_data[i + 1].rstrip('\xa0м²')
            object_data_dict['Этаж квартиры'] = object_data_dict['Этаж'].split()[0]
            object_data_dict['Этажей в доме'] = object_data_dict['Этаж'].split()[2]
            object_data_dict.pop('Этаж', None)
        except:
            raise Exception("Ошибка парсинга основной инфы об обьекте")
        return object_data_dict

    def parse_description(self, tree):
        try:
            description = tree.xpath("//div[@data-name='Description']/div/div/*/span")[0].text
        except:
            raise Exception("Ошибка парсинга описания")
        return description

    def parse_flat_and_house_additional_data(self, tree):
        try:
            add_info = [x.xpath('.//p/text()') for x in tree.xpath("//div[@data-name='OfferSummaryInfoGroup']")]
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
                        print('Аномальный  тип лифта', elevators)
                else:
                    print('Аномальное количество типов лифтов', elevators)

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
                        print('Аномальный  тип туалета', bathrooms)
                else:
                    print('Аномальное количество типов туалетов', bathrooms)

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
                        print('Аномальный  тип баллкона', louge_and_balcony)
                else:
                    print('Аномальное количество типов балконов', louge_and_balcony)
        except Exception as e:
            print(e)
            raise Exception("Ошибка парсинга доп инфы о доме или квартиры")
        return add_dict

    def parse_photos_urls(self, tree):
        try:
            images = tree.xpath("//div[@data-name='GalleryInnerComponent']/div/div")[0].xpath('.//img')
            images_urls = []
            for image in images:
                images_urls.append(image.get('src'))
        except Exception as e:
            print(e)
            return False
        return images_urls

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
