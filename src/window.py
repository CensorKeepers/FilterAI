
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
# Specify the path to chromedriver using the Service class
service = Service(executable_path=r"D:\\WebDriver\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=service)

url = "https://google.com"
driver.get(url)

main_window_handle = driver.current_window_handle

new_window_handle = None
for handle in driver.window_handles:
    if handle != main_window_handle:
        new_window_handle = handle
        break
    
import time
time.sleep(10)
# Yeni sekmenin URL'sini al
if new_window_handle:
    # Yeni sekme veya pencereye geç
    driver.switch_to.window(new_window_handle)
    
    # URL'yi al
    print("Yeni sekmenin URL'si:", driver.current_url)
    
    # Yeni sekme ile işiniz bittiğinde, ana pencereye geri dönebilirsiniz
    driver.switch_to.window(main_window_handle)
else:
    print("Yeni sekme algılanmadı.")
    
driver.quit()