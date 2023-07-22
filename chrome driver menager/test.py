import random
import time

import pychrome
import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options


# Запуск Chrome с включенным CDP
chrome_options = Options()
# chrome_options.add_argument('--proxy-server=http://' + proxy)
driver = uc.Chrome(options=chrome_options)

# Инициализация CDP клиента
driver.get("https://www.whatismyip.com/")
time.sleep(20)

# Изменение прокси
proxy_settings = {
    "mode": "fixed_servers",
    "server": "92.255.7.162:8080",  # Замените на свои данные прокси
}

t1 = time.time()
chrome_options = Options()
chrome_options.add_argument('--proxy-server=http://92.255.7.162:8080')
driver = uc.Chrome(options=chrome_options)
print(time.time() - t1)

# options = driver.options
# # options.arguments.remove(f'--proxy-server=http://{proxy}')
# options.add_argument('--proxy-server=http://' + proxy)

# Загрузка страницы
driver.get("https://www.whatismyip.com/")
time.sleep(20)

# Продолжайте работу с браузером Selenium с новым прокси

# Закрытие браузера
driver.quit()