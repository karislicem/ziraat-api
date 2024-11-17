from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  # By modülünü içe aktarıyoruz
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import chromedriver_autoinstaller  # ChromeDriver'ı otomatik kurar
import time
from datetime import datetime

app = Flask(__name__)

# Önbellek için değişkenler
cache = None  # Önbelleğe alınan veriler
cache_timestamp = None  # Önbelleğe alınan verilerin zamanı
last_friday_cache = None  # Cuma günü alınan veriler
CACHE_DURATION = 1800  # Önbelleğin süresi (30 dakika = 1800 saniye)

# Selenium ile döviz kurlarını çekme fonksiyonu
def get_exchange_rates():
    # Selenium için Chrome/Chromium ayarları
    options = Options()
    options.add_argument('--headless')  # Headless mod
    options.add_argument('--no-sandbox')  # Sandbox modunu devre dışı bırakır
    options.add_argument('--disable-dev-shm-usage')  # Bellek kullanımını optimize eder
    options.add_argument('--disable-gpu')  # GPU'yu devre dışı bırakır
    options.add_argument('--disable-extensions')  # Gereksiz uzantıları devre dışı bırakır
    options.add_argument('--window-size=1920,1080')  # Tarayıcı pencere boyutunu ayarlar

    # Chromium'un tam yolunu belirtin
    options.binary_location = "/usr/bin/chromium-browser"  # Render ortamında Chromium genelde buradadır

    # WebDriver başlat
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://www.ziraatbank.com.tr/tr")
        dolar_alis = float(driver.find_element(By.XPATH, "//h3[text()='BANKA ALIŞ']/following-sibling::span").text.strip().replace(',', '.'))
        dolar_satis = float(driver.find_element(By.XPATH, "//h3[text()='BANKA SATIŞ']/following-sibling::span").text.strip().replace(',', '.'))
        euro_alis = float(driver.find_elements(By.XPATH, "//h3[text()='BANKA ALIŞ']/following-sibling::span")[1].text.strip().replace(',', '.'))
        euro_satis = float(driver.find_elements(By.XPATH, "//h3[text()='BANKA SATIŞ']/following-sibling::span")[1].text.strip().replace(',', '.'))
        return {"dolar_alis": dolar_alis, "dolar_satis": dolar_satis, "euro_alis": euro_alis, "euro_satis": euro_satis}
    finally:
        driver.quit()

# Hafta sonu kontrol fonksiyonu
def is_weekend():
    today = datetime.now().weekday()
    return today in [5, 6]  # Cumartesi = 5, Pazar = 6

# API endpoint tanımlaması
@app.route('/api/exchange_rates', methods=['GET'])
def exchange_rates():
    global cache, cache_timestamp, last_friday_cache

    try:
        # Hafta sonuysa ve cuma cache'i boşsa, veri çek ve kaydet
        if is_weekend():
            if not last_friday_cache:  # Eğer cuma verisi yoksa
                last_friday_cache = get_exchange_rates()
            return jsonify(last_friday_cache)

        # Hafta içiyse normal önbellek kontrolü
        if not cache or (time.time() - cache_timestamp > CACHE_DURATION):  # Önbellek süresi dolmuşsa
            cache = get_exchange_rates()
            cache_timestamp = time.time()

            # Eğer bugün cuma ise bu veriyi last_friday_cache'e kaydet
            if datetime.now().weekday() == 4:  # Cuma = 4
                last_friday_cache = cache

        # Önbellekteki veriyi döndür
        return jsonify(cache)

    except NoSuchElementException:
        return jsonify({"error": "Web element not found. The page structure may have changed."}), 500
    except TimeoutException:
        return jsonify({"error": "Request timed out. The page took too long to load."}), 500
    except Exception as e:
        # Hata detaylarını logla
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Boş bir yanıt döndürür
