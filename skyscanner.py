import base64
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://www.skyscanner.com.hk/transport/flights/hkg/chc/260327/260410/?adultsv2=2&cabinclass=economy&childrenv2=&ref=home&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false"
OUT = "skyscanner_full.png"

USER_DATA_DIR = r"C:\temp\skyscanner_profile"   # persistent profile folder [web:120]
PROFILE_DIR = "Default"                         # optional [web:120]

PRICE_RE = re.compile(r"HK\$\s*\d")
CAPTCHA_PATH = "/sttc/px/captcha"

def wait_prices_stable(driver, min_prices=10, stable_seconds=4, timeout=120):
    end = time.time() + timeout
    last = -1
    stable_since = time.time()

    while time.time() < end:
        count = len(PRICE_RE.findall(driver.page_source))
        if count != last:
            last = count
            stable_since = time.time()

        if count >= min_prices and (time.time() - stable_since) >= stable_seconds:
            return True

        time.sleep(0.5)

    return False

def full_page_screenshot_png(driver, out_path):
    metrics = driver.execute_cdp_cmd("Page.getLayoutMetrics", {})  # [web:115]
    width = int(metrics["contentSize"]["width"])
    height = int(metrics["contentSize"]["height"])

    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
        "mobile": False,
        "width": width,
        "height": height,
        "deviceScaleFactor": 1,
    })

    shot = driver.execute_cdp_cmd("Page.captureScreenshot", {      # [web:115]
        "format": "png",
        "clip": {"x": 0, "y": 0, "width": width, "height": height, "scale": 1},
    })

    driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})

    with open(out_path, "wb") as f:
        f.write(base64.b64decode(shot["data"]))

options = Options()
options.add_argument(fr"--user-data-dir={USER_DATA_DIR}")          # [web:120]
options.add_argument(fr"--profile-directory={PROFILE_DIR}")        # [web:120]
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(120)

try:
    driver.get(URL)

    # If verification appears, complete it manually once.
    if CAPTCHA_PATH in driver.current_url:
        input("Verification shown. Complete 'PRESS & HOLD' in the browser, then press Enter...")
        WebDriverWait(driver, 180).until(lambda d: CAPTCHA_PATH not in d.current_url)

    wait_prices_stable(driver, min_prices=10, stable_seconds=4, timeout=120)
    full_page_screenshot_png(driver, OUT)

    input("Saved screenshot. Press Enter to close...")
finally:
    driver.quit()
