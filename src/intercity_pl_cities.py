"""City mapping for the Intercity.pl scraper.

Each CitySpec declares one canonical English city name (the value stored in
``Route.departure_station`` / ``Route.arrival_station``) together with the
station EVA codes that count as that city.

Polish cities are specified by ``kodAglomeracji`` where available; the real
EVA members are expanded at scrape time from the live stations list. Cities
without an agglomeration (single-station PL cities and all foreign cities)
list their EVAs explicitly.

``search_eva`` is the code used as ``stacjaWyjazdu`` / ``stacjaPrzyjazdu`` in
corridor searches; it is usually the "dowolna stacja" aggregate for a city.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class CitySpec:
    english_name: str
    search_eva: Optional[int] = None
    agglomeration: Optional[int] = None
    station_evas: Tuple[int, ...] = ()


CITIES: Dict[str, CitySpec] = {
    # --- Poland ---
    "Warsaw":           CitySpec("Warsaw",           search_eva=5196003, agglomeration=23),
    "Cracow":           CitySpec("Cracow",           search_eva=5196001, agglomeration=10),
    "Katowice":         CitySpec("Katowice",         search_eva=5196028, agglomeration=8),
    "Wroclaw":          CitySpec("Wroclaw",          search_eva=5196026, agglomeration=25),
    "Poznan":           CitySpec("Poznan",           station_evas=(5100081,)),
    "Lodz":             CitySpec("Lodz",             search_eva=5196010, agglomeration=12),
    "Gdansk":           CitySpec("Gdansk",           agglomeration=5),
    "Gdynia":           CitySpec("Gdynia",           station_evas=(5100010,)),
    "Torun":            CitySpec("Torun",            search_eva=5196025, agglomeration=21),
    "Bydgoszcz":        CitySpec("Bydgoszcz",        agglomeration=2),
    "Szczecin":         CitySpec("Szczecin",         search_eva=5196004, agglomeration=18),
    "Swinoujscie":      CitySpec("Swinoujscie",      station_evas=(5100059,)),
    "Kolobrzeg":        CitySpec("Kolobrzeg",        station_evas=(5100025,)),
    "Hel":              CitySpec("Hel",              station_evas=(5101340,)),
    "Zakopane":         CitySpec("Zakopane",         station_evas=(5100158,)),
    "Bielsko-Biala":    CitySpec("Bielsko-Biala",    station_evas=(5100316,)),
    "Lublin":           CitySpec("Lublin",           search_eva=5196030, agglomeration=28),
    "Przemysl":         CitySpec("Przemysl",         search_eva=5196032, agglomeration=14),
    "Rzeszow":          CitySpec("Rzeszow",          search_eva=5196031, agglomeration=31),
    "Szklarska Poreba": CitySpec("Szklarska Poreba", agglomeration=19),
    "Jelenia Gora":     CitySpec("Jelenia Gora",     agglomeration=7),
    "Klodzko":          CitySpec("Klodzko",          search_eva=5196183, agglomeration=9),
    "Czestochowa":      CitySpec("Czestochowa",      search_eva=5196005, agglomeration=4),

    # --- Foreign ---
    "Munich":     CitySpec("Munich",     station_evas=(8000261, 8000262)),
    "Vienna":     CitySpec("Vienna",     search_eva=8196001, station_evas=(8103000, 8100514, 8100003)),
    "Salzburg":   CitySpec("Salzburg",   station_evas=(8100002,)),
    "Linz":       CitySpec("Linz",       station_evas=(8100013,)),
    "Prague":     CitySpec("Prague",     search_eva=5496001, station_evas=(5400014, 5400130, 5400275)),
    "Ostrava":    CitySpec("Ostrava",    station_evas=(5400026, 5402286)),
    "Bohumin":    CitySpec("Bohumin",    station_evas=(5400038,)),
    "Bratislava": CitySpec("Bratislava", station_evas=(5600207,)),
    "Budapest":   CitySpec("Budapest",   search_eva=5596001, station_evas=(5500003, 5500728)),
    "Rijeka":     CitySpec("Rijeka",     station_evas=(7800013,)),
    "Ljubljana":  CitySpec("Ljubljana",  station_evas=(7900003,)),
    "Berlin":     CitySpec("Berlin",     search_eva=8096003,
                           station_evas=(8011160, 8010036, 8010255, 8011162, 8011102, 8010403, 8010406)),
    "Leipzig":    CitySpec("Leipzig",    station_evas=(8010205,)),
}


def build_station_eva_to_city(stations_list: List[dict]) -> Dict[int, str]:
    """Expand agglomerations into real station EVAs and merge with explicit lists.

    Returns a flat ``EVA -> city_key`` map suitable for classifying stops that
    appear in ``pobierzTrasePrzejazdu`` responses. Synthetic "dowolna stacja"
    EVAs never appear in route responses, so including them is harmless.
    """
    aggl_members: Dict[int, List[int]] = defaultdict(list)
    for s in stations_list:
        ag = s.get("kodAglomeracji") or 0
        eva = s.get("kodEVA")
        if ag and eva:
            aggl_members[int(ag)].append(int(eva))

    out: Dict[int, str] = {}
    for key, spec in CITIES.items():
        if spec.agglomeration is not None:
            for eva in aggl_members.get(spec.agglomeration, []):
                out[eva] = key
        for eva in spec.station_evas:
            out[eva] = key
        if spec.search_eva is not None:
            out[spec.search_eva] = key
    return out
