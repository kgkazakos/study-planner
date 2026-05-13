"""Tests for study_planner.planner — orchestration layer."""
import json
from datetime import date

import pytest

from study_planner.models import ResearchMethod, StudyBrief, StudyPlan
from study_planner.planner import generate_plan, parse_brief_file


def _brief(method: ResearchMethod = ResearchMethod.QUALITATIVE) -> StudyBrief:
    return StudyBrief(
        title="Planner Test",
        research_questions=["Why X?", "How Y?"],
        method=method,
        target_audience="Beta users",
        timeline_weeks=8,
        start_date=date(2026, 8, 1),
    )


@pytest.mark.parametrize("method", list(ResearchMethod))
def test_generate_plan_returns_study_plan(method):
    plan = generate_plan(_brief(method))
    assert isinstance(plan, StudyPlan)


@pytest.mark.parametrize("method", list(ResearchMethod))
def test_generate_plan_has_phases(method):
    plan = generate_plan(_brief(method))
    assert len(plan.phases) >= 4


@pytest.mark.parametrize("method", list(ResearchMethod))
def test_generate_plan_has_dates(method):
    plan = generate_plan(_brief(method))
    for p in plan.phases:
        assert p.start_date is not None
        assert p.end_date is not None


def test_generate_plan_rule_based_rationale():
    plan = generate_plan(_brief())
    assert plan.method_rationale is not None
    assert len(plan.method_rationale) > 20


def test_generate_plan_rule_based_risks():
    plan = generate_plan(_brief())
    assert isinstance(plan.risks, list)
    assert len(plan.risks) == 3


def test_generate_plan_rule_based_recommendations():
    plan = generate_plan(_brief())
    assert isinstance(plan.recommendations, list)
    assert len(plan.recommendations) == 3


def test_generate_plan_not_llm_enriched():
    plan = generate_plan(_brief(), llm_backend=None)
    assert plan.llm_enriched is False


def test_generate_plan_none_backend_string():
    plan = generate_plan(_brief(), llm_backend="none")
    assert plan.llm_enriched is False


def test_generate_plan_serialisable():
    plan = generate_plan(_brief())
    serialised = plan.to_json()
    data = json.loads(serialised)
    assert "brief" in data
    assert "phases" in data
    assert "resources" in data


def test_parse_brief_file(tmp_path):
    brief_file = tmp_path / "brief.txt"
    brief_file.write_text(
        "title: Parse Test\n"
        "method: mixed\n"
        "audience: Enterprise teams\n"
        "weeks: 10\n"
        "team: 2\n"
        "budget: 15000\n"
        "questions:\n"
        "How do teams collaborate?\n"
        "What breaks down under load?\n"
    )
    data = parse_brief_file(str(brief_file))
    assert data["title"] == "Parse Test"
    assert data["method"] == "mixed"
    assert len(data["research_questions"]) == 2
    assert data["budget"] == "15000"
