from collections import Counter, defaultdict
from datetime import timedelta

from django.db.models import Min, OuterRef, Subquery
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.utils import timezone

from .cities import (
    CITY_CATALOG,
    CITY_CONNECTIONS,
    EUROPEAN_SLEEPER,
    EUROPEAN_SLEEPER_BOOKING_URL,
    INTERCITY_PL,
    INTERCITY_PL_BOOKING_URL,
    NIGHTJET,
    NIGHTJET_BOOKING_URL,
    PROVIDER_ROUTES,
    REGIOJET,
    REGIOJET_BOOKING_URL,
    build_booking_url,
    get_city,
    get_city_options,
    get_provider_display_name,
    get_station_names,
)
from .models import CurrentAvailability, Route


def _get_routes_with_best_price(dep_station_names, arr_station_names, seat_type):
    """For each route matching the station pair, annotate with best available price
    and order cheapest-first. seat_type: 'seat' | 'couchette' | 'any'."""
    base_routes = Route.objects.filter(
        departure_station__in=dep_station_names,
        arrival_station__in=arr_station_names,
        departure_time__gte=timezone.now(),
    )

    if seat_type == 'seat':
        return (
            base_routes.filter(availability__is_couchette=False, availability__price__isnull=False)
            .annotate(
                latest_price=Min('availability__price'),
                latest_currency=Subquery(
                    CurrentAvailability.objects.filter(
                        route=OuterRef('pk'),
                        is_couchette=False,
                        price__isnull=False,
                    ).order_by('price').values('currency')[:1]
                ),
            )
            .distinct()
            .order_by('latest_price')
        )
    if seat_type == 'couchette':
        return (
            base_routes.filter(availability__is_couchette=True, availability__price__isnull=False)
            .annotate(
                latest_price=Min('availability__price'),
                latest_currency=Subquery(
                    CurrentAvailability.objects.filter(
                        route=OuterRef('pk'),
                        is_couchette=True,
                        price__isnull=False,
                    ).order_by('price').values('currency')[:1]
                ),
            )
            .distinct()
            .order_by('latest_price')
        )
    # seat_type == 'any': cheapest of seat or couchette per route
    return (
        base_routes.filter(availability__price__isnull=False)
        .annotate(
            latest_price=Min('availability__price'),
            latest_currency=Subquery(
                CurrentAvailability.objects.filter(
                    route=OuterRef('pk'),
                    price__isnull=False,
                ).order_by('price').values('currency')[:1]
            ),
        )
        .distinct()
        .order_by('latest_price')
    )


def index(request):
    return render(request, 'ui/index.html')


def about(request):
    return render(request, 'ui/about.html')


def _reconstruct_station_chain(route_rows):
    """Reconstruct one station sequence from pairwise segment rows."""
    if not route_rows:
        return []

    dep_times = {}
    dep_stations = set()
    arr_stations = set()
    arr_only_times = {}

    for row in route_rows:
        dep_station = row["departure_station"]
        arr_station = row["arrival_station"]
        dep_time = row["departure_time"]
        arr_time = row["arrival_time"]

        dep_stations.add(dep_station)
        arr_stations.add(arr_station)

        existing = dep_times.get(dep_station)
        if existing is None or dep_time < existing:
            dep_times[dep_station] = dep_time

        if arr_station not in dep_stations:
            current_arr_time = arr_only_times.get(arr_station)
            if current_arr_time is None or arr_time < current_arr_time:
                arr_only_times[arr_station] = arr_time

    station_times = dict(dep_times)
    for station, arr_time in arr_only_times.items():
        if station not in station_times:
            station_times[station] = arr_time

    chain = [station for station, _ in sorted(station_times.items(), key=lambda kv: (kv[1], kv[0]))]

    return chain if len(chain) >= 2 else []


def _split_service_rows_by_time_overlap(service_rows):
    """Split one train/day rows into time-consistent clusters."""
    clusters = []
    for row in sorted(service_rows, key=lambda x: (x["departure_time"], x["arrival_time"])):
        matched = None
        for cluster in clusters:
            if not (
                row["arrival_time"] < cluster["start"]
                or row["departure_time"] > cluster["end"]
            ):
                matched = cluster
                break

        if matched is None:
            clusters.append({
                "start": row["departure_time"],
                "end": row["arrival_time"],
                "rows": [row],
            })
            continue

        matched["rows"].append(row)
        if row["departure_time"] < matched["start"]:
            matched["start"] = row["departure_time"]
        if row["arrival_time"] > matched["end"]:
            matched["end"] = row["arrival_time"]

    return [cluster["rows"] for cluster in clusters]


def _canonical_chain_key(stops):
    chain = tuple(stops)
    return min(chain, tuple(reversed(chain)))


def _is_contiguous_subsequence(short_chain, long_chain):
    n = len(short_chain)
    if n > len(long_chain):
        return False
    for i in range(len(long_chain) - n + 1):
        if tuple(long_chain[i : i + n]) == tuple(short_chain):
            return True
    return False


def _filter_to_maximal_chains(canonical_chains):
    kept = []
    for candidate in sorted(canonical_chains, key=len, reverse=True):
        candidate_rev = tuple(reversed(candidate))
        is_subset = False
        for existing in kept:
            existing_rev = tuple(reversed(existing))
            if (
                _is_contiguous_subsequence(candidate, existing)
                or _is_contiguous_subsequence(candidate_rev, existing)
                or _is_contiguous_subsequence(candidate, existing_rev)
                or _is_contiguous_subsequence(candidate_rev, existing_rev)
            ):
                is_subset = True
                break
        if not is_subset:
            kept.append(candidate)
    return kept


def _build_intercity_coverage_routes():
    """Build Intercity.pl coverage routes from DB rows with dedup/noise filtering."""
    min_support_days = 3
    now = timezone.now()
    rows = list(
        Route.objects.filter(source=INTERCITY_PL, departure_time__gte=now)
        .values(
            "train_number",
            "travel_date",
            "departure_station",
            "arrival_station",
            "departure_time",
            "arrival_time",
        )
        .order_by("travel_date", "departure_time")
    )

    if not rows:
        return None

    rows_by_service = defaultdict(list)
    for row in rows:
        service_key = (row["train_number"], row["travel_date"])
        rows_by_service[service_key].append(row)

    merged_routes = defaultdict(lambda: {
        "distinct_days": set(),
        "train_numbers": set(),
        "oriented_counts": Counter(),
    })

    for (train_number, travel_date), service_rows in rows_by_service.items():
        for cluster_rows in _split_service_rows_by_time_overlap(service_rows):
            chain = _reconstruct_station_chain(cluster_rows)
            if len(chain) < 2:
                continue
            canonical_key = _canonical_chain_key(chain)
            entry = merged_routes[canonical_key]
            entry["distinct_days"].add(travel_date)
            entry["train_numbers"].add(str(train_number))
            entry["oriented_counts"][tuple(chain)] += 1

    supported_chains = [
        chain_key
        for chain_key, data in merged_routes.items()
        if len(data["distinct_days"]) >= min_support_days
    ]
    maximal_chains = _filter_to_maximal_chains(supported_chains)

    routes = []
    for canonical_key in maximal_chains:
        data = merged_routes[canonical_key]
        stops = list(sorted(data["oriented_counts"].items(), key=lambda kv: (-kv[1], kv[0]))[0][0])
        trains = " / ".join(sorted(data["train_numbers"], key=lambda t: (len(t), t)))
        routes.append(
            {
                "name": f"{stops[0]} — {stops[-1]}",
                "trains": trains or "—",
                "stops": stops,
                "endpoints": f"{stops[0]} — {stops[-1]}",
            }
        )

    routes.sort(key=lambda route: (route["endpoints"], route["trains"]))
    return routes or None


def coverage(request):
    providers = [
        {"id": EUROPEAN_SLEEPER, "name": "European Sleeper", "url": EUROPEAN_SLEEPER_BOOKING_URL},
        {"id": NIGHTJET,         "name": "Nightjet",         "url": NIGHTJET_BOOKING_URL},
        {"id": REGIOJET,         "name": "RegioJet",         "url": REGIOJET_BOOKING_URL},
        {"id": INTERCITY_PL,     "name": "Intercity.pl",     "url": INTERCITY_PL_BOOKING_URL},
    ]
    for p in providers:
        routes = []
        all_cities = set()

        if p["id"] == INTERCITY_PL:
            intercity_routes = _build_intercity_coverage_routes()
            if intercity_routes is not None:
                routes = intercity_routes
                for route in routes:
                    all_cities.update(route["stops"])

        if not routes:
            raw_routes = PROVIDER_ROUTES.get(p["id"], [])
            for r in raw_routes:
                resolved = [CITY_CATALOG[cid]["name"] for cid in r["stops"]]
                routes.append({
                    "name": r["name"],
                    "trains": r["trains"],
                    "stops": resolved,
                    "endpoints": f"{resolved[0]} — {resolved[-1]}",
                })
                all_cities.update(r["stops"])

        p["routes"] = routes
        p["city_count"] = len(all_cities)
    return render(request, "ui/coverage.html", {"providers": providers})


@require_GET
def get_stations(request):
    return JsonResponse(
        {
            'status': 'success',
            'data': get_city_options(),
            'connections': CITY_CONNECTIONS,
        }
    )


def _serialize_route_leg(route, start_id, end_id):
    start_city = get_city(start_id) or {}
    end_city = get_city(end_id) or {}
    booking_url = build_booking_url(
        route.source,
        start_id,
        end_id,
        route.travel_date,
        route.departure_time,
    )

    return {
        'date': route.travel_date.isoformat(),
        'departure_time_str': route.departure_time.strftime('%H:%M'),
        'arrival_time_str': route.arrival_time.strftime('%H:%M'),
        'arrival_date': route.arrival_time.date().isoformat(),
        'day_offset': (route.arrival_time.date() - route.departure_time.date()).days,
        'price': route.latest_price,
        'currency': route.latest_currency,
        'provider': route.source,
        'provider_name': get_provider_display_name(route.source),
        'booking_url': booking_url,
        'booking_mode': 'direct',
        'booking_details': {
            'from_city': start_city.get('name'),
            'to_city': end_city.get('name'),
            'travel_date': route.travel_date.isoformat(),
        },
    }


def _pto_days_needed(out_departure_dt, return_arrival_dt, work_start_hour=10, work_end_hour=17):
    """Estimate Mon-Fri vacation days needed for a round-trip.

    A weekday between leaving home and getting back home costs a PTO day,
    except: the departure day if leaving after work_end_hour (already worked),
    and the arrival day if arriving before work_start_hour (can still make it in).
    """
    if return_arrival_dt <= out_departure_dt:
        return 0
    pto = 0
    cur = out_departure_dt.date()
    end = return_arrival_dt.date()
    while cur <= end:
        if cur.weekday() < 5:
            free = False
            if cur == out_departure_dt.date() and out_departure_dt.hour >= work_end_hour:
                free = True
            if cur == return_arrival_dt.date() and return_arrival_dt.hour < work_start_hour:
                free = True
            if not free:
                pto += 1
        cur += timedelta(days=1)
    return pto


@require_GET
def search_trips(request):
    try:
        start_id = request.GET.get('start_id')
        end_id = request.GET.get('end_id')
        trip_type = request.GET.get('type', 'single').lower()
        min_duration_str = request.GET.get('min_duration', '')
        max_duration_str = request.GET.get('max_duration', '')
        seat_type = request.GET.get('seat_type', 'couchette').lower()

        if not start_id or not end_id:
            return JsonResponse({'status': 'error', 'message': 'Missing start_id or end_id parameters.'}, status=400)

        if start_id not in CITY_CATALOG or end_id not in CITY_CATALOG:
            return JsonResponse({'status': 'error', 'message': 'Invalid city IDs provided.'}, status=400)

        seat_type_normalized = seat_type if seat_type in ('seat', 'couchette', 'any') else 'any'
        outbound_dep = get_station_names(start_id)
        outbound_arr = get_station_names(end_id)

        outbound_routes = _get_routes_with_best_price(outbound_dep, outbound_arr, seat_type_normalized)

        results = []

        if trip_type == 'single':
            for route in outbound_routes:
                leg = _serialize_route_leg(route, start_id, end_id)
                results.append({
                    'outbound_date': leg['date'],
                    'outbound_price': leg['price'],
                    'currency': leg['currency'],
                    'total_price': route.latest_price,
                    'outbound_provider': leg['provider'],
                    'outbound_provider_name': leg['provider_name'],
                    'outbound_booking_url': leg['booking_url'],
                    'outbound_leg': leg,
                    'primary_booking_url': leg['booking_url'],
                })
        else:
            min_duration = max(1, int(min_duration_str)) if min_duration_str.isdigit() else 2
            max_duration = int(max_duration_str) if max_duration_str.isdigit() else 5
            max_duration = max(min_duration, max_duration)
            return_dep = get_station_names(end_id)
            return_arr = get_station_names(start_id)
            return_routes = list(_get_routes_with_best_price(return_dep, return_arr, seat_type_normalized))

            for out_route in outbound_routes:
                valid_returns = [
                    ret for ret in return_routes
                    if min_duration <= (ret.travel_date - out_route.travel_date).days <= max_duration
                ]

                if valid_returns:
                    best_return = min(valid_returns, key=lambda r: r.latest_price)
                    outbound_leg = _serialize_route_leg(out_route, start_id, end_id)
                    return_leg = _serialize_route_leg(best_return, end_id, start_id)
                    combined_booking_url = None
                    if (
                        outbound_leg['provider'] == return_leg['provider']
                        and outbound_leg['provider'] in (EUROPEAN_SLEEPER, INTERCITY_PL, REGIOJET)
                    ):
                        combined_booking_url = build_booking_url(
                            outbound_leg['provider'],
                            start_id,
                            end_id,
                            out_route.travel_date,
                            departure_time=out_route.departure_time,
                            return_date=best_return.travel_date,
                        )

                    results.append({
                        'outbound_date': outbound_leg['date'],
                        'outbound_price': outbound_leg['price'],
                        'outbound_provider': outbound_leg['provider'],
                        'outbound_provider_name': outbound_leg['provider_name'],
                        'outbound_booking_url': outbound_leg['booking_url'],
                        'outbound_leg': outbound_leg,
                        'return_date': return_leg['date'],
                        'return_price': return_leg['price'],
                        'return_provider': return_leg['provider'],
                        'return_provider_name': return_leg['provider_name'],
                        'return_booking_url': return_leg['booking_url'],
                        'return_leg': return_leg,
                        'currency': out_route.latest_currency,
                        'total_price': out_route.latest_price + best_return.latest_price,
                        'duration_days': (best_return.travel_date - out_route.travel_date).days,
                        'mixed_providers': out_route.source != best_return.source,
                        'primary_booking_url': combined_booking_url or outbound_leg['booking_url'],
                        'secondary_booking_url': None if combined_booking_url else return_leg['booking_url'],
                        '_pto_cost': _pto_days_needed(
                            out_route.departure_time,
                            best_return.arrival_time,
                        ),
                    })

        results.sort(key=lambda x: (
            x['total_price'],
            x.get('_pto_cost', 0),
            -x.get('duration_days', 0),
        ))
        for r in results:
            r.pop('_pto_cost', None)
        return JsonResponse({'status': 'success', 'trip_type': trip_type, 'routes': results})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
