import logging

logging.basicConfig(level=logging.INFO)

from prefect import flow, serve, task
import apprise
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Add project root to path so we can import src
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.EuropeanSleeperScraper import EuropeanSleeperScraper
from src.NightjetScraper import NightjetScraper
from src.RegioJetScraper import RegioJetScraper
from src.ScrapeResult import ScrapeResult, combined_failure_summary


@task()
def scrape_european_sleeper():
    """Task to run the EuropeanSleeperScraper. No task-level retries: these runs take
    hours and partial progress is already saved in batches; a failure near the end
    should not re-run the entire scrape."""
    logger.info("Starting European Sleeper Scraper task...")
    scraper = EuropeanSleeperScraper()
    result = scraper.scrape()
    if result.routes_scraped > 0:
        logger.info(f"Successfully scraped and saved {result.routes_scraped} routes.")
    else:
        logger.info("No routes were found.")
    return result


@task()
def scrape_nightjet():
    """Task to run the NightjetScraper. No task-level retries: these runs take hours
    and partial progress is already saved in batches; a failure near the end should
    not re-run the entire scrape."""
    logger.info("Starting Nightjet Scraper task...")
    scraper = NightjetScraper()
    result = scraper.scrape()
    if result.routes_scraped > 0:
        logger.info(f"Successfully scraped and saved {result.routes_scraped} routes.")
    else:
        logger.info("No routes were found.")
    return result


@task()
def scrape_regiojet():
    """Task to run the RegioJetScraper. No task-level retries: these runs take hours
    and partial progress is already saved in batches; a failure near the end should
    not re-run the entire scrape."""
    logger.info("Starting RegioJet Scraper task...")
    scraper = RegioJetScraper()
    result = scraper.scrape()
    if result.routes_scraped > 0:
        logger.info(f"Successfully scraped and saved {result.routes_scraped} routes.")
    else:
        logger.info("No routes were found.")
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
        logger.error(f"Flow failed with error: {str(e)}")
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


@flow(name="RegioJet Scraper")
def regiojet_flow():
    """Flow to run the RegioJet scraper with notifications."""
    _run_flow_with_notifications(scrape_regiojet, "RegioJet Scraper")


@flow(name="Daily Train Scraper")
def daily_scraper_flow():
    """Flow to run all scrapers (European Sleeper + Nightjet + RegioJet) with notifications."""
    apobj = apprise.Apprise()
    telegram_url = os.getenv('APPRISE_TELEGRAM_URL')
    if telegram_url:
        apobj.add(telegram_url)

    # Submit all scrapers concurrently
    es_future = scrape_european_sleeper.submit()
    nj_future = scrape_nightjet.submit()
    rj_future = scrape_regiojet.submit()

    results = []
    errors = []
    for name, future in [
        ("European Sleeper", es_future),
        ("Nightjet", nj_future),
        ("RegioJet", rj_future),
    ]:
        try:
            results.append(future.result())
        except Exception as e:
            logger.error(f"{name} scraper failed: {e}")
            errors.append(f"{name}: {e}")

    if not results and errors:
        error_msg = "All scrapers failed!\n" + "\n".join(errors)
        if telegram_url:
            apobj.notify(body=error_msg, title="🚨 Scraper Alert")
        raise RuntimeError(error_msg)

    if telegram_url:
        has_failures = any(r._failure_count > 0 for r in results) or errors
        body = combined_failure_summary(results)
        if errors:
            body += "\n\nCrashed scrapers:\n" + "\n".join(f"  • {e}" for e in errors)
        if has_failures:
            apobj.notify(body=body, title="⚠️ Scraper Warning")
        else:
            apobj.notify(body=body, title="✅ Scraper Success")


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
        regiojet_flow.to_deployment(name="regiojet"),
    )
