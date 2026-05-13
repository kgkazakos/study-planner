"""DSPy-based LLM enrichment for study plans."""
from __future__ import annotations

try:
    import dspy as _dspy_mod

    HAS_DSPY = True
except ImportError:
    HAS_DSPY = False

from study_planner.models import StudyPlan

# ---------------------------------------------------------------------------
# DSPy Signatures (defined at module level for mock-patchability in tests)
# ---------------------------------------------------------------------------

if HAS_DSPY:
    import dspy

    class StudyRationaleSignature(dspy.Signature):
        """Generate a methodological rationale, risk register, and strategic
        recommendations for a research study plan."""

        study_title: str = dspy.InputField(desc="Title of the research study")
        research_method: str = dspy.InputField(
            desc="Research method: qualitative, quantitative, or mixed"
        )
        research_questions: str = dspy.InputField(
            desc="Research questions, newline-separated"
        )
        target_audience: str = dspy.InputField(desc="Target participant audience")
        timeline_weeks: str = dspy.InputField(desc="Total study timeline in weeks")

        method_rationale: str = dspy.OutputField(
            desc="2–3 sentence methodological rationale explaining why this method fits the questions"
        )
        risks: str = dspy.OutputField(
            desc="3 key risks as newline-separated plain sentences (no bullets or numbers)"
        )
        recommendations: str = dspy.OutputField(
            desc="3 strategic recommendations as newline-separated plain sentences (no bullets or numbers)"
        )

    class PhaseGuidanceSignature(dspy.Signature):
        """Generate a practical guidance note for a specific research phase."""

        phase_name: str = dspy.InputField()
        phase_tasks: str = dspy.InputField(desc="Tasks in this phase, newline-separated")
        study_context: str = dspy.InputField(
            desc="Brief study context: title | method | target audience"
        )

        guidance: str = dspy.OutputField(
            desc="1–2 sentence practical tip or watch-out specific to this phase and study"
        )

else:
    StudyRationaleSignature = None  # type: ignore[assignment,misc]
    PhaseGuidanceSignature = None  # type: ignore[assignment,misc]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _configure_llm(backend: str) -> None:
    import litellm

    litellm.drop_params = True
    lm = _dspy_mod.LM(backend)
    _dspy_mod.configure(lm=lm)


def enrich_plan(plan: StudyPlan, backend: str) -> StudyPlan:
    """Enrich *plan* in-place with LLM-generated rationale, risks,
    recommendations, and per-phase guidance notes.

    Raises ``ImportError`` when dspy-ai / litellm are not installed.
    """
    if not HAS_DSPY:
        raise ImportError(
            "dspy-ai and litellm are required for LLM enrichment. "
            "Install with: pip install dspy-ai litellm"
        )

    _configure_llm(backend)

    study_context = (
        f"{plan.brief.title} | {plan.brief.method.value} | {plan.brief.target_audience}"
    )

    # Generate top-level rationale, risks, and recommendations
    rationale_module = _dspy_mod.ChainOfThought(StudyRationaleSignature)
    result = rationale_module(
        study_title=plan.brief.title,
        research_method=plan.brief.method.value,
        research_questions="\n".join(plan.brief.research_questions),
        target_audience=plan.brief.target_audience,
        timeline_weeks=str(plan.brief.timeline_weeks),
    )

    plan.method_rationale = result.method_rationale.strip()
    plan.risks = [
        line.strip()
        for line in result.risks.strip().splitlines()
        if line.strip()
    ][:5]
    plan.recommendations = [
        line.strip()
        for line in result.recommendations.strip().splitlines()
        if line.strip()
    ][:5]

    # Enrich each phase with practical guidance
    phase_module = _dspy_mod.ChainOfThought(PhaseGuidanceSignature)
    for phase in plan.phases:
        phase_result = phase_module(
            phase_name=phase.name,
            phase_tasks="\n".join(phase.tasks),
            study_context=study_context,
        )
        phase.notes = phase_result.guidance.strip()

    plan.llm_enriched = True
    return plan
