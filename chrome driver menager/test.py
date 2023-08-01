# import psycopg2
#
# db_conn = psycopg2.connect(user='postgres',
#                            password='1242241к',
#                            host='localhost',
#                            port=5432,
#                            database='realestatedb')
#
# cursor = db_conn.cursor()
# new_records = [
#     ('value1', None, None, '289437744'),
#     ('value2', None, None, '289417744'),
#     ('value3', None, None, '189417744')
# ]
# insert_query = f"""UPDATE Listings SET seller_name = %s,
# 		   description = %s,
# 		   price = %s
# WHERE listing_id = %s
# RETURNING *"""
#
# cursor.execute(insert_query, new_records[0])
# db_conn.commit()
#
# updated_rows = cursor.fetchall()
# d = 0
import os
import threading
import time

from selenium.webdriver.common.by import By

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-images=True")
options.add_argument('--disable-infobars')
# options.add_argument('--proxy-server=http://88.87.93.124:40973')
# options.add_argument('--disable-features=VizDisplayCompositor')
# options.add_argument("--incognito")
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument("enable-automation")
# chrome_options.add_argument("--disable-browser-side-navigation")

options.add_argument('--disable-blink-features=AutomationControlled')
options.page_load_strategy = 'normal'
driver = uc.Chrome(options=options, user_multi_procs=True
                   )
driver.execute_cdp_cmd('Page.enable', {})
driver.execute_cdp_cmd('Network.enable', {})

# driver.get('https://whatismyipaddress.com/ru/index')
# time.sleep(10)
driver.set_page_load_timeout(10)
# driver.implicitly_wait(2)
driver.switch_to.new_window('tab')
try:
    threading.Thread(target=driver.get, args=('https://realty.ya.ru/moskva/kupit/kvartira/?sort=PRICE'))
except:
    pass
# body = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
# try:
#     WebDriverWait(driver, 10).until(lambda d: False)
# except:
#     pass
# time.sleep(10)
# driver.execute_script("window.stop();")
t1 = time.time()
while time.time() - t1 < 10:
    page_source = driver.page_source
    print(page_source)
# page_source = driver.find_element(By.TAG_NAME, 'body').get_attribute("outerHTML")
print(time.time()-t1)
# print(page_source)
driver.get('https://www.cian.ru/cat.php?currency=2&deal_type=sale&engine_version=2&maxprice=8000000&minprice=100000&offer_type=flat&p=2&region=1&sort=price_object_order')
body = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
t1 = time.time()
page_source = driver.find_element(By.TAG_NAME, 'body').get_attribute("outerHTML")
print(time.time()-t1)
driver.get('https://domclick.ru/search?deal_type=sale&category=living&offer_type=flat&offer_type=layout&sale_price__lte=7000000&sort=price&sort_dir=asc&sale_price__gte=10000&offset=0')
time.sleep(10)
driver.get('https://www.avito.ru/moskva/kvartiry/prodam?bt=1&pmax=10000000&pmin=100000&p=1&s=1')
time.sleep(10)
