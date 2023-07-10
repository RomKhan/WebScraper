import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
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
    driver = uc.Chrome(options=chrome_options)

    driver.get('https://www.google.ru/')

    element = get_element_or_none(driver, "/html/body/div[2]/div/main/h1", 20)
    if element is not None:
        print("We defeated Cloudflare, 🎉🥳 :)")
    else:
        print("Cloudflare defeated us :(, No woory we will try again. ")
    driver.quit()

if __name__ == "__main__":
    run()