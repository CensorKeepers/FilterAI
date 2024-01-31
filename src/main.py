from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
# Specify the path to chromedriver using the Service class
service = Service(executable_path=r"D:\\WebDriver\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=service)

url = "https://docs.google.com/document/d/1GGQOYBCpAYAqnwLBn5mnSm83y7oMld0ni46GLhY55V4/edit"
driver.get(url)

try:
    # Wait for the entire page to load (up to 10 seconds)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    html_content = driver.page_source
    with open('html_content.txt', 'w', encoding='utf-8') as file:
        file.write(html_content)
    sleep(5)
finally:
    driver.quit()
