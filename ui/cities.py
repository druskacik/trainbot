from __future__ import annotations

from datetime import date, datetime
from urllib.parse import urlencode

EUROPEAN_SLEEPER = "europeansleeper"
NIGHTJET = "nightjet"
REGIOJET = "regiojet"
INTERCITY_PL = "intercity_pl"

EUROPEAN_SLEEPER_BOOKING_URL = "https://booking.europeansleeper.eu/en"
NIGHTJET_BOOKING_URL = "https://shop.oebbtickets.at/en/ticket"
REGIOJET_BOOKING_URL = "https://regiojet.com/"
INTERCITY_PL_BOOKING_URL = "https://ebilet.intercity.pl"


CITY_CATALOG = {
    "amsterdam": {
        "name": "Amsterdam",
        "country": "NL",
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
        "country": "NL",
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
        "country": "BE",
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
        "country": "DE",
        "station_names": [
            "Bad Schandau",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8001311"},
        },
    },
    "basel": {
        "name": "Basel",
        "country": "CH",
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
        "country": "DE",
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
        "country": "DE",
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
        "country": "SK",
        "station_names": [
            "Bratislava",
            "Bratislava hl.st.",
        ],
        "providers": {
            NIGHTJET: {"city_id": "5696001", "name": "Bratislava"},
            INTERCITY_PL: {"eva": "5600207"},
        },
    },
    "brussels": {
        "name": "Brussels",
        "country": "BE",
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
        "country": "HU",
        "station_names": [
            "Budapest",
            "Budapest-Keleti",
            "Budapest-Nyugati",
        ],
        "providers": {
            NIGHTJET: {"city_id": "5596001", "name": "Budapest"},
            INTERCITY_PL: {"eva": "5596001"},
        },
    },
    "decin": {
        "name": "Decin",
        "country": "CZ",
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
        "country": "NL",
        "station_names": [
            "Deventer",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8400173"},
        },
    },
    "dresden": {
        "name": "Dresden",
        "country": "DE",
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
        "country": "IT",
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
        "country": "DE",
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
        "country": "DE",
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
        "country": "PL",
        "station_names": [
            "Krakow Glowny",
            "Krakow Plaszow",
            "Cracow",
        ],
        "providers": {
            NIGHTJET: {"city_id": "5196001", "name": "Krakow"},
            REGIOJET: {"city_id": "1225791000"},
            INTERCITY_PL: {"eva": "5196001"},
        },
    },
    "munich": {
        "name": "Munich",
        "country": "DE",
        "station_names": [
            "Munich",
            "Munich Central Station",
            "Munich East",
            "München-Pasing",
            "München Hbf",
            "München Ost",
        ],
        "providers": {
            NIGHTJET: {"city_id": "8081998", "name": "Munich"},
            INTERCITY_PL: {"eva": "8000261"},
        },
    },
    "paris": {
        "name": "Paris",
        "country": "FR",
        "station_names": [
            "Paris-Nord",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8700015"},
        },
    },
    "prague": {
        "name": "Prague",
        "country": "CZ",
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
            INTERCITY_PL: {"eva": "5496001"},
        },
    },
    "rome": {
        "name": "Rome",
        "country": "IT",
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
        "country": "NL",
        "station_names": [
            "Roosendaal",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8400526"},
        },
    },
    "rotterdam": {
        "name": "Rotterdam",
        "country": "NL",
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
        "country": "AT",
        "station_names": [
            "Salzburg",
            "Salzburg Central Station",
            "Salzburg South Station",
            "Salzburg Hbf",
            "Salzburg Süd Bahnhst",
        ],
        "providers": {
            NIGHTJET: {"city_id": "1150101", "name": "Salzburg"},
            INTERCITY_PL: {"eva": "8100002"},
        },
    },
    "the_hague": {
        "name": "The Hague",
        "country": "NL",
        "station_names": [
            "Den Haag HS",
        ],
        "providers": {
            EUROPEAN_SLEEPER: {"station_id": "8400280"},
        },
    },
    "usti_nad_labem": {
        "name": "Usti nad Labem",
        "country": "CZ",
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
        "country": "IT",
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
        "country": "AT",
        "station_names": [
            "Vienna",
            "Vienna Central Station",
            "Wien Central Station (car transport)",
            "Wien Meidling Station",
            "Wien Hbf (Bahnsteige 3-12)",
        ],
        "providers": {
            NIGHTJET: {"city_id": "1190100", "name": "Vienna"},
            INTERCITY_PL: {"eva": "8196001"},
        },
    },
    "warsaw": {
        "name": "Warsaw",
        "country": "PL",
        "station_names": [
            "Warsaw",
            "Warsaw Central Station",
            "Warsaw Wschodnia",
            "Warsaw Zachodnia",
            "Warszawa Centralna",
        ],
        "providers": {
            NIGHTJET: {"city_id": "5196003", "name": "Warsaw"},
            INTERCITY_PL: {"eva": "5196003"},
        },
    },
    "zagreb": {
        "name": "Zagreb",
        "country": "HR",
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
        "country": "CH",
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
        "country": "CZ",
        "station_names": [
            "Bohumín",
            "Bohumin",
        ],
        "providers": {
            REGIOJET: {"city_id": "2147875000"},
            INTERCITY_PL: {"eva": "5400038"},
        },
    },
    "bystrice_trinec": {
        "name": "Bystřice (Třinec)",
        "country": "CZ",
        "station_names": [
            "Bystřice (Třinec)",
        ],
        "providers": {
            REGIOJET: {"city_id": "1313136001"},
        },
    },
    "cadca": {
        "name": "Čadca",
        "country": "SK",
        "station_names": [
            "Čadca",
        ],
        "providers": {
            REGIOJET: {"city_id": "508808002"},
        },
    },
    "ceska_trebova": {
        "name": "Česká Třebová",
        "country": "CZ",
        "station_names": [
            "Česká Třebová",
        ],
        "providers": {
            REGIOJET: {"city_id": "1313136000"},
        },
    },
    "cesky_tesin": {
        "name": "Český Těšín",
        "country": "CZ",
        "station_names": [
            "Český Těšín",
        ],
        "providers": {
            REGIOJET: {"city_id": "508808000"},
        },
    },
    "chop": {
        "name": "Chop",
        "country": "UA",
        "station_names": [
            "Chop",
        ],
        "providers": {
            REGIOJET: {"city_id": "7122881001"},
        },
    },
    "havirov": {
        "name": "Havířov",
        "country": "CZ",
        "station_names": [
            "Havířov",
        ],
        "providers": {
            REGIOJET: {"city_id": "372842004"},
        },
    },
    "hranice_na_morave": {
        "name": "Hranice na Moravě",
        "country": "CZ",
        "station_names": [
            "Hranice na M.",
        ],
        "providers": {
            REGIOJET: {"city_id": "372842003"},
        },
    },
    "kosice": {
        "name": "Košice",
        "country": "SK",
        "station_names": [
            "Košice",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202033"},
        },
    },
    "kysak": {
        "name": "Kysak (Prešov)",
        "country": "SK",
        "station_names": [
            "Kysak (u města Prešov)",
        ],
        "providers": {
            REGIOJET: {"city_id": "1762994001"},
        },
    },
    "liptovsky_mikulas": {
        "name": "Liptovský Mikuláš",
        "country": "SK",
        "station_names": [
            "Liptovský Mikuláš",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202036"},
        },
    },
    "margecany": {
        "name": "Margecany",
        "country": "SK",
        "station_names": [
            "Margecany",
        ],
        "providers": {
            REGIOJET: {"city_id": "2317706000"},
        },
    },
    "navsi": {
        "name": "Návsí (Jablunkov)",
        "country": "CZ",
        "station_names": [
            "Návsí (Jablunkov)",
        ],
        "providers": {
            REGIOJET: {"city_id": "1558067000"},
        },
    },
    "olomouc": {
        "name": "Olomouc",
        "country": "CZ",
        "station_names": [
            "Olomouc",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202031"},
        },
    },
    "opava": {
        "name": "Opava východ",
        "country": "CZ",
        "station_names": [
            "Opava východ",
        ],
        "providers": {
            REGIOJET: {"city_id": "3741270000"},
        },
    },
    "ostrava": {
        "name": "Ostrava",
        "country": "CZ",
        "station_names": [
            "Ostrava",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202000"},
            INTERCITY_PL: {"eva": "5400026"},
        },
    },
    "pardubice": {
        "name": "Pardubice",
        "country": "CZ",
        "station_names": [
            "Pardubice",
        ],
        "providers": {
            REGIOJET: {"city_id": "372842000"},
        },
    },
    "poprad": {
        "name": "Poprad",
        "country": "SK",
        "station_names": [
            "Poprad",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202035"},
        },
    },
    "premysl": {
        "name": "Przemyśl",
        "country": "PL",
        "station_names": [
            "Przemysl",
            "Přemyšl",
        ],
        "providers": {
            REGIOJET: {"city_id": "5990055004"},
            INTERCITY_PL: {"eva": "5196032"},
        },
    },
    "resov": {
        "name": "Řešov",
        "country": "PL",
        "station_names": [
            "Řešov",
        ],
        "providers": {
            REGIOJET: {"city_id": "5990055007"},
        },
    },
    "ruzomberok": {
        "name": "Ružomberok",
        "country": "SK",
        "station_names": [
            "Ružomberok",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202037"},
        },
    },
    "spisska_nova_ves": {
        "name": "Spišská Nová Ves",
        "country": "SK",
        "station_names": [
            "Spišská Nová Ves",
        ],
        "providers": {
            REGIOJET: {"city_id": "1762994000"},
        },
    },
    "strba": {
        "name": "Štrba",
        "country": "SK",
        "station_names": [
            "Štrba",
        ],
        "providers": {
            REGIOJET: {"city_id": "49584002"},
        },
    },
    "trinec": {
        "name": "Třinec centrum",
        "country": "CZ",
        "station_names": [
            "Třinec centrum",
        ],
        "providers": {
            REGIOJET: {"city_id": "508808001"},
        },
    },
    "vrutky": {
        "name": "Vrútky",
        "country": "SK",
        "station_names": [
            "Vrútky",
        ],
        "providers": {
            REGIOJET: {"city_id": "49584000"},
        },
    },
    "zabrezh_na_morave": {
        "name": "Zábřeh na Moravě",
        "country": "CZ",
        "station_names": [
            "Zábřeh na Moravě",
        ],
        "providers": {
            REGIOJET: {"city_id": "372842002"},
        },
    },
    "zilina": {
        "name": "Žilina",
        "country": "SK",
        "station_names": [
            "Žilina",
        ],
        "providers": {
            REGIOJET: {"city_id": "10202038"},
        },
    },
    "bielsko_biala": {
        "name": "Bielsko-Biała",
        "country": "PL",
        "station_names": ["Bielsko-Biala"],
        "providers": {
            INTERCITY_PL: {"eva": "5100316"},
        },
    },
    "bydgoszcz": {
        "name": "Bydgoszcz",
        "country": "PL",
        "station_names": ["Bydgoszcz"],
        "providers": {
            INTERCITY_PL: {"eva": "5100005"},
        },
    },
    "czestochowa": {
        "name": "Częstochowa",
        "country": "PL",
        "station_names": ["Czestochowa"],
        "providers": {
            INTERCITY_PL: {"eva": "5196005"},
        },
    },
    "gdansk": {
        "name": "Gdańsk",
        "country": "PL",
        "station_names": ["Gdansk"],
        "providers": {
            INTERCITY_PL: {"eva": "5100009"},
        },
    },
    "gdynia": {
        "name": "Gdynia",
        "country": "PL",
        "station_names": ["Gdynia"],
        "providers": {
            INTERCITY_PL: {"eva": "5100010"},
        },
    },
    "hel": {
        "name": "Hel",
        "country": "PL",
        "station_names": ["Hel"],
        "providers": {
            INTERCITY_PL: {"eva": "5101340"},
        },
    },
    "jelenia_gora": {
        "name": "Jelenia Góra",
        "country": "PL",
        "station_names": ["Jelenia Gora"],
        "providers": {
            INTERCITY_PL: {"eva": "5100259"},
        },
    },
    "katowice": {
        "name": "Katowice",
        "country": "PL",
        "station_names": ["Katowice"],
        "providers": {
            INTERCITY_PL: {"eva": "5196028"},
        },
    },
    "klodzko": {
        "name": "Kłodzko",
        "country": "PL",
        "station_names": ["Klodzko"],
        "providers": {
            INTERCITY_PL: {"eva": "5196183"},
        },
    },
    "kolobrzeg": {
        "name": "Kołobrzeg",
        "country": "PL",
        "station_names": ["Kolobrzeg"],
        "providers": {
            INTERCITY_PL: {"eva": "5100025"},
        },
    },
    "linz": {
        "name": "Linz",
        "country": "AT",
        "station_names": ["Linz"],
        "providers": {
            INTERCITY_PL: {"eva": "8100013"},
        },
    },
    "lublin": {
        "name": "Lublin",
        "country": "PL",
        "station_names": ["Lublin"],
        "providers": {
            INTERCITY_PL: {"eva": "5196030"},
        },
    },
    "rijeka": {
        "name": "Rijeka",
        "country": "HR",
        "station_names": ["Rijeka"],
        "providers": {
            INTERCITY_PL: {"eva": "7800013"},
        },
    },
    "lodz": {
        "name": "Łódź",
        "country": "PL",
        "station_names": ["Lodz"],
        "providers": {
            INTERCITY_PL: {"eva": "5196010"},
        },
    },
    "poznan": {
        "name": "Poznań",
        "country": "PL",
        "station_names": ["Poznan"],
        "providers": {
            INTERCITY_PL: {"eva": "5100081"},
        },
    },
    "rzeszow": {
        "name": "Rzeszów",
        "country": "PL",
        "station_names": ["Rzeszow"],
        "providers": {
            INTERCITY_PL: {"eva": "5196031"},
        },
    },
    "swinoujscie": {
        "name": "Świnoujście",
        "country": "PL",
        "station_names": ["Swinoujscie"],
        "providers": {
            INTERCITY_PL: {"eva": "5100059"},
        },
    },
    "szczecin": {
        "name": "Szczecin",
        "country": "PL",
        "station_names": ["Szczecin"],
        "providers": {
            INTERCITY_PL: {"eva": "5196004"},
        },
    },
    "szklarska_poreba": {
        "name": "Szklarska Poręba",
        "country": "PL",
        "station_names": ["Szklarska Poreba"],
        "providers": {
            INTERCITY_PL: {"eva": "5100058"},
        },
    },
    "torun": {
        "name": "Toruń",
        "country": "PL",
        "station_names": ["Torun"],
        "providers": {
            INTERCITY_PL: {"eva": "5196025"},
        },
    },
    "wroclaw": {
        "name": "Wrocław",
        "country": "PL",
        "station_names": ["Wroclaw"],
        "providers": {
            INTERCITY_PL: {"eva": "5196026"},
        },
    },
    "zakopane": {
        "name": "Zakopane",
        "country": "PL",
        "station_names": ["Zakopane"],
        "providers": {
            INTERCITY_PL: {"eva": "5100158"},
        },
    },
}

CITY_CONNECTIONS = {
    "amersfoort": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "amsterdam": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "antwerp": ["amersfoort", "amsterdam", "bad_schandau", "berlin", "decin", "deventer", "dresden", "prague", "roosendaal", "rotterdam", "the_hague", "usti_nad_labem"],
    "bad_schandau": ["amersfoort", "amsterdam", "antwerp", "berlin", "brussels", "decin", "deventer", "dresden", "prague", "roosendaal", "rotterdam", "the_hague", "usti_nad_labem"],
    "basel": ["berlin", "bonn", "frankfurt_main", "hamburg", "prague", "zurich"],
    "berlin": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "basel", "bratislava", "brussels", "budapest", "decin", "deventer", "dresden", "frankfurt_main", "hamburg", "paris", "prague", "roosendaal", "rotterdam", "the_hague", "usti_nad_labem", "vienna", "zurich"],
    "bielsko_biala": ["kolobrzeg", "poznan", "wroclaw"],
    "bohumin": ["bratislava", "budapest", "bydgoszcz", "czestochowa", "gdansk", "gdynia", "hel", "katowice", "krakow", "linz", "munich", "ostrava", "salzburg", "vienna", "warsaw"],
    "bonn": ["basel", "frankfurt_main", "munich", "salzburg", "vienna", "zurich"],
    "bratislava": ["berlin", "bohumin", "budapest", "katowice", "krakow", "ostrava", "prague", "warsaw"],
    "brussels": ["amersfoort", "amsterdam", "bad_schandau", "berlin", "decin", "deventer", "dresden", "hamburg", "paris", "prague", "roosendaal", "rotterdam", "the_hague", "usti_nad_labem"],
    "budapest": ["berlin", "bohumin", "bratislava", "katowice", "krakow", "munich", "ostrava", "prague", "salzburg", "vienna", "warsaw", "zurich"],
    "bydgoszcz": ["bohumin", "czestochowa", "gdansk", "gdynia", "hel", "katowice", "klodzko", "kolobrzeg", "krakow", "lodz", "poznan", "prague", "torun", "wroclaw"],
    "cadca": ["bohumin", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "chop": ["bohumin", "cadca", "ceska_trebova", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "czestochowa": ["bohumin", "bydgoszcz", "gdansk", "gdynia", "hel", "katowice", "kolobrzeg", "krakow", "lodz", "poznan", "swinoujscie", "szczecin", "torun", "warsaw", "zakopane"],
    "decin": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "berlin", "brussels", "deventer", "dresden", "roosendaal", "rotterdam", "the_hague"],
    "deventer": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "dresden": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "berlin", "brussels", "decin", "deventer", "prague", "roosendaal", "rotterdam", "the_hague", "usti_nad_labem"],
    "florence": ["munich", "rome", "salzburg", "vienna"],
    "frankfurt_main": ["basel", "berlin", "bonn", "hamburg", "prague", "zurich"],
    "gdansk": ["bohumin", "bydgoszcz", "czestochowa", "gdynia", "hel", "katowice", "klodzko", "kolobrzeg", "krakow", "lodz", "poznan", "prague", "torun", "warsaw", "wroclaw", "zakopane"],
    "gdynia": ["bohumin", "bydgoszcz", "czestochowa", "gdansk", "hel", "katowice", "klodzko", "kolobrzeg", "krakow", "lodz", "poznan", "prague", "torun", "warsaw", "wroclaw", "zakopane"],
    "hamburg": ["basel", "berlin", "brussels", "frankfurt_main", "munich", "paris", "salzburg", "vienna", "zurich"],
    "havirov": ["cadca", "ceska_trebova", "chop", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "hel": ["bohumin", "bydgoszcz", "czestochowa", "gdansk", "gdynia", "katowice", "krakow", "lodz", "torun"],
    "jelenia_gora": ["lodz", "szklarska_poreba", "warsaw", "wroclaw"],
    "katowice": ["bohumin", "bratislava", "budapest", "bydgoszcz", "czestochowa", "gdansk", "gdynia", "hel", "kolobrzeg", "krakow", "linz", "munich", "ostrava", "poznan", "premysl", "rzeszow", "salzburg", "swinoujscie", "szczecin", "vienna", "warsaw", "wroclaw"],
    "klodzko": ["bydgoszcz", "gdansk", "gdynia", "poznan", "prague", "torun", "wroclaw"],
    "kolobrzeg": ["bielsko_biala", "bydgoszcz", "czestochowa", "gdansk", "gdynia", "katowice", "krakow", "lodz", "poznan", "torun", "warsaw", "wroclaw"],
    "kosice": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "krakow": ["bohumin", "bratislava", "budapest", "bydgoszcz", "czestochowa", "gdansk", "gdynia", "hel", "katowice", "kolobrzeg", "lodz", "munich", "olomouc", "ostrava", "pardubice", "poznan", "prague", "premysl", "resov", "rzeszow", "salzburg", "swinoujscie", "szczecin", "torun", "vienna", "warsaw", "wroclaw", "zakopane"],
    "kysak": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "linz": ["bohumin", "katowice", "munich", "ostrava", "salzburg", "vienna", "warsaw"],
    "liptovsky_mikulas": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "lodz": ["bydgoszcz", "czestochowa", "gdansk", "gdynia", "hel", "jelenia_gora", "kolobrzeg", "krakow", "poznan", "swinoujscie", "szczecin", "szklarska_poreba", "torun", "warsaw", "wroclaw", "zakopane"],
    "margecany": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "olomouc", "opava", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "munich": ["bohumin", "bonn", "budapest", "florence", "hamburg", "katowice", "krakow", "linz", "ostrava", "rome", "salzburg", "venice", "vienna", "warsaw", "zagreb"],
    "olomouc": ["cadca", "chop", "havirov", "kosice", "krakow", "kysak", "liptovsky_mikulas", "margecany", "ostrava", "pardubice", "poprad", "prague", "premysl", "resov", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zilina"],
    "ostrava": ["bohumin", "bratislava", "budapest", "cadca", "chop", "havirov", "katowice", "kosice", "krakow", "kysak", "linz", "liptovsky_mikulas", "margecany", "munich", "olomouc", "pardubice", "poprad", "prague", "premysl", "resov", "ruzomberok", "salzburg", "spisska_nova_ves", "strba", "vienna", "vrutky", "warsaw", "zilina"],
    "pardubice": ["cadca", "chop", "havirov", "kosice", "krakow", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "poprad", "prague", "premysl", "resov", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zilina"],
    "paris": ["berlin", "brussels", "hamburg"],
    "poprad": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "prague", "ruzomberok", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "poznan": ["bielsko_biala", "bydgoszcz", "czestochowa", "gdansk", "gdynia", "katowice", "klodzko", "kolobrzeg", "krakow", "lodz", "prague", "premysl", "rzeszow", "swinoujscie", "szczecin", "torun", "warsaw", "wroclaw", "zakopane"],
    "prague": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "basel", "berlin", "bratislava", "brussels", "budapest", "bydgoszcz", "cadca", "chop", "deventer", "dresden", "frankfurt_main", "gdansk", "gdynia", "havirov", "klodzko", "kosice", "krakow", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "poznan", "premysl", "resov", "roosendaal", "rotterdam", "ruzomberok", "spisska_nova_ves", "strba", "the_hague", "torun", "vienna", "vrutky", "wroclaw", "zilina", "zurich"],
    "premysl": ["katowice", "krakow", "olomouc", "ostrava", "pardubice", "poznan", "prague", "resov", "rzeszow", "swinoujscie", "szczecin", "wroclaw"],
    "resov": ["krakow", "olomouc", "ostrava", "pardubice", "prague", "premysl"],
    "rome": ["florence", "munich", "salzburg", "vienna"],
    "roosendaal": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "rotterdam": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "ruzomberok": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "spisska_nova_ves", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "rzeszow": ["katowice", "krakow", "poznan", "premysl", "swinoujscie", "szczecin", "wroclaw"],
    "salzburg": ["bohumin", "bonn", "budapest", "florence", "hamburg", "katowice", "krakow", "linz", "munich", "ostrava", "rome", "venice", "vienna", "warsaw", "zagreb", "zurich"],
    "spisska_nova_ves": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "strba", "vrutky", "zabrezh_na_morave", "zilina"],
    "strba": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kosice", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "prague", "ruzomberok", "spisska_nova_ves", "vrutky", "zabrezh_na_morave", "zilina"],
    "swinoujscie": ["czestochowa", "katowice", "krakow", "lodz", "poznan", "premysl", "rzeszow", "szczecin", "warsaw", "wroclaw", "zakopane"],
    "szczecin": ["czestochowa", "katowice", "krakow", "lodz", "poznan", "premysl", "rzeszow", "swinoujscie", "warsaw", "wroclaw", "zakopane"],
    "szklarska_poreba": ["jelenia_gora", "lodz", "warsaw", "wroclaw"],
    "the_hague": ["antwerp", "bad_schandau", "berlin", "brussels", "decin", "dresden", "prague", "usti_nad_labem"],
    "torun": ["bydgoszcz", "czestochowa", "gdansk", "gdynia", "hel", "klodzko", "kolobrzeg", "krakow", "lodz", "poznan", "prague", "wroclaw"],
    "usti_nad_labem": ["amersfoort", "amsterdam", "antwerp", "bad_schandau", "berlin", "brussels", "deventer", "dresden", "roosendaal", "rotterdam", "the_hague"],
    "venice": ["munich", "salzburg", "vienna"],
    "vienna": ["berlin", "bohumin", "bonn", "budapest", "florence", "hamburg", "katowice", "krakow", "linz", "munich", "ostrava", "prague", "rome", "salzburg", "venice", "warsaw", "zagreb", "zurich"],
    "vrutky": ["bohumin", "cadca", "ceska_trebova", "chop", "havirov", "hranice_na_morave", "kysak", "liptovsky_mikulas", "margecany", "olomouc", "ostrava", "pardubice", "poprad", "prague", "ruzomberok", "spisska_nova_ves", "strba", "zabrezh_na_morave", "zilina"],
    "warsaw": ["bohumin", "bratislava", "budapest", "czestochowa", "gdansk", "gdynia", "jelenia_gora", "katowice", "kolobrzeg", "krakow", "linz", "lodz", "munich", "ostrava", "poznan", "salzburg", "swinoujscie", "szczecin", "szklarska_poreba", "vienna", "wroclaw", "zakopane"],
    "wroclaw": ["bielsko_biala", "bydgoszcz", "gdansk", "gdynia", "jelenia_gora", "katowice", "klodzko", "kolobrzeg", "krakow", "lodz", "poznan", "prague", "premysl", "rzeszow", "swinoujscie", "szczecin", "szklarska_poreba", "torun", "warsaw"],
    "zagreb": ["munich", "salzburg", "vienna", "zurich"],
    "zakopane": ["czestochowa", "gdansk", "gdynia", "krakow", "lodz", "poznan", "swinoujscie", "szczecin", "warsaw"],
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
    INTERCITY_PL: [
        {"name": "Warsaw — Budapest",          "trains": "EN 407 / 406", "stops": ["warsaw", "budapest"]},
        {"name": "Warsaw — Munich",            "trains": "EN 457 / 456", "stops": ["warsaw", "munich"]},
        {"name": "Warsaw — Rijeka",            "trains": "seasonal",     "stops": ["warsaw", "rijeka"]},
        {"name": "Warsaw — Świnoujście",       "trains": "—",            "stops": ["warsaw", "swinoujscie"]},
        {"name": "Warsaw — Szklarska Poręba",  "trains": "—",            "stops": ["warsaw", "szklarska_poreba"]},
        {"name": "Warsaw — Jelenia Góra",      "trains": "—",            "stops": ["warsaw", "jelenia_gora"]},
        {"name": "Cracow — Budapest",          "trains": "—",            "stops": ["krakow", "budapest"]},
        {"name": "Cracow — Świnoujście",       "trains": "—",            "stops": ["krakow", "swinoujscie"]},
        {"name": "Cracow — Hel",               "trains": "—",            "stops": ["krakow", "hel"]},
        {"name": "Cracow — Kołobrzeg",         "trains": "—",            "stops": ["krakow", "kolobrzeg"]},
        {"name": "Zakopane — Szczecin",        "trains": "—",            "stops": ["zakopane", "szczecin"]},
        {"name": "Zakopane — Świnoujście",     "trains": "—",            "stops": ["zakopane", "swinoujscie"]},
        {"name": "Lublin — Kołobrzeg",         "trains": "—",            "stops": ["lublin", "kolobrzeg"]},
        {"name": "Przemyśl — Gdynia",          "trains": "—",            "stops": ["premysl", "gdynia"]},
        {"name": "Przemyśl — Hel",             "trains": "—",            "stops": ["premysl", "hel"]},
        {"name": "Przemyśl — Świnoujście",     "trains": "—",            "stops": ["premysl", "swinoujscie"]},
        {"name": "Gdynia — Zakopane",          "trains": "—",            "stops": ["gdynia", "zakopane"]},
        {"name": "Gdynia — Prague",            "trains": "—",            "stops": ["gdynia", "prague"]},
        {"name": "Hel — Bohumín",              "trains": "—",            "stops": ["hel", "bohumin"]},
        {"name": "Kołobrzeg — Bielsko-Biała",  "trains": "—",            "stops": ["kolobrzeg", "bielsko_biala"]},
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
    INTERCITY_PL: "Intercity.pl",
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

    if source == INTERCITY_PL:
        start_eva = (
            start_city.get("providers", {}).get(INTERCITY_PL, {}).get("eva")
        )
        end_eva = (
            end_city.get("providers", {}).get(INTERCITY_PL, {}).get("eva")
        )
        if not start_eva or not end_eva:
            return None

        domestic = str(start_eva).startswith("51") and str(end_eva).startswith("51")
        path = "/wyszukiwanie" if domestic else "/polaczenia-miedzynarodowe"

        out_time = (
            departure_time.strftime("%H:%M")
            if departure_time is not None
            else "00:00"
        )

        base_params = {
            "dwyj": departure_date.strftime("%Y-%m-%d"),
            "swyj": str(start_eva),
            "sprzy": str(end_eva),
            "time": out_time,
            "przy": "0",
            "sprzez": "",
            "ticket100": "1010",
            "ticket50": "",
            "polbez": "0",
        }

        if return_date is None:
            return f"{INTERCITY_PL_BOOKING_URL}{path}?{urlencode(base_params)}"

        return_params = {
            "backdwyj": return_date.strftime("%Y-%m-%d"),
            "backswyj": str(end_eva),
            "backsprzy": str(start_eva),
            "backtime": "00:00",
            "backprzy": "0",
            "backsprzez": "",
            "backpolbez": "0",
        }
        return (
            f"{INTERCITY_PL_BOOKING_URL}{path}"
            f"?{urlencode({**base_params, **return_params})}"
        )

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
