from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

driver = webdriver.Chrome()
url = "https://hk.trip.com/sale/w/8198/citimastercardoffer.html?promo_referer=11_8198_2"
driver.get(url)

wait = WebDriverWait(driver, 20)

while True:
    try:
        elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='ui-coupon-card_name' and contains(text(),'Citi Mastercard 半價酒店優惠')]")))
        parent_div = elem.find_element(By.XPATH, "..")
        classes = parent_div.get_attribute("class")

        if "ui-coupon-card-disabled" in classes:
            print("名額已用盡，繼續監控...")
        else:
            print(">>> 有半價酒店名額！快去搶！")
            break

    except TimeoutException:
        print("元素超時未找到，重新嘗試...")

    time.sleep(10)  # 每10秒檢查一次

driver.quit()
