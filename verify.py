import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Route, Price

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "train46")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = SessionLocal()
print(f"Total routes in DB: {session.query(Route).count()}")
print(f"Total prices in DB: {session.query(Price).count()}")

first_route = session.query(Route).first()
if first_route:
    print(f"Sample Route Data: {first_route}")
    prices = session.query(Price).filter(Price.route_id == first_route.id).all()
    print(f"Prices for this Route: {prices}")
session.close()
