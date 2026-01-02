from playwright.sync_api import sync_playwright

def capture_streams(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        m3u8_urls = []
        subtitle_urls = []

        def handle_route(route):
            u = route.request.url
            lower = u.lower()
            if '.m3u8' in lower and 'master.m3u8' in lower:
                print(f"[VIDEO] {u}")
                m3u8_urls.append(u)
            elif any(ext in lower for ext in ['.vtt', '.srt']) and 'thumb' not in lower:
                print(f"[SUB]   {u}")
                subtitle_urls.append(u)
            route.continue_()

        page.route("**/*", handle_route)
        page.goto(url)
        print("Play the video in the browser, wait ~15s…")
        page.wait_for_timeout(15000)
        browser.close()
        return m3u8_urls, subtitle_urls

if __name__ == "__main__":
    url = "https://www.southparkstudios.com/episodes/er4a32/south-park-weight-gain-4000-season-1-ep-2"
    streams, subs = capture_streams(url)

    print("\n=== COPY THESE INTO VLC ===")
    if streams:
        print("Video m3u8:")
        print(streams[0])
    else:
        print("No m3u8 found.")

    if subs:
        print("\nSubtitle URL(s):")
        for s in subs:
            print(s)
    else:
        print("\nNo proper subtitle URLs found (only thumbs or none).")
