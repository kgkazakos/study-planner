"""Rule-based rationale, risks, and recommendations per research method."""
from __future__ import annotations

from study_planner.models import ResearchMethod

_RATIONALES: dict[ResearchMethod, str] = {
    ResearchMethod.QUALITATIVE: (
        "A qualitative approach surfaces the nuanced behaviours, motivations, and mental models "
        "that structured surveys cannot capture. Moderated sessions allow the research team to probe "
        "unexpected directions and build a rich explanatory model of the problem space — making this "
        "method the right fit when the 'why' matters as much as the 'what'."
    ),
    ResearchMethod.QUANTITATIVE: (
        "A quantitative approach enables the team to measure the prevalence and statistical significance "
        "of observed patterns across a representative sample. This method is best suited for validating "
        "hypotheses, benchmarking metrics against baselines, and producing generalisable findings that "
        "can inform product decisions with statistical confidence."
    ),
    ResearchMethod.MIXED: (
        "A mixed-methods design leverages the complementary strengths of both qualitative and "
        "quantitative inquiry. Qualitative interviews generate hypotheses and surface the 'why' "
        "behind behaviours; quantitative fielding tests those hypotheses at scale and provides "
        "statistically robust prevalence estimates. Integration of both strands produces richer, "
        "more defensible insights than either approach alone."
    ),
}

_RISKS: dict[ResearchMethod, list[str]] = {
    ResearchMethod.QUALITATIVE: [
        "Recruitment delays — panel fatigue or a narrow screener can extend fielding by 1–2 weeks; "
        "build buffer into the recruitment phase",
        "Insufficient saturation — with fewer than 10 participants, theme coverage may be incomplete; "
        "use saturation-meter (CPR #8) to monitor coverage during analysis",
        "Interviewer bias — leading or loaded questions can skew findings; review the guide with "
        "qual-sniffer (CPR #3) before fielding",
    ],
    ResearchMethod.QUANTITATIVE: [
        "Response quality — speeders and straight-liners inflate noise; apply survey-cleaner (CPR #4) "
        "post-field and enforce minimum completion time thresholds",
        "Low completion rate — overly long or complex instruments reduce response rates; keep surveys "
        "under 10 minutes and pilot before fielding",
        "Sampling bias — panel recruitment can skew toward certain demographics; monitor quotas in "
        "real time and close field if quotas diverge",
    ],
    ResearchMethod.MIXED: [
        "Integration failure — findings from each strand may not cleanly converge; plan a dedicated "
        "synthesis session before reporting to surface and resolve divergence",
        "Scope creep — dual-strand studies can expand unpredictably; establish a strict change-control "
        "process and protect the timeline with phase gates",
        "Resource strain — mixed methods require more team bandwidth; confirm capacity before fielding "
        "both strands simultaneously and consider staggering them",
    ],
}

_RECOMMENDATIONS: dict[ResearchMethod, list[str]] = {
    ResearchMethod.QUALITATIVE: [
        "Run a pilot session with an internal colleague before fielding to stress-test the discussion "
        "guide and calibrate timing",
        "Schedule a mid-study check-in after the first 4–5 sessions to assess emerging themes and "
        "adjust the guide if needed",
        "Pair with bias-audit (CPR #14) and saturation-meter (CPR #8) during analysis for a "
        "rigorous, auditable qual workflow",
    ],
    ResearchMethod.QUANTITATIVE: [
        "Run a 5-response internal pilot to catch confusing question wording before launch — "
        "fixing errors post-field is costly",
        "Use power-analyst (CPR #4.9) to validate your target sample size against the effect sizes "
        "you care about detecting",
        "Pre-register your hypotheses and analysis plan before fielding to strengthen "
        "the credibility of your findings",
    ],
    ResearchMethod.MIXED: [
        "Define your integration logic upfront — decide whether qual informs quant (sequential) "
        "or both run in parallel — and document the rationale before data collection begins",
        "Use quant-qual-bridge (CPR #28) to link quantitative segments to qualitative insight "
        "threads during the synthesis phase",
        "Allocate at least 20% of total study time to the integration phase; rushing synthesis "
        "is the most common failure mode in mixed-methods research",
    ],
}


def get_rationale(method: ResearchMethod) -> str:
    return _RATIONALES[method]


def get_risks(method: ResearchMethod) -> list[str]:
    return list(_RISKS[method])


def get_recommendations(method: ResearchMethod) -> list[str]:
    return list(_RECOMMENDATIONS[method])
