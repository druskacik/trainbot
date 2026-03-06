from prefect import flow, task
import apprise
import os
import sys
from pathlib import Path

# Add project root to path so we can import src
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.EuropeanSleeperScraper import EuropeanSleeperScraper

@task(retries=3, retry_delay_seconds=60)
def scrape_train_data():
    """Task to run the EuropeanSleeperScraper."""
    print("Starting European Sleeper Scraper task...")
    scraper = EuropeanSleeperScraper()
    routes = scraper.scrape()
    if routes:
        scraper.save_routes(routes)
        print(f"Successfully scraped and saved {len(routes)} routes.")
    else:
        print("No routes were found.")
    return routes

@flow(name="Daily Train Scraper")
def daily_scraper_flow():
    """Flow to orchestrate the daily train scraping with notifications."""
    apobj = apprise.Apprise()
    # E.g., tgram://bot_token/chat_id configurable via .env
    telegram_url = os.getenv('APPRISE_TELEGRAM_URL')
    if telegram_url:
        apobj.add(telegram_url)
        
    try:
        scrape_train_data()
    except Exception as e:
        print(f"Flow failed with error: {str(e)}")
        if telegram_url:
            apobj.notify(
                body=f"The European Sleeper scraper failed! Error: {str(e)}",
                title="🚨 Scraper Alert"
            )
        raise e

if __name__ == "__main__":
    # Use serve() to keep the process alive and run on a schedule
    daily_scraper_flow.serve(
        name="daily-train-scrape",
        cron="0 3 * * *", # Run at 3:00 AM every day
    )
