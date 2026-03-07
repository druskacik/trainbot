# Train46 - Train Route Scraper & Price Tracker

A robust train route scraping and price tracking application designed to help you find the cheapest train trips (including sleepers/couchettes) between European cities.

## 🚀 Quick Start

### Running Locally (with `uv`)
Ensure you have a PostgreSQL database running and configured in your `.env` file.
```bash
# Install dependencies
uv sync

# Run migrations
uv run python manage.py migrate

# Start the dev server
uv run python manage.py runserver
```

## 🛠 Tech Stack
- **Backend:** [Django](https://www.djangoproject.com/) 6.0
- **Orchestration:** [Prefect](https://www.prefect.io/) 3.6
- **Database:** [PostgreSQL](https://www.postgresql.org/) with [Alembic](https://alembic.sqlalchemy.org/) & [SQLAlchemy](https://www.sqlalchemy.org/)
- **Package Manager:** [uv](https://github.com/astral-sh/uv)
- **Containerization:** [Docker](https://www.docker.com/) & Docker Compose
- **Scraping:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/), [Requests](https://requests.readthedocs.io/)
- **Data Handling:** [Pandas](https://pandas.pydata.org/)
- **Notifications:** [Apprise](https://github.com/caronc/apprise)

## 📦 Project Structure
- `ui/`: Django application responsible for the web interface.
- `web/`: Django project configuration and settings.
- `src/`: Core logic, including scrapers and Prefect flows.
- `alembic/`: Database migrations.
- `Dockerfile` & `docker-compose.yml`: Containerization setup.

## 🚢 Useful Commands
- **Create Superuser:** `uv run python manage.py createsuperuser`
- **Run Scraper Manually:** `uv run python src/flows.py`
- **Interactive Notebooks:** Check `100_scrape_europeansleeper.ipynb` for scraping experiments.
