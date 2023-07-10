import time


def parse_all(scraper_type, link, city, type, website_name):
    t1 = time.time()
    url = scraper_type.parse_link(link)
    scraper = scraper_type(url, website_name, city, type)
    while not scraper.is_end:
        scraper.iter()
    t2 = time.time()
    print(f'Удалось спарсить {scraper.count_of_parsed} обявлений, '
          f'было отправлено {scraper.count_of_requests} запросов за {t2-t1} секунд')