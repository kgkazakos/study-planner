"""study-planner — AI-assisted research study scoping, timeline generation,
and resource estimation. CPR Orbital #24."""

__version__ = "0.1.0"

from study_planner.models import (
    Phase,
    ResearchMethod,
    ResourceEstimate,
    StudyBrief,
    StudyPlan,
)
from study_planner.planner import generate_plan

__all__ = [
    "Phase",
    "ResearchMethod",
    "ResourceEstimate",
    "StudyBrief",
    "StudyPlan",
    "generate_plan",
]
