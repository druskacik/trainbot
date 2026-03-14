import os
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from .models import Route, CurrentAvailability

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "train46")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

class RoutesScraper(ABC):
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._route_buffer = []
        self._batch_size = 50
        self._total_saved = 0

    @abstractmethod
    def scrape(self):
        """Implement the scraping logic here. Must return a ScrapeResult."""
        pass

    def save_route_in_batch(self, route_obj, prices, availability: List[Tuple[bool, Optional[float], Optional[str]]]):
        """Add a route to the current batch, flushing to the database if the batch is full.
        availability: list of (is_couchette, price, currency) for seat and couchette; use None for price when sold out.
        """
        self._route_buffer.append((route_obj, prices, availability))
        if len(self._route_buffer) >= self._batch_size:
            self.flush_routes()

    def flush_routes(self):
        """Save any routes currently in the buffer to the database."""
        if not self._route_buffer:
            return
            
        self.save_routes(self._route_buffer)
        self._total_saved += len(self._route_buffer)
        self._route_buffer = []

    def save_routes(self, routes_prices_availability: list):
        """Save the list of routes, prices, and availability to the database.
        Each item is (route_obj, prices, availability) where availability is list of (is_couchette, price, currency).
        """
        if not routes_prices_availability:
            print("No routes to save.")
            return

        session = self.SessionLocal()
        now = datetime.utcnow()
        try:
            route_count = 0
            price_count = 0
            availability_count = 0
            seen_route_ids = set()

            for route_obj, prices, availability in routes_prices_availability:
                if route_obj.id not in seen_route_ids:
                    session.merge(route_obj)
                    seen_route_ids.add(route_obj.id)
                    route_count += 1

                if getattr(prices, '__iter__', False) and not isinstance(prices, (str, dict)):
                    for price_obj in prices:
                        if price_obj is not None:
                            session.merge(price_obj)
                            price_count += 1
                elif prices is not None:
                    session.merge(prices)
                    price_count += 1

                for is_couchette, price, currency in availability:
                    existing = session.query(CurrentAvailability).filter_by(
                        route_id=route_obj.id,
                        is_couchette=is_couchette
                    ).first()
                    if existing:
                        existing.price = price
                        existing.currency = currency
                        existing.last_scraped_at = now
                        if price is not None:
                            existing.last_seen_available_at = now
                        availability_count += 1
                    else:
                        session.add(CurrentAvailability(
                            route_id=route_obj.id,
                            is_couchette=is_couchette,
                            price=price,
                            currency=currency,
                            last_scraped_at=now,
                            last_seen_available_at=now if price is not None else None
                        ))
                        availability_count += 1

            session.commit()
            print(f"Successfully saved {route_count} routes, {price_count} prices, {availability_count} availability rows.")
        except Exception as e:
            session.rollback()
            print(f"Error saving routes: {e}")
            raise
        finally:
            session.close()