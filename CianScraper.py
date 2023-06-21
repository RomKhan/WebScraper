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
    def __init__(self, url, link_token, pics_folder, image_loader, prev_address=None):
        Scraper.__init__(self, url, link_token, pics_folder, image_loader, prev_address)
        self.offer_load_indicator = "//div[@data-name='PriceInfo']"
        self.main_page_load_indicator = "//div[@data-name='SummaryHeader']"
        self.by_settings = By.XPATH

    def get_offer_data(self, link, id, driver):
        try:
            driver.get(link)
            WebDriverWait(driver, timeout=10).until(
                EC.presence_of_element_located((By.XPATH, self.offer_load_indicator)))
            driver.execute_script("window.stop();")
            asyncio.run(self.parse_offer_page(driver.page_source, link, id))
            return True
        except:
            print('не смог полностью загрузить', link)

        return False

    async def parse_offer_page(self, content, link, id):
        tree = html.fromstring(content)
        offer_data = {}
        try:
            price, offer_facts = self.parse_aside_main_info(tree)
            rooms_count, house_type, total_square, adress, residential_complex = self.parse_main_title(tree)
            object_data_dict = self.parse_object_factors(tree)
            description = self.parse_description(tree)
            flat_info_dict, house_info_dict = self.parse_flat_and_house_additional_data(tree)
            image_url_data = ('cian', id, self.parse_photos_urls(tree))
            offer_data = {'id': id,
                          'Цена': price,
                          # 'Условия сделки': transaction_terms,
                          # 'Ипотека': mortgage,
                          'Факты о сделке': offer_facts,
                          'Число комнат': rooms_count,
                          'Тип жилья': house_type,
                          'Общая площадь': total_square,
                          # 'Город': city,
                          # 'Улица': street,
                          # 'Номер дома': house_id,
                          'Адресс': adress,
                          'Название ЖК': residential_complex,
                          'Описание': description,
                          'Ссылка': link}
            offer_data.update(object_data_dict)
            offer_data.update(flat_info_dict)
            offer_data.update(house_info_dict)
            self.image_loader.image_to_disk_queue.append(image_url_data)
            print(image_url_data)
        except Exception as e:
            print(e, link)

        print(offer_data)

    def parse_aside_main_info(self, tree):
        try:
            asideMainInfo = tree.xpath("//div[@data-name='AsideMainInfo']")[0]
            price = unidecode.unidecode(asideMainInfo.xpath(".//div[@data-name='PriceInfo']/div/span")[0].text[:-2])
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
            flat_info, house_info = tree.xpath("//div[@data-name='OfferSummaryInfoGroup']")
            p_tags_flats = flat_info.xpath(".//p/text()")
            flat_info_dict = {}
            for i in range(0, len(p_tags_flats), 2):
                flat_info_dict[p_tags_flats[i]] = p_tags_flats[i + 1].rstrip('\xa0м')
            p_tags_house = house_info.xpath(".//p/text()")
            house_info_dict = {}
            for i in range(0, len(p_tags_house), 2):
                house_info_dict[p_tags_house[i]] = p_tags_house[i + 1].rstrip('\xa0м')
        except Exception as e:
            print(e)
            raise Exception("Ошибка парсинга доп инфы о доме или квартиры")
        return flat_info_dict, house_info_dict

    def parse_photos_urls(self, tree):
        try:
            images = tree.xpath("//div[@data-name='GalleryInnerComponent']/div/div")[0].xpath('.//img')
            images_urls = []
            for image in images:
                images_urls.append(image.get('src'))
        except Exception as e:
            print(e)
            raise Exception("Ошибка парсинга фото")
        return images_urls

    def get_link_by_page(self):
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
