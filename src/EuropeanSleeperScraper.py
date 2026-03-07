import time
from datetime import date, timedelta, datetime
import requests
from typing import List

from .RoutesScraper import RoutesScraper
from .models import Route, Price

class EuropeanSleeperScraper(RoutesScraper):
    def __init__(self):
        super().__init__()
        self.api_url = 'https://europeansleeperprod-api.azurewebsites.net/api/search/availability'
        
        # Route mapping mapping from train number to (source_name, source_id, dest_name, dest_id)
        self.train_routes = {
            '452': ('europeansleeper', '5457076', '8400058', 'Prague', 'Amsterdam'),
            '453': ('europeansleeper', '8400058', '5457076', 'Amsterdam', 'Prague')
        }

    def _search_availability(self, date_str: str, train_number: str) -> dict:
        source_name, from_id, to_id, from_name, to_name = self.train_routes[train_number]
        
        body = {
            "trainRouteId": "77ab1c5a-ea0b-4634-7cdd-08db0daabe3f",
            "fromLocationId": from_id,
            "toLocationId": to_id,
            "passengerTypes": [72], # 72 = Adult
            "trainNumber": train_number,
            "travelDate": date_str,
            "bicycleCount": 0
        }
        
        try:
            response = requests.post(self.api_url, json=body)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                print(f"Skipping {date_str} for train {train_number} due to 400 Bad Request.")
                return {}
            print(f"Failed to fetch {date_str} for train {train_number}: {e}")
            return {}
        except Exception as e:
            print(f"Failed to fetch {date_str} for train {train_number}: {e}")
            return {}

    def scrape(self) -> List[Route]:
        results = []
        start_date = date.today()
        
        # 3 months = 90 days
        for i in range(90):
            current_date_obj = start_date + timedelta(days=i)
            current_date_str = current_date_obj.strftime('%Y-%m-%d')
            
            for train_number in ['452', '453']:
                print(f"Scraping train {train_number} for {current_date_str}")
                
                result = self._search_availability(current_date_str, train_number)
                # Wait 1 second to avoid rate limiting
                time.sleep(1)
                if not result or 'availabilityResult' not in result or not result['availabilityResult']:
                    continue
                    
                availability = result['availabilityResult'].get('availability')
                if not availability or availability.get('departureStationName') == 'Not available':
                    continue
                
                # Use departure and arrival station names from the response API if available, else fallback
                source, from_id, to_id, from_name, to_name = self.train_routes[train_number]
                departure_station = availability.get('departureStationName', from_name)
                arrival_station = availability.get('arrivalStationName', to_name)
                
                # Parse datetime strings from the API, note that European Sleeper sends strings like "2026-03-26T18:04:00"
                # If they include Z or offsets, handling might need to adjust.
                try:
                    dep_time = datetime.fromisoformat(availability['departureTime'])
                    arr_time = datetime.fromisoformat(availability['arrivalTime'])
                except (KeyError, ValueError):
                    print(f"Could not parse dates for {current_date_str}. Skipping.")
                    continue
                
                # For prices, we check different accommodation types. Let's find the minimum price available.
                # E.g. seat, couchette-5, sleeper-3, etc. We'll store the lowest available price.
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
                
                route_id = f"{source}|{train_number}|{departure_station}|{arrival_station}|{dep_time.isoformat()}"
                
                route_obj = Route(
                    id=route_id,
                    source=source,
                    train_number=train_number,
                    departure_station=departure_station,
                    arrival_station=arrival_station,
                    travel_date=current_date_obj,
                    departure_time=dep_time,
                    arrival_time=arr_time
                )
                
                # Create Price objects, linking them via route_id
                price_objs = []
                if min_price is not None:
                    price_objs.append(Price(
                        route_id=route_id,
                        price=min_price,
                        currency=currency,
                        is_couchette=False
                    ))
                if min_couchette_price is not None:
                    price_objs.append(Price(
                        route_id=route_id,
                        price=min_couchette_price,
                        currency=currency,
                        is_couchette=True
                    ))
                
                results.append((route_obj, price_objs))
                
        return results
