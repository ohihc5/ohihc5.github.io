#!/usr/bin/env python3
"""
NBA Link Scraper with Browser - Click elements and extract play.sportsteam368.com links
Usage: python3 nba_link_scraper_browser.py [url] [--json|--csv|--txt]
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sys
import json
from datetime import datetime
import time


def setup_browser():
    """Initialize Chrome browser with Selenium"""
    chrome_options = Options()
    # Uncomment the line below to run in headless mode (no window)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    return webdriver.Chrome(options=chrome_options)


def browse_and_click(url):
    """Browse URL, wait for page load, and click signal_show elements"""
    driver = setup_browser()

    try:
        print(f"🌐 Opening URL: {url}")
        driver.get(url)

        # Wait for page to load
        time.sleep(3)

        # Find and click all elements with class "signal_show"
        try:
            wait = WebDriverWait(driver, 10)
            signal_elements = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "signal_show"))
            )

            print(f"✅ Found {len(signal_elements)} signal_show element(s)")

            # Click each element with a delay
            for i, element in enumerate(signal_elements, 1):
                try:
                    print(f"   Clicking element {i}...")
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    element.click()
                    time.sleep(2)
                except Exception as e:
                    print(f"   ⚠️  Could not click element {i}: {e}")

        except Exception as e:
            print(f"⚠️  No signal_show elements found or error: {e}")

        # Wait a bit for dynamic content to load
        time.sleep(3)

        # Get page source after clicks
        html_content = driver.page_source
        print("✅ Page loaded and elements clicked successfully")

        return html_content

    except Exception as e:
        print(f"❌ Error browsing URL: {e}")
        return None

    finally:
        driver.quit()


def extract_sportsteam_links(html_content):
    """Extract only play.sportsteam368.com links from HTML"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        all_links = soup.find_all('a', href=True)

        sportsteam_links = []
        seen_urls = set()  # To avoid duplicates

        for link in all_links:
            href = link.get('href', '').strip()
            text = link.get_text(strip=True)

            # Only include play.sportsteam368.com links
            if 'play.sportsteam368.com' in href and href not in seen_urls:
                sportsteam_links.append({
                    'url': href,
                    'text': text
                })
                seen_urls.add(href)

        return sportsteam_links
    except Exception as e:
        print(f"❌ Error parsing HTML: {e}")
        return []


def print_results(links):
    """Print results in a clean format"""
    if not links:
        print("\n⚠️  No play.sportsteam368.com links found.")
        return

    print(f"\n✅ Found {len(links)} play.sportsteam368.com link(s):\n")
    print("=" * 80)

    for i, link in enumerate(links, 1):
        print(f"\n[Link {i}]")
        print(f"  URL:  {link['url']}")
        print(f"  Text: {link['text'] if link['text'] else '(no text)'}")

    print("\n" + "=" * 80)
    print(f"\nTotal: {len(links)} links")


def export_results(links, format='json'):
    """Export results to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format == 'json':
        filename = f"sportsteam_links_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=2)

    elif format == 'csv':
        filename = f"sportsteam_links_{timestamp}.csv"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("URL,Link Text\n")
            for link in links:
                url = link['url'].replace('"', '""')
                text = link['text'].replace('"', '""')
                f.write(f'"{url}","{text}"\n')

    elif format == 'txt':
        filename = f"sportsteam_links_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for link in links:
                f.write(f"{link['url']}\n")

    print(f"\n💾 Results exported to: {filename}")
    return filename


def main():
    # Get URL from command line argument or prompt user
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        url = sys.argv[1]
    else:
        print("🔍 NBA Link Scraper with Browser Automation\n")
        url = input("📍 Please enter the URL to scan: ").strip()

        if not url:
            print("❌ URL cannot be empty!")
            sys.exit(1)

    export_format = None

    if len(sys.argv) > 2:
        export_format = sys.argv[2].lstrip('-').lower()

    print(f"\n🔍 Starting browser automation...\n")

    # Browse, click elements, and get HTML
    html_content = browse_and_click(url)
    if not html_content:
        sys.exit(1)

    # Extract sportsteam links
    links = extract_sportsteam_links(html_content)

    # Display results
    print_results(links)

    # Export if requested
    if export_format in ['json', 'csv', 'txt']:
        export_results(links, export_format)


if __name__ == "__main__":
    main()
