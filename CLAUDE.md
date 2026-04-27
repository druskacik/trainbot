## Project Overview

TrainBot is a train fare aggregator for European sleeper/couchette trains. It scrapes pricing from multiple train providers' APIs, stores results in PostgreSQL, and serves a search UI via Django.

## Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run python manage.py runserver

# Run scrapers manually
uv run python -c "from src.flows import scrape_european_sleeper; scrape_european_sleeper()"
uv run python -c "from src.flows import scrape_nightjet; scrape_nightjet()"
uv run python -c "from src.flows import daily_scraper_flow; daily_scraper_flow()"

# Query the database (read-only)
uv run agent_utils/search_db.py --query "SELECT ..." --format csv

# Rebuild CITY_CONNECTIONS from routes table
uv run agent_utils/build_city_connections.py
```

## Architecture

**Data flow:** Scrapers → PostgreSQL → Django API → JS frontend → External booking URLs

### Scraping Layer (`src/`)
- `RoutesScraper.py` — Abstract base; manages SQLAlchemy sessions and batch saves (50 routes/flush)
- `scrapers/european_sleeper/scraper.py` — Scrapes 4 hardcoded train configs; station IDs are provider-specific integers
- `scrapers/nightjet/scraper.py` — Discovers stations dynamically via API; separate seat/couchette pricing
- `flows.py` — Prefect orchestration; daily cron at 2 AM; Telegram notifications via Apprise
- `models.py` — SQLAlchemy ORM: `Route`, `Price` (historical), `CurrentAvailability` (latest per route+seat type)

### Web Layer (`ui/`, `web/`)
- `ui/models.py` — Django ORM mirrors `src/models.py`; all models have `managed = False` (Alembic owns schema)
- `ui/views.py` — Five endpoints: `index`, `about`, `get_stations`, `search_trips`, `_get_routes_with_best_price`
- `ui/cities.py` — `CITY_CATALOG` (30+ cities with station aliases and provider IDs) and `CITY_CONNECTIONS` (adjacency dict); `build_booking_url()` constructs deep links to europeansleeper.eu and oebbtickets.at
- Frontend is a Django-served SPA: `index.html` + `script.js` do AJAX to `/search_trips`, inject results dynamically

### Key Design Decisions
- **Two ORM layers coexist:** SQLAlchemy (`src/`) for scraping writes; Django ORM (`ui/`) for read queries. They share the same tables.
- **`CurrentAvailability` table** holds the latest price per `(route_id, is_couchette)` — queries use this for speed rather than scanning all `Price` history.
- **Round-trip search** pairs outbound routes with the best-priced return leg within `max_duration` days; European Sleeper round-trips get a combined booking URL.
- **`CITY_CONNECTIONS`** in `cities.py` is a manually maintained dict (regenerate with `build_city_connections.py` after schema changes).

## Design Principles (from .impeccable.md)

This project has explicit design guidance — follow it when touching CSS or templates:

- **Tone:** Calm, precise, grounded. Ecology + technology. No hype, no greenwashing.
- **CSS approach:** Token-first (CSS variables); one accent color; clear hierarchy.
- **Accessibility defaults:** `focus-visible` on all interactive elements; 44px touch targets; ARIA attributes; no `alert()` dialogs.
- **What to avoid:** Glassmorphism (`backdrop-filter`), gradient text on headings, cyan/indigo palette (reads as "AI-generated"), generic SaaS dashboard aesthetics, sustainability clichés.

Full design context (brand, aesthetic, principles) is in `.impeccable.md`. Consult it before making UI changes.

## Environment

Configure via `.env` file. Key variables: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`.

## Guidelines

- never run the DEV server (uv run python manage.py runserver) to check UI changes, I'll run it manually and check by myself
