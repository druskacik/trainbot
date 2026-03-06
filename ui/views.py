import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Min, Max, Prefetch, F, Q
from django.shortcuts import render
from django.views.decorators.http import require_GET
from .models import Route, Price

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

        # Build the price filter based on seat type
        price_filter = Q()
        if seat_type == 'couchette':
            price_filter = Q(prices__is_couchette=True)

        # Fetch all available prices for outbound
        # To get the CHEAPEST price for each route, we can annotate
        outbound_routes = Route.objects.filter(
            departure_station=outbound_dep,
            arrival_station=outbound_arr
        ).values('travel_date').annotate(
            cheapest_price=Min('prices__price', filter=price_filter),
            currency=Max('prices__currency', filter=price_filter)
        ).filter(cheapest_price__isnull=False).order_by('travel_date')

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
            
            return_routes = Route.objects.filter(
                departure_station=return_dep,
                arrival_station=return_arr
            ).values('travel_date').annotate(
                cheapest_price=Min('prices__price', filter=price_filter),
                currency=Max('prices__currency', filter=price_filter)
            ).filter(cheapest_price__isnull=False).order_by('travel_date')

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
