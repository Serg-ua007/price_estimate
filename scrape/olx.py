from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

def search_olx(driver, query):
    driver.get("https://www.olx.ua/uk/")
    search_box = driver.find_element(By.ID, "search")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(1)

def modify_url(driver):
    current_url = driver.current_url
    modified_url = f"{current_url}?currency=UAH&search%5Bfilter_enum_state%5D%5B0%5D=used"
    driver.get(modified_url)
    time.sleep(1)

def smooth_scroll(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def parse_results(driver):
    items = []
    results = driver.find_elements(By.CSS_SELECTOR, "[data-cy='l-card']")
    for result in results:
        title_element = result.find_element(By.CSS_SELECTOR, "[data-cy='ad-card-title'] a")
        title = title_element.text
        link = title_element.get_attribute("href")
        price = result.find_element(By.CSS_SELECTOR, "[data-testid='ad-price']").text
        image_element = result.find_element(By.CSS_SELECTOR, "img")
        image_src = image_element.get_attribute("data-src") or image_element.get_attribute("src")
        items.append({
            "title": title,
            "link": link,
            "price": price,
            "image": image_src
        })
    return items

def parse_olx(query):
    driver = setup_driver()
    items = []
    try:
        search_olx(driver, query)
        modify_url(driver)
        driver.execute_script("document.body.style.zoom='10%'")
        smooth_scroll(driver)
        items = parse_results(driver)
    except Exception as e:
        logging.error(f"Error occurred while parsing OLX: {e}")
    finally:
        driver.quit()
    return items

if __name__ == "__main__":
    query = "nike shoes"
    items = parse_olx(query)
    for item in items:
        print(item)
