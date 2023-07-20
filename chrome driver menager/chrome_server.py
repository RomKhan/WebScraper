import asyncio
import atexit
import logging
import os
import random
import signal
import sys
import time

from flask import Flask, request

import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver

app = Flask(__name__)
lock = False
shutdown_flag = False
# atexit.register(lambda: sys.exit(1))
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
# options.add_argument('--disable-features=VizDisplayCompositor')
# options.add_argument("--incognito")
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument("enable-automation")
# chrome_options.add_argument("--disable-browser-side-navigation")

options.add_argument('--disable-blink-features=AutomationControlled')
options.page_load_strategy = 'none'
driver = uc.Chrome(options=options,
                   user_multi_procs=True,
                   driver_executable_path=os.environ['CHROMEDRIVER_PATH']
                   )
# driver.execute_script(f"window.open('about:blank','_blank')")
# driver.execute_script(f"window.open('about:blank','_blank')")
# driver.switch_to.window(driver.window_handles[-1])

websites = dict()


async def async_get_page():
    # tabs_before = driver.window_handles
    # driver.get(url)
    #driver.execute_script(f"window.open('{url}','_blank')")
    # tab_id = list(set(driver.window_handles) - set(tabs_before))[0]
    # driver.switch_to.window(tab_id)
    # try:
    #     WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    # except:
    #     pass
    time.sleep(10)

@app.before_request
def check_shutdown():
    global shutdown_flag
    if shutdown_flag:
        os.kill(os.getpid(), signal.SIGINT)

@app.route('/getCooldown', methods=['GET'])
def get_cooldown():
    website = request.args.get('website')
    global websites
    if website in websites:
        return str(time.time() - websites[website])
    else:
        return '10000'


@app.route('/getPage', methods=['GET'])
async def handle_request():
    url = request.json['url']
    website = request.json['website']
    try:
        t1 = time.time()

        global lock
        while lock:
            await asyncio.sleep(0.5)
        lock = True
        driver.switch_to.new_window('tab')
        current_tab = driver.current_window_handle
        global websites
        websites[website] = time.time()
        driver.get(url)
        lock = False

        await asyncio.sleep(10)

        while lock:
            await asyncio.sleep(0.5)
        lock = True
        driver.switch_to.window(current_tab)
        driver.execute_script('window.stop;')
        page_source = driver.page_source
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        lock = False

        t2 = time.time()
        logging.info(t2 - t1)

        return page_source
    except Exception as e:
            # Если возникает исключение, вызываем sys.exit() только внутри функции handle_request()
            logging.error(f'An error occurred: {str(e)}')
            global shutdown_flag
            shutdown_flag = True
            lock = False


if __name__ == '__main__':
    host = 'localhost'
    port = 8082

    # Получение порта из переменной среды, если есть
    if 'PORT' in os.environ:
        port = int(os.environ['PORT'])

    app.run(host=host, port=port)
