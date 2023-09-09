from datetime import datetime, timedelta
import json
import logging
import time
from kubernetes import client, config
import random

namespace = 'default'
configmap_name = "scraper-config"


def get_configmap():
    # config.load_kube_config()
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    configmap = v1.read_namespaced_config_map(name=configmap_name, namespace=namespace)
    return configmap, v1


def get_actual_state(website, type):
    configmap, v1 = get_configmap()
    key = f'{website}_{type}_state'
    cities = get_cities(configmap)
    urls = json.loads(configmap.data['shallow_url_dict'])
    if key not in configmap.data:
        first_city = cities[0]
        link = urls[f'{website}_{type}_{first_city}']
        return first_city, 0, 0, link
    else:
        city, min_price = configmap.data[key].split(':')
        city_index = cities.index(city)
        link = urls[f'{website}_{type}_{city}']
        return city, int(min_price), city_index, link


def get_cities(configmap):
    return configmap.data['cities'].split(',')


def next_city(website, current_city, type):
    configmap, v1 = get_configmap()
    cities = get_cities(configmap)
    urls = json.loads(configmap.data['shallow_url_dict'])
    current_city_index = cities.index(current_city)
    if current_city_index + 1 >= len(cities):
        return cities[0], 0, urls[f'{website}_{type}_{cities[0]}']
    else:
        return cities[current_city_index + 1], current_city_index + 1, urls[f'{website}_{type}_{cities[current_city_index + 1]}']


def save_state(website, city, type, min_price):
    configmap, v1 = get_configmap()
    key = f'{website}_{type}_state'
    # configmap.data[key] = f'{city}:{min_price + 50000}'
    patch = [{"op": "replace", "path": f"/data/{key}", "value": f'{city}:{min_price + 50000}'}]

    v1.patch_namespaced_config_map(
        name=configmap_name,
        namespace=namespace,
        body=patch
    )


def reset_state(website, type):
    configmap, v1 = get_configmap()
    key = f'{website}_{type}_state'
    patch = [{"op": "replace", "path": f"/data/{key}", "value": f'{get_cities(configmap)[0]}:{0}'}]

    v1.patch_namespaced_config_map(
        name=configmap_name,
        namespace=namespace,
        body=patch
    )


def shallow_parser(scraper_type, website, type):
    city, min_price, start_index, link = get_actual_state(website, type)
    save_state(website, city, type, min_price)
    is_new_cycle = False
    start_time = time.time()
    while not (is_new_cycle and (time.time()-start_time) < 24 * 60 * 60):
        if is_new_cycle:
            is_new_cycle = False
            start_time = time.time()
        t1 = time.time()
        url = scraper_type.parse_link(link)
        scraper = scraper_type(url, city, website, type, min_price)
        while not scraper.is_end:
            scraper.iter()
            save_state(website, city, type, scraper.current_price)

        city, current_index, link = next_city(website, city, type)
        if current_index == start_index:
            is_new_cycle = True
        min_price = 0

        t2 = time.time()
        logging.info(f'Удалось спарсить {scraper.count_of_parsed} обявлений, '
              f'было отправлено {scraper.count_of_requests} запросов за {t2 - t1} секунд')

    reset_state(website, type)
    logging.info(f'Успешно закончил обход по городам. Потребовалось {(time.time()-start_time) // 60} минут')


def get_deep_urls_with_appearing_mask(website, type):
    configmap, v1 = get_configmap()
    cities = get_cities(configmap)
    urls = json.loads(configmap.data['deep_url_dict'])
    link_token = urls[f'{website}_{type}']
    website_urls = []
    appearing_mask = []
    for city in cities:
        period, url = urls[f'{website}_{type}_{city}'].split(',')
        period = int(period)
        website_urls.append(url)
        appearing_mask.append(period)
    return cities, website_urls, appearing_mask, link_token



def deep_parser(scraper_type, website, type):
    cities, website_urls, appearing_mask, link_token = get_deep_urls_with_appearing_mask(website, type)
    sort_mask = sorted(range(len(appearing_mask)), key=lambda k: appearing_mask[k])
    finish_times = [0 for x in range(len(appearing_mask))]
    scrapers = []

    for i in range(len(website_urls)):
        url_components = scraper_type.parse_link(website_urls[i])
        scraper = scraper_type(url_components, link_token, website, cities[i], type)
        scrapers.append(scraper)

    while True:
        for i in sort_mask:
            t1 = time.time()
            if t1 - finish_times[i] > (appearing_mask[i] - 5)*60:
                logging.info(f'Парсю обялвения с города: {cities[i]}')
                scrapers[i].run()
                t2 = time.time()
                finish_times[i] = t2
                wait = random.randint(50, 240)
                time.sleep(wait)
        time.sleep(random.randint(appearing_mask[sort_mask[0]]-5, appearing_mask[sort_mask[0]]+5) * 60)
