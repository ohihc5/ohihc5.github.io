import time
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- ⚠️ 用戶設定 (請確保這裡填對) ---
MATCH_URL = "https://bet.hkjc.com/ch/football/allodds/50059378"
TELEGRAM_TOKEN = "8280639222:AAFJKch8jXT55D9z_e1LE7tEp-pc2OtQgJQ"
TELEGRAM_CHAT_ID = "531773457"

# --- 設定匯報間隔 (分鐘) ---
REPORT_INTERVAL_MINUTES = 30


def send_telegram(message):
    """發送訊息到 Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram 發送失敗: {e}")


def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def get_real_handicap(driver):
    try:
        # 直接鎖定 .oddsLine.HDC (最準確的讓球區塊)
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".oddsLine.HDC"))
        )

        items = container.find_elements(By.CLASS_NAME, "hdcOddsItem")

        if len(items) >= 2:
            home_line = items[0].find_element(By.CLASS_NAME, "cond").text.strip()
            home_odd = items[0].find_element(By.CSS_SELECTOR, ".oddsValue span").text.strip()

            away_line = items[1].find_element(By.CLASS_NAME, "cond").text.strip()
            away_odd = items[1].find_element(By.CSS_SELECTOR, ".oddsValue span").text.strip()

            return {
                "home_line": home_line,
                "home_odd": home_odd,
                "away_line": away_line,
                "away_odd": away_odd,
                "time": datetime.now().strftime("%H:%M:%S")
            }
    except:
        return None


def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 啟動監控 (每 {REPORT_INTERVAL_MINUTES} 分鐘匯報一次)...")
    send_telegram(f"🚀 監控程式已啟動！\n監察賽事：阿仙奴 vs 阿士東維拉\n設定：每 {REPORT_INTERVAL_MINUTES} 分鐘匯報一次")

    driver = init_driver()

    try:
        driver.get(MATCH_URL)
        print("   ...正在載入頁面...")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        last_data = None
        # 記錄上次發送 Telegram 的時間
        last_tg_time = datetime.now()

        while True:
            # 1. 獲取數據
            try:
                current_data = get_real_handicap(driver)
            except Exception as e:
                print(f"\n⚠️ 瀏覽器連接問題，正在重連... ({e})")
                try:
                    driver.quit()
                except:
                    pass
                driver = init_driver()
                driver.get(MATCH_URL)
                time.sleep(5)
                continue

            if current_data:
                # 當前數據 Tuple
                current_values = (
                    current_data['home_line'], current_data['home_odd'],
                    current_data['away_line'], current_data['away_odd']
                )

                info_str = f"主(阿仙奴) {current_data['home_line']} @ *{current_data['home_odd']}*\n客(維拉)   {current_data['away_line']} @ *{current_data['away_odd']}*"

                # A. 第一次運行
                if last_data is None:
                    last_data = current_values
                    print(f"\n[{current_data['time']}] 🔵 初始盤口鎖定")
                    send_telegram(f"🔵 *初始盤口鎖定*\n{info_str}")
                    last_tg_time = datetime.now()  # 更新發送時間

                # B. 發現變動 (優先級最高，即刻 Send)
                elif current_values != last_data:
                    print(f"\n[{current_data['time']}] 🔥 賠率變動！")

                    try:
                        trend = "🔺 升水" if float(current_data['home_odd']) > float(last_data[1]) else "🔻 跌水"
                    except:
                        trend = "⚠️ 變盤"

                    msg = f"🔥 *賠率變動警告* ({trend})\n\n{info_str}\n\n(前值: {last_data[1]})"
                    send_telegram(msg)

                    last_data = current_values  # 更新記憶
                    last_tg_time = datetime.now()  # 重置定時器

                # C. 無變動，但時間到了 (每30分鐘)
                else:
                    # 計算距離上次發送過了多久
                    time_diff = datetime.now() - last_tg_time
                    if time_diff > timedelta(minutes=REPORT_INTERVAL_MINUTES):
                        print(f"\n[{current_data['time']}] ⏰ 發送定時匯報...")
                        send_telegram(f"⏰ *{REPORT_INTERVAL_MINUTES}分鐘定時匯報* (無變動)\n\n{info_str}")
                        last_tg_time = datetime.now()  # 重置定時器

            else:
                # 抓不到數據時的重試邏輯
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ⚠️ 暫時無數據 (重刷中)...", end='')
                driver.refresh()
                time.sleep(5)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # --- 倒數計時顯示 ---
            # 為了讓你知道程式還活著
            for i in range(30, 0, -1):
                # 顯示目前盤口與下次檢查時間
                status_msg = f"[{datetime.now().strftime('%H:%M:%S')}] 🟢 監控中... (主: {last_data[1] if last_data else '?'}) | 下次檢查: {i}s "
                print(status_msg, end='\r', flush=True)
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 停止程式。")
        send_telegram("🛑 監控程式已手動停止。")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()