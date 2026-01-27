import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DAILY_STREAK_URL = "https://www.nba2kmobile.com/dailystreak"

PLAYER_IDS = [
    "1000117281547",
    "35932434",
]

# --- AUTO-GENERATED SELECTORS START ---
CLAIM_SELECTORS = [
    "button#buy-button-1KpDKvhJLRLmPXNnd78W4W",  # D1 CLAIM
    "button#buy-button-2L8m303YrHQKgfHlcQALwD",  # D2 CLAIM
    "button#buy-button-3cOtvjyvWemL4qrN0iHztw",  # D3 CLAIM
    "button#buy-button-3pL7JBXXzOGO4VLnJGDwUS",  # D4 CLAIM
    "button#buy-button-3Qt0vdqOrCGDop9UA4wERu",  # D5 CLAIM
    "button#buy-button-1PEdEiSB8ZKFtu3HUBOX1m",  # D6 CLAIM
    "button#buy-button-7GaRsbOfuZn0MH9zBgryQ",  # D7 CLAIM
    "button#buy-button-5Y6m2LwZwzmrV5RNxzMntq",  # Final Reward CLAIM
]

# D7 CLAIM selector
D7_SELECTOR = "button#buy-button-7GaRsbOfuZn0MH9zBgryQ"

# Final Reward CLAIM selector
FINAL_REWARD_SELECTOR = "button#buy-button-5Y6m2LwZwzmrV5RNxzMntq"
# --- AUTO-GENERATED SELECTORS END ---
def create_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # uncomment for headless
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver

def element_exists(driver, by, selector, timeout=1):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return True
    except TimeoutException:
        return False

def clear_player_id_cookies(driver):
    driver.get("https://www.nba2kmobile.com")
    driver.delete_all_cookies()

def claim_for_player(driver, player_id):
    """One full run of your workflow for a single Player ID."""
    clear_player_id_cookies(driver)
    driver.get(DAILY_STREAK_URL)
    time.sleep(3)

    claimed_any = False
    for selector in CLAIM_SELECTORS:
        if element_exists(driver, By.CSS_SELECTOR, selector, timeout=1):
            print(f"{player_id} Found claim button {selector}")
            claim_reward(driver, selector, player_id)
            claimed_any = True

            # If this was the D7 CLAIM, click Final Reward CLAIM after process finishes
            if selector == D7_SELECTOR:
                time.sleep(2)  # Let D7 claim complete
                try:
                    final_reward_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, FINAL_REWARD_SELECTOR))
                    )
                    driver.execute_script("arguments[0].click();", final_reward_btn)
                    print(f"{player_id} Final Reward clicked.")

                    # Wait for and click the CONTINUE button that appears
                    time.sleep(1)  # Small delay for dialog to appear
                    try:
                        continue_btn = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, 'button[data-testid="userid-continue-button"]'))
                        )
                        driver.execute_script("arguments[0].click();", continue_btn)
                        print(f"{player_id} Final Reward CONTINUE button clicked.")
                    except TimeoutException:
                        print(f"{player_id} Continue button not found for Final Reward.")

                    print(f"{player_id} Final Reward claimed successfully.")

                except TimeoutException:
                    print(f"{player_id} Final Reward button not clickable.")
            break

    if claimed_any:
        print(f"{player_id} Done!")
    else:
        print(f"{player_id} No claimable reward found.")


def claim_reward(driver, claim_selector, player_id):
    # Initial claim button click
    claim_btn = driver.find_element(By.CSS_SELECTOR, claim_selector)
    driver.execute_script("arguments[0].click();", claim_btn)

    # "text-button-m" button - this is failing
    button_m = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.text-button-m"))
    )
    driver.execute_script("arguments[0].click();", button_m)

    # User ID input
    userid_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="userid-input"]'))
    )
    userid_input.clear()
    userid_input.send_keys(player_id)

    # Redeem button
    redeem_btn = driver.find_element(By.XPATH, '//*[@id="product-redeem-button"]')
    driver.execute_script("arguments[0].click();", redeem_btn)

    # Continue button (if exists)
    try:
        continue_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="userid-continue-button"]'))
        )
        driver.execute_script("arguments[0].click();", continue_btn)
    except TimeoutException:
        print(f"{player_id} Already Done or no CONTINUE button.")  # Change to player_id

    # Close button (if exists)
    try:
        close_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="lightbox-close-button"]'))
        )
        driver.execute_script("arguments[0].click();", close_btn)
    except TimeoutException:
        pass


def main():
    driver = create_driver()
    try:
        for pid in PLAYER_IDS:
            claim_for_player(driver, pid)
            # small delay between accounts
            time.sleep(2)
    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    main()
