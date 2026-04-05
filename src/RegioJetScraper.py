import time
import random
from datetime import date, timedelta, datetime
from typing import List, Optional, Tuple

import requests

from .RoutesScraper import RoutesScraper
from .models import Route, Price
from .ScrapeResult import ScrapeResult, ScrapeFailure

MAX_FAILURES_STORED = 2000

SEARCH_URL = "https://brn-ybus-pubapi.sa.cz/restapi/routes/search/simple"
DETAIL_URL = "https://brn-ybus-pubapi.sa.cz/restapi/routes/{route_id}/simple"
SOURCE = "regiojet"
CURRENCY = "eur"

NIGHT_TRAINS = {"RJ 1020", "RJ 1021", "RJ 1022", "RJ 1023"}

# Each train's ordered stops as (city_name, city_id).
# Duplicate cities (e.g. Ostrava appearing 3×) are kept in the raw data
# but deduplicated when generating search pairs.
TRAIN_ROUTES = {
    "RJ 1020": [
        ("Chop", 7122881001),
        ("Košice", 10202033),
        ("Kysak (u města Prešov)", 1762994001),
        ("Margecany", 2317706000),
        ("Spišská Nová Ves", 1762994000),
        ("Poprad", 10202035),
        ("Štrba", 49584002),
        ("Liptovský Mikuláš", 10202036),
        ("Ružomberok", 10202037),
        ("Vrútky", 49584000),
        ("Žilina", 10202038),
        ("Čadca", 508808002),
        ("Návsí (Jablunkov)", 1558067000),
        ("Bystřice (Třinec)", 1313136001),
        ("Třinec centrum", 508808001),
        ("Český Těšín", 508808000),
        ("Havířov", 372842004),
        ("Ostrava", 10202000),
        ("Bohumín", 2147875000),
        ("Opava východ", 3741270000),
        ("Hranice na M.", 372842003),
        ("Olomouc", 10202031),
        ("Zábřeh na Moravě", 372842002),
        ("Česká Třebová", 1313136000),
        ("Pardubice", 372842000),
        ("Prague", 10202003),
    ],
    "RJ 1021": [
        ("Prague", 10202003),
        ("Pardubice", 372842000),
        ("Česká Třebová", 1313136000),
        ("Zábřeh na Moravě", 372842002),
        ("Olomouc", 10202031),
        ("Hranice na M.", 372842003),
        ("Ostrava", 10202000),
        ("Opava východ", 3741270000),
        ("Bohumín", 2147875000),
        ("Havířov", 372842004),
        ("Český Těšín", 508808000),
        ("Třinec centrum", 508808001),
        ("Bystřice (Třinec)", 1313136001),
        ("Návsí (Jablunkov)", 1558067000),
        ("Čadca", 508808002),
        ("Žilina", 10202038),
        ("Vrútky", 49584000),
        ("Ružomberok", 10202037),
        ("Liptovský Mikuláš", 10202036),
        ("Štrba", 49584002),
        ("Poprad", 10202035),
        ("Spišská Nová Ves", 1762994000),
        ("Margecany", 2317706000),
        ("Kysak (u města Prešov)", 1762994001),
        ("Košice", 10202033),
        ("Chop", 7122881001),
    ],
    "RJ 1022": [
        ("Přemyšl", 5990055004),
        ("Řešov", 5990055007),
        ("Cracow", 1225791000),
        ("Ostrava", 10202000),
        ("Olomouc", 10202031),
        ("Pardubice", 372842000),
        ("Prague", 10202003),
    ],
    "RJ 1023": [
        ("Prague", 10202003),
        ("Pardubice", 372842000),
        ("Olomouc", 10202031),
        ("Ostrava", 10202000),
        ("Cracow", 1225791000),
        ("Řešov", 5990055007),
        ("Přemyšl", 5990055004),
    ],
}


def _deduplicated_stops(stops: list) -> list:
    """Remove duplicate city_ids from a stop list, keeping first occurrence."""
    seen = set()
    result = []
    for name, city_id in stops:
        if city_id not in seen:
            seen.add(city_id)
            result.append((name, city_id))
    return result


def _collect_city_pairs() -> List[Tuple[int, int]]:
    """Collect all unique directed (from_city_id, to_city_id) pairs across all routes."""
    pairs = set()
    for stops in TRAIN_ROUTES.values():
        deduped = _deduplicated_stops(stops)
        for i, (_, from_id) in enumerate(deduped):
            for _, to_id in deduped[i + 1:]:
                pairs.add((from_id, to_id))
    return list(pairs)


def _search_routes(from_city_id: int, to_city_id: int, departure_date: str) -> list:
    """Search RegioJet API for routes between two cities on a given date.
    Uses the /simple endpoint which correctly respects the departureDate parameter.
    Returns the list of route objects from the 'routes' key."""
    params = {
        "fromLocationId": from_city_id,
        "fromLocationType": "CITY",
        "toLocationId": to_city_id,
        "toLocationType": "CITY",
        "departureDate": departure_date,
    }
    r = requests.get(SEARCH_URL, params=params)
    r.raise_for_status()
    data = r.json()
    return data.get("routes") or []


def _get_route_detail(route_id: str, from_station_id: int, to_station_id: int) -> dict:
    """Fetch full route details (priceClasses, sections, city names) for a specific route.
    Uses /routes/{routeId}/simple with station IDs and tariff."""
    url = DETAIL_URL.format(route_id=route_id)
    params = {
        "fromStationId": from_station_id,
        "toStationId": to_station_id,
        "tariffs": "REGULAR",
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()


def _get_train_code(detail: dict) -> Optional[str]:
    """Extract the train line code (e.g. 'RJ 1021') from a route's sections."""
    for section in detail.get("sections") or []:
        line = section.get("line") or {}
        code = line.get("code")
        if code:
            return code
    return None


def _parse_prices(detail: dict) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse priceClasses for cheapest seat and cheapest sleeping price.
    seatClassKey containing 'COUCHETTE' = sleeping, else = seat.
    Only considers bookable classes with available seats.
    Returns (min_seat_price, min_couchette_price); either may be None.
    """
    seat_prices: List[float] = []
    couchette_prices: List[float] = []

    for pc in detail.get("priceClasses") or []:
        if not pc.get("bookable"):
            continue
        if (pc.get("freeSeatsCount") or 0) <= 0:
            continue
        price = pc.get("price")
        if price is None:
            continue

        key = pc.get("seatClassKey", "")
        if "COUCHETTE" in key:
            couchette_prices.append(float(price))
        else:
            seat_prices.append(float(price))

    min_seat = min(seat_prices) if seat_prices else None
    min_couchette = min(couchette_prices) if couchette_prices else None
    return (min_seat, min_couchette)


class RegioJetScraper(RoutesScraper):
    def __init__(self):
        super().__init__()

    def scrape(self) -> ScrapeResult:
        failures: List[ScrapeFailure] = []
        total_failures = 0
        total_requests = 0
        start_date = date.today()

        city_pairs = _collect_city_pairs()
        random.shuffle(city_pairs)

        for from_city_id, to_city_id in city_pairs:
            for day_offset in range(90):
                current_date = start_date + timedelta(days=day_offset)
                date_str = current_date.strftime("%Y-%m-%d")

                total_requests += 1
                try:
                    routes_data = _search_routes(from_city_id, to_city_id, date_str)
                except requests.exceptions.RequestException as e:
                    total_failures += 1
                    if len(failures) < MAX_FAILURES_STORED:
                        failures.append(
                            ScrapeFailure(date_str, f"{from_city_id}-{to_city_id}", str(e))
                        )
                    time.sleep(0.5)
                    continue

                for simple_route in routes_data:
                    rj_route_id = simple_route.get("id")
                    from_station_id = simple_route.get("departureStationId")
                    to_station_id = simple_route.get("arrivalStationId")
                    if not rj_route_id or not from_station_id or not to_station_id:
                        continue

                    # Filter by departure date — the simple endpoint may return
                    # routes from neighbouring days too
                    dep_time_str = simple_route.get("departureTime", "")
                    if not dep_time_str.startswith(date_str):
                        continue

                    try:
                        detail = _get_route_detail(rj_route_id, from_station_id, to_station_id)
                    except requests.exceptions.RequestException as e:
                        total_failures += 1
                        if len(failures) < MAX_FAILURES_STORED:
                            failures.append(
                                ScrapeFailure(date_str, f"{from_city_id}-{to_city_id}", str(e))
                            )
                        time.sleep(0.5)
                        continue

                    train_code = _get_train_code(detail)
                    if not train_code or train_code not in NIGHT_TRAINS:
                        continue

                    dep_city = detail.get("departureCityName", "")
                    arr_city = detail.get("arrivalCityName", "")
                    detail_dep_str = detail.get("departureTime")
                    detail_arr_str = detail.get("arrivalTime")

                    if not detail_dep_str or not detail_arr_str:
                        continue

                    try:
                        dep_time = datetime.fromisoformat(detail_dep_str)
                        arr_time = datetime.fromisoformat(detail_arr_str)
                    except (ValueError, TypeError):
                        print(f"Could not parse times for {train_code} {date_str}. Skipping.")
                        continue

                    print(f"Scraping {train_code} {date_str}: {dep_city} -> {arr_city}")

                    min_seat, min_couchette = _parse_prices(detail)

                    route_id = f"{SOURCE}|{train_code}|{dep_city}|{arr_city}|{dep_time.isoformat()}"

                    route_obj = Route(
                        id=route_id,
                        source=SOURCE,
                        train_number=train_code,
                        departure_station=dep_city,
                        arrival_station=arr_city,
                        travel_date=dep_time.date(),
                        departure_time=dep_time,
                        arrival_time=arr_time,
                    )

                    price_objs: List[Optional[Price]] = []
                    if min_seat is not None:
                        price_objs.append(
                            Price(
                                route_id=route_id,
                                price=min_seat,
                                currency=CURRENCY,
                                is_couchette=False,
                            )
                        )
                    if min_couchette is not None:
                        price_objs.append(
                            Price(
                                route_id=route_id,
                                price=min_couchette,
                                currency=CURRENCY,
                                is_couchette=True,
                            )
                        )

                    availability: List[Tuple[bool, Optional[float], Optional[str]]] = [
                        (False, min_seat, CURRENCY),
                        (True, min_couchette, CURRENCY),
                    ]
                    self.save_route_in_batch(route_obj, price_objs, availability)

                time.sleep(0.25)

        self.flush_routes()
        return ScrapeResult(
            routes_scraped=self._total_saved,
            failures=failures,
            total_requests=total_requests,
            total_failures=total_failures,
            scraper_name="RegioJet",
        )
