from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Route(Base):
    __tablename__ = 'routes'

    id = Column(String, primary_key=True)
    source = Column(String, nullable=False, index=True)
    train_number = Column(String, nullable=False, index=True)
    departure_station = Column(String, nullable=False, index=True)
    arrival_station = Column(String, nullable=False, index=True)
    travel_date = Column(Date, nullable=False, index=True)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)

    prices = relationship("Price", back_populates="route", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Route(id='{self.id}', train='{self.train_number}', from='{self.departure_station}', to='{self.arrival_station}', date='{self.travel_date}')>"

class Price(Base):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(String, ForeignKey('routes.id'), nullable=False, index=True)
    price = Column(Float, nullable=True)
    currency = Column(String(3), nullable=True)
    is_couchette = Column(Boolean, nullable=False, default=False)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    route = relationship("Route", back_populates="prices")

    def __repr__(self):
        return f"<Price(route_id='{self.route_id}', price={self.price} {self.currency}, scraped_at='{self.scraped_at}')>"
