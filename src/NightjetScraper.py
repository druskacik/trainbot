import time
import random
from datetime import date, timedelta, datetime
from typing import List, Optional, Tuple

import requests

from .RoutesScraper import RoutesScraper
from .models import Route, Price
from .ScrapeResult import ScrapeResult, ScrapeFailure

# Cap in-memory failures for long runs to avoid unbounded memory growth
MAX_FAILURES_STORED = 2000

BASE_URL = "https://www.nightjet.com/nj-booking-ocp"
SOURCE = "nightjet"
CURRENCY = "eur"


def _get_token() -> str:
    """Get the token for the Nightjet booking API."""
    r = requests.post(f"{BASE_URL}/init/start", json={"lang": "en"})
    r.raise_for_status()
    return r.json()["token"]


def _get_stations(from_id: Optional[str] = None) -> List[dict]:
    """
    Get stations from Nightjet.
    If from_id is provided, get destination stations from that city.
    Returns only stations with meta != ''.
    """
    url = f"{BASE_URL}/stations/find"
    params = {"lang": "en"}
    if from_id:
        params["evaFrom"] = from_id
    r = requests.get(url, params=params)
    r.raise_for_status()
    stations = r.json()
    return [s for s in stations if s.get("meta") != ""]


def _get_routes_on_date(from_id: str, to_id: str, travel_date: date) -> dict:
    """Get all routes on a given date between two city IDs."""
    date_str = travel_date.strftime("%Y-%m-%d")
    url = f"{BASE_URL}/connection/{from_id}/{to_id}/{date_str}"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def _get_route_details(
    from_station_id: str,
    to_station_id: str,
    departure_utc_ms: int,
    train: str,
    token: str,
) -> dict:
    """
    Fetch offer details for a given Nightjet route.
    Uses concrete station numbers and UTC departure timestamp from the route.
    """
    url = f"{BASE_URL}/offer/get"
    headers = {
        "x-token": token,
        "Content-Type": "application/json",
    }
    # API expects integers for njFrom, njTo, njDep
    body = {
        "njFrom": int(from_station_id),
        "njDep": departure_utc_ms,
        "njTo": int(to_station_id),
        "maxChanges": 0,
        "connections": 5,
        "filter": {
            "njTrain": train,
            "njDeparture": departure_utc_ms,
        },
        "objects": [
            {
                "type": "person",
                "birthDate": "1996-03-09",
            }
        ],
        "lang": "en",
    }
    r = requests.post(url, headers=headers, json=body)
    r.raise_for_status()
    return r.json()


def _parse_details_prices(details: dict) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse details JSON for cheapest seat and cheapest couchette/sleeper.
    Returns (min_seat_price, min_couchette_price); either may be None.

    Iterates all offers and all compartments within each offer.
    accommodationType "SE" = seat, anything else = couchette/sleeper.
    """
    try:
        result = details.get("result") or []
        if not result or result[0] is None:
            return (None, None)
        connections = result[0].get("connections") or []
        if not connections or connections[0] is None:
            return (None, None)
        offers = connections[0].get("offers") or []
        if not offers:
            return (None, None)
    except (IndexError, KeyError, TypeError):
        return (None, None)

    seat_prices: List[float] = []
    couchette_prices: List[float] = []

    for offer in offers:
        reservation = offer.get("reservation") or {}
        segments = reservation.get("reservationSegments") or []
        if not segments:
            continue
        for comp in segments[0].get("compartments") or []:
            objs = comp.get("objects") or []
            if not objs or objs[0].get("price") is None:
                continue
            price = float(objs[0]["price"])
            if comp.get("accommodationType") == "SE":
                seat_prices.append(price)
            else:
                couchette_prices.append(price)

    min_seat = min(seat_prices) if seat_prices else None
    min_couchette = min(couchette_prices) if couchette_prices else None
    return (min_seat, min_couchette)


class NightjetScraper(RoutesScraper):
    def __init__(self):
        super().__init__()

    def scrape(self) -> ScrapeResult:
        failures: List[ScrapeFailure] = []
        total_failures = 0
        total_requests = 0
        start_date = date.today()

        token = _get_token()
        all_cities = _get_stations()
        if not all_cities:
            return ScrapeResult(routes_scraped=0, failures=failures, total_requests=0)

        shuffled_cities = list(all_cities)
        random.shuffle(shuffled_cities)

        for from_city in shuffled_cities:
            from_id = from_city.get("number")
            if not from_id:
                continue
            destinations = _get_stations(from_id=from_id)
            for to_city in destinations:
                to_id = to_city.get("number")
                if not to_id or to_id == from_id:
                    continue

                for day_offset in range(90):
                    current_date = start_date + timedelta(days=day_offset)
                    try:
                        routes_result = _get_routes_on_date(from_id, to_id, current_date)
                    except requests.exceptions.RequestException as e:
                        date_str = current_date.strftime("%Y-%m-%d")
                        total_failures += 1
                        if len(failures) < MAX_FAILURES_STORED:
                            failures.append(
                                ScrapeFailure(
                                    date_str,
                                    f"{from_id}-{to_id}",
                                    str(e),
                                )
                            )
                        continue

                    connections = routes_result.get("connections") or []
                    for connection in connections:
                        from_station_id = (connection.get("from") or {}).get("number")
                        to_station_id = (connection.get("to") or {}).get("number")
                        from_name = (connection.get("from") or {}).get("name", "")
                        to_name = (connection.get("to") or {}).get("name", "")
                        trains = connection.get("trains") or []

                        for train_info in trains:
                            train_name = train_info.get("train", "")
                            dep = train_info.get("departure") or {}
                            arr = train_info.get("arrival") or {}
                            dep_utc = dep.get("utc")
                            dep_local = dep.get("local")
                            arr_local = arr.get("local")
                            train_date_str = train_info.get("date")

                            if not from_station_id or not to_station_id or dep_utc is None:
                                continue
                            if not dep_local or not arr_local or not train_date_str:
                                continue

                            total_requests += 1
                            print(
                                f"Scraping {train_name} {train_date_str}: {from_name} -> {to_name}"
                            )

                            try:
                                details = _get_route_details(
                                    from_station_id,
                                    to_station_id,
                                    dep_utc,
                                    train_name,
                                    token,
                                )
                            except requests.exceptions.HTTPError as e:
                                if e.response is not None and e.response.status_code == 401:
                                    try:
                                        token = _get_token()
                                        details = _get_route_details(
                                            from_station_id,
                                            to_station_id,
                                            dep_utc,
                                            train_name,
                                            token,
                                        )
                                    except Exception as retry_e:
                                        total_failures += 1
                                        if len(failures) < MAX_FAILURES_STORED:
                                            failures.append(
                                                ScrapeFailure(
                                                    train_date_str,
                                                    train_name,
                                                    str(retry_e),
                                                )
                                            )
                                        time.sleep(1)
                                        continue
                                else:
                                    total_failures += 1
                                    if len(failures) < MAX_FAILURES_STORED:
                                        failures.append(
                                            ScrapeFailure(
                                                train_date_str,
                                                train_name,
                                                str(e),
                                            )
                                        )
                                    time.sleep(1)
                                    continue
                            except Exception as e:
                                total_failures += 1
                                if len(failures) < MAX_FAILURES_STORED:
                                    failures.append(
                                        ScrapeFailure(train_date_str, train_name, str(e))
                                    )
                                time.sleep(1)
                                continue
                            finally:
                                pass
                                # time.sleep(1)

                            min_seat, min_couchette = _parse_details_prices(details)

                            try:
                                dep_time = datetime.fromisoformat(
                                    dep_local.replace("Z", "+00:00")
                                )
                                arr_time = datetime.fromisoformat(
                                    arr_local.replace("Z", "+00:00")
                                )
                            except (ValueError, TypeError):
                                print(
                                    f"Could not parse times for {train_date_str} {train_name}. Skipping."
                                )
                                continue

                            try:
                                travel_date = datetime.strptime(
                                    train_date_str, "%Y-%m-%d"
                                ).date()
                            except (ValueError, TypeError):
                                travel_date = current_date

                            route_id = (
                                f"{SOURCE}|{train_name}|{from_name}|{to_name}|{dep_time.isoformat()}"
                            )

                            route_obj = Route(
                                id=route_id,
                                source=SOURCE,
                                train_number=train_name,
                                departure_station=from_name,
                                arrival_station=to_name,
                                travel_date=travel_date,
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
                            self.save_route_in_batch(
                                route_obj, price_objs, availability
                            )

        self.flush_routes()
        return ScrapeResult(
            routes_scraped=self._total_saved,
            failures=failures,
            total_requests=total_requests,
            total_failures=total_failures,
        )
