from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By

app = Flask(__name__)

def get_exchange_rates():
    driver = webdriver.Chrome()
    try:
        driver.get("https://www.ziraatbank.com.tr/tr")
        dolar_alis = driver.find_element(By.XPATH, "//h3[text()='BANKA ALIŞ']/following-sibling::span").text.strip()
        dolar_satis = driver.find_element(By.XPATH, "//h3[text()='BANKA SATIŞ']/following-sibling::span").text.strip()
        euro_alis = driver.find_elements(By.XPATH, "//h3[text()='BANKA ALIŞ']/following-sibling::span")[1].text.strip()
        euro_satis = driver.find_elements(By.XPATH, "//h3[text()='BANKA SATIŞ']/following-sibling::span")[1].text.strip()
        return {"dolar_alis": dolar_alis, "dolar_satis": dolar_satis, "euro_alis": euro_alis, "euro_satis": euro_satis}
    finally:
        driver.quit()

@app.route('/api/exchange_rates', methods=['GET'])
def exchange_rates():
    rates = get_exchange_rates()
    return jsonify(rates)


