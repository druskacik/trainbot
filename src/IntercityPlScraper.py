import logging
import random
import time
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import curl_cffi

logger = logging.getLogger(__name__)

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

# Routes copied from 500_scrape_intercity_pl.ipynb (cell ba895f70).
ROUTES: List[Dict[str, int]] = [
    {"from_eva": 5196003, "to_eva": 5596001},  # Warsaw – Budapest
    {"from_eva": 5196003, "to_eva": 5100059},  # Warsaw – Świnoujście
    {"from_eva": 5196003, "to_eva": 5100058},  # Warsaw – Szklarska Poręba
    {"from_eva": 5196003, "to_eva": 5100259},  # Warsaw – Jelenia Góra
    {"from_eva": 5196003, "to_eva": 7800013},  # Warsaw – Rijeka
    {"from_eva": 5196003, "to_eva": 8000261},  # Warsaw – Munich
    {"from_eva": 5100158, "to_eva": 5196004},  # Zakopane – Szczecin
    {"from_eva": 5100158, "to_eva": 5100059},  # Zakopane – Świnoujście
    {"from_eva": 5196001, "to_eva": 5100059},  # Cracow – Świnoujście
    {"from_eva": 5196001, "to_eva": 5101340},  # Cracow – Hel
    {"from_eva": 5196030, "to_eva": 5100025},  # Lublin – Kołobrzeg
    {"from_eva": 5196032, "to_eva": 5100010},  # Przemyśl – Gdynia
    {"from_eva": 5196032, "to_eva": 5101340},  # Przemyśl – Hel
    {"from_eva": 5100059, "to_eva": 5196032},  # Świnoujście – Przemyśl
    {"from_eva": 5100010, "to_eva": 5100158},  # Gdynia – Zakopane
    {"from_eva": 5100010, "to_eva": 5496001},  # Gdynia – Prague
    {"from_eva": 5101340, "to_eva": 5400038},  # Hel – Bohumín
    {"from_eva": 5100025, "to_eva": 5100316},  # Kołobrzeg – Bielsko-Biała
    {"from_eva": 5196001, "to_eva": 5100025},  # Cracow – Kołobrzeg
]

# EVA → display metadata. Used to pick the English station name we persist.
# Copied from 500_scrape_intercity_pl.ipynb (cell 19e3639f).
STATIONS: Dict[int, Dict[str, str]] = {
    5196003: {"english_name": "Warsaw", "name": "Warszawa (dowolna stacja)"},
    5596001: {"english_name": "Budapest", "name": "Budapeszt (dowolna stacja)"},
    5100059: {"english_name": "Swinoujscie", "name": "Świnoujście"},
    5100058: {"english_name": "Szklarska Poreba", "name": "Szklarska Por.G."},
    5100259: {"english_name": "Jelenia Gora", "name": "Jelenia Góra"},
    7800013: {"english_name": "Rijeka", "name": "Rijeka"},
    8000261: {"english_name": "Munich", "name": "München Hbf / Monachium Główne"},
    5100158: {"english_name": "Zakopane", "name": "Zakopane"},
    5196004: {"english_name": "Szczecin", "name": "Szczecin (dowolna stacja)"},
    5196001: {"english_name": "Cracow", "name": "Kraków (dowolna stacja)"},
    5101340: {"english_name": "Hel", "name": "Hel"},
    5196030: {"english_name": "Lublin", "name": "Lublin (dowolna stacja)"},
    5100025: {"english_name": "Kolobrzeg", "name": "Kołobrzeg"},
    5400038: {"english_name": "Bohumin", "name": "Bohumín / Bogumin"},
    5196032: {"english_name": "Przemysl", "name": "Przemyśl (dowolna stacja)"},
    5100010: {"english_name": "Gdynia", "name": "Gdynia Gł."},
    5496001: {"english_name": "Prague", "name": "Praga (dowolna stacja)"},
    5100316: {"english_name": "Bielsko-Biala", "name": "Bielsko-Biała Gł."},
}


def _station_display_name(eva: int) -> str:
    meta = STATIONS.get(eva)
    if meta:
        return meta["english_name"]
    return str(eva)


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
        seen_routes: set = set()

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

        shuffled_routes = list(ROUTES)
        random.shuffle(shuffled_routes)

        for route in shuffled_routes:
            from_eva = route["from_eva"]
            to_eva = route["to_eva"]
            dep_city = _station_display_name(from_eva)
            arr_city = _station_display_name(to_eva)

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

                for connection in search_res.get("polaczenia") or []:
                    pociagi = connection.get("pociagi") or []
                    if len(pociagi) != 1:
                        continue
                    pociag = pociagi[0]
                    if not _is_night_train(pociag):
                        continue

                    train_number = pociag.get("nrPociagu")
                    dep_dt_str = pociag.get("dataWyjazdu")
                    arr_dt_str = pociag.get("dataPrzyjazdu")
                    kod_from = pociag.get("stacjaWyjazdu")
                    kod_to = pociag.get("stacjaPrzyjazdu")
                    kategoria_pociagu = pociag.get("kategoriaPociagu")
                    if not train_number or not dep_dt_str or not arr_dt_str:
                        continue
                    if kod_from is None or kod_to is None:
                        continue

                    kod_from_int = int(kod_from)
                    kod_to_int = int(kod_to)

                    # A segment is "domestic" when both endpoints are Polish
                    # stations (present in the kod→EVA map). Foreign stations
                    # come back as full EVAs that aren't in the Polish stations
                    # list, and sprawdzCene (international, EUR) is the right
                    # endpoint for those. Domestic segments must go through
                    # sprawdzCenyLite (PLN); sprawdzCene rejects them with
                    # "Presale period for the operator exceeded".
                    is_domestic = (
                        kod_from_int in kod_to_eva and kod_to_int in kod_to_eva
                    )
                    station_from_eva = kod_to_eva.get(kod_from_int, kod_from_int)
                    station_to_eva = kod_to_eva.get(kod_to_int, kod_to_int)

                    try:
                        dep_time = datetime.strptime(dep_dt_str, "%Y-%m-%d %H:%M:%S")
                        arr_time = datetime.strptime(arr_dt_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        logger.warning(
                            f"Could not parse times for train {train_number} {date_str}. Skipping."
                        )
                        continue

                    route_id = (
                        f"{SOURCE}|{train_number}|{dep_city}|{arr_city}|"
                        f"{dep_time.isoformat()}"
                    )
                    if route_id in seen_routes:
                        continue
                    seen_routes.add(route_id)

                    logger.info(
                        f"Scraping IC.pl train {train_number} {date_str}: "
                        f"{dep_city} -> {arr_city} ({'domestic' if is_domestic else 'intl'})"
                    )

                    try:
                        if is_domestic:
                            price_res = _fetch_price_lite(
                                kod_from_int,
                                kod_to_int,
                                train_number,
                                dep_dt_str,
                                kategoria_pociagu,
                            )
                            min_seat, min_couchette = _parse_prices_lite(price_res)
                            currency = CURRENCY_PLN
                        else:
                            price_res = _fetch_price(
                                station_from_eva,
                                station_to_eva,
                                train_number,
                                dep_dt_str,
                            )
                            min_seat, min_couchette = _parse_prices(price_res)
                            currency = CURRENCY_EUR
                    except Exception as e:
                        total_failures += 1
                        if len(failures) < MAX_FAILURES_STORED:
                            failures.append(
                                ScrapeFailure(date_str, str(train_number), str(e))
                            )
                        time.sleep(1)
                        continue

                    route_obj = Route(
                        id=route_id,
                        source=SOURCE,
                        train_number=str(train_number),
                        departure_station=dep_city,
                        arrival_station=arr_city,
                        travel_date=dep_time.date(),
                        departure_time=dep_time,
                        arrival_time=arr_time,
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

                    availability: List[Tuple[bool, Optional[float], Optional[str]]] = [
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
