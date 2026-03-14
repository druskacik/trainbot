from django.test import TestCase
from django.utils import timezone
from django.db import connection
from .models import Route, CurrentAvailability
from .views import _get_routes_with_best_price


def _tables_exist():
    """Check if routes and current_availability tables exist (schema from Alembic)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'routes')
            AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'current_availability')
        """)
        return cursor.fetchone()[0]


class SearchLogicTest(TestCase):
    def test_any_seat_type_selects_cheapest_of_seat_or_couchette(self):
        """
        When seat_type is 'any', the search returns the cheapest available option
        per route (min of seat and couchette prices).
        Requires routes and current_availability tables (run Alembic migrations on test DB).
        """
        if not _tables_exist():
            self.skipTest("routes and current_availability tables required; run Alembic on test DB")
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

        now = timezone.now()
        CurrentAvailability.objects.create(
            route=route,
            is_couchette=True,
            price=49.99,
            currency="EUR",
            last_scraped_at=now,
            last_seen_available_at=now
        )
        CurrentAvailability.objects.create(
            route=route,
            is_couchette=False,
            price=29.99,
            currency="EUR",
            last_scraped_at=now,
            last_seen_available_at=now
        )

        routes = _get_routes_with_best_price(
            ["PRAHA HL. N."], ["Amsterdam CS"], "any"
        )
        results = list(routes)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].latest_price, 29.99)
        self.assertEqual(results[0].latest_currency, "EUR")
