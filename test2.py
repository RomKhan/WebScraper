from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import ChromiumOptions
import undetected_chromedriver
from threading import Thread
from time import sleep
import time
import os
import yadisk

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-size=%s" % '1920 1080')
chrome_options.page_load_strategy = 'none'
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
driver = uc.Chrome(options=chrome_options, user_multi_procs=True)

driver.get('https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=2&region=1&sort=creation_date_desc')
time.sleep(100)