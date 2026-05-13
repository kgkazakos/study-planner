"""Working-day date assignment for study phases."""
from __future__ import annotations

from datetime import date, timedelta

from study_planner.models import Phase


def add_working_days(start: date, n: int) -> date:
    """Return the date that is exactly n working days (Mon–Fri) after start,
    counting start itself as day 1."""
    current = start
    count = 1
    while count < n:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Mon–Fri
            count += 1
    return current


def next_working_day(d: date) -> date:
    """Return the next working day after d."""
    candidate = d + timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate += timedelta(days=1)
    return candidate


def assign_dates(phases: list[Phase], start_date: date) -> list[Phase]:
    """Mutate phases in-place, assigning start_date and end_date to each."""
    cursor = start_date
    # Advance to the first working day if start falls on a weekend
    while cursor.weekday() >= 5:
        cursor += timedelta(days=1)

    for phase in phases:
        phase.start_date = cursor
        phase.end_date = add_working_days(cursor, phase.duration_days)
        cursor = next_working_day(phase.end_date)

    return phases
