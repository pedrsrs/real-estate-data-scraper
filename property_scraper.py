import time
import re
import sqlite3
from selenium import webdriver
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
    unparsed_property_price = element.find_element(By.CSS_SELECTOR, "h3.olx-text.olx-text--body-large.olx-text--block.olx-text--semibold.olx-ad-card__price").text
    location = element.find_element(By.CSS_SELECTOR, "div.olx-ad-card__location-date-container > p").text
    data = element.find_element(By.CSS_SELECTOR, "p.olx-ad-card__date--horizontal").text

    other_prices_elements = element.find_elements(By.CSS_SELECTOR, "div.olx-ad-card__priceinfo.olx-ad-card__priceinfo--horizontal > p")
    other_prices = [el.text for el in other_prices_elements]

    iptu, condominio = parse_other_prices(other_prices)

    spans = element.find_elements(By.CSS_SELECTOR, 'li.olx-ad-card__labels-item > span')
    labels = [span.get_attribute('aria-label') for span in spans]

    quartos, metros_quadrados, vagas_garagem, banheiros = parse_information(labels)

    property_price = parse_property_price(unparsed_property_price)
    neighborhood = parse_location(location)
    return title, property_price, neighborhood, data, other_prices, iptu, condominio, quartos, metros_quadrados, vagas_garagem, banheiros, labels

def parse_property_price(unparsed_property_price):
    property_price_digits = re.findall(r'\d+', unparsed_property_price)
    concatenated_price = ''.join(property_price_digits)
    return int(concatenated_price)

def parse_other_prices(other_prices):
    iptu = condominio = None

    for item in other_prices:
        if 'IPTU' in item:
            iptu = int(item.split()[-1].replace(".", ""))
        elif 'Condomínio' in item:
            condominio = int(item.split()[-1].replace(".", ""))

    return iptu, condominio

def parse_information(other_prices):
    quartos = metros_quadrados = vagas_garagem = banheiros = None

    for item in other_prices:
        if 'quarto' in item:
            quartos = int(item.split()[0])
        elif 'metro' in item:
            metros_quadrados = int(item.split()[0])
        elif 'garagem' in item:
            vagas_garagem = int(item.split()[0])
        elif 'banheiro' in item:
            banheiros = int(item.split()[0])

    return quartos, metros_quadrados, vagas_garagem, banheiros

def parse_location(location):
    neighborhood = location.split(", ")[1]
    return neighborhood

def insert_into_database(info, cursor, conn):
    cursor.execute('''
    INSERT INTO property_info (
        title, property_price, neighborhood, data, iptu, condominio, quartos, metros_quadrados, vagas_garagem, banheiros
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', info)
    conn.commit()
    
def main():
    # SQLite database connection
    conn = sqlite3.connect('property_data.db')
    cursor = conn.cursor()

    driver = initialize_driver()

    url = 'https://www.olx.com.br/imoveis/venda/estado-sp/sao-paulo-e-regiao/zona-sul?pe=550000&ps=500001'
    class_name = 'renderIfVisible'

    elements = get_elements(driver, url, class_name)

    for element in elements:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        info = extract_information(element)
        insert_into_database(info, cursor, conn)
        time.sleep(0.5)

    driver.quit()
    conn.close()

if __name__ == "__main__":
    main()
