from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def initialize_driver():
    return webdriver.Chrome()

def get_elements(driver, url, class_name):
    driver.get(url)

    elements = WebDriverWait(driver, 35).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, class_name))
    )
    return elements

def extract_information(element):
    title = element.find_element(By.CSS_SELECTOR, "h2").text
    price = element.find_element(By.CSS_SELECTOR, "h3.olx-text.olx-text--body-large.olx-text--block.olx-text--semibold.olx-ad-card__price").text
    location = element.find_element(By.CSS_SELECTOR, "div.olx-ad-card__location-date-container > p").text
    data = element.find_element(By.CSS_SELECTOR, "p.olx-ad-card__date--horizontal").text

    other_prices_elements = element.find_elements(By.CSS_SELECTOR, "div.olx-ad-card__priceinfo.olx-ad-card__priceinfo--horizontal > p")
    other_prices = [el.text for el in other_prices_elements]

    spans = element.find_elements(By.CSS_SELECTOR, 'li.olx-ad-card__labels-item > span')
    labels = [span.get_attribute('aria-label') for span in spans]

    return title, price, location, data, other_prices, labels


def print_information(title, price, location, data, other_prices, labels):
    print(title)
    print(price)
    print(other_prices)
    print(location)
    print(data)
    print(labels)
    print("-" * 10)
    time.sleep(0.5)

def main():
    driver = initialize_driver()

    url = 'https://www.olx.com.br/imoveis/venda/estado-sp/sao-paulo-e-regiao/zona-sul?pe=550000&ps=500001'
    class_name = 'renderIfVisible'

    elements = get_elements(driver, url, class_name)

    for element in elements:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        info = extract_information(element)
        print_information(*info)

    driver.quit()

if __name__ == "__main__":
    main()
