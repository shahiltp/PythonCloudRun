import requests
import time
import platform
import subprocess
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

# === TELEGRAM CONFIG ===
BOT_TOKEN = '8352820438:AAGCkgwc6t51rYlMZ5fiUeFHaJg9HqCEuwc'
CHAT_ID = '727059746'

# === TRACK SEEN LISTINGS ===
seen_links = set()
print("✅ Tracking seen links...")

# === DETECT CHROME VERSION ===
def get_chrome_major_version():
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                [r"reg", "query", r"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon", "/v", "version"],
                capture_output=True, text=True
            )
            version_line = result.stdout.strip().split('\n')[-1]
            version = version_line.split()[-1]
        else:
            result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
            version = result.stdout.strip().split()[-1]

        print(f"📦 Chrome version detected: {version}")
        return int(version.split('.')[0])
    except Exception as e:
        print(f"⚠️ Could not detect Chrome version: {e}")
        return None

# === SCRAPE HARAAJ LISTINGS ===
def get_nissan_patrol_listings():
    print("📡 Launching headless browser...")
    major_version = get_chrome_major_version()

    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = uc.Chrome(version_main=major_version, options=options)

    url = "https://haraj.com.sa/en/search/Nissan%20Patrol"
    driver.get(url)

    time.sleep(5)  # Allow JS to load

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

# === TELEGRAM MESSAGE SENDER ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"⚠️ Telegram error: {response.text}")

# === CHECK + NOTIFY FUNCTION ===
def check_and_notify():
    listings = get_nissan_patrol_listings()
    print(f"🧾 Found {len(listings)} listings.")

    if len(listings) == 0:
        send_telegram_message("🔍 No new Nissan Patrol listings found.")

    for title, link in listings:
        if link not in seen_links:
            message = f"🚗 New Nissan Patrol listed:\n{title}\n{link}"
            send_telegram_message(message)
            seen_links.add(link)
    print(f"✅ Total seen links: {len(seen_links)}")

# === MAIN LOOP ===
if __name__ == "__main__":
    while True:
        try:
            check_and_notify()
        except Exception as e:
            print(f"❌ Error: {e}")
        print("⏳ Waiting for next check...")
        time.sleep(900)  # Wait 15 minutes
