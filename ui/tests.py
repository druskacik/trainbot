from django.test import TestCase
from django.utils import timezone
from .models import Route, Price
from .views import _get_routes_by_date

class SearchLogicTest(TestCase):
    def test_cheapest_price_selection_same_timestamp(self):
        """
        Test that when multiple prices have the same scraped_at timestamp,
        the cheapest one is selected.
        """
        travel_date = timezone.now().date()
        route = Route.objects.create(
            id="test-route-1",
            source="test",
            train_number="452",
            departure_station="PRAHA HL. N.",
            arrival_station="Amsterdam CS",
            travel_date=travel_date,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=10)
        )
        
        timestamp = timezone.now()
        
        # Create a more expensive couchette price
        Price.objects.create(
            route=route,
            price=49.99,
            currency="EUR",
            is_couchette=True,
            scraped_at=timestamp
        )
        
        # Create a cheaper non-couchette price with the EXACT same timestamp
        Price.objects.create(
            route=route,
            price=29.99,
            currency="EUR",
            is_couchette=False,
            scraped_at=timestamp
        )
        
        # Call the logic being tested
        results = _get_routes_by_date("PRAHA HL. N.", "Amsterdam CS", "any")
        
        # Verify the results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['cheapest_price'], 29.99)
