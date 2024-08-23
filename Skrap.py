import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.robotparser import RobotFileParser
import logging

# Setup logging
logging.basicConfig(filename='scraper.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# User agents for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

def rate_limit(min_delay=1, max_delay=2):
    time.sleep(random.uniform(min_delay, max_delay))

def check_robots(url):
    rp = RobotFileParser()
    rp.set_url(f"{url}/robots.txt")
    try:
        rp.read()
        return rp
    except Exception as e:
        logging.error(f"Failed to read robots.txt from {url}: {e}")
        return None

def scrape_website(url, selector):
    try:
        # Check robots.txt
        rp = check_robots(url)
        if rp and not rp.can_fetch("*", url):
            logging.warning(f"Access to {url} not allowed by robots.txt")
            return []

        headers = {'User-Agent': random.choice(user_agents)}
        with requests.Session() as session:
            response = session.get(url, headers=headers)
            response.raise_for_status()
            rate_limit()  # Apply rate limiting
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.select(selector)
            return [item.text for item in content]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error scraping {url}: {e}")
        return []

def main():
    # Get user input for the website
    url = input("Enter the URL to scrape: ")

    # Ensure the URL has a protocol
    if not url.lower().startswith(('http://', 'https://')):
        url = 'https://' + url

    selector = input("Enter the CSS selector for the content you want to scrape: ")

    articles = scrape_website(url, selector)
    if articles:
        df = pd.DataFrame({'content': articles})
        print(df)
        # Optionally save to CSV
        df.to_csv('scraped_data.csv', index=False)
    else:
        print("No content was scraped or access was denied.")

if __name__ == "__main__":
    main()
