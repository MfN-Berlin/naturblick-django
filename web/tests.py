import json

from datetime import datetime as dt
from django.test import TestCase
from web.utils import from_time

class UtilsTestCase(TestCase):
    def test_from_today(self):
        t = dt.fromisoformat("2026-05-05 12:00:00")
        now = dt.fromisoformat("2026-05-05 11:00:00")
        self.assertEqual(from_time(t, now), "neulich")

    def test_from_last_week(self):
        t = dt.fromisoformat("2026-05-05 12:00:00")
        now = dt.fromisoformat("2026-04-30 11:00:00")
        self.assertEqual(from_time(t, now), "neulich")

    def test_from_last_month(self):
        t = dt.fromisoformat("2026-05-05 12:00:00")
        now = dt.fromisoformat("2026-04-05 11:00:00")
        self.assertEqual(from_time(t, now), "neulich")

    def test_from_2_months_ago(self):
        t = dt.fromisoformat("2026-05-05 12:00:00")
        now = dt.fromisoformat("2026-03-05 11:00:00")
        self.assertEqual(from_time(t, now), "vor 2 Monaten")

    def test_from_7_months_ago(self):
        t = dt.fromisoformat("2026-05-05 12:00:00")
        now = dt.fromisoformat("2025-10-05 11:00:00")
        self.assertEqual(from_time(t, now), "vor 7 Monaten")

    def test_from_a_year_ago(self):
        t = dt.fromisoformat("2026-05-05 12:00:00")
        now = dt.fromisoformat("2025-05-05 11:00:00")
        self.assertEqual(from_time(t, now), "vor einem Jahr")

    def test_from_many_years_ago(self):
        t = dt.fromisoformat("2026-05-05 12:00:00")
        now = dt.fromisoformat("2022-05-05 11:00:00")
        self.assertEqual(from_time(t, now), "vor 4 Jahren")
