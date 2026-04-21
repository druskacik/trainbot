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
from src.IntercityPlScraper import IntercityPlScraper
from src.NightjetScraper import NightjetScraper
from src.RegioJetScraper import RegioJetScraper
from src.ScrapeResult import combined_failure_summary, _cap_for_telegram


def _make_scrape_task(scraper_cls, name):
    """Create a Prefect task for a scraper. No task-level retries: these runs take
    hours and partial progress is already saved in batches; a failure near the end
    should not re-run the entire scrape."""
    @task(name=name)
    def _task():
        logger.info(f"Starting {name} task...")
        result = scraper_cls().scrape()
        if result.routes_scraped > 0:
            logger.info(f"Successfully scraped and saved {result.routes_scraped} routes.")
        else:
            logger.info("No routes were found.")
        return result
    return _task


scrape_european_sleeper = _make_scrape_task(EuropeanSleeperScraper, "European Sleeper")
scrape_nightjet = _make_scrape_task(NightjetScraper, "Nightjet")
scrape_regiojet = _make_scrape_task(RegioJetScraper, "RegioJet")
scrape_intercity_pl = _make_scrape_task(IntercityPlScraper, "Intercity.pl")


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
        raise

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


def _make_flow(scrape_task, name):
    @flow(name=name)
    def _flow():
        _run_flow_with_notifications(scrape_task, name)
    _flow.__name__ = name.lower().replace(' ', '_') + '_flow'
    return _flow


european_sleeper_flow = _make_flow(scrape_european_sleeper, "European Sleeper Scraper")
nightjet_flow = _make_flow(scrape_nightjet, "Nightjet Scraper")
regiojet_flow = _make_flow(scrape_regiojet, "RegioJet Scraper")
intercity_pl_flow = _make_flow(scrape_intercity_pl, "Intercity.pl Scraper")


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
    ic_future = scrape_intercity_pl.submit()

    results = []
    errors = []
    for name, future in [
        ("European Sleeper", es_future),
        ("Nightjet", nj_future),
        ("RegioJet", rj_future),
        ("Intercity.pl", ic_future),
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
        body = _cap_for_telegram(body)
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
        intercity_pl_flow.to_deployment(name="intercity-pl"),
    )
