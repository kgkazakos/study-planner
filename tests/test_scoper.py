"""Tests for study_planner.scoper."""
import pytest

from study_planner.models import ResearchMethod
from study_planner.scoper import scope_phases


@pytest.mark.parametrize("method", list(ResearchMethod))
def test_scope_phases_returns_phases(method):
    phases = scope_phases(method, timeline_weeks=8)
    assert len(phases) >= 4
    assert all(p.name for p in phases)
    assert all(p.duration_days >= 3 for p in phases)


@pytest.mark.parametrize("method", list(ResearchMethod))
def test_scope_phases_total_days_proportional(method):
    phases_8 = scope_phases(method, timeline_weeks=8)
    phases_12 = scope_phases(method, timeline_weeks=12)
    total_8 = sum(p.duration_days for p in phases_8)
    total_12 = sum(p.duration_days for p in phases_12)
    assert total_12 > total_8


def test_qual_phases_have_expected_names():
    phases = scope_phases(ResearchMethod.QUALITATIVE, timeline_weeks=8)
    names = [p.name for p in phases]
    assert any("Planning" in n for n in names)
    assert any("Analysis" in n for n in names)
    assert any("Report" in n or "Synthesis" in n for n in names)


def test_quant_phases_have_expected_names():
    phases = scope_phases(ResearchMethod.QUANTITATIVE, timeline_weeks=8)
    names = [p.name for p in phases]
    assert any("Instrument" in n or "Design" in n for n in names)
    assert any("Field" in n or "Recruit" in n for n in names)
    assert any("Analysis" in n for n in names)


def test_mixed_phases_have_expected_names():
    phases = scope_phases(ResearchMethod.MIXED, timeline_weeks=12)
    names = [p.name for p in phases]
    assert any("Qualitative" in n or "Qual" in n for n in names)
    assert any("Quantitative" in n or "Quant" in n for n in names)


def test_phases_have_tasks_and_deliverables():
    for method in ResearchMethod:
        phases = scope_phases(method, timeline_weeks=8)
        for p in phases:
            assert len(p.tasks) >= 1, f"{p.name} has no tasks"
            assert len(p.deliverables) >= 1, f"{p.name} has no deliverables"


def test_minimum_duration_enforced():
    # Even with 4 weeks, no phase should be shorter than 3 days
    for method in ResearchMethod:
        phases = scope_phases(method, timeline_weeks=4)
        for p in phases:
            assert p.duration_days >= 3
