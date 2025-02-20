from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

def parse_olx(query):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    items = []
    try:
        # Open the web page
        driver.get("https://www.olx.ua/uk/")

        # Set the viewport size
        driver.set_window_size(1200, 11000)

        # Find the search box element
        search_box = driver.find_element(By.ID, "search")

        # Enter the search query
        search_query = query
        search_box.send_keys(search_query)

        # Submit the search form
        search_box.send_keys(Keys.RETURN)

        # Wait for the results to load
        time.sleep(1)

        # Modify the URL to include additional parameters
        current_url = driver.current_url
        modified_url = f"{current_url}?currency=UAH&search%5Bfilter_enum_state%5D%5B0%5D=used"
        driver.get(modified_url)

        # Wait for the results to update
        time.sleep(1)

        # Smooth scroll through the page to load all images
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(2)  # Wait for images to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Parse the results
        results = driver.find_elements(By.CSS_SELECTOR, "[data-cy='l-card']")
        for result in results:
            title_element = result.find_element(By.CSS_SELECTOR, "[data-cy='ad-card-title'] a")
            title = title_element.text
            link = title_element.get_attribute("href")
            price = result.find_element(By.CSS_SELECTOR, "[data-testid='ad-price']").text
            
            image_element = result.find_element(By.CSS_SELECTOR, "img")
            image_src = image_element.get_attribute("data-src") or image_element.get_attribute("src")
            
            # Wait for the image to load if it's a placeholder
            if 'no_thumbnail' in image_src:
                WebDriverWait(driver, 10).until(
                    lambda d: image_element.get_attribute("data-src") != image_src or image_element.get_attribute("src") != image_src
                )
                image_src = image_element.get_attribute("data-src") or image_element.get_attribute("src")
            
            items.append({
                "title": title,
                "link": link,
                "price": price,
                "image": image_src
            })
    except Exception as e:
        logging.error(f"Error occurred while parsing OLX: {e}")
    finally:
        driver.quit()
    return items

# Example usage
if __name__ == "__main__":
    query = "nike shoes"
    items = parse_olx(query)
    for item in items:
        print(item)
