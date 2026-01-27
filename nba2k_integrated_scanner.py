import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DAILY_STREAK_URL = "https://www.nba2kmobile.com/dailystreak"

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Default player IDs - update with your actual IDs
PLAYER_IDS = [
    "1000117281547",
    "35932434",
]

def scan_buy_buttons_static(url):
    """
    Scan the NBA 2K Mobile daily streak page for all 'buy-button-' elements (static HTML parsing).
    
    Args:
        url (str): The URL to scan
        
    Returns:
        dict: Contains button data and statistics
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        buttons = []
        
        for element in soup.find_all(True):
            element_id = element.get('id', '')
            element_class = element.get('class', [])
            
            if isinstance(element_class, list):
                element_class = ' '.join(element_class)
            
            if 'buy-button-' in element_id or 'buy-button-' in element_class:
                button_info = {
                    'tag': element.name,
                    'id': element_id if element_id else None,
                    'class': element.get('class', []),
                    'text': element.get_text(strip=True)[:100],
                    'type': element.get('type', None),
                    'data_attributes': {k: v for k, v in element.attrs.items() if k.startswith('data-')},
                    'onclick': element.get('onclick', None),
                    'selector': f"button#{element_id}" if element_id else None
                }
                buttons.append(button_info)
        
        results = {
            'url': url,
            'scan_type': 'static',
            'total_buttons_found': len(buttons),
            'buttons': buttons,
            'summary': {
                'button_types': {},
                'button_ids': [b['id'] for b in buttons if b['id']],
                'button_classes': []
            }
        }
        
        for button in buttons:
            tag = button['tag']
            results['summary']['button_types'][tag] = results['summary']['button_types'].get(tag, 0) + 1
        
        return results
        
    except requests.RequestException as e:
        return {
            'error': str(e),
            'url': url,
            'status': 'failed'
        }

def scan_buy_buttons_selenium(url):
    """
    Scan using Selenium to capture dynamically rendered buttons.
    
    Args:
        url (str): The URL to scan
        
    Returns:
        dict: Contains button data from Selenium
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Uncomment below for headless mode
    # options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        # Wait for page to load
        time.sleep(3)
        
        # Find all elements with 'buy-button-' in their ID
        buttons = []
        
        # Execute JavaScript to find all buy-button elements
        script = """
        return Array.from(document.querySelectorAll('[id*="buy-button-"]')).map(el => ({
            tag: el.tagName.toLowerCase(),
            id: el.id,
            class: el.className,
            text: el.innerText.substring(0, 100),
            type: el.type || null,
            visible: el.offsetParent !== null,
            selector: 'button#' + el.id
        }));
        """
        
        buttons = driver.execute_script(script)
        
        results = {
            'url': url,
            'scan_type': 'selenium',
            'total_buttons_found': len(buttons),
            'buttons': buttons,
            'summary': {
                'button_types': {},
                'visible_buttons': sum(1 for b in buttons if b['visible']),
                'hidden_buttons': sum(1 for b in buttons if not b['visible']),
            }
        }
        
        for button in buttons:
            tag = button['tag']
            results['summary']['button_types'][tag] = results['summary']['button_types'].get(tag, 0) + 1
        
        return results
        
    except Exception as e:
        return {
            'error': str(e),
            'url': url,
            'status': 'failed',
            'scan_type': 'selenium'
        }
    
    finally:
        driver.quit()

def generate_claim_selectors(button_data):
    """
    Generate CSS selectors from button data for CLAIM_SELECTORS list.
    
    Args:
        button_data (dict): Results from scan_buy_buttons
        
    Returns:
        list: CSS selectors ready to use
    """
    selectors = []
    
    if 'buttons' in button_data:
        for i, button in enumerate(button_data['buttons'], 1):
            if button.get('id'):
                selector = f"button#{button['id']}"  # Day {i} CLAIM
                selectors.append(selector)
    
    return selectors

def print_results(results):
    """Print formatted results to console."""
    if 'error' in results:
        print(f"Error scanning {results['url']}: {results['error']}")
        return
    
    print(f"\n{'='*80}")
    print(f"NBA 2K Mobile Buy Button Scanner Results [{results.get('scan_type', 'unknown').upper()}]")
    print(f"{'='*80}")
    print(f"URL: {results['url']}")
    print(f"Total 'buy-button-' elements found: {results['total_buttons_found']}")
    
    if 'visible_buttons' in results['summary']:
        print(f"Visible: {results['summary']['visible_buttons']} | Hidden: {results['summary']['hidden_buttons']}")
    
    print(f"\n{'SUMMARY':^80}")
    print(f"{'-'*80}")
    print(f"Button Types: {results['summary']['button_types']}")
    
    if results['buttons']:
        print(f"\n{'DETAILED BUTTON LIST':^80}")
        print(f"{'-'*80}")
        for i, button in enumerate(results['buttons'], 1):
            print(f"\nButton #{i}")
            print(f"  Selector: {button.get('selector', 'N/A')}")
            print(f"  Tag: {button['tag']}")
            print(f"  ID: {button.get('id', 'N/A')}")
            print(f"  Text: {button['text']}")
            if button.get('visible') is not None:
                print(f"  Visible: {button['visible']}")
    
    print(f"\n{'='*80}\n")

def print_python_code(selectors):
    """Print Python code snippet for CLAIM_SELECTORS."""
    if not selectors:
        print("No selectors found to generate code.")
        return
    
    print(f"\n{'='*80}")
    print("PYTHON CODE - Copy this into your nba2kmobile.py:")
    print(f"{'='*80}\n")
    print("CLAIM_SELECTORS = [")
    for i, selector in enumerate(selectors, 1):
        if i == len(selectors) - 1:
            print(f'    "{selector}",  # D{i} CLAIM')
        elif i == len(selectors):
            print(f'    "{selector}",  # Final Reward CLAIM')
        else:
            print(f'    "{selector}",  # D{i} CLAIM')
    print("]\n")
    
    # Print D7 and Final Reward constants
    if len(selectors) >= 7:
        d7_selector = selectors[6]  # D7 is the 7th button (index 6)
        print(f'D7_SELECTOR = "{d7_selector}"')
    
    if len(selectors) >= 8:
        final_reward_selector = selectors[7]  # Final Reward is the 8th button (index 7)
        print(f'FINAL_REWARD_SELECTOR = "{final_reward_selector}"  # replace with the actual Final Reward selector1')
    
    print(f"\n{'='*80}\n")

def save_json_results(results, filename='buy_buttons.json'):
    """Save results to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {filename}")

def save_selectors_to_file(selectors, filename='claim_selectors.py'):
    """Save selectors as Python code."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Auto-generated CLAIM_SELECTORS from button scanner\n\n")
        f.write("CLAIM_SELECTORS = [\n")
        for i, selector in enumerate(selectors, 1):
            if i == len(selectors) - 1:
                f.write(f'    "{selector}",  # D{i} CLAIM\n')
            elif i == len(selectors):
                f.write(f'    "{selector}",  # Final Reward CLAIM\n')
            else:
                f.write(f'    "{selector}",  # D{i} CLAIM\n')
        f.write("]\n\n")
        
        # Add D7 and Final Reward constants if we have enough selectors
        if len(selectors) >= 7:
            d7_selector = selectors[6]  # D7 is the 7th button (index 6)
            f.write(f"# D7 CLAIM selector\n")
            f.write(f'D7_SELECTOR = "{d7_selector}"\n\n')
        
        if len(selectors) >= 8:
            final_reward_selector = selectors[7]  # Final Reward is the 8th button (index 7)
            f.write(f"# Final Reward CLAIM selector\n")
            f.write(f'FINAL_REWARD_SELECTOR = "{final_reward_selector}"\n')
    
    print(f"Selectors saved to {filename}")

if __name__ == "__main__":
    print("Starting NBA 2K Mobile Buy Button Scanner...")
    print("\nChoose scan method:")
    print("1. Static (faster, uses requests+BeautifulSoup)")
    print("2. Selenium (detects dynamic elements)")
    
    choice = input("Enter choice (1 or 2, default 2): ").strip() or "2"
    
    if choice == "1":
        print("\nRunning static scan...")
        results = scan_buy_buttons_static(DAILY_STREAK_URL)
    else:
        print("\nRunning Selenium scan (opening browser)...")
        results = scan_buy_buttons_selenium(DAILY_STREAK_URL)
    
    # Display results
    print_results(results)
    
    # Generate selectors
    if 'buttons' in results:
        selectors = generate_claim_selectors(results)
        print_python_code(selectors)
        
        # Save files
        save_json_results(results)
        save_selectors_to_file(selectors)
    
    print("\n✓ Scan complete!")
    print("  - Results saved to: buy_buttons.json")
    print("  - Selectors saved to: claim_selectors.py")
    print("\nNext step: Copy the CLAIM_SELECTORS code into your nba2kmobile.py file")
