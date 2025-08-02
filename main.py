import requests
import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

# === TELEGRAM CONFIG ===
BOT_TOKEN = '8352820438:AAGCkgwc6t51rYlMZ5fiUeFHaJg9HqCEuwc'
CHAT_ID = '727059746'

import subprocess

def print_chrome_version():
    try:
        result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
        print("📦 Chrome version in Railway:", result.stdout.strip())
    except Exception as e:
        print("⚠️ Could not detect Chrome version:", e)

print_chrome_version()


# === TRACK SEEN LISTINGS ===
seen_links = set()
print("Tracking seen links...")
# === FUNCTION TO SCRAPE HARAAJ FOR NISSAN PATROL ===
def get_nissan_patrol_listings():
    print("📡 Launching headless browser...")

    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    #driver = uc.Chrome(options=options)
    driver = uc.Chrome(
    version_main=137,  # 👈 Force version 137
    options=options
    )

    url = "https://haraj.com.sa/en/search/Nissan%20Patrol"
    driver.get(url)

    time.sleep(5)  # Let JS load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    listings = []

    for a in soup.select("a[data-testid='post-title-link']"):
        title_element = a.find("span")
        if not title_element:
            continue
        title = title_element.get_text(strip=True)
        link = "https://haraj.com.sa" + a['href']
        if "nissan patrol" in title.lower():
            listings.append((title, link))

    print(f"✅ Found {len(listings)} Nissan Patrol listings.")
    return listings

# === FUNCTION TO SEND TELEGRAM MESSAGE ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    }
    requests.post(url, data=data)

# === MAIN CHECK + NOTIFY LOOP ===
def check_and_notify():
    listings = get_nissan_patrol_listings()
    print(f"Found {len(listings)} listings.")
    if len(listings) == 0:
        message = "🔍 No new Nissan Patrol listings found."
        print(len(seen_links))
        send_telegram_message(message)

    for title, link in listings:
        if link not in seen_links:
            message = f"🚗 New Nissan Patrol listed:\n{title}\n{link}"
            send_telegram_message(message)
            seen_links.add(link)
    print(f"Total seen links: {len(seen_links)}")

# === LOOP TO RUN EVERY 5 MINUTES ===
if __name__ == "__main__":
    while True:
        try:
            check_and_notify()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1000)  # Wait 5 minutes
