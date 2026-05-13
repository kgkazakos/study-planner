"""Rule-based phase generation for research studies."""
from __future__ import annotations

from study_planner.models import Phase, ResearchMethod

# ---------------------------------------------------------------------------
# Phase template definitions — weight = fraction of total working days
# ---------------------------------------------------------------------------

QUAL_PHASES: list[dict] = [
    {
        "name": "Planning & Guide Design",
        "weight": 0.15,
        "tasks": [
            "Define research objectives and scope",
            "Draft and peer-review discussion guide",
            "Design recruitment screener",
            "Set up scheduling and consent workflow",
        ],
        "deliverables": ["Discussion guide v1", "Recruitment screener", "Consent form"],
        "owner": "Lead Researcher",
    },
    {
        "name": "Recruitment",
        "weight": 0.15,
        "tasks": [
            "Launch recruitment ads or engage panel provider",
            "Screen and qualify applicants",
            "Schedule and confirm sessions",
            "Send pre-study participant briefing",
        ],
        "deliverables": ["Confirmed participant list", "Session schedule"],
        "owner": "Research Coordinator",
    },
    {
        "name": "Data Collection",
        "weight": 0.25,
        "tasks": [
            "Conduct moderated sessions",
            "Capture observer notes in real time",
            "Collect signed consent forms",
            "Back up recordings and raw transcripts",
        ],
        "deliverables": ["Session recordings", "Observer notes", "Raw transcripts"],
        "owner": "Lead Researcher",
    },
    {
        "name": "Analysis",
        "weight": 0.25,
        "tasks": [
            "Clean and review transcripts",
            "Open coding pass across all sessions",
            "Thematic clustering and affinity mapping",
            "Validate themes with second coder",
        ],
        "deliverables": ["Coded transcripts", "Theme map", "Key insights draft"],
        "owner": "Lead Researcher",
    },
    {
        "name": "Synthesis & Reporting",
        "weight": 0.20,
        "tasks": [
            "Write research report with evidence citations",
            "Create executive summary (one-pager)",
            "Build stakeholder slide deck",
            "Present findings and capture feedback",
        ],
        "deliverables": ["Full research report", "Executive summary", "Stakeholder deck"],
        "owner": "Lead Researcher",
    },
]

QUANT_PHASES: list[dict] = [
    {
        "name": "Instrument Design & Pilot",
        "weight": 0.20,
        "tasks": [
            "Define hypotheses and key metrics",
            "Design survey or measurement instrument",
            "Pilot test with 5–10 internal respondents",
            "Revise instrument based on pilot feedback",
        ],
        "deliverables": ["Survey instrument v1", "Pilot debrief notes"],
        "owner": "Lead Researcher",
    },
    {
        "name": "Recruitment & Fielding",
        "weight": 0.30,
        "tasks": [
            "Define sampling frame and quota targets",
            "Launch survey via panel or product surface",
            "Monitor response quality in real time",
            "Close field when target N is reached",
        ],
        "deliverables": ["Raw response dataset", "Fielding progress log"],
        "owner": "Research Operations",
    },
    {
        "name": "Data Cleaning",
        "weight": 0.15,
        "tasks": [
            "Remove speeders, straight-liners, and gibberish open-ends",
            "Verify quota balance across key demographics",
            "Flag and exclude low-quality responses",
            "Export clean, analysis-ready dataset",
        ],
        "deliverables": ["Clean dataset", "Data quality report"],
        "owner": "Lead Researcher",
    },
    {
        "name": "Analysis",
        "weight": 0.20,
        "tasks": [
            "Descriptive statistics and cross-tabulations",
            "Inferential testing (t-test, ANOVA, regression)",
            "Effect size calculation and power check",
            "Open-end thematic coding",
        ],
        "deliverables": ["Analysis file", "Statistical summary", "Key findings draft"],
        "owner": "Lead Researcher",
    },
    {
        "name": "Reporting",
        "weight": 0.15,
        "tasks": [
            "Write findings narrative with data visualisations",
            "Prepare stakeholder summary slide deck",
            "Circulate report for internal review",
            "Incorporate feedback and publish final version",
        ],
        "deliverables": ["Research report", "Executive summary", "Stakeholder deck"],
        "owner": "Lead Researcher",
    },
]

MIXED_PHASES: list[dict] = [
    {
        "name": "Planning & Design",
        "weight": 0.12,
        "tasks": [
            "Define integration strategy (concurrent vs. sequential)",
            "Design qualitative discussion guide and quantitative instrument",
            "Align timelines across both research strands",
            "Set up consent, data governance, and storage workflow",
        ],
        "deliverables": ["Study design doc", "Discussion guide", "Survey instrument", "Consent form"],
        "owner": "Lead Researcher",
    },
    {
        "name": "Qualitative Data Collection",
        "weight": 0.20,
        "tasks": [
            "Recruit and schedule interview participants",
            "Conduct moderated qualitative sessions",
            "Capture observer notes and raw transcripts",
        ],
        "deliverables": ["Session recordings", "Raw transcripts", "Observer notes"],
        "owner": "Lead Researcher",
    },
    {
        "name": "Quantitative Fielding",
        "weight": 0.18,
        "tasks": [
            "Launch survey to target population via panel",
            "Monitor response rates and quality metrics",
            "Close field at target N and export raw data",
        ],
        "deliverables": ["Raw survey dataset", "Fielding log"],
        "owner": "Research Operations",
    },
    {
        "name": "Parallel Analysis",
        "weight": 0.25,
        "tasks": [
            "Qualitative: thematic coding and affinity mapping",
            "Quantitative: data cleaning, descriptive stats, inferential tests",
            "Identify convergence and divergence points across strands",
        ],
        "deliverables": ["Coded transcripts", "Clean dataset", "Convergence / divergence map"],
        "owner": "Lead Researcher",
    },
    {
        "name": "Integration & Reporting",
        "weight": 0.25,
        "tasks": [
            "Synthesise qual and quant findings in a unified narrative",
            "Write integrated research report with evidence matrix",
            "Create stakeholder deck with mixed evidence",
            "Present and gather feedback from key stakeholders",
        ],
        "deliverables": ["Integrated research report", "Executive summary", "Stakeholder deck"],
        "owner": "Lead Researcher",
    },
]

_TEMPLATE_MAP: dict[ResearchMethod, list[dict]] = {
    ResearchMethod.QUALITATIVE: QUAL_PHASES,
    ResearchMethod.QUANTITATIVE: QUANT_PHASES,
    ResearchMethod.MIXED: MIXED_PHASES,
}


def scope_phases(method: ResearchMethod, timeline_weeks: int) -> list[Phase]:
    """Generate a list of research phases scaled to the given timeline."""
    templates = _TEMPLATE_MAP[method]
    total_days = timeline_weeks * 5  # working days
    phases: list[Phase] = []
    for t in templates:
        duration = max(3, round(t["weight"] * total_days))
        phases.append(
            Phase(
                name=t["name"],
                duration_days=duration,
                tasks=list(t["tasks"]),
                deliverables=list(t["deliverables"]),
                owner=t.get("owner", "Researcher"),
            )
        )
    return phases
