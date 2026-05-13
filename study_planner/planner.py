"""Orchestration: combines scoper, timeline, resources, defaults, and enricher."""
from __future__ import annotations

from datetime import date
from typing import Optional

from study_planner.defaults import get_rationale, get_recommendations, get_risks
from study_planner.models import StudyBrief, StudyPlan
from study_planner.resources import estimate_resources
from study_planner.scoper import scope_phases
from study_planner.timeline import assign_dates


def generate_plan(
    brief: StudyBrief,
    llm_backend: Optional[str] = None,
) -> StudyPlan:
    """Generate a complete StudyPlan from a StudyBrief.

    Parameters
    ----------
    brief:
        Populated StudyBrief with all study parameters.
    llm_backend:
        Optional DSPy-compatible model string, e.g. ``"openai/gpt-4o-mini"``.
        When provided (and dspy-ai / litellm are installed), the plan is
        enriched with LLM-generated rationale, risks, and phase guidance.
        Enriched fields fall back to rule-based values when omitted or when
        the backend is ``None`` / ``"none"``.
    """
    phases = scope_phases(brief.method, brief.timeline_weeks)

    start = brief.start_date or date.today()
    phases = assign_dates(phases, start)

    resources = estimate_resources(brief)

    plan = StudyPlan(
        brief=brief,
        phases=phases,
        resources=resources,
        method_rationale=get_rationale(brief.method),
        risks=get_risks(brief.method),
        recommendations=get_recommendations(brief.method),
        llm_enriched=False,
    )

    if llm_backend and llm_backend.lower() not in ("", "none"):
        from study_planner.enricher import enrich_plan

        plan = enrich_plan(plan, llm_backend)

    return plan


def parse_brief_file(path: str) -> dict:
    """Parse a plain-text brief file into a dict of kwargs for StudyBrief.

    Expected format (lines)::

        title: My Study
        method: qualitative
        audience: Mobile app users
        weeks: 8
        team: 2
        budget: 5000
        questions:
        Why do users abandon the checkout flow?
        What is the biggest friction point in onboarding?

    Lines before ``questions:`` are key-value pairs.
    Lines after ``questions:`` (or bare lines with a ``?``) are questions.
    """
    result: dict = {}
    questions: list[str] = []
    in_questions = False

    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip()
            if not line:
                continue
            if line.lower().startswith("questions:"):
                in_questions = True
                continue
            if in_questions:
                questions.append(line.lstrip("- ").strip())
            elif ":" in line:
                k, _, v = line.partition(":")
                result[k.strip().lower()] = v.strip()

    if questions:
        result["research_questions"] = questions

    return result
