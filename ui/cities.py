from __future__ import annotations

from datetime import date, datetime
from urllib.parse import urlencode

EUROPEAN_SLEEPER = "europeansleeper"
NIGHTJET = "nightjet"
REGIOJET = "regiojet"

EUROPEAN_SLEEPER_BOOKING_URL = "https://booking.europeansleeper.eu/en"
NIGHTJET_BOOKING_URL = "https://shop.oebbtickets.at/en/ticket"
REGIOJET_BOOKING_URL = "https://regiojet.com/"


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
            NIGHTJET: {"city_id": "8596001", "name": "Basel"},
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
            NIGHTJET: {"city_id": "8096003", "name": "Berlin"},
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
            NIGHTJET: {"city_id": "8081996", "name": "Bonn"},
        },
    },
    "bratislava": {
        "name": "Bratislava",
        "station_names": [
            "Bratislava hl.st.",
        ],
        "providers": {
            NIGHTJET: {"city_id": "5696001", "name": "Bratislava"},
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
            NIGHTJET: {"city_id": "5596001", "name": "Budapest"},
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
            NIGHTJET: {"city_id": "8396001", "name": "Florence"},
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
            NIGHTJET: {"city_id": "8096021", "name": "Frankfurt (Main)"},
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
            NIGHTJET: {"city_id": "8096009", "name": "Hamburg"},
        },
    },
    "krakow": {
        "name": "Krakow",
        "station_names": [
            "Krakow Glowny",
            "Krakow Plaszow",
            "Cracow",
        ],
        "providers": {
            NIGHTJET: {"city_id": "5196001", "name": "Krakow"},
            REGIOJET: {"city_id": "1225791000"},
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
            NIGHTJET: {"city_id": "8081998", "name": "Munich"},
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
            "Prague",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "5457076"},
            NIGHTJET: {"city_id": "5496001", "name": "Prague"},
            REGIOJET: {"city_id": "10202003"},
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
            NIGHTJET: {"city_id": "8396004", "name": "Rome"},
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
            NIGHTJET: {"city_id": "1150101", "name": "Salzburg"},
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
            NIGHTJET: {"city_id": "8396008", "name": "Venice"},
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
            NIGHTJET: {"city_id": "1190100", "name": "Vienna"},
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
            NIGHTJET: {"city_id": "5196003", "name": "Warsaw"},
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
            NIGHTJET: {"city_id": "7896001", "name": "Zagreb"},
        },
    },
    "zurich": {
        "name": "Zurich",
        "station_names": [
            "Zurich HB",
            "Zürich HB",
        ],
        "providers": {
            NIGHTJET: {"city_id": "8596008", "name": "Zurich"},
        },
    },
    "bohumin": {
        "name": "Bohumín",
        "station_names": [
            "Bohumín",
        ],
        "providers": {
            REGIOJET: {"city_id": "2147875000"},
        },
    },
    "bystrice_trinec": {
        "name": "Bystřice (Třinec)",
        "station_names": [
            "Bystřice (Třinec)",
        ],
        "providers": {
            REGIOJET: {"city_id": "1313136001"},
        },
    },
    "cadca": {
        "name": "Čadca",
        "station_names": [
            "Čadca",
        ],
        "providers": {
            REGIOJET: {"city_id": "508808002"},
        },
    },
    "ceska_trebova": {
        "name": "Česká Třebová",
        "station_names": [
            "Česká Třebová",
        ],
        "providers": {
            REGIOJET: {"city_id": "1313136000"},
        },
    },
    "cesky_tesin": {
        "name": "Český Těšín",
        "station_names": [
            "Český Těšín",
        ],
        "providers": {
            REGIOJET: {"city_id": "508808000"},
        },
    },
    "chop": {
        "name": "Chop",
        "station_names": [
            "Chop",
        ],
        "providers": {
            REGIOJET: {"city_id": "7122881001"},
        },
    },
    "havirov": {
        "name": "Havířov",
        "station_names": [
            "Havířov",
        ],
        "providers": {
            REGIOJET: {"city_id": "372842004"},
        },
    },
    "hranice_na_morave": {
        "name": "Hranice na Moravě",
        "station_names": [
            "Hranice na M.",
        ],
        "providers": {
            REGIOJET: {"city_id": "372842003"},
        },
    },
    "kosice": {
        "name": "Košice",
        "station_names": [
            "Košice",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202033"},
        },
    },
    "kysak": {
        "name": "Kysak (Prešov)",
        "station_names": [
            "Kysak (u města Prešov)",
        ],
        "providers": {
            REGIOJET: {"city_id": "1762994001"},
        },
    },
    "liptovsky_mikulas": {
        "name": "Liptovský Mikuláš",
        "station_names": [
            "Liptovský Mikuláš",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202036"},
        },
    },
    "margecany": {
        "name": "Margecany",
        "station_names": [
            "Margecany",
        ],
        "providers": {
            REGIOJET: {"city_id": "2317706000"},
        },
    },
    "navsi": {
        "name": "Návsí (Jablunkov)",
        "station_names": [
            "Návsí (Jablunkov)",
        ],
        "providers": {
            REGIOJET: {"city_id": "1558067000"},
        },
    },
    "olomouc": {
        "name": "Olomouc",
        "station_names": [
            "Olomouc",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202031"},
        },
    },
    "opava": {
        "name": "Opava východ",
        "station_names": [
            "Opava východ",
        ],
        "providers": {
            REGIOJET: {"city_id": "3741270000"},
        },
    },
    "ostrava": {
        "name": "Ostrava",
        "station_names": [
            "Ostrava",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202000"},
        },
    },
    "pardubice": {
        "name": "Pardubice",
        "station_names": [
            "Pardubice",
        ],
        "providers": {
            REGIOJET: {"city_id": "372842000"},
        },
    },
    "poprad": {
        "name": "Poprad",
        "station_names": [
            "Poprad",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202035"},
        },
    },
    "premysl": {
        "name": "Přemyšl",
        "station_names": [
            "Přemyšl",
        ],
        "providers": {
            REGIOJET: {"city_id": "5990055004"},
        },
    },
    "resov": {
        "name": "Řešov",
        "station_names": [
            "Řešov",
        ],
        "providers": {
            REGIOJET: {"city_id": "5990055007"},
        },
    },
    "ruzomberok": {
        "name": "Ružomberok",
        "station_names": [
            "Ružomberok",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202037"},
        },
    },
    "spisska_nova_ves": {
        "name": "Spišská Nová Ves",
        "station_names": [
            "Spišská Nová Ves",
        ],
        "providers": {
            REGIOJET: {"city_id": "1762994000"},
        },
    },
    "strba": {
        "name": "Štrba",
        "station_names": [
            "Štrba",
        ],
        "providers": {
            REGIOJET: {"city_id": "49584002"},
        },
    },
    "trinec": {
        "name": "Třinec centrum",
        "station_names": [
            "Třinec centrum",
        ],
        "providers": {
            REGIOJET: {"city_id": "508808001"},
        },
    },
    "vrutky": {
        "name": "Vrútky",
        "station_names": [
            "Vrútky",
        ],
        "providers": {
            REGIOJET: {"city_id": "49584000"},
        },
    },
    "zabrezh_na_morave": {
        "name": "Zábřeh na Moravě",
        "station_names": [
            "Zábřeh na Moravě",
        ],
        "providers": {
            REGIOJET: {"city_id": "372842002"},
        },
    },
    "zilina": {
        "name": "Žilina",
        "station_names": [
            "Žilina",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202038"},
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
    "cadca": ["bohumin", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "chop": ["bohumin", "cadca", "ceska_trebova", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "decin": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "berlin", "brussels", "deventer", "dresden", "roosendaal", "rotterdam", "the_hague"],
    "deventer": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "dresden": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "berlin", "brussels", "decin", "deventer", "prague", "roosendaal", "rotterdam", "the_hague", "usti_nad_labem"],
    "florence": ["munich", "rome", "salzburg", "vienna"],
    "frankfurt_main": ["basel", "berlin", "bonn", "hamburg", "prague", "zurich"],
    "hamburg": ["basel", "frankfurt_main", "munich", "salzburg", "vienna", "zurich"],
    "havirov": ["cadca", "ceska_trebova", "chop", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "kosice": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "krakow": ["munich", "olomouc", "ostrava", "pardubice", "prague", "premysl", "resov", "salzburg", "vienna"],
    "kysak": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "liptovsky_mikulas": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "margecany": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "olomouc", "opava", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "munich": ["bonn", "budapest", "florence", "hamburg", "krakow", "rome", "salzburg", "venice", "vienna", "warsaw", "zagreb"],
    "olomouc": ["cadca", "chop", "havirov", "kosice", "krakow", "kysak", "liptovsky_mikulas", "margecany", "ostrava", "pardubice", "poprad", "prague", "premysl", "resov", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zilina"],
    "ostrava": ["cadca", "chop", "havirov", "kosice", "krakow", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "pardubice", "poprad", "prague", "premysl", "resov", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zilina"],
    "pardubice": ["cadca", "chop", "havirov", "kosice", "krakow", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "poprad", "prague", "premysl", "resov", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zilina"],
    "paris": ["berlin", "brussels"],
    "poprad": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "prague": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "basel", "berlin", "bratislava", "brussels", "budapest", "cadca", "chop", "deventer", "dresden", "frankfurt_main", "havirov", "kosice", "krakow", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "premysl", "resov", "roosendaal", "rotterdam", "ruzomberok", "spisska_nova_ves", "strba", "the_hague", "vienna", "vrutky", "zilina", "zurich"],
    "premysl": ["krakow", "olomouc", "ostrava", "pardubice", "prague", "resov"],
    "resov": ["krakow", "olomouc", "ostrava", "pardubice", "prague", "premysl"],
    "rome": ["florence", "munich", "salzburg", "vienna"],
    "roosendaal": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "rotterdam": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "ruzomberok": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "salzburg": ["bonn", "budapest", "florence", "hamburg", "krakow", "munich", "rome", "venice", "vienna", "warsaw", "zagreb", "zurich"],
    "spisska_nova_ves": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "strba": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "prague", "ruzomberok", "spisska_nova_ves", "vrutky", "zabrezh_na_morave", "zilina"],
    "the_hague": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "usti_nad_labem": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "berlin", "brussels", "deventer", "dresden", "roosendaal", "rotterdam", "the_hague"],
    "venice": ["munich", "salzburg", "vienna"],
    "vienna": ["berlin", "bonn", "budapest", "florence", "hamburg", "krakow", "munich", "prague", "rome", "salzburg", "venice", "warsaw", "zagreb", "zurich"],
    "vrutky": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "zabrezh_na_morave", "zilina"],
    "warsaw": ["munich", "salzburg", "vienna"],
    "zagreb": ["munich", "salzburg", "vienna", "zurich"],
    "zilina": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave"],
    "zurich": ["basel", "berlin", "bonn", "budapest", "frankfurt_main", "hamburg", "prague", "salzburg", "vienna", "zagreb"],
}

PROVIDER_ROUTES = {
    EUROPEAN_SLEEPER: [
        {
            "name": "Brussels — Prague",
            "trains": "453 / 452",
            "stops": [
                "brussels", "antwerp", "roosendaal", "rotterdam", "the_hague",
                "amsterdam", "amersfoort", "deventer", "berlin", "dresden",
                "bad_schandau", "decin", "usti_nad_labem", "prague",
            ],
        },
        {
            "name": "Paris — Berlin",
            "trains": "475 / 474",
            "stops": ["paris", "brussels", "hamburg", "berlin"],
        },
    ],
    NIGHTJET: [
        {
            "name": "Vienna — Zurich",
            "trains": "NJ 466 / 467",
            "stops": ["vienna", "salzburg", "zurich"],
        },
        {
            "name": "Vienna — Prague — Berlin",
            "trains": "NJ 456 / 457",
            "stops": ["vienna", "prague", "berlin"],
        },
        {
            "name": "Vienna — Munich — Bonn",
            "trains": "NJ 468 / 469",
            "stops": ["vienna", "salzburg", "munich", "bonn"],
        },
        {
            "name": "Vienna — Munich — Hamburg",
            "trains": "NJ 492 / 493",
            "stops": ["vienna", "salzburg", "munich", "hamburg"],
        },
        {
            "name": "Vienna — Venice",
            "trains": "NJ 40466 / 40236",
            "stops": ["vienna", "salzburg", "venice"],
        },
        {
            "name": "Vienna — Florence — Rome",
            "trains": "NJ 40233 / 40294",
            "stops": ["vienna", "florence", "rome"],
        },
        {
            "name": "Vienna — Zagreb",
            "trains": "EN 1272 / 1273",
            "stops": ["vienna", "zagreb"],
        },
        {
            "name": "Munich — Venice",
            "trains": "NJ 237 / 236",
            "stops": ["munich", "salzburg", "venice"],
        },
        {
            "name": "Munich — Florence — Rome",
            "trains": "NJ 294 / 295",
            "stops": ["rome", "florence", "salzburg", "munich"],
        },
        {
            "name": "Munich — Hamburg",
            "trains": "NJ 40420 / 40491",
            "stops": ["munich", "hamburg"],
        },
        {
            "name": "Munich — Vienna — Warsaw",
            "trains": "EN 40406 / 40407",
            "stops": ["munich", "salzburg", "vienna", "warsaw"],
        },
        {
            "name": "Munich — Vienna — Krakow",
            "trains": "EN 40416 / 40417",
            "stops": ["munich", "salzburg", "vienna", "krakow"],
        },
        {
            "name": "Munich — Vienna — Budapest",
            "trains": "EN 50237 / 50462",
            "stops": ["munich", "salzburg", "vienna", "budapest"],
        },
        {
            "name": "Berlin — Prague — Budapest",
            "trains": "EN 40457 / 40476",
            "stops": ["berlin", "prague", "bratislava", "budapest"],
        },
        {
            "name": "Budapest — Vienna — Zurich",
            "trains": "EN 40462 / 40467",
            "stops": ["budapest", "vienna", "salzburg", "zurich"],
        },
        {
            "name": "Zurich — Basel — Frankfurt — Hamburg",
            "trains": "NJ 470 / 471",
            "stops": ["zurich", "basel", "frankfurt_main", "hamburg"],
        },
        {
            "name": "Zurich — Basel — Frankfurt — Bonn",
            "trains": "NJ 402 / 403",
            "stops": ["zurich", "basel", "frankfurt_main", "bonn"],
        },
        {
            "name": "Berlin — Frankfurt — Basel — Zurich",
            "trains": "NJ 408 / 409",
            "stops": ["berlin", "frankfurt_main", "basel", "zurich"],
        },
        {
            "name": "Prague — Frankfurt — Basel — Zurich",
            "trains": "EN 40458 / 40459",
            "stops": ["prague", "frankfurt_main", "basel", "zurich"],
        },
        {
            "name": "Zurich — Salzburg — Zagreb",
            "trains": "EN 40465 / 40414",
            "stops": ["zurich", "salzburg", "zagreb"],
        },
    ],
    REGIOJET: [
        {
            "name": "Prague — Chop",
            "trains": "RJ 1020 / 1021",
            "stops": [
                "prague", "pardubice", "ceska_trebova", "zabrezh_na_morave",
                "olomouc", "hranice_na_morave", "opava", "bohumin", "ostrava",
                "havirov", "cesky_tesin", "trinec", "bystrice_trinec", "navsi",
                "cadca", "zilina", "vrutky", "ruzomberok", "liptovsky_mikulas",
                "strba", "poprad", "spisska_nova_ves", "margecany", "kysak",
                "kosice", "chop",
            ],
        },
        {
            "name": "Prague — Przemysl",
            "trains": "RJ 1022 / 1023",
            "stops": [
                "prague", "pardubice", "olomouc", "ostrava", "krakow",
                "resov", "premysl",
            ],
        },
    ],
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
    REGIOJET: "RegioJet",
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

    if source == REGIOJET:
        start_rj = start_city.get("providers", {}).get(REGIOJET, {})
        end_rj = end_city.get("providers", {}).get(REGIOJET, {})
        start_city_id_rj = start_rj.get("city_id")
        end_city_id_rj = end_rj.get("city_id")
        if not start_city_id_rj or not end_city_id_rj:
            return None
        params = {
            "departureDate": departure_date.strftime("%Y-%m-%d"),
            "tariffs": "REGULAR",
            "fromLocationId": start_city_id_rj,
            "fromLocationType": "CITY",
            "toLocationId": end_city_id_rj,
            "toLocationType": "CITY",
        }
        if return_date is not None:
            params["returnDepartureDate"] = return_date.strftime("%Y-%m-%d")
        return f"{REGIOJET_BOOKING_URL}?{urlencode(params)}"

    if source == NIGHTJET:
        start_name = (
            start_city.get("providers", {})
            .get(NIGHTJET, {})
            .get("name")
        )
        end_name = (
            end_city.get("providers", {})
            .get(NIGHTJET, {})
            .get("name")
        )
        if not start_name or not end_name:
            return None

        outward_datetime = (
            departure_time.strftime("%Y-%m-%dT%H:%M")
            if departure_time is not None
            else departure_date.strftime("%Y-%m-%dT00:00")
        )
        query_string = urlencode(
            {
                "outwardDateTime": outward_datetime,
                "stationOrigName": start_name,
                "stationDestName": end_name,
                "cref": "trainbot",
                "connectionFilterDirect": "true",
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
