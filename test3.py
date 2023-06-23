# import dropbox
#
#
# def upload_file_to_dropbox(file_url, dropbox_path):
#     response = client.files_save_url(dropbox_path, file_url)
#     return response
#
# access_token = 'sl.Bg2pPDXgB-faWuiZVUxgDZpxBnwgZ3KL19UM1j3oSwja1ivxGur8SMjo_WHylWhGzdgMgUfowrcaozh3kS7lLACKbJqNL6i9JNp15a-920C4msmHuka-h8hulnBzU6S69sbJGTs'
# client = dropbox.Dropbox(access_token)
#
# file_url = 'https://spb.cian.ru/sale/flat/286944730/'
# dropbox_path = '/test/page.html'
# response = upload_file_to_dropbox(file_url, dropbox_path)
# print(response)
import time

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import ChromiumOptions
from selenium import webdriver
from lxml import html


chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--proxy-server=%s' % PROXY)
#chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--window-size=%s" % "1920,1080")
chrome_options.page_load_strategy = 'none'
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
driver = uc.Chrome(options=chrome_options)
url = 'https://www.google.ru/search?q=https://spb.cian.ru/sale/flat/286944730/'
driver.get(url)
time.sleep(1)
content = driver.page_source
tree = html.fromstring(content)
links = tree.xpath("//a")
for i in range(len(links)):
    url = links[i].get('href')
    print(url)
time.sleep(5)
