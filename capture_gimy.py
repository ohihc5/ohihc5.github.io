import requests
import datetime
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
# 1. Paste your "Internal Integration Secret" here (keep the quotes)


# 2. Your specific Database ID (extracted from your link)



# --- PART 1: SCRAPE DATA ---
def capture_streams(url):
    print(f"🚀 Starting scrape for: {url}")
    with sync_playwright() as p:
        # headless=True runs it in the background. Change to False to see the browser.
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        m3u8_urls = set()
        subtitle_urls = set()

        def handle_route(route):
            url_lower = route.request.url.lower()
            if '.m3u8' in url_lower:
                print(f"🎥 HLS Found: {route.request.url}")
                m3u8_urls.add(route.request.url)
            elif any(ext in url_lower for ext in ['.vtt', '.srt', '.ass', '.ssa']):
                print(f"📝 Subtitle Found: {route.request.url}")
                subtitle_urls.add(route.request.url)
            route.continue_()

        page.route("**/*", handle_route)

        try:
            page.goto(url, timeout=60000)
            print("⏳ Waiting for page load and video init...")
            page.wait_for_timeout(10000)

            # Check for <track> elements explicitly
            tracks = page.eval_on_selector_all('video track[src]', 'els => els.map(el => el.src)')
            for track in tracks:
                if track:
                    subtitle_urls.add(track)

        except Exception as e:
            print(f"⚠️ Warning during scrape: {e}")
        finally:
            browser.close()

        return list(m3u8_urls), list(subtitle_urls)


# --- PART 2: SEND TO NOTION ---
def send_to_notion(source_url, streams, subs):
    create_url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    # Format lists into a single string
    stream_content = "\n".join(streams) if streams else "No streams found"
    sub_content = "\n".join(subs) if subs else "No subtitles found"

    # Truncate to 2000 chars to fit Notion limit
    stream_content = stream_content[:2000]
    sub_content = sub_content[:2000]

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": source_url}}
                ]
            },
            "Streams": {
                "rich_text": [
                    {"text": {"content": stream_content}}
                ]
            },
            "Subtitles": {
                "rich_text": [
                    {"text": {"content": sub_content}}
                ]
            },
            "Status": {
                "select": {
                    "name": "Success" if streams else "No Data"
                }
            }
        }
    }

    response = requests.post(create_url, headers=headers, json=payload)

    if response.status_code == 200:
        print("✅ Successfully saved to Notion!")
    else:
        print(f"❌ Error sending to Notion: {response.status_code}")
        print(response.text)


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    target_url = 'https://gimy.com.tw/video/50689-155.html#sid=2'

    print("--- 1. Scraping Data ---")
    video_streams, sub_files = capture_streams(target_url)

    print(f"--- 2. Sending {len(video_streams)} streams and {len(sub_files)} subtitles to Notion ---")
    send_to_notion(target_url, video_streams, sub_files)