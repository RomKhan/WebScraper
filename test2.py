import unidecode
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import ChromiumOptions
import undetected_chromedriver
from threading import Thread
from time import sleep
import time
import os
import yadisk
import requests

# y = yadisk.YaDisk("ec228561582a46baa7c3f88907c0395d", "46145e37e4cf415d8283490af86b6113")
# y.token = 'y0_AgAAAAANYmzbAAf07QAAAADl13LC72bkYNO7So6osrxeT1dmwOorZhQ'
# if y.exists('test'):
#     y.remove('test')
# time.sleep(2)
# y.mkdir('test')
# y.upload_url('https://spb.cian.ru/sale/flat/286944730/', 'test/page.html')

# importing geopy library
# from geopy.geocoders import Nominatim
#
# t1 = time.time()
# # calling the Nominatim tool
# loc = Nominatim(user_agent="GetLoc")
#
# # entering the location name
# getLoc = loc.geocode("Санкт-Петербург, ул. Адмирала Коновалова, 2-4")
#
# # printing address
# print(getLoc.address)
#
# # printing latitude and longitude
# print("Latitude = ", getLoc.latitude, "\n")
# print("Longitude = ", getLoc.longitude)
# t2 = time.time()
# print(t2-t1)
import subprocess

chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
subprocess.call([chrome_path])