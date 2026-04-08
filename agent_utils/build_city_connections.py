from __future__ import annotations

"""
One-off helper script to derive city-to-city connections from the routes table.

It maps (departure_station, arrival_station) pairs from the database to
CITY_CATALOG city_ids via station_names, and prints a Python dict literal:

    CITY_CONNECTIONS = {
        "amsterdam": ["antwerp", "berlin", ...],
        ...
    }

Run from the project root:

    uv run agent_utils/build_city_connections.py

Copy the printed CITY_CONNECTIONS dict into ui/cities.py.
"""

from collections import defaultdict
import pathlib
import sys

# Ensure project root is on sys.path so we can import project modules
ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_utils.search_db import get_connection  # type: ignore
from ui.cities import CITY_CATALOG  # type: ignore


def build_station_to_city_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for city_id, city in CITY_CATALOG.items():
        for name in city.get("station_names", []):
            existing = mapping.get(name)
            if existing and existing != city_id:
                # Ambiguous station name; keep the first and ignore the rest.
                continue
            mapping[name] = city_id
    return mapping


def build_city_connections() -> dict[str, list[str]]:
    station_to_city = build_station_to_city_map()

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT DISTINCT departure_station, arrival_station "
            "FROM routes "
            "ORDER BY departure_station, arrival_station"
        )
        rows = cur.fetchall()

    connections: dict[str, set[str]] = defaultdict(set)

    for departure_station, arrival_station in rows:
        from_city = station_to_city.get(departure_station)
        to_city = station_to_city.get(arrival_station)
        if not from_city or not to_city:
            # Ignore stations we don't know how to map.
            continue
        if from_city == to_city:
            # Skip self-loops at city level.
            continue
        connections[from_city].add(to_city)

    # Convert sets to sorted lists for stable output.
    result: dict[str, list[str]] = {}
    for city_id in sorted(CITY_CATALOG.keys()):
        if city_id in connections:
            result[city_id] = sorted(connections[city_id])
    return result


def main() -> None:
    connections = build_city_connections()

    # Print as a Python dict literal that can be pasted into ui/cities.py
    print("CITY_CONNECTIONS = {")
    for city_id in sorted(connections.keys()):
        dests = connections[city_id]
        dests_literal = ", ".join(f'"{d}"' for d in dests)
        print(f'    "{city_id}": [{dests_literal}],')
    print("}")


if __name__ == "__main__":
    main()

