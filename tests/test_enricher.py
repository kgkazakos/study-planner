"""Tests for study_planner.enricher (LLM calls fully mocked)."""
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from study_planner.models import ResearchMethod, StudyBrief, StudyPlan
from study_planner.planner import generate_plan


def _make_plan(method: ResearchMethod = ResearchMethod.QUALITATIVE) -> StudyPlan:
    brief = StudyBrief(
        title="Mock Study",
        research_questions=["Why do users churn?"],
        method=method,
        target_audience="Mobile users",
        timeline_weeks=8,
        start_date=date(2026, 6, 1),
    )
    return generate_plan(brief, llm_backend=None)


def _mock_rationale_result() -> MagicMock:
    result = MagicMock()
    result.method_rationale = "Qualitative is ideal for surfacing nuanced motivations."
    result.risks = "Risk one\nRisk two\nRisk three"
    result.recommendations = "Rec one\nRec two\nRec three"
    return result


def _mock_phase_result() -> MagicMock:
    result = MagicMock()
    result.guidance = "Ensure a thorough pilot before fielding."
    return result


@patch("study_planner.enricher._dspy_mod")
@patch("study_planner.enricher.HAS_DSPY", True)
def test_enrich_plan_sets_llm_enriched(mock_dspy):
    plan = _make_plan()

    mock_cot = MagicMock()
    mock_cot.side_effect = [_mock_rationale_result()] + [
        _mock_phase_result() for _ in plan.phases
    ]
    mock_dspy.ChainOfThought.return_value = mock_cot
    mock_dspy.LM.return_value = MagicMock()

    from study_planner.enricher import enrich_plan

    enriched = enrich_plan(plan, backend="openai/gpt-4o-mini")
    assert enriched.llm_enriched is True


@patch("study_planner.enricher._dspy_mod")
@patch("study_planner.enricher.HAS_DSPY", True)
def test_enrich_plan_sets_rationale(mock_dspy):
    plan = _make_plan()

    mock_cot = MagicMock()
    mock_cot.side_effect = [_mock_rationale_result()] + [
        _mock_phase_result() for _ in plan.phases
    ]
    mock_dspy.ChainOfThought.return_value = mock_cot
    mock_dspy.LM.return_value = MagicMock()

    from study_planner.enricher import enrich_plan

    enriched = enrich_plan(plan, backend="openai/gpt-4o-mini")
    assert "qualitative" in enriched.method_rationale.lower()


@patch("study_planner.enricher._dspy_mod")
@patch("study_planner.enricher.HAS_DSPY", True)
def test_enrich_plan_parses_risks_list(mock_dspy):
    plan = _make_plan()

    mock_cot = MagicMock()
    mock_cot.side_effect = [_mock_rationale_result()] + [
        _mock_phase_result() for _ in plan.phases
    ]
    mock_dspy.ChainOfThought.return_value = mock_cot
    mock_dspy.LM.return_value = MagicMock()

    from study_planner.enricher import enrich_plan

    enriched = enrich_plan(plan, backend="openai/gpt-4o-mini")
    assert isinstance(enriched.risks, list)
    assert len(enriched.risks) == 3


@patch("study_planner.enricher._dspy_mod")
@patch("study_planner.enricher.HAS_DSPY", True)
def test_enrich_plan_sets_phase_notes(mock_dspy):
    plan = _make_plan()

    mock_cot = MagicMock()
    mock_cot.side_effect = [_mock_rationale_result()] + [
        _mock_phase_result() for _ in plan.phases
    ]
    mock_dspy.ChainOfThought.return_value = mock_cot
    mock_dspy.LM.return_value = MagicMock()

    from study_planner.enricher import enrich_plan

    enriched = enrich_plan(plan, backend="openai/gpt-4o-mini")
    for phase in enriched.phases:
        assert phase.notes is not None
        assert len(phase.notes) > 0


@patch("study_planner.enricher.HAS_DSPY", False)
def test_enrich_plan_raises_when_dspy_missing():
    plan = _make_plan()
    from study_planner.enricher import enrich_plan

    with pytest.raises(ImportError, match="dspy-ai"):
        enrich_plan(plan, backend="openai/gpt-4o-mini")


def test_generate_plan_no_backend_not_enriched():
    plan = _make_plan()
    assert plan.llm_enriched is False
    assert plan.method_rationale is not None  # rule-based fallback
