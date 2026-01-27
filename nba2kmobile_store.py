import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

STORE_URL = "https://www.nba2kmobile.com/"
STORE_CLAIM_SELECTOR = "button#buy-button-41phPr2U3tIPS96a4lPSSk"  # From your JSON

PLAYER_IDS = [
    "35932434",  # First in your Store JSON
    "1000117281547",  # Second in your Store JSON
]


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver


def element_exists(driver, by, selector, timeout=3):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return True
    except TimeoutException:
        return False


def clear_player_id_cookies(driver):
    driver.get(STORE_URL)
    driver.delete_all_cookies()


def fill_and_submit_player_id(driver, player_id):
    # Click "type in my player id" (matches your event-click "button.text-button-m")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.text-button-m"))
    ).click()

    # Fill userid-input (matches your forms block)
    userid_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="userid-input"]'))
    )
    userid_input.clear()
    userid_input.send_keys(player_id)

    # Submit (matches your event-click "//*[@id=\"product-redeem-button\"]")
    driver.find_element(By.XPATH, '//*[@id="product-redeem-button"]').click()

    # CONTINUE button (matches your event-click with waitForSelector=true)
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-testid="userid-continue-button"]')
            )
        ).click()
    except TimeoutException:
        pass  # Matches your onError handling

    # Close lightbox (matches your event-click)
    try:
        close_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-testid="lightbox-close-button"]')
            )
        )
        close_btn.click()
    except TimeoutException:
        pass


def claim_store_for_player(driver, player_id):
    clear_player_id_cookies(driver)

    driver.get(STORE_URL)
    time.sleep(3)

    if element_exists(driver, By.CSS_SELECTOR, STORE_CLAIM_SELECTOR):
        print(f"[Store][{player_id}] CLAIM GIFT button found.")

        # FIXED: Scroll using direct CSS selector (no stale element)
        driver.execute_script(f"""
            let btn = document.querySelector('{STORE_CLAIM_SELECTOR}');
            if (btn) {{
                btn.scrollIntoView({{block: 'center'}});
            }}
        """)
        time.sleep(1)

        # Try normal click first
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, STORE_CLAIM_SELECTOR))
            ).click()
        except:
            # JS click fallback
            driver.execute_script(f"document.querySelector('{STORE_CLAIM_SELECTOR}').click();")
            print(f"[Store][{player_id}] Using JS click fallback.")

        fill_and_submit_player_id(driver, player_id)
        driver.refresh()
        time.sleep(2)
        print(f"[Store][{player_id}] Done!")
    else:
        print(f"[Store][{player_id}] No claimable gift.")


def main():
    driver = create_driver()
    try:
        for pid in PLAYER_IDS:
            claim_store_for_player(driver, pid)
            time.sleep(2)  # Delay between accounts
    finally:
        time.sleep(2)
        driver.quit()


if __name__ == "__main__":
    main()
