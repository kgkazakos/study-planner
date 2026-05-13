"""Tests for study_planner.resources."""
import pytest

from study_planner.models import ResearchMethod, StudyBrief
from study_planner.resources import estimate_resources


def _brief(method: ResearchMethod, team: int = 1) -> StudyBrief:
    return StudyBrief(
        title="Test",
        research_questions=["Q?"],
        method=method,
        target_audience="Users",
        team_size=team,
    )


@pytest.mark.parametrize("method", list(ResearchMethod))
def test_estimate_returns_resource_estimate(method):
    r = estimate_resources(_brief(method))
    assert r.researcher_hours > 0
    assert r.participant_count > 0
    assert r.incentive_budget_usd >= 0


def test_qual_participant_scales_with_team():
    r1 = estimate_resources(_brief(ResearchMethod.QUALITATIVE, team=1))
    r3 = estimate_resources(_brief(ResearchMethod.QUALITATIVE, team=3))
    assert r3.participant_count > r1.participant_count


def test_qual_participant_capped_at_20():
    r = estimate_resources(_brief(ResearchMethod.QUALITATIVE, team=6))
    assert r.participant_count <= 20


def test_quant_large_participant_count():
    r = estimate_resources(_brief(ResearchMethod.QUANTITATIVE))
    assert r.participant_count >= 100


def test_mixed_combines_both_arms():
    r = estimate_resources(_brief(ResearchMethod.MIXED))
    # Mixed should have more participants than qual alone
    r_qual = estimate_resources(_brief(ResearchMethod.QUALITATIVE))
    assert r.participant_count > r_qual.participant_count


def test_total_cost_includes_buffer():
    r = estimate_resources(_brief(ResearchMethod.QUALITATIVE))
    base = r.estimated_researcher_cost_usd + r.incentive_budget_usd
    assert r.total_cost_estimate_usd > base


@pytest.mark.parametrize("method", list(ResearchMethod))
def test_tooling_notes_non_empty(method):
    r = estimate_resources(_brief(method))
    assert len(r.tooling_notes) >= 2


@pytest.mark.parametrize("method", list(ResearchMethod))
def test_to_dict_complete(method):
    r = estimate_resources(_brief(method))
    d = r.to_dict()
    required_keys = {
        "researcher_hours",
        "participant_count",
        "incentive_budget_usd",
        "estimated_researcher_cost_usd",
        "total_cost_estimate_usd",
        "tooling_notes",
    }
    assert required_keys <= set(d.keys())
