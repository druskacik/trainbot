import os
from abc import ABC, abstractmethod
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from .models import Route

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

    @abstractmethod
    def scrape(self):
        """Implement the scraping logic here. Must return a list of tuples: (Route, Price)."""
        pass

    def save_routes(self, routes_and_prices: list):
        """Save the list of routes and prices to the database."""
        if not routes_and_prices:
            print("No routes to save.")
            return

        session = self.SessionLocal()
        try:
            route_count = 0
            price_count = 0
            for route_obj, prices in routes_and_prices:
                session.merge(route_obj)
                route_count += 1
                if getattr(prices, '__iter__', False) and not isinstance(prices, (str, dict)):
                    for price_obj in prices:
                        if price_obj is not None:
                            session.add(price_obj)
                            price_count += 1
                elif prices is not None:
                    session.add(prices)
                    price_count += 1
            session.commit()
            print(f"Successfully saved {route_count} routes and {price_count} prices.")
        except Exception as e:
            session.rollback()
            print(f"Error saving routes: {e}")
            raise
        finally:
            session.close()