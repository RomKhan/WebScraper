import asyncio
import logging
import queue
import time

import requests
from dadata import Dadata


class MyQueue(queue.Queue):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = 0

    def put(self, item, block=True, timeout=None):
        super().put(item, block, timeout)
        self.size += 1

    def get(self, block=True, timeout=None):
        item = super().get(block, timeout)
        self.size -= 1
        return item


class AddressManager:
    def __init__(self, tokens):
        self.free_dadata = {}
        self.address_queue = MyQueue()
        self.address_history = {}
        # self.tokens_time_to_update = {}
        self.is_active = True
        self.dataworker = None
        self.db_loop = None
        for token, secret in tokens:
            dadata = Dadata(token, secret)
            sug_count = dadata.get_daily_stats()['services']['suggestions']
            self.free_dadata[token] = [dadata, sug_count]
            # self.tokens_time_to_update[token] = time.time()

    def check_for_update(self):
        for token in self.free_dadata:
            try:
                self.free_dadata[token][1] = self.free_dadata[token][0].get_daily_stats()['services']['suggestions']
            except:
                continue
            # if time.time() - self.free_dadata[token][2] > 86400:
            #     self.free_dadata[token] = [Dadata(token), 0, time.time()]

    def get_address_via_yandex(self, address):
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
            'part': address,
            'pos': '0',
            'spn': '0.041027069091796875,0.0007298896081664452',
            'v': '9',
            'yu': '464076991637414352',
        }
        response = requests.get('https://suggest-maps.yandex.kz/suggest-geo', params=params, cookies=cookies,
                                headers=headers)
        result = response.json()['results'][0]
        lon, lat = result['pos'].split(',')
        full_address = result['log_id']['where']['name']
        return lon, lat, full_address

    def address_finder(self):
        while self.is_active:
            dadata = None
            for token in self.free_dadata:
                if self.free_dadata[token][1] < 10000:
                    dadata = self.free_dadata[token][0]
                    self.free_dadata[token][1] += 1
                # if self.free_dadata[token][1] == 10000:
                #     self.free_dadata.pop(0)
            if dadata is None:
                self.check_for_update()
                logging.info(f'в очереди: {self.address_queue.size}')
                time.sleep(300)
                continue

            offer = self.address_queue.get()
            # t1 = time.time()
            if offer['Адресс'] in self.address_history:
                lon, lat, full_address = self.address_history[offer['Адресс']]
            else:
                try:
                    result = dadata.suggest("address", offer['Адресс'])
                    if len(result) == 0:
                        lon, lat, full_address = self.get_address_via_yandex(offer['Адресс'])
                    else:
                        lon, lat, full_address = result[0]['data']['geo_lon'], result[0]['data']['geo_lat'], result[0]['unrestricted_value']
                except:
                    lon, lat, full_address = None, None, None

            self.db_loop.create_task(self.dataworker.patch_address(lat, lon, full_address, offer))
            self.address_history[offer['Адресс']] = (lon, lat, full_address)
            if len(self.address_history) > 200:
                first_key = next(iter(self.address_history))
                self.address_history.pop(first_key)
            # print(time.time() - t1, lon, lat, full_address, offer['listing_id'])









