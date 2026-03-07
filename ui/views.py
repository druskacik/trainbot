import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Subquery, OuterRef
from django.shortcuts import render
from django.views.decorators.http import require_GET
from .models import Route, Price


def _get_routes_by_date(dep_station, arr_station, seat_type):
    """Get the cheapest latest-scraped price per travel date."""
    price_qs = Price.objects.filter(route_id=OuterRef('pk'))
    if seat_type == 'couchette':
        price_qs = price_qs.filter(is_couchette=True)

    latest_price = Subquery(price_qs.order_by('-scraped_at', 'price').values('price')[:1])
    latest_currency = Subquery(price_qs.order_by('-scraped_at', 'price').values('currency')[:1])

    routes = Route.objects.filter(
        departure_station=dep_station,
        arrival_station=arr_station,
    ).annotate(
        latest_price=latest_price,
        latest_currency=latest_currency,
    ).filter(
        latest_price__isnull=False,
    ).order_by('travel_date')

    # Group by travel_date and find cheapest latest price
    result = {}
    for route in routes:
        date = route.travel_date
        if date not in result or route.latest_price < result[date]['cheapest_price']:
            result[date] = {
                'travel_date': date,
                'cheapest_price': route.latest_price,
                'currency': route.latest_currency,
            }

    return sorted(result.values(), key=lambda x: x['travel_date'])


def index(request):
    return render(request, 'ui/index.html')

@require_GET
def search_trips(request):
    try:
        start_city = request.GET.get('start', 'prague').lower()
        trip_type = request.GET.get('type', 'single').lower()
        max_duration_str = request.GET.get('max_duration', '')
        seat_type = request.GET.get('seat_type', 'any').lower()
        
        if start_city == 'prague':
            outbound_dep = 'PRAHA HL. N.'
            outbound_arr = 'Amsterdam CS'
            return_dep = 'Amsterdam CS'
            return_arr = 'PRAHA HL. N.'
            dep_id = '5457076'
            arr_id = '8400058'
        else:
            outbound_dep = 'Amsterdam CS'
            outbound_arr = 'PRAHA HL. N.'
            return_dep = 'PRAHA HL. N.'
            return_arr = 'Amsterdam CS'
            dep_id = '8400058'
            arr_id = '5457076'

        # Get cheapest latest-scraped price per travel date
        outbound_routes = _get_routes_by_date(outbound_dep, outbound_arr, seat_type)

        results = []

        if trip_type == 'single':
            for route in outbound_routes:
                date_str = route['travel_date'].strftime('%Y-%m-%d')
                booking_url = f"https://booking.europeansleeper.eu/en?departureStation={dep_id}&arrivalStation={arr_id}&departureDate={date_str}&bicycleCount=0&petsCount=0&passengerTypes=72"
                results.append({
                    'outbound_date': route['travel_date'].isoformat(),
                    'outbound_price': route['cheapest_price'],
                    'currency': route['currency'],
                    'total_price': route['cheapest_price'],
                    'booking_url': booking_url
                })
        else:
            # Return journey
            max_duration = int(max_duration_str) if max_duration_str.isdigit() else 30
            
            return_routes = _get_routes_by_date(return_dep, return_arr, seat_type)

            # Build list of combinations
            return_list = list(return_routes)
            for out_route in outbound_routes:
                valid_returns = [
                    ret for ret in return_list 
                    if 0 <= (ret['travel_date'] - out_route['travel_date']).days <= max_duration
                ]
                
                if valid_returns:
                    best_return = min(valid_returns, key=lambda x: x['cheapest_price'])
                    out_date_str = out_route['travel_date'].strftime('%Y-%m-%d')
                    ret_date_str = best_return['travel_date'].strftime('%Y-%m-%d')
                    booking_url = f"https://booking.europeansleeper.eu/en?departureStation={dep_id}&arrivalStation={arr_id}&departureDate={out_date_str}&returnDate={ret_date_str}&bicycleCount=0&petsCount=0&passengerTypes=72"
                    
                    results.append({
                        'outbound_date': out_route['travel_date'].isoformat(),
                        'outbound_price': out_route['cheapest_price'],
                        'return_date': best_return['travel_date'].isoformat(),
                        'return_price': best_return['cheapest_price'],
                        'currency': out_route['currency'],
                        'total_price': out_route['cheapest_price'] + best_return['cheapest_price'],
                        'duration_days': (best_return['travel_date'] - out_route['travel_date']).days,
                        'booking_url': booking_url
                    })

        # Sort results by total price ascending
        results.sort(key=lambda x: x['total_price'])

        return JsonResponse({'status': 'success', 'data': results})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
