import asyncio
import atexit
import logging
import os
import random
import signal
import string
import subprocess
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from fastapi import FastAPI, HTTPException, Response
import asyncio
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver

app = FastAPI()
lock = False
shutdown_flag = False
logging.basicConfig(level=logging.INFO, format='%(message)s')

useragents = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.2.625 Yowser/2.5 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 YaBrowser/20.12.2.105 Yowser/2.5 Safari/537.36'
]

# Инициализация Selenium ChromeDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-infobars')
options.add_argument(f"--user-agent={random.choice(useragents)}")
options.add_argument('--blink-settings=imagesEnabled=false')

options.add_argument('--disable-blink-features=AutomationControlled')
options.page_load_strategy = 'none'
driver = uc.Chrome(options=options,
                   driver_executable_path=os.environ['CHROMEDRIVER_PATH'],
                   user_multi_procs=True
                   )

websites = dict()
driver.set_page_load_timeout(8)


@app.get("/ping", status_code=200)
def ping():
    return "I AM OK!"

def waiter(website):
    page_source = None
    try:
        if website == 'cian':
            page_source = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))).get_attribute("outerHTML")
        elif website == 'domclick':
            page_source = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'noscript'))).get_attribute("outerHTML")
        elif website == 'avito':
            page_source = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))).get_attribute("outerHTML")
        elif website == 'yandex':
            page_source = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))).get_attribute("outerHTML")
    except:
        pass
    return page_source

def shutdown_gunicorn():
    # Команда для завершения сервера Gunicorn
    cmd = 'pkill -f "gunicorn"'
    subprocess.call(cmd, shell=True)

def shutdown_docker():
    # Команда для завершения контейнера Docker
    cmd = 'docker container stop your_container_name'
    subprocess.call(cmd, shell=True)

def shutdown():
    global shutdown_flag
    if shutdown_flag:
        os.kill(os.getpid(), signal.SIGINT)


@app.get('/tryReserve', status_code=200)
async def try_reserve(website: str, cooldown: str):
    key = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    global websites
    if website in websites:
        if time.time() - websites[website][0] >= float(cooldown):
            websites[website][2] = key
            websites[website][1] = True
            websites[website][0] = time.time()
            return {'key': f'{key}'}
    else:
        websites[website] = [time.time(), True, key]
        return {'key': f'{key}'}

    raise HTTPException(status_code=404, detail="not reserved")


page_queue = []
url_queue = []
buffer = dict()
home_page_id = driver.current_window_handle
def page_manager():
    global shutdown_flag
    global websites
    while True:
        logging.info(f'Количество открытых вкладок: {len(driver.window_handles)}')
        for i in range(len(url_queue)):
            url, website, key = url_queue.pop(0)
            websites[website][0] = time.time()
            driver.switch_to.new_window('tab')
            driver.get(url)
            page_tab = driver.current_window_handle
            page_queue.append([page_tab, website, key, time.time()])
        if len(page_queue) > 0:
            current_tab, website, key, start_time = page_queue.pop(0)
            try:
                t1 = time.time()
                driver.switch_to.window(current_tab)
                page_source = waiter(website)
                logging.info(f'Прошел waiter, {website}, {time.time() - t1}')
                if page_source is not None and len(page_source) > 1000:
                    buffer[key] = page_source.encode('utf-8')
                    driver.close()
                    driver.switch_to.window(home_page_id)
                    websites[website][1] = False
                    logging.info(f'Получилось, {website}, {time.time() - t1}')
                else:
                    page_queue.append([current_tab, website, key, start_time])
            except Exception as e:
                logging.error(f'An error occurred: {str(e)}')
                shutdown_flag = True
                shutdown()
        if len(page_queue) == len(url_queue) == 0:
            time.sleep(1)

async def parse_page(website, url):
    logging.info(f'Количество открытых вкладок: {len(driver.window_handles)}')
    global lock
    global shutdown_flag
    while lock:
        if shutdown_flag:
            raise Exception('shutdown')
        websites[website][0] = time.time()
        time.sleep(1)
    lock = True
    websites[website][0] = time.time()
    driver.switch_to.new_window('tab')
    page_tab = driver.current_window_handle
    driver.get(url)
    lock = False

    await asyncio.sleep(5)

    while lock:
        if shutdown_flag:
            raise Exception('shutdown')
        time.sleep(1)
    lock = True
    t1 = time.time()
    driver.switch_to.window(page_tab)
    page_source = driver.page_source
    # logging.info(f'page_source - {page_source}, {website}, {time.time() - t1}')
    driver.close()
    driver.switch_to.window(home_page_id)
    lock = False
    websites[website][1] = False
    logging.info(f'Получилось, {website}, {time.time() - t1}')
    return page_source

@app.get('/getPage', status_code=200)
async def handle_request(request_json: dict):
    url = request_json['url']
    website = request_json['website']
    key = request_json['key']
    logging.info(f"Получил запрос, {website}")

    global websites
    if website not in websites:
        raise HTTPException(status_code=404, detail="not reserved")
    if websites[website][2] != key:
        raise HTTPException(status_code=404, detail="wrong pod key")

    page_source = ''
    global shutdown_flag
    try:
        page_source = await parse_page(website, url)
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        shutdown_flag = True
        shutdown()
    headers = {
        "Content-Type": "text/html"
    }
    return Response(content=page_source, headers=headers)
