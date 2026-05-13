"""Tests for study_planner.timeline."""
from datetime import date

import pytest

from study_planner.models import ResearchMethod
from study_planner.scoper import scope_phases
from study_planner.timeline import add_working_days, assign_dates, next_working_day


def test_add_working_days_simple():
    # Monday + 5 working days = Friday
    monday = date(2026, 1, 5)  # Monday
    result = add_working_days(monday, 5)
    assert result == date(2026, 1, 9)  # Friday


def test_add_working_days_skips_weekend():
    # Friday = day 1, Monday = day 2 → result is Monday
    friday = date(2026, 1, 9)  # Friday
    result = add_working_days(friday, 2)
    assert result == date(2026, 1, 12)  # Monday (Friday=1, Monday=2)


def test_add_working_days_single_day():
    monday = date(2026, 1, 5)
    assert add_working_days(monday, 1) == monday


def test_next_working_day_from_friday():
    friday = date(2026, 1, 9)
    assert next_working_day(friday) == date(2026, 1, 12)  # Monday


def test_next_working_day_from_weekday():
    monday = date(2026, 1, 5)
    assert next_working_day(monday) == date(2026, 1, 6)  # Tuesday


def test_assign_dates_sequential():
    phases = scope_phases(ResearchMethod.QUALITATIVE, timeline_weeks=8)
    start = date(2026, 6, 1)  # Monday
    phases = assign_dates(phases, start)

    for i in range(len(phases) - 1):
        # Each phase must start strictly after the previous ends
        assert phases[i + 1].start_date > phases[i].end_date


def test_assign_dates_no_gaps():
    phases = scope_phases(ResearchMethod.QUALITATIVE, timeline_weeks=8)
    start = date(2026, 6, 1)
    phases = assign_dates(phases, start)
    for p in phases:
        assert p.start_date is not None
        assert p.end_date is not None
        assert p.end_date >= p.start_date


def test_assign_dates_weekend_start():
    saturday = date(2026, 6, 6)  # Saturday
    phases = scope_phases(ResearchMethod.QUANTITATIVE, timeline_weeks=6)
    phases = assign_dates(phases, saturday)
    # First phase should start on Monday
    assert phases[0].start_date.weekday() < 5


@pytest.mark.parametrize("method", list(ResearchMethod))
def test_assign_dates_all_methods(method):
    phases = scope_phases(method, timeline_weeks=10)
    start = date(2026, 7, 1)
    phases = assign_dates(phases, start)
    for p in phases:
        assert p.start_date is not None
        assert p.end_date is not None
