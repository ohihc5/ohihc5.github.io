import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

# URL to scan
url = "https://www.nba2kmobile.com/dailystreak"

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scan_buy_buttons(url):
    """
    Scan the NBA 2K Mobile daily streak page for all 'buy-button-' elements.
    
    Args:
        url (str): The URL to scan
        
    Returns:
        dict: Contains button data and statistics
    """
    try:
        # Fetch the page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all elements with IDs or classes containing 'buy-button-'
        buttons = []
        
        # Search by ID containing 'buy-button-'
        for element in soup.find_all(True):  # Find all elements
            element_id = element.get('id', '')
            element_class = element.get('class', [])
            
            if isinstance(element_class, list):
                element_class = ' '.join(element_class)
            
            # Check if 'buy-button-' is in ID or class
            if 'buy-button-' in element_id or 'buy-button-' in element_class:
                button_info = {
                    'tag': element.name,
                    'id': element_id if element_id else None,
                    'class': element.get('class', []),
                    'text': element.get_text(strip=True)[:100],  # First 100 chars
                    'type': element.get('type', None),
                    'data_attributes': {k: v for k, v in element.attrs.items() if k.startswith('data-')},
                    'onclick': element.get('onclick', None),
                    'attributes': dict(element.attrs)
                }
                buttons.append(button_info)
        
        # Compile results
        results = {
            'url': url,
            'total_buttons_found': len(buttons),
            'buttons': buttons,
            'summary': {
                'button_types': {},
                'button_ids': [b['id'] for b in buttons if b['id']],
                'button_classes': set()
            }
        }
        
        # Generate summary statistics
        for button in buttons:
            tag = button['tag']
            results['summary']['button_types'][tag] = results['summary']['button_types'].get(tag, 0) + 1
            if button['class']:
                results['summary']['button_classes'].update(button['class'])
        
        results['summary']['button_classes'] = list(results['summary']['button_classes'])
        
        return results
        
    except requests.RequestException as e:
        return {
            'error': str(e),
            'url': url,
            'status': 'failed'
        }

def print_results(results):
    """Print formatted results to console."""
    if 'error' in results:
        print(f"Error scanning {results['url']}: {results['error']}")
        return
    
    print(f"\n{'='*70}")
    print(f"NBA 2K Mobile Buy Button Scanner Results")
    print(f"{'='*70}")
    print(f"URL: {results['url']}")
    print(f"Total 'buy-button-' elements found: {results['total_buttons_found']}")
    print(f"\n{'SUMMARY':^70}")
    print(f"{'-'*70}")
    print(f"Button Types: {results['summary']['button_types']}")
    print(f"Total Unique IDs: {len(results['summary']['button_ids'])}")
    print(f"Total Unique Classes: {len(results['summary']['button_classes'])}")
    
    if results['buttons']:
        print(f"\n{'DETAILED BUTTON LIST':^70}")
        print(f"{'-'*70}")
        for i, button in enumerate(results['buttons'], 1):
            print(f"\nButton #{i}")
            print(f"  Tag: {button['tag']}")
            if button['id']:
                print(f"  ID: {button['id']}")
            print(f"  Classes: {', '.join(button['class']) if button['class'] else 'None'}")
            print(f"  Text: {button['text']}")
            if button['type']:
                print(f"  Type: {button['type']}")
            if button['data_attributes']:
                print(f"  Data Attributes: {button['data_attributes']}")
            if button['onclick']:
                print(f"  OnClick: {button['onclick'][:80]}...")
    
    print(f"\n{'='*70}\n")

def save_json_results(results, filename='buy_buttons.json'):
    """Save results to JSON file."""
    # Convert sets to lists for JSON serialization
    if 'summary' in results and 'button_classes' in results['summary']:
        results['summary']['button_classes'] = list(results['summary']['button_classes'])
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    print("Starting NBA 2K Mobile Buy Button Scanner...")
    
    # Scan the page
    results = scan_buy_buttons(url)
    
    # Display results
    print_results(results)
    
    # Save to JSON
    save_json_results(results)
