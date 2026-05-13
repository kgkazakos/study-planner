"""Resource estimation for research studies."""
from __future__ import annotations

from study_planner.models import ResearchMethod, ResourceEstimate, StudyBrief

# ---------------------------------------------------------------------------
# Defaults per method
# ---------------------------------------------------------------------------

_QUAL_DEFAULTS = {
    "base_participants": 12,
    "session_hours": 1.0,
    "transcription_hours_per_session": 1.5,
    "analysis_hours_per_participant": 0.75,
    "report_hours": 20.0,
    "incentive_per_participant_usd": 75.0,
    "sessions_per_participant": 1,
    "tooling_notes": [
        "Zoom or Teams for remote moderated sessions",
        "Otter.ai or Descript for transcription",
        "Dovetail or Miro for thematic analysis",
        "Calendly or Doodle for session scheduling",
    ],
}

_QUANT_DEFAULTS = {
    "base_participants": 200,
    "analysis_hours_per_response": 0.05,
    "instrument_and_cleaning_hours": 15.0,
    "report_hours": 25.0,
    "incentive_per_participant_usd": 10.0,
    "sessions_per_participant": 1,
    "tooling_notes": [
        "Qualtrics, SurveyMonkey, or Typeform for fielding",
        "Python / R or SPSS for statistical analysis",
        "Lucid, Dynata, or Prolific for panel recruitment",
        "power-analyst (CPR #4.9) for sample size validation",
    ],
}

_MIXED_DEFAULTS = {
    "qual_participants": 12,
    "quant_participants": 150,
    "session_hours": 1.0,
    "transcription_hours_per_session": 1.5,
    "analysis_hours_per_qual_participant": 0.75,
    "analysis_hours_per_quant_response": 0.05,
    "integration_overhead_hours": 10.0,
    "report_hours": 30.0,
    "qual_incentive_usd": 75.0,
    "quant_incentive_usd": 10.0,
    "sessions_per_participant": 1,
    "tooling_notes": [
        "Zoom for moderated sessions; Qualtrics for survey fielding",
        "Dovetail for qual analysis; Python / R for quant analysis",
        "Dedicated integration session for convergence mapping",
        "Panel provider (Lucid, Dynata) for quantitative arm",
    ],
}


def estimate_resources(brief: StudyBrief) -> ResourceEstimate:
    """Produce a ResourceEstimate based on brief parameters."""
    method = brief.method

    if method == ResearchMethod.QUALITATIVE:
        d = _QUAL_DEFAULTS
        # Scale participant count with team size (each extra researcher handles ~3 more)
        participants = min(d["base_participants"] + (brief.team_size - 1) * 3, 20)
        researcher_hours = round(
            (participants * d["session_hours"])
            + (participants * d["transcription_hours_per_session"])
            + (participants * d["analysis_hours_per_participant"])
            + d["report_hours"],
            1,
        )
        incentive_budget = participants * d["incentive_per_participant_usd"] * d["sessions_per_participant"]
        return ResourceEstimate(
            researcher_hours=researcher_hours,
            participant_count=participants,
            incentive_budget_usd=round(incentive_budget, 2),
            sessions_per_participant=d["sessions_per_participant"],
            tooling_notes=list(d["tooling_notes"]),
        )

    elif method == ResearchMethod.QUANTITATIVE:
        d = _QUANT_DEFAULTS
        participants = d["base_participants"]
        researcher_hours = round(
            (participants * d["analysis_hours_per_response"])
            + d["instrument_and_cleaning_hours"]
            + d["report_hours"],
            1,
        )
        incentive_budget = participants * d["incentive_per_participant_usd"]
        return ResourceEstimate(
            researcher_hours=researcher_hours,
            participant_count=participants,
            incentive_budget_usd=round(incentive_budget, 2),
            sessions_per_participant=d["sessions_per_participant"],
            tooling_notes=list(d["tooling_notes"]),
        )

    else:  # MIXED
        d = _MIXED_DEFAULTS
        qual_n = d["qual_participants"]
        quant_n = d["quant_participants"]
        researcher_hours = round(
            (qual_n * d["session_hours"])
            + (qual_n * d["transcription_hours_per_session"])
            + (qual_n * d["analysis_hours_per_qual_participant"])
            + (quant_n * d["analysis_hours_per_quant_response"])
            + d["integration_overhead_hours"]
            + d["report_hours"],
            1,
        )
        incentive_budget = (qual_n * d["qual_incentive_usd"]) + (quant_n * d["quant_incentive_usd"])
        return ResourceEstimate(
            researcher_hours=researcher_hours,
            participant_count=qual_n + quant_n,
            incentive_budget_usd=round(incentive_budget, 2),
            sessions_per_participant=d["sessions_per_participant"],
            tooling_notes=list(d["tooling_notes"]),
        )
