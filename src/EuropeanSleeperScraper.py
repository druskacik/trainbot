import logging
import time
from datetime import date, timedelta, datetime
import requests
from typing import List

logger = logging.getLogger(__name__)

from .RoutesScraper import RoutesScraper
from .models import Route, Price
from .ScrapeResult import ScrapeResult, ScrapeFailure

# Cap in-memory failures for long runs to avoid unbounded memory growth
MAX_FAILURES_STORED = 2000

STATIONS = {
    '8800104': {'name': 'Bruxelles Midi/Brussel Zuid', 'country': '88'},
    '8800210': {'name': 'Antwerpen Centraal', 'country': '88'},
    '8700015': {'name': 'Paris-Nord', 'country': '87'},
    '8400526': {'name': 'Roosendaal', 'country': '84'},
    '8400530': {'name': 'Rotterdam Centraal', 'country': '84'},
    '8400280': {'name': 'Den Haag HS', 'country': '84'},
    '8400058': {'name': 'Amsterdam Centraal', 'country': '84'},
    '8400055': {'name': 'Amersfoort Centraal', 'country': '84'},
    '8400173': {'name': 'Deventer', 'country': '84'},
    '8020401': {'name': 'Hamburg Harburg', 'country': '80'},
    '8010110': {'name': 'Berlin Ostbahnhof', 'country': '80'},
    '8010100': {'name': 'Berlin Hbf', 'country': '80'},
    '8001305': {'name': 'Dresden Hbf', 'country': '80'},
    '8001311': {'name': 'Bad Schandau', 'country': '80'},
    '5455659': {'name': 'Děčín hl.n.', 'country': '54'},
    '5453179': {'name': 'Ústí nad Labem hl.n.', 'country': '54'},
    '5457076': {'name': 'Praha hl.n. (main station)', 'country': '54'},
}

DOMESTIC_DISABLED = ['84', '88', '54', '87']

ROUTE_1_ID = '77ab1c5a-ea0b-4634-7cdd-08db0daabe3f'
ROUTE_1_STATIONS = ['8800104', '8800210', '8400526', '8400530', '8400280', '8400058', '8400055', '8400173', '8010100', '8010110', '8001305', '8001311', '5455659', '5453179', '5457076']

ROUTE_2_ID = 'c181e609-05b7-456a-bab6-4203dc2c3402'
ROUTE_2_STATIONS = ['8700015', '8800104', '8020401', '8010110', '8010100']

class EuropeanSleeperScraper(RoutesScraper):
    def __init__(self):
        super().__init__()
        self.api_url = 'https://europeansleeperprod-api.azurewebsites.net/api/search/availability'
        
        self.train_configs = [
            {
                'train_number': '453',
                'route_id': ROUTE_1_ID,
                'stations': ROUTE_1_STATIONS, # Bruxelles to Prague
                'active_from': None,
                'origin_days': [0, 2, 4], # Mon, Wed, Fri
                'midnight_index': 8       # Berlin Hbf and onwards are next day
            },
            {
                'train_number': '452',
                'route_id': ROUTE_1_ID,
                'stations': list(reversed(ROUTE_1_STATIONS)), # Prague to Bruxelles
                'active_from': None,
                'origin_days': [1, 3, 6], # Tue, Thu, Sun
                'midnight_index': 7       # Deventer and onwards are next day
            },
            {
                'train_number': '475',
                'route_id': ROUTE_2_ID,
                'stations': ROUTE_2_STATIONS, # Paris to Berlin
                'active_from': date(2026, 3, 26),
                'origin_days': [1, 3, 6], # Tue, Thu, Sun
                'midnight_index': 2       # Hamburg and onwards are next day
            },
            {
                'train_number': '474',
                'route_id': ROUTE_2_ID,
                'stations': list(reversed(ROUTE_2_STATIONS)), # Berlin to Paris
                'active_from': date(2026, 3, 26),
                'origin_days': [0, 2, 4], # Mon, Wed, Fri
                'midnight_index': 3       # Brussels and onwards are next day
            }
        ]

    def _search_availability(self, date_str: str, train_number: str, route_id: str, from_id: str, to_id: str) -> dict:
        body = {
            "trainRouteId": route_id,
            "fromLocationId": from_id,
            "toLocationId": to_id,
            "passengerTypes": [72], # 72 = Adult
            "trainNumber": train_number,
            "travelDate": date_str,
            "bicycleCount": 0
        }
        
        response = requests.post(self.api_url, json=body)
        response.raise_for_status()
        return response.json()

    def scrape(self) -> ScrapeResult:
        failures: List[ScrapeFailure] = []
        total_failures = 0
        total_requests = 0
        start_date = date.today()
        
        # 3 months = 90 days
        for i in range(90):
            current_date_obj = start_date + timedelta(days=i)
            current_date_str = current_date_obj.strftime('%Y-%m-%d')
            
            for config in self.train_configs:
                if config['active_from'] and current_date_obj < config['active_from']:
                    continue
                    
                stations = config['stations']
                for i_st in range(len(stations)):
                    # Compute if current_date_obj is a valid travel date for this station
                    is_next_day = i_st >= config['midnight_index']
                    valid_origin_days = config['origin_days']
                    valid_days = [(d + 1) % 7 if is_next_day else d for d in valid_origin_days]
                    
                    if current_date_obj.weekday() not in valid_days:
                        continue
                        
                    for j_st in range(i_st + 1, len(stations)):
                        from_id = stations[i_st]
                        to_id = stations[j_st]
                        
                        from_c = STATIONS[from_id]['country']
                        to_c = STATIONS[to_id]['country']
                        
                        if from_c == to_c and from_c in DOMESTIC_DISABLED:
                            continue
                            
                        train_number = config['train_number']
                        route_id = config['route_id']
                        from_name = STATIONS[from_id]['name']
                        to_name = STATIONS[to_id]['name']
                        
                        total_requests += 1
                        logger.info(f"Scraping train {train_number} for {current_date_str}: {from_name} to {to_name}")
                        
                        try:
                            result = self._search_availability(current_date_str, train_number, route_id, from_id, to_id)
                        except requests.exceptions.HTTPError as e:
                            if e.response is not None and e.response.status_code == 400:
                                logger.warning(f"Skipping {current_date_str} for train {train_number} ({from_name}->{to_name}) due to 400 Bad Request.")
                            else:
                                error_msg = str(e)
                                logger.warning(f"Failed to fetch {current_date_str} for train {train_number} ({from_name}->{to_name}): {error_msg}")
                                total_failures += 1
                                if len(failures) < MAX_FAILURES_STORED:
                                    failures.append(ScrapeFailure(current_date_str, train_number, error_msg))
                            continue
                        except Exception as e:
                            error_msg = str(e)
                            logger.warning(f"Failed to fetch {current_date_str} for train {train_number} ({from_name}->{to_name}): {error_msg}")
                            total_failures += 1
                            if len(failures) < MAX_FAILURES_STORED:
                                failures.append(ScrapeFailure(current_date_str, train_number, error_msg))
                            continue
                        finally:
                            # Wait 1 second to avoid rate limiting
                            time.sleep(1)

                        if not result or 'availabilityResult' not in result or not result['availabilityResult']:
                            continue
                            
                        availability = result['availabilityResult'].get('availability')
                        if not availability or availability.get('departureStationName') == 'Not available':
                            continue
                        
                        # Use departure and arrival station names from the response API if available, else fallback
                        departure_station = availability.get('departureStationName', from_name)
                        arrival_station = availability.get('arrivalStationName', to_name)
                        source = 'europeansleeper'
                        
                        try:
                            dep_time = datetime.fromisoformat(availability['departureTime'])
                            arr_time = datetime.fromisoformat(availability['arrivalTime'])
                        except (KeyError, ValueError):
                            logger.warning(f"Could not parse dates for {current_date_str}. Skipping.")
                            continue
                        
                        min_price = None
                        min_couchette_price = None
                        currency = 'eur' # Default
                        
                        if 'priceClasses' in availability and availability['priceClasses']:
                            all_prices = []
                            couchette_prices = []
                            for pc in availability['priceClasses']:
                                if pc.get('prices') and pc['prices'].get('eur') is not None:
                                    p = pc['prices']['eur']
                                    all_prices.append(p)
                                    if pc.get('placeTypeKey') != 'seat-second-class':
                                        couchette_prices.append(p)
                            
                            if all_prices:
                                min_price = min(all_prices)
                            if couchette_prices:
                                min_couchette_price = min(couchette_prices)
                        
                        route_db_id = f"{source}|{train_number}|{departure_station}|{arrival_station}|{dep_time.isoformat()}"
                        
                        route_obj = Route(
                            id=route_db_id,
                            source=source,
                            train_number=train_number,
                            departure_station=departure_station,
                            arrival_station=arrival_station,
                            travel_date=current_date_obj,
                            departure_time=dep_time,
                            arrival_time=arr_time
                        )
                        
                        price_objs = []
                        if min_price is not None:
                            price_objs.append(Price(
                                route_id=route_db_id,
                                price=min_price,
                                currency=currency,
                                is_couchette=False
                            ))
                        if min_couchette_price is not None:
                            price_objs.append(Price(
                                route_id=route_db_id,
                                price=min_couchette_price,
                                currency=currency,
                                is_couchette=True
                            ))

                        availability = [
                            (False, min_price, currency),
                            (True, min_couchette_price, currency),
                        ]
                        self.save_route_in_batch(route_obj, price_objs, availability)
                
        self.flush_routes()
        return ScrapeResult(
            routes_scraped=self._total_saved,
            failures=failures,
            total_requests=total_requests,
            total_failures=total_failures,
            scraper_name="European Sleeper",
        )
