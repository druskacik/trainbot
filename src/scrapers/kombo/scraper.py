import logging
import re
import time
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple

import curl_cffi

from ...RoutesScraper import RoutesScraper
from ...models import Price, Route
from ...ScrapeResult import ScrapeFailure, ScrapeResult

logger = logging.getLogger(__name__)

SOURCE = "kombo"
CURRENCY_EUR = "eur"
MAX_FAILURES_STORED = 2000

SEARCH_URL = "https://search.kombo.co/search"
POLL_URL = "https://search.kombo.co/search/trips"
CHECK_AVAILABILITY_URL = "https://booking.kombo.co/checkAvailability"

# Kombo's company ID for SNCF Intercités (IdN/IC). All daytime IC and night IdN
# trains share this id; we filter further by direct, single-segment trips.
IDN_COMPANY_ID = 17287

# Sent on every kombo request; the front-end pins this and the API rejects calls
# without it. Bump if kombo ever ships a new website version that 4xxs us.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.kombo.co",
    "Referer": "https://www.kombo.co/en/train",
    "k-version": "8.1.0",
}

# City IDs from place.kombo.co/search autocomplete. Latour-de-Carol is mapped
# to kombo's "Enveitg" entry (the cross-border station is named Enveitg in
# their data); the resolved station label still reads as Latour-de-Carol.
CITY_IDS: Dict[str, int] = {
    "Paris": 1,
    "Toulouse": 16,
    "Rodez": 26891,
    "Latour-de-Carol": 87432,
    "Cerbère": 95335,
    "Tarbes": 75,
    "Briançon": 69,
    "Nice": 5,
    "Aurillac": 27059,
}

_ROUTE_PAIRS: List[Tuple[str, str]] = [
    ("Paris", "Toulouse"),
    ("Paris", "Rodez"),
    ("Paris", "Latour-de-Carol"),
    ("Paris", "Cerbère"),
    ("Paris", "Tarbes"),
    ("Paris", "Briançon"),
    ("Paris", "Nice"),
    ("Paris", "Aurillac"),
]

ROUTES: List[Tuple[str, str]] = [
    pair for a, b in _ROUTE_PAIRS for pair in ((a, b), (b, a))
]

_TRAIN_NUMBER_RE = re.compile(r"^\d+$")

# Flexibility name keywords that mark a fare as a couchette/sleeper rather than
# a seat. Kombo's `flexibilities[<id>].name` for IdN couchettes is "Bunk bed";
# the others cover SNCF-localized variants we may encounter on other routes.
_COUCHETTE_FLEX_KEYWORDS = ("bunk", "couchette", "lit", "sleeper", "berth")
# Backup signal: SNCF's seat-option codes for couchette berth positions.
# CBAS/CHAU/CMIL/CIRE = bottom/top/middle/bottom-compulsory.
_COUCHETTE_VALUE_CODES = {"CBAS", "CHAU", "CMIL", "CIRE"}


def _post_search(origin_id: int, destination_id: int, current_date: date) -> str:
    body = {
        "departureCityId": origin_id,
        "arrivalCityId": destination_id,
        "dateOutward": current_date.isoformat(),
        "passengers": [{"ageGroup": "Adult"}],
        "transportType": "train",
        "currency": "EUR",
        "locale": "en",
    }
    r = curl_cffi.post(
        SEARCH_URL, headers=HEADERS, json=body,
        impersonate="chrome131", timeout=20,
    )
    r.raise_for_status()
    return r.json()["key"]


def _poll_trips(key: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Poll until percentageDone == 100 or we hit ~25 polls (kombo searches usually
    finish in 2-3 polls; capped to avoid hanging on a stuck backend).

    Each poll response carries only the dependencies (stations, cities, companies)
    referenced by the trips returned in *that* poll, so we merge across polls
    rather than overwriting — otherwise late polls can clobber station data for
    trips returned by earlier polls.
    """
    trips: List[Dict[str, Any]] = []
    deps: Dict[str, Dict[Any, Any]] = {}
    last_index = 0
    for _ in range(25):
        r = curl_cffi.get(
            POLL_URL, headers=HEADERS,
            params={"key": key, "lastIndex": last_index},
            impersonate="chrome131", timeout=20,
        )
        r.raise_for_status()
        j = r.json()
        trips.extend(j.get("trips") or [])
        for dep_key, dep_value in (j.get("dependencies") or {}).items():
            if isinstance(dep_value, dict):
                deps.setdefault(dep_key, {}).update(dep_value)
        last_index = j.get("newLastIndex", last_index)
        if j.get("percentageDone") == 100:
            return trips, deps
        time.sleep(1)
    raise RuntimeError(
        f"kombo poll did not complete within 25 attempts (key={key})"
    )


def _post_check_availability(trip_id: str) -> Dict[str, Any]:
    body = {
        "locale": "en",
        "outwardTripId": trip_id,
        "outwardCurrency": "EUR",
        "passengers": [{
            "ageGroup": "Adult", "discountCards": [],
            "reducedMobility": False, "hasWheelchair": False,
            "hasMobilityCard": False, "onLap": False,
        }],
        "inwardCurrency": "EUR",
    }
    r = curl_cffi.post(
        CHECK_AVAILABILITY_URL, headers=HEADERS, json=body,
        impersonate="chrome131", timeout=30,
    )
    r.raise_for_status()
    return r.json()


def _iter_idn_trips(trips: List[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
    """Direct, single-segment Intercités *de Nuit* trips with a numeric train
    number. Kombo lumps all Intercités (companyId=17287) together — daytime IC
    and night IdN — so we additionally require the arrival calendar date to
    differ from the departure date, which uniquely identifies night trains."""
    for t in trips:
        sub_trips = t.get("subTrips") or []
        if len(sub_trips) != 1:
            continue
        segments = sub_trips[0].get("segments") or []
        if len(segments) != 1:
            continue
        seg = segments[0]
        if seg.get("companyId") != IDN_COMPANY_ID:
            continue
        train_number = seg.get("transportNumber")
        if not train_number or not _TRAIN_NUMBER_RE.match(str(train_number)):
            continue
        try:
            dep_dt = datetime.fromisoformat(
                seg["departureTime"].replace("Z", "+00:00")
            )
            arr_dt = datetime.fromisoformat(
                seg["arrivalTime"].replace("Z", "+00:00")
            )
        except (KeyError, ValueError):
            continue
        if dep_dt.date() == arr_dt.date():
            continue
        yield t


def _resolve_station(station_id: Any, deps: Dict[str, Any]) -> Optional[str]:
    """Map a station id from a segment to its display name. Tries int and str
    keys because the dependencies dict has string keys but segment ids are ints."""
    if station_id is None:
        return None
    stations = (deps.get("stations") or {})
    info = stations.get(str(station_id)) or stations.get(station_id) or {}
    return info.get("name")


def _is_couchette_option(option: Dict[str, Any], flexibilities: Dict[str, Any]) -> bool:
    flex_id = option.get("flexibilityId")
    if flex_id is not None:
        flex_info = flexibilities.get(str(flex_id)) or flexibilities.get(flex_id) or {}
        flex_name = (flex_info.get("name") or "").lower()
        if any(kw in flex_name for kw in _COUCHETTE_FLEX_KEYWORDS):
            return True
    for so in option.get("seatOptions") or []:
        for inner in so.get("options") or []:
            value = (inner.get("value") or "").upper()
            label = (inner.get("translations") or {}).get("label") or ""
            if value in _COUCHETTE_VALUE_CODES:
                return True
            if any(kw in label.lower() for kw in _COUCHETTE_FLEX_KEYWORDS):
                return True
    return False


def _classify_prices(
    availability: Dict[str, Any],
) -> Tuple[Optional[float], Optional[float]]:
    """Walk the (option_bundle, sortedPriceOptions) pairs and split into seat
    vs couchette buckets via flexibility name; return the cheapest of each."""
    deps = availability.get("dependencies") or {}
    flex = deps.get("flexibilities") or {}
    outward = (availability.get("availability") or {}).get("outwardTrip") or {}
    # Sold-out / unsellable trips still come back with a single placeholder
    # option (amount=0, flexibilityId=1 "Standard", no seatOptions) which would
    # otherwise be misclassified as a real €0 seat fare.
    if outward.get("isAvailable") is False:
        return None, None
    sub_trips = outward.get("subTrips") or []
    if not sub_trips:
        return None, None
    sub = sub_trips[0]
    prices = sub.get("sortedPriceOptions") or []
    segments = sub.get("segments") or []
    if not segments:
        return None, None
    option_bundles = segments[0].get("options") or []

    seat_prices: List[float] = []
    couchette_prices: List[float] = []
    classified_any = False
    for i, bundle in enumerate(option_bundles):
        if i >= len(prices) or not bundle:
            continue
        if bundle[0].get("remainingSeats") == 0:
            continue
        amount_cents = (prices[i] or {}).get("amount")
        if amount_cents is None:
            continue
        eur = amount_cents / 100.0
        # Bundle is a list of per-segment options; for direct single-segment
        # trips it has exactly one entry. Use it for classification.
        if _is_couchette_option(bundle[0], flex):
            couchette_prices.append(eur)
        else:
            seat_prices.append(eur)
        classified_any = True

    if not classified_any and prices:
        # Defensive fallback: if no options were classifiable but we have
        # sortedPriceOptions, treat the cheapest as seat and the rest as
        # couchette. IdN seats are always the cheapest fare empirically.
        amounts = [(p.get("amount") or 0) / 100.0 for p in prices if p.get("amount") is not None]
        if amounts:
            amounts.sort()
            seat_prices.append(amounts[0])
            couchette_prices.extend(amounts[1:])
            logger.info(
                "Kombo: no flexibility data on options; falling back to price-rank "
                "classification (seat=%s, couchette=%s)",
                seat_prices, couchette_prices,
            )

    min_seat = min(seat_prices) if seat_prices else None
    min_couchette = min(couchette_prices) if couchette_prices else None
    return min_seat, min_couchette


class KomboScraper(RoutesScraper):
    def __init__(self):
        super().__init__()

    def scrape(self) -> ScrapeResult:
        failures: List[ScrapeFailure] = []
        total_failures = 0
        total_requests = 0
        seen_routes: Set[str] = set()
        start_date = date.today()

        for from_city, to_city in ROUTES:
            origin_id = CITY_IDS[from_city]
            destination_id = CITY_IDS[to_city]

            for day_offset in range(90):
                current_date = start_date + timedelta(days=day_offset)
                date_str = current_date.strftime("%Y-%m-%d")

                total_requests += 1
                try:
                    key = _post_search(origin_id, destination_id, current_date)
                    trips, deps = _poll_trips(key)
                except Exception as e:
                    total_failures += 1
                    if len(failures) < MAX_FAILURES_STORED:
                        failures.append(
                            ScrapeFailure(date_str, f"{from_city}-{to_city}", str(e))
                        )
                    time.sleep(1)
                    continue

                idn_trips = list(_iter_idn_trips(trips))
                if not idn_trips:
                    logger.info(
                        "Kombo %s %s->%s: no direct IdN trips",
                        date_str, from_city, to_city,
                    )

                for trip in idn_trips:
                    seg = trip["subTrips"][0]["segments"][0]
                    train_number = str(seg["transportNumber"])
                    try:
                        dep_time = datetime.fromisoformat(
                            seg["departureTime"].replace("Z", "+00:00")
                        ).replace(tzinfo=None)
                        arr_time = datetime.fromisoformat(
                            seg["arrivalTime"].replace("Z", "+00:00")
                        ).replace(tzinfo=None)
                    except (KeyError, ValueError):
                        continue

                    dep_station = _resolve_station(seg.get("departureStationId"), deps)
                    arr_station = _resolve_station(seg.get("arrivalStationId"), deps)
                    if not dep_station or not arr_station:
                        logger.warning(
                            "Kombo: missing station label for train %s (dep_id=%s arr_id=%s)",
                            train_number, seg.get("departureStationId"), seg.get("arrivalStationId"),
                        )
                        continue

                    route_id = (
                        f"{SOURCE}|{train_number}|{dep_station}|{arr_station}"
                        f"|{dep_time.isoformat()}"
                    )
                    if route_id in seen_routes:
                        continue
                    seen_routes.add(route_id)

                    total_requests += 1
                    try:
                        availability = _post_check_availability(trip["tripId"])
                    except Exception as e:
                        total_failures += 1
                        if len(failures) < MAX_FAILURES_STORED:
                            failures.append(
                                ScrapeFailure(date_str, train_number, str(e))
                            )
                        continue

                    min_seat, min_couchette = _classify_prices(availability)

                    logger.info(
                        "Scraping Kombo train %s: %s -> %s @ %s (seat=%s, couchette=%s)",
                        train_number, dep_station, arr_station,
                        dep_time.isoformat(), min_seat, min_couchette,
                    )

                    route_obj = Route(
                        id=route_id,
                        source=SOURCE,
                        train_number=train_number,
                        departure_station=dep_station,
                        arrival_station=arr_station,
                        travel_date=dep_time.date(),
                        departure_time=dep_time,
                        arrival_time=arr_time,
                    )

                    price_objs: List[Price] = []
                    if min_seat is not None:
                        price_objs.append(Price(
                            route_id=route_id, price=min_seat,
                            currency=CURRENCY_EUR, is_couchette=False,
                        ))
                    if min_couchette is not None:
                        price_objs.append(Price(
                            route_id=route_id, price=min_couchette,
                            currency=CURRENCY_EUR, is_couchette=True,
                        ))

                    availability_rows: List[Tuple[bool, Optional[float], Optional[str]]] = [
                        (False, min_seat, CURRENCY_EUR),
                        (True, min_couchette, CURRENCY_EUR),
                    ]
                    self.save_route_in_batch(route_obj, price_objs, availability_rows)

                time.sleep(0.25)

        self.flush_routes()
        return ScrapeResult(
            routes_scraped=self._total_saved,
            failures=failures,
            total_requests=total_requests,
            total_failures=total_failures,
            scraper_name="Kombo",
        )
