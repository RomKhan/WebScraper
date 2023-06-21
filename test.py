import base64
import os
import shutil

import cv2
import yadisk

import undetected_chromedriver as uc
import time
import requests
import scrapy
import cloudscraper
from selenium import webdriver
from bs4 import BeautifulSoup, SoupStrainer
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
from lxml import html
from lxml.etree import tostring
import urllib.request

PROXY = "92.255.7.162:8080"
chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--proxy-server=%s' % PROXY)
#chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--window-size=%s" % "1920,1080")
chrome_options.page_load_strategy = 'none'
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
#chrome_options.add_argument('--disable-blink-features=AutomationControlled')
driver = uc.Chrome(options=chrome_options)
#driver = webdriver.Chrome(options=chrome_options)
# driver.get("https://www.google.com")
# scraper = cloudscraper.create_scraper()

t1 = time.time()
url = 'https://www.cian.ru/sale/flat/288994161/'
driver.get(url)
# time.sleep(300)
try:
    WebDriverWait(driver, timeout=100).until(EC.presence_of_element_located((By.XPATH, "//div[@data-name='PriceInfo']")))
    driver.execute_script("window.stop();")
except:
    print('не успел')
# print(driver.execute_script('return navigator.webdriver'))
# print(driver.find_element(By.XPATH, "//meta[@itemprop='price']").get_attribute("content"))
content = driver.page_source
# with open("page_source.html", "r", encoding="utf-8") as file:
#    content = file.read()
with open("page_source.html", "w", encoding='utf-8') as f:
    f.write(content)
# soup = BeautifulSoup(content, features="html.parser")
tree = html.fromstring(content)

# блок 1
asideMainInfo = tree.xpath("//div[@data-name='AsideMainInfo']")[0]
price = asideMainInfo.xpath(".//div[@data-name='PriceInfo']/div/span")[0].text
offerFacts = asideMainInfo.xpath(".//div[@data-name='OfferFactItem']")
transaction_terms = offerFacts[1].xpath(".//p")[1].text
mortgage = offerFacts[2].xpath(".//p")[1].text

# блок 2
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
# residential_complex = mainNew.xpath(".//div[@data-name='ParentNew']/a/text()")[0]
adress_items = mainNew.xpath(".//div[@data-name='AddressContainer']/a/text()")
city = adress_items[0]
street = adress_items[3][4:]
house_id = adress_items[4]

# блок 3
objectFactoids = tree.xpath("//div[@data-name='ObjectFactoids']")[0]
object_data = objectFactoids.xpath(".//div[@data-name='ObjectFactoidsItem']/div[2]/span/text()")
object_data_dict = {}
for i in range(0, len(object_data), 2):
    object_data_dict[object_data[i]] = object_data[i + 1].rstrip('\xa0м²')
object_data_dict['Этаж квартиры'] = object_data_dict['Этаж'].split()[0]
object_data_dict['Этажей в доме'] = object_data_dict['Этаж'].split()[2]
object_data_dict.pop('Этаж', None)
# living_square = object_data[1].text
# kitchen_square = object_data[2].text
# flat_floor = object_data[3].text.split()[0]
# max_floor = object_data[3].text.split()[2]
# house_year = object_data[4].text

# блок 4
description = tree.xpath("//div[@data-name='Description']/div/div/*/span")[0].text

# блок 5
flat_info, house_info = tree.xpath("//div[@data-name='OfferSummaryInfoGroup']")
p_tags_flats = flat_info.xpath(".//p/text()")
flat_info_dict = {}
for i in range(0, len(p_tags_flats), 2):
    flat_info_dict[p_tags_flats[i]] = p_tags_flats[i + 1].rstrip('\xa0м')
p_tags_house = house_info.xpath(".//p/text()")
house_info_dict = {}
for i in range(0, len(p_tags_house), 2):
    house_info_dict[p_tags_house[i]] = p_tags_house[i + 1].rstrip('\xa0м')

# блок 6
# y = yadisk.YaDisk("ec228561582a46baa7c3f88907c0395d", "46145e37e4cf415d8283490af86b6113")
# y.token = 'y0_AgAAAAANYmzbAAf07QAAAADl13LC72bkYNO7So6osrxeT1dmwOorZhQ'
images = tree.xpath("//div[@data-name='GalleryInnerComponent']/div/div")[0].xpath('.//img')
print(images)
# if y.exists('temp'):
#     y.remove('temp')
# if os.path.exists("temp"):
#     shutil.rmtree("temp")
# if os.path.exists("cian"):
#     shutil.rmtree("cian")
#
# time.sleep(5)
# y.mkdir('temp')
# os.mkdir('temp')
# os.mkdir('cian')
# offer_id, images_url = 5435738945, [x.get('src') for x in images]
# for i in range(len(images_url)):
#     y.upload_url(images_url[i], path=f'temp/image{i}.jpg')
#
# for i in range(len(images_url)):
#     y.download(f'temp/image{i}.jpg', f'temp/image{i}.jpg')
#     y.remove(f'temp/image{i}.jpg')

# os.mkdir(f'cian/{offer_id}')
# for i in range(len(images_url)):
#     img = cv2.imread(f'temp/image{i}.jpg')
#     resize_img = cv2.resize(img, (256, 256))
#     cv2.imwrite(f'cian/{offer_id}/image{i}.jpg', resize_img)
#     os.remove(f'temp/image{i}.jpg')



# images = tree.xpath("//div[@data-name='GalleryInnerComponent']/div/div")[0].xpath('.//img')
# print(len(images))
# for i in range(len(images)):
#     image_url = images[i].get('src')
#     print(image_url)
#     urllib.request.urlretrieve(image_url, f'cian/image{i}.jpg')
# images = driver.find_elements(By.XPATH, "//div[@data-name='GalleryInnerComponent']/div/div")[0].find_elements(By.XPATH, './/img')
# print(images)
#
# # Проходимся по списку изображений
# for index, image in enumerate(images):
#     # Получаем изображение в формате base64
#     image_base64 = image.screenshot_as_base64
#
#     # Преобразуем изображение в файл и сохраняем на компьютер
#     with open(f"cian/image_{index}.png", "wb") as f:
#         f.write(base64.b64decode(image_base64))


print(f'Цена: {str(price)}\n'
      f'Условия сделки: {transaction_terms}\n'
      f'Ипотека: {mortgage}\n'
      f'Количество комнат: {rooms_count}\n'
      f'Тип недвижимости: {house_type}\n'
      f'Общая площадь: {total_square}\n'
      # f'ЖК: {residential_complex}\n'
      f'Город: {city}\n'
      f'Улица: {street}\n'
      f'Номер дома: {house_id}\n'
      f'Основные данные об обьекте: {object_data_dict}\n'
      # f'Жилая площадь: {living_square}\n'
      # f'Кухонная площадь: {kitchen_square}\n'
      # f'Этаж квартиры: {flat_floor}\n'
      # f'Всего этажей: {max_floor}\n'
      # f'Год постройки: {house_year}\n'
      f'Описание: {[description]}\n'
      f'Инфо о квартире: {flat_info_dict}\n'
      f'Инфо о доме: {house_info_dict}\n')
# dom = etree.HTML(str(soup))
# print(dom.xpath("//span[starts-with(@class, 'style-price-value-main')]/span")[0].text)
t2 = time.time()
print(t2 - t1)

# t1 = time.time()
# links = []
# idx = []
# for link in soup:
#     if link.has_attr('href') and 'card' in link['href']:
#         id = list(filter(None, re.split('_|/', link['href'])))[-1]
#         if re.match('^[0-9]{5,}', id):
#             links.append(link['href'])
#             idx.append(int(id))
# print(links)
# t2 = time.time()
# print(t2-t1)
