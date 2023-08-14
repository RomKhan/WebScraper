import csv
import time

import yadisk

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
# getLoc = loc.geocode("Москва, п. Рязановское, с. Остафьево, ЖК «Остафьево»")
#
# # printing address
# print(getLoc.address)
#
# # printing latitude and longitude
# print("Latitude = ", getLoc.latitude)
# print("Longitude = ", getLoc.longitude)
# t2 = time.time()
# print(t2-t1)

# t1 = time.time()
# from dadata import Dadata
# token = "6dbb03e58a44a30b7f7ddcf27a6bf2711d731a71"
# dadata = Dadata(token)
# result = dadata.suggest("address", "г Москва, Басманный, Большая Почтовая, 38, стр 6 ")
# print(result)
# t2 = time.time()
# print(t2-t1)

import requests

csv_file_path = "data-1690913646095.csv"
csv_reader = csv.reader(open(csv_file_path, 'r'))
next(csv_reader)
for row in csv_reader:
    t1 = time.time()
    adress = row[1]
    cookies = {
        'is_gdpr': '0',
        'is_gdpr_b': 'CI3/eBCctwEoAg==',
        '_ym_uid': '1684029496202916917',
        'yandexuid': '464076991637414352',
        'yuidss': '464076991637414352',
        'i': 'S26VXV33O8LfJIsq7xVoMuH13fkG4irH/S648kxDPU/Tng5bAE8Psd0yv5quDgTIsIlPZDDsmMvHOv5lmTLBsuTdQYk=',
        'my': 'YwA=',
        '_ym_d': '1687522995',
        'gdpr': '0',
        '_ym_isad': '2',
        'yp': '1690201385.csc.1#1690201395.hdrc.0#2002897385.pcs.1#4294967295.skin.s#1699797498.szm.2:1440x900:1440x434#1690114977.ygu.1#1691004166.yu.464076991637414352',
        'ymex': '1693509766.oyu.464076991637414352#1999389499.yrts.1684029499',
        '_yasc': '+JjcWQJL6DSw7zB6+iy6UqpKAVs+il/HmEvEv1Pdu0neNs/ykjRF34RBW1s+Tw==',
        'bh': 'Ej8iTm90L0EpQnJhbmQiO3Y9Ijk5IiwiR29vZ2xlIENocm9tZSI7dj0iMTE1IiwiQ2hyb21pdW0iO3Y9IjExNSIaBSJhcm0iIhAiMTE1LjAuNTc5MC4xMTQiKgI/MDoHIm1hY09TIkIIIjEzLjQuMCJKBCI2NCJSXCJOb3QvQSlCcmFuZCI7dj0iOTkuMC4wLjAiLCJHb29nbGUgQ2hyb21lIjt2PSIxMTUuMC41NzkwLjExNCIsIkNocm9taXVtIjt2PSIxMTUuMC41NzkwLjExNCIi',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        # 'Cookie': 'is_gdpr=0; is_gdpr_b=CI3/eBCctwEoAg==; _ym_uid=1684029496202916917; yandexuid=464076991637414352; yuidss=464076991637414352; i=S26VXV33O8LfJIsq7xVoMuH13fkG4irH/S648kxDPU/Tng5bAE8Psd0yv5quDgTIsIlPZDDsmMvHOv5lmTLBsuTdQYk=; my=YwA=; _ym_d=1687522995; gdpr=0; _ym_isad=2; yp=1690201385.csc.1#1690201395.hdrc.0#2002897385.pcs.1#4294967295.skin.s#1699797498.szm.2:1440x900:1440x434#1690114977.ygu.1#1691004166.yu.464076991637414352; ymex=1693509766.oyu.464076991637414352#1999389499.yrts.1684029499; _yasc=+JjcWQJL6DSw7zB6+iy6UqpKAVs+il/HmEvEv1Pdu0neNs/ykjRF34RBW1s+Tw==; bh=Ej8iTm90L0EpQnJhbmQiO3Y9Ijk5IiwiR29vZ2xlIENocm9tZSI7dj0iMTE1IiwiQ2hyb21pdW0iO3Y9IjExNSIaBSJhcm0iIhAiMTE1LjAuNTc5MC4xMTQiKgI/MDoHIm1hY09TIkIIIjEzLjQuMCJKBCI2NCJSXCJOb3QvQSlCcmFuZCI7dj0iOTkuMC4wLjAiLCJHb29nbGUgQ2hyb21lIjt2PSIxMTUuMC41NzkwLjExNCIsIkNocm9taXVtIjt2PSIxMTUuMC41NzkwLjExNCIi',
        'Origin': 'https://yandex.kz',
        'Referer': 'https://yandex.kz/maps/213/moscow/house/zhiloy_kompleks_kvartal_maryino_k1/Z04YdQdhTk0PQFtvfXl1eXVmZQ==/?ll=37.301788%2C55.548951&utm_source=main_stripe_big&z=15',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    params = {
        'add_chains_loc': '1',
        'add_coords': '1',
        'add_rubrics_loc': '1',
        'bases': 'geo,biz,transit',
        'client_reqid': '1690918422368_4713',
        'exprt': '282,283',
        'fullpath': '1',
        'lang': 'ru_KZ',
        'll': '37.301788,55.548951',
        'origin': 'maps-search-form',
        'outformat': 'json',
        'part': adress,
        'pos': '0',
        'spn': '0.041027069091796875,0.0007298896081664452',
        'v': '9',
        'yu': '464076991637414352',
    }
    response = requests.get('https://suggest-maps.yandex.kz/suggest-geo', params=params, cookies=cookies, headers=headers)
    t2 = time.time()
    d = response.json()
    try:
        print(t2-t1, response.json()['results'][0]['pos'], adress)
    except:
        print('не вышло', t2-t1, adress)
    time.sleep(0.5)


# import requests
# import json
# import time
# import zipfile
# import io
# from bs4 import BeautifulSoup
#
#
# class Batch:
#     SERVICE_URL = "https://batch.geocoder.ls.hereapi.com/6.2/jobs"
#     jobId = None
#
#     def __init__(self, apikey="Ваш ключ для REST API "):
#         self.apikey = apikey
#
#     def start(self, filename, indelim=";", outdelim=";"):
#
#         file = open(filename, 'rb')
#
#         params = {
#             "action": "run",
#             "apiKey": self.apikey,
#             "politicalview": "RUS",
#             "gen": 9,
#             "maxresults": "1",
#             "header": "true",
#             "indelim": indelim,
#             "outdelim": outdelim,
#             "outcols": "displayLatitude,displayLongitude,locationLabel,houseNumber,street,district,city,postalCode,county,state,country",
#             "outputcombined": "true",
#         }
#
#         response = requests.post(self.SERVICE_URL, params=params, data=file)
#         self.__stats(response)
#         file.close()
#
#     def status(self, jobId=None):
#
#         if jobId is not None:
#             self.jobId = jobId
#
#         statusUrl = self.SERVICE_URL + "/" + self.jobId
#
#         params = {
#             "action": "status",
#             "apiKey": self.apikey,
#         }
#
#         response = requests.get(statusUrl, params=params)
#         self.__stats(response)
#
#     def result(self, jobId=None):
#
#         if jobId is not None:
#             self.jobId = jobId
#
#         print("Requesting result data ...")
#
#         resultUrl = self.SERVICE_URL + "/" + self.jobId + "/result"
#
#         params = {
#             "apiKey": self.apikey
#         }
#
#         response = requests.get(resultUrl, params=params, stream=True)
#
#         if (response.ok):
#             zipResult = zipfile.ZipFile(io.BytesIO(response.content))
#             zipResult.extractall()
#             print("File saved successfully")
#
#         else:
#             print("Error")
#             print(response.text)
#
#     def __stats(self, response):
#         if (response.ok):
#             parsedXMLResponse = BeautifulSoup(response.text, "lxml")
#
#             self.jobId = parsedXMLResponse.find('requestid').get_text()
#
#             for stat in parsedXMLResponse.find('response').findChildren():
#                 if (len(stat.findChildren()) == 0):
#                     print("{name}: {data}".format(name=stat.name, data=stat.get_text()))
#
#         else:
#             print(response.text)
#
# encoder = Batch('cvLoXDb_2zNQBQedLLtvqx-ZFc6Tbi5_m9ERrOgSBgE')
# encoder.start("data-1690913646095.csv", indelim=";", outdelim=";")


# import cloudscraper
#
# scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
# # Or: scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
# print(scraper.get("https://domclick.ru/search?deal_type=sale&category=living&offer_type=flat&offer_type=layout&sale_price__lte=10000000&sort=published&sort_dir=desc&sale_price__gte=100000&offset=0").text)  # => "<!DOCTYPE html><html><head>..."
