import logging

logging.basicConfig(level=logging.INFO)

from prefect import flow, serve, task
import apprise
import os
import sys
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# Add project root to path so we can import src
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.scrapers.european_sleeper import EuropeanSleeperScraper
from src.scrapers.intercity_pl import IntercityPlScraper
from src.scrapers.nightjet import NightjetScraper
from src.scrapers.regiojet import RegioJetScraper
from src.ScrapeResult import combined_failure_summary, _cap_for_telegram


SCRAPE_TASK_TIMEOUT_SECONDS = 24 * 3600


def _make_scrape_task(scraper_cls, name):
    """Create a Prefect task for a scraper. No task-level retries: these runs take
    hours and partial progress is already saved in batches; a failure near the end
    should not re-run the entire scrape. Hard timeout above the flow's soft
    deadline acts as a backstop against wedged tasks lingering forever."""
    @task(name=name, timeout_seconds=SCRAPE_TASK_TIMEOUT_SECONDS)
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


# Soft deadline for the daily flow. We enforce this ourselves (instead of using
# Prefect's `timeout_seconds`) so a Telegram notification is guaranteed to go
# out even when scrapers exceed it. Sits under the 24h schedule with margin.
DAILY_FLOW_DEADLINE_SECONDS = 23 * 3600


@flow(name="Daily Train Scraper")
def daily_scraper_flow():
    """Flow to run all scrapers (European Sleeper + Nightjet + RegioJet + Intercity.pl)
    with a shared soft deadline. Scrapers that exceed the deadline are reported as
    timed out; the flow still sends a Telegram notification and returns so the
    deployment's concurrency slot frees up for the next scheduled run."""
    apobj = apprise.Apprise()
    telegram_url = os.getenv('APPRISE_TELEGRAM_URL')
    if telegram_url:
        apobj.add(telegram_url)

    deadline = time.monotonic() + DAILY_FLOW_DEADLINE_SECONDS

    futures = [
        ("European Sleeper", scrape_european_sleeper.submit()),
        ("Nightjet", scrape_nightjet.submit()),
        ("RegioJet", scrape_regiojet.submit()),
        ("Intercity.pl", scrape_intercity_pl.submit()),
    ]

    results = []
    errors = []
    timed_out = []
    for name, future in futures:
        remaining = max(0.0, deadline - time.monotonic())
        try:
            results.append(future.result(timeout=remaining))
        except TimeoutError:
            logger.error(f"{name} scraper exceeded {DAILY_FLOW_DEADLINE_SECONDS}s deadline")
            timed_out.append(name)
        except Exception as e:
            logger.error(f"{name} scraper failed: {e}")
            errors.append(f"{name}: {e}")

    if not results and (errors or timed_out):
        body = "All scrapers failed or timed out!"
        if errors:
            body += "\n\nCrashed scrapers:\n" + "\n".join(f"  • {e}" for e in errors)
        if timed_out:
            body += "\n\nTimed out:\n" + "\n".join(f"  • {n}" for n in timed_out)
        if telegram_url:
            apobj.notify(body=_cap_for_telegram(body), title="🚨 Scraper Alert")
        raise RuntimeError(body)

    if telegram_url:
        has_failures = any(r._failure_count > 0 for r in results) or errors or timed_out
        body = combined_failure_summary(results)
        if errors:
            body += "\n\nCrashed scrapers:\n" + "\n".join(f"  • {e}" for e in errors)
        if timed_out:
            body += "\n\nTimed out (exceeded 23h):\n" + "\n".join(f"  • {n}" for n in timed_out)
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
            # Prevent stacking: if yesterday's run is still active when today's
            # would start, the new run waits rather than running in parallel.
            concurrency_limit=1,
        ),
        european_sleeper_flow.to_deployment(name="european-sleeper"),
        nightjet_flow.to_deployment(name="nightjet"),
        regiojet_flow.to_deployment(name="regiojet"),
        intercity_pl_flow.to_deployment(name="intercity-pl"),
    )
