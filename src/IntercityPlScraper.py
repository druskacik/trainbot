import logging
import random
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple

import curl_cffi

logger = logging.getLogger(__name__)

from .intercity_pl_cities import build_station_eva_to_city
from .RoutesScraper import RoutesScraper
from .models import Price, Route
from .ScrapeResult import ScrapeFailure, ScrapeResult

MAX_FAILURES_STORED = 2000

API_BASE = "https://api-gateway.intercity.pl/server/public/endpoint"
STATIONS_URL = f"{API_BASE}/Aktualizacja"
SEARCH_URL = f"{API_BASE}/Pociagi"
PRICE_URL = f"{API_BASE}/Sprzedaz"

SOURCE = "intercity_pl"
# Domestic PKP IC fares are quoted in PLN (via sprawdzCenyLite);
# international fares are quoted in EUR (via sprawdzCene).
CURRENCY_PLN = "pln"
CURRENCY_EUR = "eur"

# rodzajeMiejsc codes: 1 = seat, 2 = couchette, 3 = sleeper.
# A train is a night train if it offers couchettes or sleeping berths.
NIGHT_RODZAJE = {2, 3}

# rodzajMiejscaKod values in the Sprzedaz `ceny` response have the same meaning
# as the rodzajeMiejsc codes above.
SEAT_KOD = 1
COUCHETTE_KODS = {2, 3}

HEADERS = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    ),
}

# Seed corridors used only to discover night trains. Intermediate stops are
# expanded from each train's own route — each corridor is expanded into two
# ROUTES entries so the scraper queries both directions.
_CORRIDORS: List[Tuple[int, int]] = [
    (5196003, 5596001),  # Warsaw ↔ Budapest
    (5196003, 5100059),  # Warsaw ↔ Świnoujście
    (5196003, 5100058),  # Warsaw ↔ Szklarska Poręba
    (5196003, 5100259),  # Warsaw ↔ Jelenia Góra
    (5196003, 7800013),  # Warsaw ↔ Rijeka
    (5196003, 8000261),  # Warsaw ↔ Munich
    (5100158, 5196004),  # Zakopane ↔ Szczecin
    (5100158, 5100059),  # Zakopane ↔ Świnoujście
    (5196001, 5596001),  # Cracow ↔ Budapest
    (5196001, 5100059),  # Cracow ↔ Świnoujście
    (5196001, 5101340),  # Cracow ↔ Hel
    (5196030, 5100025),  # Lublin ↔ Kołobrzeg
    (5196032, 5100010),  # Przemyśl ↔ Gdynia
    (5196032, 5101340),  # Przemyśl ↔ Hel
    (5100059, 5196032),  # Świnoujście ↔ Przemyśl
    (5100010, 5100158),  # Gdynia ↔ Zakopane
    (5100010, 5496001),  # Gdynia ↔ Prague
    (5101340, 5400038),  # Hel ↔ Bohumín
    (5100025, 5100316),  # Kołobrzeg ↔ Bielsko-Biała
    (5196001, 5100025),  # Cracow ↔ Kołobrzeg
]

ROUTES: List[Dict[str, int]] = [
    {"from_eva": a, "to_eva": b}
    for pair in _CORRIDORS
    for a, b in (pair, pair[::-1])
]


_MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def _parse_java_date(s: Optional[str]) -> Optional[datetime]:
    """Parse ``'Fri May 08 19:20:00 CEST 2026'`` to a naive local datetime.

    The route endpoint returns timestamps in Java's ``Date.toString()`` format
    regardless of the ``jezyk`` flag. We ignore the TZ abbrev and treat times
    as local, matching the naive datetimes produced elsewhere in this scraper.
    """
    if not s:
        return None
    parts = s.split()
    if len(parts) != 6:
        return None
    try:
        month = _MONTHS[parts[1]]
        day = int(parts[2])
        hh, mm, ss = (int(x) for x in parts[3].split(":"))
        year = int(parts[5])
        return datetime(year, month, day, hh, mm, ss)
    except (KeyError, ValueError):
        return None


@dataclass(frozen=True)
class _CityStop:
    city: str
    stop_index: int
    eva: int
    dep_time: Optional[datetime]
    arr_time: Optional[datetime]
    ws: bool  # dozwoloneWsiadanie — boarding allowed here
    wy: bool  # dozwoloneWysiadanie — alighting allowed here


@dataclass(frozen=True)
class _CityAnchor:
    city: str
    # First stop in this city-block where boarding is allowed (or None).
    dep_stop: Optional[_CityStop]
    # Last stop in this city-block where alighting is allowed (or None).
    arr_stop: Optional[_CityStop]


def _stops_to_city_stops(
    stops: List[dict], eva_to_city: Dict[int, str]
) -> List[_CityStop]:
    """Filter raw route stops to known cities and attach parsed times."""
    out: List[_CityStop] = []
    for idx, s in enumerate(stops):
        eva = s.get("stacja")
        if eva is None:
            continue
        city = eva_to_city.get(int(eva))
        if city is None:
            continue
        out.append(
            _CityStop(
                city=city,
                stop_index=idx,
                eva=int(eva),
                dep_time=_parse_java_date(s.get("dataWyjazdu")),
                arr_time=_parse_java_date(s.get("dataPrzyjazdu")),
                ws=bool(s.get("dozwoloneWsiadanie")),
                wy=bool(s.get("dozwoloneWysiadanie")),
            )
        )
    return out


def _collapse_to_anchors(city_stops: List[_CityStop]) -> List[_CityAnchor]:
    """Collapse consecutive same-city stops into one anchor per city-block.

    Cities may appear more than once if a train visits a city, leaves, and
    returns; each visit becomes its own anchor.
    """
    anchors: List[_CityAnchor] = []
    i = 0
    n = len(city_stops)
    while i < n:
        city = city_stops[i].city
        j = i
        while j < n and city_stops[j].city == city:
            j += 1
        block = city_stops[i:j]
        dep = next((s for s in block if s.ws), None)
        arr = next((s for s in reversed(block) if s.wy), None)
        anchors.append(_CityAnchor(city=city, dep_stop=dep, arr_stop=arr))
        i = j
    return anchors


def _fetch_stations_json() -> List[dict]:
    """Fetch the Intercity.pl station list. Each entry has `kod` and `kodEVA`."""
    payload = {
        "metoda": "pobierzStacje",
        "ostatniaAktualizacjaData": "2020-01-01 00:00:00.000",
        "urzadzenieNr": 956,
    }
    r = curl_cffi.post(STATIONS_URL, headers=HEADERS, json=payload, impersonate="chrome")
    r.raise_for_status()
    return r.json().get("stacje") or []


def _build_kod_to_eva(stations_list: List[dict]) -> Dict[int, int]:
    """Build a `kod` (short station code used inside train responses) → `kodEVA` map."""
    mapping: Dict[int, int] = {}
    for s in stations_list:
        kod = s.get("kod")
        eva = s.get("kodEVA")
        if kod is None or eva is None:
            continue
        mapping[int(kod)] = int(eva)
    return mapping


def _fetch_connections(from_eva: int, to_eva: int, date_str: str) -> dict:
    """Search Intercity.pl for connections on `date_str` between two EVA codes."""
    ticket_url = (
        f"https://ebilet.intercity.pl/polaczenia-miedzynarodowe"
        f"?dwyj={date_str}&swyj={from_eva}&sprzy={to_eva}"
        f"&time=12%3A00&przy=0&sprzez=&ticket100=1010&ticket50=&polbez=0"
    )
    payload = {
        "metoda": "wyszukajPolaczenia",
        "wersja": "1.4.2_desktop",
        "url": ticket_url,
        "dataWyjazdu": f"{date_str} 00:00:00",
        "dataPrzyjazdu": f"{date_str} 23:59:59",
        "stacjaWyjazdu": from_eva,
        "stacjaPrzyjazdu": to_eva,
        "czasNaPrzesiadkeMin": 5,
        "stacjePrzez": [],
        "polaczeniaBezposrednie": 0,
        "polaczeniaNajszybsze": 0,
        "liczbaPolaczen": 0,
        "kategoriePociagow": [],
        "kodyPrzewoznikow": [],
        "rodzajeMiejsc": [],
        "typyMiejsc": [],
        "czasNaPrzesiadkeMax": 1440,
        "braille": 0,
        "liczbaPrzesiadekMax": 2,
        "atrybutyHandlowe": [],
        "urzadzenieNr": 956,
    }
    r = curl_cffi.post(SEARCH_URL, headers=HEADERS, json=payload, impersonate="chrome")
    r.raise_for_status()
    return r.json()


def _fetch_route(
    from_eva: int, to_eva: int, train_number: int, train_dep_datetime_str: str
) -> List[dict]:
    """Fetch the list of stops for a specific train branch, in train order.

    ``pobierzTrasePrzejazdu`` filters by the (from_eva, to_eva) query — a train
    number like 407 serves both Munich and Budapest under one ``nrPociagu``,
    but each call returns only the branch relevant to the passed endpoints.
    Both endpoints must be EVA codes, not short `kod` values.
    """
    ticket_url = (
        f"https://ebilet.intercity.pl/polaczenia-miedzynarodowe"
        f"?dwyj={train_dep_datetime_str[:10]}&swyj={from_eva}&sprzy={to_eva}"
        f"&time=12%3A00&przy=0&sprzez=&ticket100=1010&ticket50=&polbez=0"
    )
    payload = {
        "metoda": "pobierzTrasePrzejazdu",
        "wersja": "1.4.2_desktop",
        "url": ticket_url,
        "urzadzenieNr": 956,
        "jezyk": "PL",
        "numerPociagu": int(train_number),
        "dataWyjazdu": train_dep_datetime_str,
        "stacjaWyjazdu": int(from_eva),
        "stacjaPrzyjazdu": int(to_eva),
    }
    r = curl_cffi.post(SEARCH_URL, headers=HEADERS, json=payload, impersonate="chrome")
    r.raise_for_status()
    return (r.json().get("trasePrzejezdu") or {}).get("trasaPrzejazdu") or []


def _fetch_price(
    station_from_eva: int,
    station_to_eva: int,
    train_number: int,
    dep_datetime_str: str,
) -> dict:
    """Fetch international fare offers for a specific train segment via sprawdzCene.

    `dep_datetime_str` must be in `"YYYY-MM-DD HH:MM:SS"` form (same shape the
    search endpoint returns in `pociag["dataWyjazdu"]`).
    """
    date_only = dep_datetime_str[:10]
    ticket_url = (
        f"https://ebilet.intercity.pl/polaczenia-miedzynarodowe"
        f"?dwyj={date_only}&swyj={station_from_eva}&sprzy={station_to_eva}"
        f"&time=12%3A00&przy=0&sprzez=&ticket100=1010&ticket50=&polbez=0"
    )
    payload = {
        "odcinki": [
            {
                "pociagNr": int(train_number),
                "wyjazdData": dep_datetime_str,
                "stacjaOdKod": int(station_from_eva),
                "stacjaDoKod": int(station_to_eva),
            }
        ],
        "podrozni": [
            {
                "dataUrodzenia": None,
                "podrozZOpiekunem": 0,
                "typOpiekuna": 0,
                "typBiletuOpiekuna": 0,
                "wspolneMiejsce": 0,
            }
        ],
        "jezyk": "EN",
        "ofertaKod": 1,
        "biletTyp": 4,
        "powrot": False,
        "metoda": "sprawdzCene",
        "wersja": "1.4.2_desktop",
        "url": ticket_url,
        "urzadzenieNr": 956,
    }
    r = curl_cffi.post(PRICE_URL, headers=HEADERS, json=payload, impersonate="chrome")
    r.raise_for_status()
    return r.json()


def _fetch_price_lite(
    kod_from: int,
    kod_to: int,
    train_number: int,
    dep_datetime_str: str,
    kategoria_pociagu,
) -> dict:
    """Fetch domestic PKP IC fare offers via sprawdzCenyLite.

    Domestic endpoint uses short `kod` station codes (not full EVAs) and returns
    prices in `cena` (PLN grosze). `dep_datetime_str` is `"YYYY-MM-DD HH:MM:SS"`.
    """
    date_only = dep_datetime_str[:10]
    ticket_url = (
        f"https://ebilet.intercity.pl/wyszukiwanie"
        f"?dwyj={date_only}&swyj={kod_from}&sprzy={kod_to}"
        f"&time=12%3A00&przy=0&sprzez=&ticket100=1010&ticket50=&polbez=0"
    )
    odcinek: Dict[str, object] = {
        "pociagNr": int(train_number),
        "wyjazdData": dep_datetime_str,
        "stacjaOdKod": int(kod_from),
        "stacjaDoKod": int(kod_to),
    }
    if kategoria_pociagu is not None:
        odcinek["kategoriaPociagu"] = kategoria_pociagu
    payload = {
        "metoda": "sprawdzCenyLite",
        "biletTyp": 1,
        "ofertyZaznaczone": [
            {"ofertaKod": 4, "uwzglednic": 0},
            {"ofertaKod": 14, "uwzglednic": 0},
            {"ofertaKod": 15, "uwzglednic": 0},
        ],
        "polaczenia": [{"idPolaczenia": 1, "odcinki": [odcinek]}],
        "podrozni": [{"kodZakupowyZnizki": 1010}],
        "wersja": "1.4.2_desktop",
        "url": ticket_url,
        "urzadzenieNr": 956,
    }
    r = curl_cffi.post(PRICE_URL, headers=HEADERS, json=payload, impersonate="chrome")
    r.raise_for_status()
    return r.json()


def _is_night_train(pociag: dict) -> bool:
    codes = pociag.get("rodzajeMiejsc") or []
    return any(c in NIGHT_RODZAJE for c in codes)


def _parse_prices(price_json: dict) -> Tuple[Optional[float], Optional[float]]:
    """Return (min_seat_eur, min_couchette_eur) from a sprawdzCene response.

    `cenaEuro` is expressed in euro cents.
    """
    seat_prices: List[float] = []
    couchette_prices: List[float] = []

    for offer in price_json.get("ceny") or []:
        if offer.get("blad"):
            continue
        cena_euro = offer.get("cenaEuro")
        if cena_euro is None or cena_euro <= 0:
            continue
        price_eur = float(cena_euro) / 100.0
        kod = offer.get("rodzajMiejscaKod")
        if kod == SEAT_KOD:
            seat_prices.append(price_eur)
        elif kod in COUCHETTE_KODS:
            couchette_prices.append(price_eur)

    min_seat = min(seat_prices) if seat_prices else None
    min_couchette = min(couchette_prices) if couchette_prices else None
    return (min_seat, min_couchette)


def _parse_prices_lite(price_json: dict) -> Tuple[Optional[float], Optional[float]]:
    """Return (min_seat_pln, min_couchette_pln) from a sprawdzCenyLite response.

    `cena` is expressed in PLN grosze (1/100 PLN).
    """
    seat_prices: List[float] = []
    couchette_prices: List[float] = []

    for conn in price_json.get("cenyPolaczen") or []:
        for offer in conn.get("ceny") or []:
            # "komunikatTekst" carries things like "Brak danych" / "Brak wolnych miejsc"
            # — skip those rather than treating them as valid prices.
            komunikat = offer.get("komunikatTekst") or ""
            if komunikat.strip():
                continue
            cena = offer.get("cena")
            if cena is None or cena <= 0:
                continue
            price_pln = float(cena) / 100.0
            kod = offer.get("rodzajMiejscaKod")
            if kod == SEAT_KOD:
                seat_prices.append(price_pln)
            elif kod in COUCHETTE_KODS:
                couchette_prices.append(price_pln)

    min_seat = min(seat_prices) if seat_prices else None
    min_couchette = min(couchette_prices) if couchette_prices else None
    return (min_seat, min_couchette)


class IntercityPlScraper(RoutesScraper):
    def __init__(self):
        super().__init__()

    def scrape(self) -> ScrapeResult:
        failures: List[ScrapeFailure] = []
        total_failures = 0
        total_requests = 0
        start_date = date.today()
        seen_routes: Set[str] = set()
        # Per-run route cache. The same physical train is rediscovered by
        # overlapping corridors, and the same nrPociagu can serve multiple
        # branches (e.g. 407 Chopin → Munich vs → Budapest), so the cache
        # key includes the query endpoints.
        route_cache: Dict[Tuple[int, str, int, int], List[dict]] = {}

        try:
            stations_list = _fetch_stations_json()
        except Exception as e:
            logger.error(f"Failed to fetch Intercity.pl stations list: {e}")
            return ScrapeResult(
                routes_scraped=0,
                failures=[ScrapeFailure("-", "-", f"stations fetch: {e}")],
                total_requests=0,
                total_failures=1,
                scraper_name="Intercity.pl",
            )

        kod_to_eva = _build_kod_to_eva(stations_list)
        eva_to_kod = {eva: kod for kod, eva in kod_to_eva.items()}
        polish_evas = set(kod_to_eva.values())
        eva_to_city = build_station_eva_to_city(stations_list)

        shuffled_routes = list(ROUTES)
        random.shuffle(shuffled_routes)

        for route in shuffled_routes:
            from_eva = route["from_eva"]
            to_eva = route["to_eva"]

            for day_offset in range(90):
                current_date = start_date + timedelta(days=day_offset)
                date_str = current_date.strftime("%Y-%m-%d")

                total_requests += 1
                try:
                    search_res = _fetch_connections(from_eva, to_eva, date_str)
                except Exception as e:
                    total_failures += 1
                    if len(failures) < MAX_FAILURES_STORED:
                        failures.append(
                            ScrapeFailure(date_str, f"{from_eva}-{to_eva}", str(e))
                        )
                    time.sleep(1)
                    continue

                # PKP IC sometimes reports the same physical night train
                # under two nrPociagu (e.g. Warsaw–Munich as 407 and 40407,
                # Gdynia–Prague as 461 and 50461) — one per operator leg.
                # Sort ascending so the lower, canonical PKP number is seen
                # first and the duplicate is skipped by `seen_routes` below.
                connections = sorted(
                    search_res.get("polaczenia") or [],
                    key=lambda c: (c.get("pociagi") or [{}])[0].get("nrPociagu") or 0,
                )

                for connection in connections:
                    pociagi = connection.get("pociagi") or []
                    if len(pociagi) != 1:
                        continue
                    pociag = pociagi[0]
                    if not _is_night_train(pociag):
                        continue

                    train_number = pociag.get("nrPociagu")
                    train_dep_str = pociag.get("dataWyjazdu")
                    kod_from = pociag.get("stacjaWyjazdu")
                    kod_to = pociag.get("stacjaPrzyjazdu")
                    kategoria_pociagu = pociag.get("kategoriaPociagu")
                    if (
                        not train_number
                        or not train_dep_str
                        or kod_from is None
                        or kod_to is None
                    ):
                        continue

                    # Search responses return `kod` for PL stations and EVA for
                    # foreign ones; pobierzTrasePrzejazdu needs EVAs on both sides.
                    query_from_eva = kod_to_eva.get(int(kod_from), int(kod_from))
                    query_to_eva = kod_to_eva.get(int(kod_to), int(kod_to))

                    cache_key = (
                        int(train_number),
                        train_dep_str,
                        query_from_eva,
                        query_to_eva,
                    )
                    if cache_key not in route_cache:
                        total_requests += 1
                        try:
                            stops = _fetch_route(
                                query_from_eva,
                                query_to_eva,
                                int(train_number),
                                train_dep_str,
                            )
                        except Exception as e:
                            total_failures += 1
                            if len(failures) < MAX_FAILURES_STORED:
                                failures.append(
                                    ScrapeFailure(
                                        date_str, str(train_number), f"route: {e}"
                                    )
                                )
                            time.sleep(1)
                            continue
                        route_cache[cache_key] = stops
                        time.sleep(0.5)
                    stops = route_cache[cache_key]

                    city_stops = _stops_to_city_stops(stops, eva_to_city)
                    anchors = _collapse_to_anchors(city_stops)
                    if len(anchors) < 2:
                        continue

                    for i in range(len(anchors)):
                        dep_anchor = anchors[i]
                        if (
                            dep_anchor.dep_stop is None
                            or dep_anchor.dep_stop.dep_time is None
                        ):
                            continue
                        for j in range(i + 1, len(anchors)):
                            arr_anchor = anchors[j]
                            if (
                                arr_anchor.arr_stop is None
                                or arr_anchor.arr_stop.arr_time is None
                            ):
                                continue

                            from_city = dep_anchor.city
                            to_city = arr_anchor.city
                            seg_dep_time = dep_anchor.dep_stop.dep_time
                            seg_arr_time = arr_anchor.arr_stop.arr_time
                            seg_from_eva = dep_anchor.dep_stop.eva
                            seg_to_eva = arr_anchor.arr_stop.eva

                            route_id = (
                                f"{SOURCE}|{from_city}|{to_city}|{seg_dep_time.isoformat()}"
                            )
                            if route_id in seen_routes:
                                continue
                            seen_routes.add(route_id)

                            is_domestic = (
                                seg_from_eva in polish_evas
                                and seg_to_eva in polish_evas
                            )
                            seg_dep_str = seg_dep_time.strftime("%Y-%m-%d %H:%M:%S")

                            logger.info(
                                f"Scraping IC.pl train {train_number}: "
                                f"{from_city} -> {to_city} @ {seg_dep_str} "
                                f"({'domestic' if is_domestic else 'intl'})"
                            )

                            total_requests += 1
                            try:
                                if is_domestic:
                                    price_res = _fetch_price_lite(
                                        eva_to_kod[seg_from_eva],
                                        eva_to_kod[seg_to_eva],
                                        int(train_number),
                                        seg_dep_str,
                                        kategoria_pociagu,
                                    )
                                    min_seat, min_couchette = _parse_prices_lite(price_res)
                                    currency = CURRENCY_PLN
                                else:
                                    price_res = _fetch_price(
                                        seg_from_eva,
                                        seg_to_eva,
                                        int(train_number),
                                        seg_dep_str,
                                    )
                                    min_seat, min_couchette = _parse_prices(price_res)
                                    currency = CURRENCY_EUR
                            except Exception as e:
                                total_failures += 1
                                if len(failures) < MAX_FAILURES_STORED:
                                    failures.append(
                                        ScrapeFailure(
                                            date_str, str(train_number), f"price: {e}"
                                        )
                                    )
                                time.sleep(1)
                                continue

                            route_obj = Route(
                                id=route_id,
                                source=SOURCE,
                                train_number=str(train_number),
                                departure_station=from_city,
                                arrival_station=to_city,
                                travel_date=seg_dep_time.date(),
                                departure_time=seg_dep_time,
                                arrival_time=seg_arr_time,
                            )

                            price_objs: List[Price] = []
                            if min_seat is not None:
                                price_objs.append(
                                    Price(
                                        route_id=route_id,
                                        price=min_seat,
                                        currency=currency,
                                        is_couchette=False,
                                    )
                                )
                            if min_couchette is not None:
                                price_objs.append(
                                    Price(
                                        route_id=route_id,
                                        price=min_couchette,
                                        currency=currency,
                                        is_couchette=True,
                                    )
                                )

                            availability: List[
                                Tuple[bool, Optional[float], Optional[str]]
                            ] = [
                                (False, min_seat, currency),
                                (True, min_couchette, currency),
                            ]
                            self.save_route_in_batch(route_obj, price_objs, availability)

                            time.sleep(0.5)

        self.flush_routes()
        return ScrapeResult(
            routes_scraped=self._total_saved,
            failures=failures,
            total_requests=total_requests,
            total_failures=total_failures,
            scraper_name="Intercity.pl",
        )
