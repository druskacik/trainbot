from prefect import flow, serve, task
import apprise
import os
import sys
from pathlib import Path

# Add project root to path so we can import src
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.EuropeanSleeperScraper import EuropeanSleeperScraper
from src.NightjetScraper import NightjetScraper
from src.ScrapeResult import ScrapeResult


@task()
def scrape_european_sleeper():
    """Task to run the EuropeanSleeperScraper. No task-level retries: these runs take
    hours and partial progress is already saved in batches; a failure near the end
    should not re-run the entire scrape."""
    print("Starting European Sleeper Scraper task...")
    scraper = EuropeanSleeperScraper()
    result = scraper.scrape()
    if result.routes_scraped > 0:
        print(f"Successfully scraped and saved {result.routes_scraped} routes.")
    else:
        print("No routes were found.")
    return result


@task()
def scrape_nightjet():
    """Task to run the NightjetScraper. No task-level retries: these runs take hours
    and partial progress is already saved in batches; a failure near the end should
    not re-run the entire scrape."""
    print("Starting Nightjet Scraper task...")
    scraper = NightjetScraper()
    result = scraper.scrape()
    if result.routes_scraped > 0:
        print(f"Successfully scraped and saved {result.routes_scraped} routes.")
    else:
        print("No routes were found.")
    return result


def _merge_results(a: ScrapeResult, b: ScrapeResult) -> ScrapeResult:
    """Merge two ScrapeResults for combined reporting."""
    return ScrapeResult(
        routes_scraped=a.routes_scraped + b.routes_scraped,
        failures=a.failures + b.failures,
        total_requests=a.total_requests + b.total_requests,
    )


def _run_flow_with_notifications(scrape_task, flow_name: str):
    """Run a scrape task and send Telegram notifications on success/failure."""
    apobj = apprise.Apprise()
    telegram_url = os.getenv('APPRISE_TELEGRAM_URL')
    if telegram_url:
        apobj.add(telegram_url)

    try:
        result = scrape_task()
    except Exception as e:
        print(f"Flow failed with error: {str(e)}")
        if telegram_url:
            apobj.notify(
                body=f"{flow_name} failed!\nError: {str(e)}",
                title="🚨 Scraper Alert"
            )
        raise e

    if telegram_url and result is not None:
        if result.failures:
            apobj.notify(
                body=result.failure_summary(),
                title="⚠️ Scraper Warning"
            )
        else:
            apobj.notify(
                body=result.failure_summary(),
                title="✅ Scraper Success"
            )


@flow(name="European Sleeper Scraper")
def european_sleeper_flow():
    """Flow to run the European Sleeper scraper with notifications."""
    _run_flow_with_notifications(scrape_european_sleeper, "European Sleeper Scraper")


@flow(name="Nightjet Scraper")
def nightjet_flow():
    """Flow to run the Nightjet scraper with notifications."""
    _run_flow_with_notifications(scrape_nightjet, "Nightjet Scraper")


@flow(name="Daily Train Scraper")
def daily_scraper_flow():
    """Flow to run both scrapers (European Sleeper + Nightjet) with notifications."""
    apobj = apprise.Apprise()
    telegram_url = os.getenv('APPRISE_TELEGRAM_URL')
    if telegram_url:
        apobj.add(telegram_url)

    try:
        es_result = scrape_european_sleeper()
        nj_result = scrape_nightjet()
        result = _merge_results(es_result, nj_result)
    except Exception as e:
        print(f"Flow failed with error: {str(e)}")
        if telegram_url:
            apobj.notify(
                body=f"The train scraper failed!\nError: {str(e)}",
                title="🚨 Scraper Alert"
            )
        raise e

    if telegram_url and result is not None:
        if result.failures:
            apobj.notify(
                body=result.failure_summary(),
                title="⚠️ Scraper Warning"
            )
        else:
            apobj.notify(
                body=result.failure_summary(),
                title="✅ Scraper Success"
            )


if __name__ == "__main__":
    # Serve all three flows so each can be run from the Prefect dashboard.
    # Only the daily flow has a schedule; the other two are run on demand.
    serve(
        daily_scraper_flow.to_deployment(
            name="daily-train-scrape",
            cron="0 2 * * *",  # Run at 2:00 AM every day
        ),
        european_sleeper_flow.to_deployment(name="european-sleeper"),
        nightjet_flow.to_deployment(name="nightjet"),
    )
