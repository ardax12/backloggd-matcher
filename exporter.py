import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

COOKIE_FILE = "cookies.json"

def load_cookies():
    with open(COOKIE_FILE, "r") as f:
        return json.load(f)

def init_driver_with_cookies():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-features=Translate,BackForwardCache,WebRtcHideLocalIpsWithMdns")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-sync")
    options.add_argument("--metrics-recording-only")
    options.add_argument("--disable-default-apps")
    options.add_argument("--mute-audio")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--ignore-certificate-errors")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://backloggd.com")

    for cookie in load_cookies():
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print("Cookie add failed:", e)

    return driver

def fetch_profile_page(driver, profile_url, page):
    try:
        paginated_url = f"{profile_url}?page={page}"
        driver.get(paginated_url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        game_entries = soup.select(".rating-hover")
        return game_entries
    except Exception as e:
        print(f"Error on page {page}: {e}")
        return []

def extract_game_data(game_entries):
    game_data = []
    for game_entry in game_entries:
        # Extract game title
        title_element = game_entry.select_one(".game-text-centered")
        title = title_element.get_text(strip=True) if title_element else "Unknown Title"

        # Extract game rating - Method 1: stars-top
        stars_top_element = game_entry.select_one(".stars-top")
        rating = 0.0  # Default rating if nothing is found

        if stars_top_element:
            style = stars_top_element.get("style", "")
            width = (
                style.split("width:")[1].split("%")[0].strip()
                if "width:" in style
                else "0"
            )
            try:
                rating = float(width) / 20  # Convert percentage width to 5-star scale
            except ValueError:
                rating = 0.0

        # Method 2: data-rating (only if stars-top is missing)
        if rating == 0.0:
            game_cover_element = game_entry.find(attrs={"data-rating": True})
            if game_cover_element:
                data_rating = game_cover_element.get("data-rating")
                try:
                    rating = float(data_rating) / 2  # Convert 10-point scale to 5-star
                except (ValueError, TypeError):
                    rating = 0.0

        game_data.append((title, rating)) 
    return game_data


def fetch_all_game_data(profile_url):
    driver = init_driver_with_cookies()
    all_game_data = []
    seen_hashes = set()
    page = 1

    try:
        while True:
            print(f"Fetching page {page}...")
            game_entries = fetch_profile_page(driver, profile_url, page)

            if not game_entries:
                print("No entries found. Ending.")
                break

            # Hash the raw HTML of game entries to detect duplicates
            html_chunk = "".join(str(e) for e in game_entries)
            current_hash = hash(html_chunk)
            if current_hash in seen_hashes:
                print("Duplicate page detected. Ending.")
                break
            seen_hashes.add(current_hash)

            game_data = extract_game_data(game_entries)
            if not game_data:
                print("No new data. Ending.")
                break

            all_game_data.extend(game_data)
            page += 1
    finally:
        driver.quit()

    return all_game_data

def save_to_csv(username, game_data):
    filename = f"{username}_games.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Rating"])
        writer.writerows(game_data)
    print(f"Data saved to {filename}")


def fetch_all_game_data_with_driver(profile_url, driver):

    all_game_data = []
    seen_hashes = set()
    page = 1

    while True:
        print(f"Fetching page {page}...")
        game_entries = fetch_profile_page(driver, profile_url, page)

        if not game_entries:
            print("No entries found. Ending.")
            break

        # Hash the raw HTML of game entries to detect duplicates
        html_chunk = "".join(str(e) for e in game_entries)
        current_hash = hash(html_chunk)
        if current_hash in seen_hashes:
            print("Duplicate page detected. Ending.")
            break
        seen_hashes.add(current_hash)

        game_data = extract_game_data(game_entries)
        if not game_data:
            print("No new data. Ending.")
            break

        all_game_data.extend(game_data)
        page += 1

    return all_game_data

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Backloggd scraper with headless Selenium")
    parser.add_argument("profile_url_or_username", type=str)
    args = parser.parse_args()

    if args.profile_url_or_username.startswith("http"):
        profile_url = args.profile_url_or_username
        username = profile_url.split("/u/")[1].split("/")[0]
    else:
        username = args.profile_url_or_username
        profile_url = f"https://backloggd.com/u/{username}/games/"

    print(f"Scraping for: {username}")
    game_data = fetch_all_game_data(profile_url)
    save_to_csv(username, game_data)
