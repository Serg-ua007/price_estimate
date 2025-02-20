from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

def parse_shafa(query):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    items = []
    try:
        # Open the web page
        driver.get("https://shafa.ua/uk/")

        # Find the search box element
        search_box = driver.find_element(By.NAME, "search_text")

        # Enter the search query
        search_box.send_keys(query)

        # Submit the search form
        search_box.send_keys(Keys.RETURN)

        # Wait for the results to load
        time.sleep(1)

        # Click on the checkbox element
        try:
            checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='KcVwEkK1Bdm2A16S32kw' and text()='Ідеальний']"))
            )
            checkbox.click()
            logging.debug("Clicked on the checkbox element")
        except Exception as e:
            logging.error(f"Error clicking on the checkbox element: {e}")
            driver.quit()
            return items

        # Wait for the results to load
        time.sleep(2)  

        # Parse the results
        results = driver.find_elements(By.CSS_SELECTOR, ".dqgIPe4iXPIqxKvRxLb7")
        for result in results:
            title_element = result.find_element(By.CSS_SELECTOR, "a.CnMTkDcKcdyrztQsbqaj")
            title = title_element.text
            link = title_element.get_attribute("href")
            price = result.find_element(By.CSS_SELECTOR, ".D8o9s7KcxqtQ7bd2ka_W p").text
            
            # Extract the original image URL from the data-src attribute
            image_element = result.find_element(By.CSS_SELECTOR, "img.wD1fsK7iYTacsxprHLBA")
            image = image_element.get_attribute("data-src")
            
            items.append({
                "title": title,
                "link": link,
                "price": price,
                "image": image
            })
    except Exception as e:
        logging.error(f"Error occurred while parsing Shafa: {e}")
    finally:
        driver.quit()
    return items

# Example usage
if __name__ == "__main__":
    query = "nike shoes"
    items = parse_shafa(query)
    for item in items:
        print(item)
