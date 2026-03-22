from django.db.models import Min, OuterRef, Subquery
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.utils import timezone

from .cities import (
    CITY_CATALOG,
    CITY_CONNECTIONS,
    EUROPEAN_SLEEPER,
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
            max_duration = int(max_duration_str) if max_duration_str.isdigit() else 30
            return_dep = get_station_names(end_id)
            return_arr = get_station_names(start_id)
            return_routes = list(_get_routes_with_best_price(return_dep, return_arr, seat_type_normalized))

            for out_route in outbound_routes:
                valid_returns = [
                    ret for ret in return_routes
                    if 0 < (ret.travel_date - out_route.travel_date).days <= max_duration
                ]

                if valid_returns:
                    best_return = min(valid_returns, key=lambda r: r.latest_price)
                    outbound_leg = _serialize_route_leg(out_route, start_id, end_id)
                    return_leg = _serialize_route_leg(best_return, end_id, start_id)
                    combined_booking_url = None
                    if (
                        outbound_leg['provider'] == EUROPEAN_SLEEPER
                        and return_leg['provider'] == EUROPEAN_SLEEPER
                    ):
                        combined_booking_url = build_booking_url(
                            EUROPEAN_SLEEPER,
                            start_id,
                            end_id,
                            out_route.travel_date,
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
                    })

        results.sort(key=lambda x: x['total_price'])
        return JsonResponse({'status': 'success', 'trip_type': trip_type, 'routes': results})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

