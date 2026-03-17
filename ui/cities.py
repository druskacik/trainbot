from __future__ import annotations

from datetime import date, datetime
from urllib.parse import urlencode

EUROPEAN_SLEEPER = "europeansleeper"
NIGHTJET = "nightjet"

EUROPEAN_SLEEPER_BOOKING_URL = "https://booking.europeansleeper.eu/en"
NIGHTJET_BOOKING_URL = "https://shop.oebbtickets.at/en/ticket"


CITY_CATALOG = {
    "amsterdam": {
        "name": "Amsterdam",
        "station_names": [
            "Amsterdam Centraal",
            "Amsterdam CS",
            "Amsterdam Bijlmer Arena",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8400058"},
        },
    },
    "amersfoort": {
        "name": "Amersfoort",
        "station_names": [
            "Amersfoort",
            "Amersfoort Centraal",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8400055"},
        },
    },
    "antwerp": {
        "name": "Antwerp",
        "station_names": [
            "Antwerpen Centraal",
            "Antwerpen-Centraal",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8800210"},
        },
    },
    "bad_schandau": {
        "name": "Bad Schandau",
        "station_names": [
            "Bad Schandau",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8001311"},
        },
    },
    "basel": {
        "name": "Basel",
        "station_names": [
            "Basel SBB",
            "Basel Bad Station",
        ],
        "providers": {
            NIGHTJET: {"city_id": "8596001"},
        },
    },
    "berlin": {
        "name": "Berlin",
        "station_names": [
            "Berlin Hbf",
            "Berlin Central Station",
            "Berlin Hbf (tief)",
            "Berlin Hbf (Tiefgeschoß)",
            "Berlin Hbf (Tiefgeschoss)",
            "Berlin-Gesundbrunnen",
            "Berlin Gesundbrunnen",
            "Berlin Ost",
            "Berlin Ostbahnhof",
            "Berlin Ostbahnnhof",
            "Berlin Südkreuz",
            "Berlin Sudkreuz",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8010100"},
            NIGHTJET: {"city_id": "8096003"},
        },
    },
    "bonn": {
        "name": "Bonn",
        "station_names": [
            "Bonn Central Station",
            "Bonn-Beuel",
            "Bonn Hbf",
        ],
        "providers": {
            NIGHTJET: {"city_id": "8081996"},
        },
    },
    "bratislava": {
        "name": "Bratislava",
        "station_names": [
            "Bratislava hl.st.",
        ],
        "providers": {
            NIGHTJET: {"city_id": "5696001"},
        },
    },
    "brussels": {
        "name": "Brussels",
        "station_names": [
            "Bruxelles Midi",
            "Bruxelles Midi/Brussel Zuid",
            "Brussels Midi",
            "Brussels-North",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8800104"},
        },
    },
    "budapest": {
        "name": "Budapest",
        "station_names": [
            "Budapest-Keleti",
            "Budapest-Nyugati",
        ],
        "providers": {
            NIGHTJET: {"city_id": "5596001"},
        },
    },
    "decin": {
        "name": "Decin",
        "station_names": [
            "Děčín hl.n.",
            "DECIN",
            "Decin hl.n.",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "5455659"},
        },
    },
    "deventer": {
        "name": "Deventer",
        "station_names": [
            "Deventer",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8400173"},
        },
    },
    "dresden": {
        "name": "Dresden",
        "station_names": [
            "Dresden Hbf",
            "Dresden Central Station",
            "Dresden-Neustadt",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8001305"},
        },
    },
    "florence": {
        "name": "Florence",
        "station_names": [
            "Florence Campo di Marte",
            "Firenze Campo di Marte",
        ],
        "providers": {
            NIGHTJET: {"city_id": "8396001"},
        },
    },
    "frankfurt_main": {
        "name": "Frankfurt (Main)",
        "station_names": [
            "Frankfurt(Main)Hbf",
            "Frankfurt (Main) Hbf",
            "Frankfurt(M) Airport Station",
            "Frankfurt (Main) South",
            "Frankfurt(Main)Süd",
            "Frankfurt(M) Flughafen Fernbf",
        ],
        "providers": {
            NIGHTJET: {"city_id": "8096021"},
        },
    },
    "hamburg": {
        "name": "Hamburg",
        "station_names": [
            "Hamburg Harburg",
            "Hamburg-Harburg",
            "Hamburg Central Station",
            "Hamburg Dammtor",
            "Hamburg-Altona",
            "Hamburg Hbf",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8020401"},
            NIGHTJET: {"city_id": "8096009"},
        },
    },
    "krakow": {
        "name": "Krakow",
        "station_names": [
            "Krakow Glowny",
            "Krakow Plaszow",
        ],
        "providers": {
            NIGHTJET: {"city_id": "5196001"},
        },
    },
    "munich": {
        "name": "Munich",
        "station_names": [
            "Munich Central Station",
            "Munich East",
            "München-Pasing",
            "München Hbf",
            "München Ost",
        ],
        "providers": {
            NIGHTJET: {"city_id": "8081998"},
        },
    },
    "paris": {
        "name": "Paris",
        "station_names": [
            "Paris-Nord",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8700015"},
        },
    },
    "prague": {
        "name": "Prague",
        "station_names": [
            "PRAHA HL. N.",
            "Praha hl.n.",
            "Praha hl.n. (main station)",
            "Prague Main Station",
            "Prague-Holesovice",
            "Praha-Holesovice",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "5457076"},
            NIGHTJET: {"city_id": "5496001"},
        },
    },
    "rome": {
        "name": "Rome",
        "station_names": [
            "Roma Tiburtina",
            "Rome Tiburtina",
            "Roma Termini",
            "Rome Termini",
        ],
        "providers": {
            NIGHTJET: {"city_id": "8396004"},
        },
    },
    "roosendaal": {
        "name": "Roosendaal",
        "station_names": [
            "Roosendaal",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8400526"},
        },
    },
    "rotterdam": {
        "name": "Rotterdam",
        "station_names": [
            "Rotterdam CS",
            "Rotterdam Centraal",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8400530"},
        },
    },
    "salzburg": {
        "name": "Salzburg",
        "station_names": [
            "Salzburg Central Station",
            "Salzburg South Station",
            "Salzburg Hbf",
            "Salzburg Süd Bahnhst",
        ],
        "providers": {
            NIGHTJET: {"city_id": "1150101"},
        },
    },
    "the_hague": {
        "name": "The Hague",
        "station_names": [
            "Den Haag HS",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8400280"},
        },
    },
    "usti_nad_labem": {
        "name": "Usti nad Labem",
        "station_names": [
            "Ústí nad Labem hl.n.",
            "USTI NAD LABEM",
            "Usti nad Labem hl.n.",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "5453179"},
        },
    },
    "venice": {
        "name": "Venice",
        "station_names": [
            "Venice Santa Lucia",
            "Venice Mestre",
            "Venezia Santa Lucia",
        ],
        "providers": {
            NIGHTJET: {"city_id": "8396008"},
        },
    },
    "vienna": {
        "name": "Vienna",
        "station_names": [
            "Vienna Central Station",
            "Wien Central Station (car transport)",
            "Wien Meidling Station",
            "Wien Hbf (Bahnsteige 3-12)",
        ],
        "providers": {
            NIGHTJET: {"city_id": "1190100"},
        },
    },
    "warsaw": {
        "name": "Warsaw",
        "station_names": [
            "Warsaw Central Station",
            "Warsaw Wschodnia",
            "Warsaw Zachodnia",
            "Warszawa Centralna",
        ],
        "providers": {
            NIGHTJET: {"city_id": "5196003"},
        },
    },
    "zagreb": {
        "name": "Zagreb",
        "station_names": [
            "Zagreb Glavni Kolod.",
            "Zagreb Zapadni kolodvor",
            "Zagreb Glavni kolodvor",
        ],
        "providers": {
            NIGHTJET: {"city_id": "7896001"},
        },
    },
    "zurich": {
        "name": "Zurich",
        "station_names": [
            "Zurich HB",
            "Zürich HB",
        ],
        "providers": {
            NIGHTJET: {"city_id": "8596008"},
        },
    },
}

CITY_CONNECTIONS = {
    "amersfoort": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "amsterdam": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "antwerp": ["amersfoort", "amsterdam", "bad_schandau", "berlin", "decin", "deventer", "dresden", "prague", "roosendaal", "rotterdam", "the_hague", "usti_nad_labem"],
    "bad_schandau": ["amersfoort", "amsterdam", "antwerp", "berlin", "brussels", "decin", "deventer", "dresden", "prague", "roosendaal", "rotterdam", "the_hague", "usti_nad_labem"],
    "basel": ["berlin", "bonn", "frankfurt_main", "hamburg", "prague", "zurich"],
    "berlin": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "basel", "bratislava", "brussels", "budapest", "decin", "deventer", "dresden", "frankfurt_main", "paris", "prague", "roosendaal", "rotterdam", "the_hague", "usti_nad_labem", "vienna", "zurich"],
    "bonn": ["basel", "frankfurt_main", "munich", "salzburg", "vienna", "zurich"],
    "bratislava": ["berlin", "budapest", "prague"],
    "brussels": ["amersfoort", "amsterdam", "bad_schandau", "berlin", "decin", "deventer", "dresden", "paris", "prague", "roosendaal", "rotterdam", "the_hague", "usti_nad_labem"],
    "budapest": ["berlin", "bratislava", "munich", "prague", "salzburg", "vienna", "zurich"],
    "decin": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "berlin", "brussels", "deventer", "dresden", "roosendaal", "rotterdam", "the_hague"],
    "deventer": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "dresden": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "berlin", "brussels", "decin", "deventer", "prague", "roosendaal", "rotterdam", "the_hague", "usti_nad_labem"],
    "florence": ["munich", "rome", "salzburg", "vienna"],
    "frankfurt_main": ["basel", "berlin", "bonn", "hamburg", "prague", "zurich"],
    "hamburg": ["basel", "frankfurt_main", "munich", "salzburg", "vienna", "zurich"],
    "krakow": ["munich", "salzburg", "vienna"],
    "munich": ["bonn", "budapest", "florence", "hamburg", "krakow", "rome", "salzburg", "venice", "vienna", "warsaw", "zagreb"],
    "paris": ["berlin", "brussels"],
    "prague": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "basel", "berlin", "bratislava", "brussels", "budapest", "deventer", "dresden", "frankfurt_main", "roosendaal", "rotterdam", "the_hague", "vienna", "zurich"],
    "rome": ["florence", "munich", "salzburg", "vienna"],
    "roosendaal": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "rotterdam": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "salzburg": ["bonn", "budapest", "florence", "hamburg", "krakow", "munich", "rome", "venice", "vienna", "warsaw", "zagreb", "zurich"],
    "the_hague": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "usti_nad_labem": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "berlin", "brussels", "deventer", "dresden", "roosendaal", "rotterdam", "the_hague"],
    "venice": ["munich", "salzburg", "vienna"],
    "vienna": ["berlin", "bonn", "budapest", "florence", "hamburg", "krakow", "munich", "prague", "rome", "salzburg", "venice", "warsaw", "zagreb", "zurich"],
    "warsaw": ["munich", "salzburg", "vienna"],
    "zagreb": ["munich", "salzburg", "vienna", "zurich"],
    "zurich": ["basel", "berlin", "bonn", "budapest", "frankfurt_main", "hamburg", "prague", "salzburg", "vienna", "zagreb"],
}

POPULAR_CITY_IDS = [
    "prague",
    "amsterdam",
    "brussels",
    "berlin",
    "paris",
    "vienna",
]
DEFAULT_START_CITY_ID = "prague"
DEFAULT_END_CITY_ID = "amsterdam"

PROVIDER_DISPLAY_NAMES = {
    EUROPEAN_SLEEPER: "European Sleeper",
    NIGHTJET: "NightJet",
}


def get_city(city_id: str) -> dict | None:
    return CITY_CATALOG.get(city_id)


def get_city_options() -> list[dict]:
    return [
        {"id": city_id, "name": city["name"]}
        for city_id, city in sorted(
            CITY_CATALOG.items(),
            key=lambda item: item[1]["name"],
        )
    ]


def get_station_names(city_id: str) -> list[str]:
    city = get_city(city_id)
    if not city:
        return []

    seen = set()
    names = []
    for station_name in city["station_names"]:
        if station_name not in seen:
            names.append(station_name)
            seen.add(station_name)
    return names


def get_provider_display_name(source: str) -> str:
    return PROVIDER_DISPLAY_NAMES.get(source, source.replace("_", " ").title())


def build_booking_url(
    source: str,
    start_city_id: str,
    end_city_id: str,
    departure_date: date,
    departure_time: datetime | None = None,
    return_date: date | None = None,
) -> str | None:
    start_city = get_city(start_city_id)
    end_city = get_city(end_city_id)
    if not start_city or not end_city:
        return None

    if source == NIGHTJET:
        start_station_id = (
            start_city.get("providers", {})
            .get(NIGHTJET, {})
            .get("city_id")
        )
        end_station_id = (
            end_city.get("providers", {})
            .get(NIGHTJET, {})
            .get("city_id")
        )
        if not start_station_id or not end_station_id:
            return None

        outward_datetime = (
            departure_time.strftime("%Y-%m-%dT%H:%M")
            if departure_time is not None
            else departure_date.strftime("%Y-%m-%dT00:00")
        )
        query_string = urlencode(
            {
                "cref": "scotty",
                "outwardDateTime": outward_datetime,
                "stationOrigEva": start_station_id,
                "stationDestEva": end_station_id,
            }
        )
        return f"{NIGHTJET_BOOKING_URL}?{query_string}"

    if source != EUROPEAN_SLEEPER:
        return None

    start_station_id = (
        start_city.get("providers", {})
        .get(EUROPEAN_SLEEPER, {})
        .get("station_id")
    )
    end_station_id = (
        end_city.get("providers", {})
        .get(EUROPEAN_SLEEPER, {})
        .get("station_id")
    )
    if not start_station_id or not end_station_id:
        return None

    query_parts = [
        f"departureStation={start_station_id}",
        f"arrivalStation={end_station_id}",
        f"departureDate={departure_date.strftime('%Y-%m-%d')}",
        "bicycleCount=0",
        "petsCount=0",
        "passengerTypes=72",
    ]
    if return_date is not None:
        query_parts.insert(3, f"returnDate={return_date.strftime('%Y-%m-%d')}")

    return f"{EUROPEAN_SLEEPER_BOOKING_URL}?{'&'.join(query_parts)}"
