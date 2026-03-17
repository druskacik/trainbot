from datetime import date, datetime
import json
from types import SimpleNamespace
from unittest.mock import patch

from django.db import connection
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.utils import timezone

from .cities import NIGHTJET_BOOKING_URL, build_booking_url, get_station_names
from .models import CurrentAvailability, Route
from .views import _get_routes_with_best_price, get_stations, search_trips


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

    def test_routes_in_the_past_are_filtered_out(self):
        if not _tables_exist():
            self.skipTest("routes and current_availability tables required; run Alembic on test DB")

        now = timezone.now()
        future_route = Route.objects.create(
            id="test-route-future",
            source="test",
            train_number="452",
            departure_station="PRAHA HL. N.",
            arrival_station="Amsterdam CS",
            travel_date=now.date(),
            departure_time=now + timezone.timedelta(hours=2),
            arrival_time=now + timezone.timedelta(hours=12),
        )
        past_route = Route.objects.create(
            id="test-route-past",
            source="test",
            train_number="453",
            departure_station="PRAHA HL. N.",
            arrival_station="Amsterdam CS",
            travel_date=now.date(),
            departure_time=now - timezone.timedelta(hours=2),
            arrival_time=now + timezone.timedelta(hours=8),
        )

        for route in (future_route, past_route):
            CurrentAvailability.objects.create(
                route=route,
                is_couchette=False,
                price=39.99,
                currency="EUR",
                last_scraped_at=now,
                last_seen_available_at=now,
            )

        results = list(
            _get_routes_with_best_price(
                ["PRAHA HL. N."], ["Amsterdam CS"], "seat"
            )
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, future_route.id)


class CityCatalogTest(SimpleTestCase):
    def test_prague_aliases_include_provider_variants(self):
        aliases = get_station_names("prague")

        self.assertIn("PRAHA HL. N.", aliases)
        self.assertIn("Praha hl.n.", aliases)
        self.assertIn("Prague Main Station", aliases)
        self.assertIn("Prague-Holesovice", aliases)

    def test_nightjet_booking_url_uses_direct_booking_parameters(self):
        booking_url = build_booking_url(
            "nightjet",
            "prague",
            "vienna",
            date(2026, 3, 21),
            datetime(2026, 3, 21, 21, 58),
        )

        self.assertTrue(booking_url.startswith(NIGHTJET_BOOKING_URL))
        self.assertIn("stationOrigEva=5496001", booking_url)
        self.assertIn("stationDestEva=1190100", booking_url)
        self.assertIn("outwardDateTime=2026-03-21T21%3A58", booking_url)

    def test_european_sleeper_booking_url_uses_city_mapping(self):
        booking_url = build_booking_url(
            "europeansleeper",
            "prague",
            "amsterdam",
            date(2026, 3, 21),
            return_date=date(2026, 3, 28),
        )

        self.assertIn("departureStation=5457076", booking_url)
        self.assertIn("arrivalStation=8400058", booking_url)
        self.assertIn("departureDate=2026-03-21", booking_url)
        self.assertIn("returnDate=2026-03-28", booking_url)


class SearchTripsViewTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _json(self, response):
        return json.loads(response.content)

    def test_get_stations_returns_city_options(self):
        response = get_stations(self.factory.get("/api/stations"))
        payload = self._json(response)

        self.assertEqual(payload["status"], "success")
        self.assertIn({"id": "prague", "name": "Prague"}, payload["data"])
        self.assertNotIn({"id": "5457076", "name": "Praha hl.n."}, payload["data"])

    @patch("ui.views._get_routes_with_best_price")
    def test_single_search_returns_results_from_multiple_providers(self, mock_get_routes):
        mock_get_routes.return_value = [
            SimpleNamespace(
                travel_date=date(2026, 3, 21),
                departure_time=datetime(2026, 3, 21, 19, 22),
                latest_price=39.99,
                latest_currency="EUR",
                source="europeansleeper",
            ),
            SimpleNamespace(
                travel_date=date(2026, 3, 21),
                departure_time=datetime(2026, 3, 21, 21, 58),
                latest_price=49.99,
                latest_currency="EUR",
                source="nightjet",
            ),
        ]

        response = search_trips(
            self.factory.get(
                "/api/search",
                {"start_id": "prague", "end_id": "berlin", "type": "single", "seat_type": "any"},
            )
        )
        payload = self._json(response)

        self.assertEqual(payload["status"], "success")
        self.assertEqual(len(payload["routes"]), 2)
        european_sleeper_trip = payload["routes"][0]
        nightjet_trip = payload["routes"][1]

        self.assertEqual(european_sleeper_trip["outbound_provider"], "europeansleeper")
        self.assertEqual(european_sleeper_trip["outbound_booking_url"].split("?")[0], "https://booking.europeansleeper.eu/en")
        self.assertEqual(european_sleeper_trip["outbound_leg"]["booking_mode"], "direct")
        self.assertEqual(european_sleeper_trip["outbound_leg"]["booking_details"]["from_city"], "Prague")
        self.assertEqual(european_sleeper_trip["outbound_leg"]["booking_details"]["to_city"], "Berlin")
        self.assertEqual(european_sleeper_trip["primary_booking_url"], european_sleeper_trip["outbound_booking_url"])

        self.assertEqual(nightjet_trip["outbound_provider"], "nightjet")
        self.assertTrue(nightjet_trip["outbound_booking_url"].startswith(NIGHTJET_BOOKING_URL))
        self.assertIn("stationOrigEva=5496001", nightjet_trip["outbound_booking_url"])
        self.assertIn("stationDestEva=8096003", nightjet_trip["outbound_booking_url"])
        self.assertIn("outwardDateTime=2026-03-21T21%3A58", nightjet_trip["outbound_booking_url"])
        self.assertEqual(nightjet_trip["outbound_leg"]["booking_mode"], "direct")
        self.assertEqual(nightjet_trip["outbound_leg"]["booking_details"]["from_city"], "Prague")
        self.assertEqual(nightjet_trip["outbound_leg"]["booking_details"]["to_city"], "Berlin")
        self.assertEqual(nightjet_trip["primary_booking_url"], nightjet_trip["outbound_booking_url"])

        outbound_aliases, arrival_aliases, seat_type = mock_get_routes.call_args.args
        self.assertIn("Praha hl.n.", outbound_aliases)
        self.assertIn("Berlin Hbf (Tiefgeschoß)", arrival_aliases)
        self.assertEqual(seat_type, "any")

    @patch("ui.views._get_routes_with_best_price")
    def test_return_search_supports_mixed_providers(self, mock_get_routes):
        outbound_routes = [
            SimpleNamespace(
                travel_date=date(2026, 3, 21),
                departure_time=datetime(2026, 3, 21, 19, 22),
                latest_price=39.99,
                latest_currency="EUR",
                source="europeansleeper",
            )
        ]
        return_routes = [
            SimpleNamespace(
                travel_date=date(2026, 3, 25),
                departure_time=datetime(2026, 3, 25, 22, 10),
                latest_price=59.99,
                latest_currency="EUR",
                source="nightjet",
            )
        ]
        mock_get_routes.side_effect = [outbound_routes, return_routes]

        response = search_trips(
            self.factory.get(
                "/api/search",
                {
                    "start_id": "prague",
                    "end_id": "vienna",
                    "type": "return",
                    "max_duration": "14",
                    "seat_type": "any",
                },
            )
        )
        payload = self._json(response)

        self.assertEqual(payload["status"], "success")
        self.assertEqual(len(payload["routes"]), 1)
        result = payload["routes"][0]
        self.assertTrue(result["mixed_providers"])
        self.assertEqual(result["outbound_provider"], "europeansleeper")
        self.assertEqual(result["return_provider"], "nightjet")
        self.assertTrue(result["return_booking_url"].startswith(NIGHTJET_BOOKING_URL))
        self.assertIn("stationOrigEva=1190100", result["return_booking_url"])
        self.assertIn("stationDestEva=5496001", result["return_booking_url"])
        self.assertIn("outwardDateTime=2026-03-25T22%3A10", result["return_booking_url"])
        self.assertEqual(result["outbound_leg"]["booking_mode"], "direct")
        self.assertEqual(result["return_leg"]["booking_mode"], "direct")
        self.assertEqual(result["return_leg"]["booking_details"]["from_city"], "Vienna")
        self.assertEqual(result["return_leg"]["booking_details"]["to_city"], "Prague")
        self.assertEqual(result["primary_booking_url"], result["outbound_booking_url"])
        self.assertEqual(result["secondary_booking_url"], result["return_booking_url"])

    @patch("ui.views._get_routes_with_best_price")
    def test_return_search_uses_combined_european_sleeper_booking_url(self, mock_get_routes):
        outbound_routes = [
            SimpleNamespace(
                travel_date=date(2026, 3, 21),
                departure_time=datetime(2026, 3, 21, 19, 22),
                latest_price=39.99,
                latest_currency="EUR",
                source="europeansleeper",
            )
        ]
        return_routes = [
            SimpleNamespace(
                travel_date=date(2026, 3, 25),
                departure_time=datetime(2026, 3, 25, 18, 16),
                latest_price=49.99,
                latest_currency="EUR",
                source="europeansleeper",
            )
        ]
        mock_get_routes.side_effect = [outbound_routes, return_routes]

        response = search_trips(
            self.factory.get(
                "/api/search",
                {
                    "start_id": "prague",
                    "end_id": "amsterdam",
                    "type": "return",
                    "max_duration": "14",
                    "seat_type": "any",
                },
            )
        )
        payload = self._json(response)

        self.assertEqual(payload["status"], "success")
        result = payload["routes"][0]
        self.assertFalse(result["mixed_providers"])
        self.assertIn("departureDate=2026-03-21", result["primary_booking_url"])
        self.assertIn("returnDate=2026-03-25", result["primary_booking_url"])
        self.assertIsNone(result["secondary_booking_url"])
        self.assertEqual(result["outbound_leg"]["booking_mode"], "direct")
        self.assertEqual(result["return_leg"]["booking_mode"], "direct")
