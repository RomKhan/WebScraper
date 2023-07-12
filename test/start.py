import undetected_chromedriver as uc
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as Firefox_Options
from selenium.webdriver.firefox.service import Service
from selenium import webdriver


def get_element_or_none(driver, xpath, wait=None):
    try:
        if wait is None:
            return driver.find_element(By.XPATH, xpath)
        else:
            return WebDriverWait(driver, wait).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
    except:
        return None


def run():
    print('ggr34345bgfbr402342olvfovfvdf--34=4234023')
    chrome_options = webdriver.ChromeOptions()
    # PROXY = "92.255.7.162:8080"
    # chrome_options.add_argument('--proxy-server=%s' % PROXY)
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--incognito")
    # chrome_options.add_argument('--disable-dev-shm-usage')

    # chrome_options.add_argument("enable-automation")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--disable-browser-side-navigation")

    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument("--window-size=%s" % "1920,1080")
    chrome_options.page_load_strategy = 'none'
    # chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    # driver = uc.Chrome(options=chrome_options)
    binary = FirefoxBinary('geckodriver.log')
    firefox_options = Firefox_Options()
    driverService = Service('geckodriver')
    profile = webdriver.FirefoxProfile()
    firefox_options.profile = profile
    PROXY_HOST = "92.255.7.162"
    PROXY_PORT = "8080"
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.http", PROXY_HOST)
    profile.set_preference("network.proxy.http_port", int(PROXY_PORT))
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference('useAutomationExtension', False)
    profile.update_preferences()
    desired = DesiredCapabilities.FIREFOX
    driver = webdriver.Firefox(service=driverService, options=firefox_options)

    driver.get('https://spys.one/proxys/RU/')


    element = get_element_or_none(driver, "/html/body/div[2]/div/main/h1", 20)
    if element is not None:
        print("We defeated Cloudflare, 🎉🥳 :)")
    else:
        print("Cloudflare defeated us :(, No woory we will try again. ")
    driver.quit()

if __name__ == "__main__":
    run()