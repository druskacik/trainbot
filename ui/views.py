from django.http import JsonResponse
from django.db.models import Subquery, OuterRef
from django.shortcuts import render
from django.views.decorators.http import require_GET
from .models import Route, Price

# Map EuropeanSleeper API ID to all known database station representations
STATIONS = {
    '8800104': {'name': 'Bruxelles Midi/Brussel Zuid', 'db_names': ['Bruxelles Midi']},
    '8800210': {'name': 'Antwerpen Centraal', 'db_names': ['Antwerpen-Centraal']},
    '8700015': {'name': 'Paris-Nord', 'db_names': ['Paris-Nord']},
    '8400526': {'name': 'Roosendaal', 'db_names': ['Roosendaal']},
    '8400530': {'name': 'Rotterdam Centraal', 'db_names': ['Rotterdam CS']},
    '8400280': {'name': 'Den Haag HS', 'db_names': ['Den Haag HS']},
    '8400058': {'name': 'Amsterdam Centraal', 'db_names': ['Amsterdam CS']},
    '8400055': {'name': 'Amersfoort Centraal', 'db_names': ['Amersfoort']},
    '8400173': {'name': 'Deventer', 'db_names': ['Deventer']},
    '8020401': {'name': 'Hamburg Harburg', 'db_names': ['Hamburg Harburg']},
    '8010110': {'name': 'Berlin Ostbahnhof', 'db_names': ['Berlin Ostbahnnhof']},
    '8010100': {'name': 'Berlin Hbf', 'db_names': ['Berlin Hbf', 'Berlin-Gesundbrunnen']},
    '8001305': {'name': 'Dresden Hbf', 'db_names': ['Dresden Hbf', 'Dresden-Neustadt']},
    '8001311': {'name': 'Bad Schandau', 'db_names': ['Bad Schandau']},
    '5455659': {'name': 'Děčín hl.n.', 'db_names': ['DECIN']},
    '5453179': {'name': 'Ústí nad Labem hl.n.', 'db_names': ['USTI NAD LABEM']},
    '5457076': {'name': 'Praha hl.n.', 'db_names': ['PRAHA HL. N.']}
}


def _get_routes_with_latest_prices(dep_station_names, arr_station_names, is_couchette):
    """For each route matching the station pair, annotate with its latest scraped
    price (filtered by is_couchette) and order cheapest-first."""
    latest_price_sq = Price.objects.filter(
        route=OuterRef('pk'),
        is_couchette=is_couchette,
    ).order_by('-scraped_at')

    return (
        Route.objects.filter(
            departure_station__in=dep_station_names,
            arrival_station__in=arr_station_names,
        )
        .annotate(
            latest_price=Subquery(latest_price_sq.values('price')[:1]),
            latest_currency=Subquery(latest_price_sq.values('currency')[:1]),
        )
        .filter(latest_price__isnull=False)
        .order_by('latest_price')
    )


def index(request):
    return render(request, 'ui/index.html')


@require_GET
def get_stations(request):
    stations_list = [
        {'id': st_id, 'name': info['name']}
        for st_id, info in STATIONS.items()
    ]
    return JsonResponse({'status': 'success', 'data': stations_list})


@require_GET
def search_trips(request):
    try:
        start_id = request.GET.get('start_id')
        end_id = request.GET.get('end_id')
        trip_type = request.GET.get('type', 'single').lower()
        max_duration_str = request.GET.get('max_duration', '')
        seat_type = request.GET.get('seat_type', 'seat').lower()

        if not start_id or not end_id:
            return JsonResponse({'status': 'error', 'message': 'Missing start_id or end_id parameters.'}, status=400)

        if start_id not in STATIONS or end_id not in STATIONS:
            return JsonResponse({'status': 'error', 'message': 'Invalid station IDs provided.'}, status=400)

        is_couchette = seat_type == 'couchette'
        outbound_dep = STATIONS[start_id]['db_names']
        outbound_arr = STATIONS[end_id]['db_names']

        outbound_routes = _get_routes_with_latest_prices(outbound_dep, outbound_arr, is_couchette)

        results = []

        if trip_type == 'single':
            for route in outbound_routes:
                date_str = route.travel_date.strftime('%Y-%m-%d')
                booking_url = (
                    f"https://booking.europeansleeper.eu/en?"
                    f"departureStation={start_id}&arrivalStation={end_id}"
                    f"&departureDate={date_str}"
                    f"&bicycleCount=0&petsCount=0&passengerTypes=72"
                )
                results.append({
                    'outbound_date': route.travel_date.isoformat(),
                    'outbound_price': route.latest_price,
                    'currency': route.latest_currency,
                    'total_price': route.latest_price,
                    'booking_url': booking_url,
                })
        else:
            max_duration = int(max_duration_str) if max_duration_str.isdigit() else 30
            return_dep = STATIONS[end_id]['db_names']
            return_arr = STATIONS[start_id]['db_names']
            return_routes = list(_get_routes_with_latest_prices(return_dep, return_arr, is_couchette))

            for out_route in outbound_routes:
                valid_returns = [
                    ret for ret in return_routes
                    if 0 < (ret.travel_date - out_route.travel_date).days <= max_duration
                ]

                if valid_returns:
                    best_return = min(valid_returns, key=lambda r: r.latest_price)
                    out_date_str = out_route.travel_date.strftime('%Y-%m-%d')
                    ret_date_str = best_return.travel_date.strftime('%Y-%m-%d')
                    booking_url = (
                        f"https://booking.europeansleeper.eu/en?"
                        f"departureStation={start_id}&arrivalStation={end_id}"
                        f"&departureDate={out_date_str}&returnDate={ret_date_str}"
                        f"&bicycleCount=0&petsCount=0&passengerTypes=72"
                    )
                    results.append({
                        'outbound_date': out_route.travel_date.isoformat(),
                        'outbound_price': out_route.latest_price,
                        'return_date': best_return.travel_date.isoformat(),
                        'return_price': best_return.latest_price,
                        'currency': out_route.latest_currency,
                        'total_price': out_route.latest_price + best_return.latest_price,
                        'duration_days': (best_return.travel_date - out_route.travel_date).days,
                        'booking_url': booking_url,
                    })

        results.sort(key=lambda x: x['total_price'])
        return JsonResponse({'status': 'success', 'trip_type': trip_type, 'routes': results})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

