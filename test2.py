from selenium.webdriver.chrome.options import ChromiumOptions
import undetected_chromedriver
from threading import Thread
from time import sleep
import time
import os
import yadisk

# y = yadisk.YaDisk("ec228561582a46baa7c3f88907c0395d", "46145e37e4cf415d8283490af86b6113")
# url = y.get_code_url()
#
# print("Go to the following url: %s" % url)
# code = input("Enter the confirmation code: ")
# response = y.get_token(code)
#y.token = response.access_token
# if y.check_token():
#     print("Sucessfully received token!")
# else:
#     print("Something went wrong. Not sure how though...")

y = yadisk.YaDisk("ec228561582a46baa7c3f88907c0395d", "46145e37e4cf415d8283490af86b6113")
y.token = 'y0_AgAAAAANYmzbAAf07QAAAADl13LC72bkYNO7So6osrxeT1dmwOorZhQ'

y.upload_url('https://cdn-p.cian.site/images/1779637157-1.jpg', path='test/img1')