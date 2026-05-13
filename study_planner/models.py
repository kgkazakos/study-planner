"""Data models for study-planner."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class ResearchMethod(str, Enum):
    QUALITATIVE = "qualitative"
    QUANTITATIVE = "quantitative"
    MIXED = "mixed"


@dataclass
class Phase:
    name: str
    duration_days: int
    tasks: list[str]
    deliverables: list[str]
    owner: str = "Researcher"
    notes: Optional[str] = None          # LLM-enriched guidance
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "duration_days": self.duration_days,
            "tasks": self.tasks,
            "deliverables": self.deliverables,
            "owner": self.owner,
            "notes": self.notes,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
        }


@dataclass
class ResourceEstimate:
    researcher_hours: float
    participant_count: int
    incentive_budget_usd: float
    sessions_per_participant: int = 1
    tooling_notes: list[str] = field(default_factory=list)

    @property
    def estimated_researcher_cost_usd(self) -> float:
        return round(self.researcher_hours * 85.0, 2)

    @property
    def total_cost_estimate_usd(self) -> float:
        return round((self.estimated_researcher_cost_usd + self.incentive_budget_usd) * 1.15, 2)

    def to_dict(self) -> dict:
        return {
            "researcher_hours": self.researcher_hours,
            "participant_count": self.participant_count,
            "incentive_budget_usd": round(self.incentive_budget_usd, 2),
            "sessions_per_participant": self.sessions_per_participant,
            "estimated_researcher_cost_usd": self.estimated_researcher_cost_usd,
            "total_cost_estimate_usd": self.total_cost_estimate_usd,
            "tooling_notes": self.tooling_notes,
        }


@dataclass
class StudyBrief:
    title: str
    research_questions: list[str]
    method: ResearchMethod
    target_audience: str
    timeline_weeks: int = 8
    budget_usd: Optional[float] = None
    team_size: int = 1
    start_date: Optional[date] = None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "research_questions": self.research_questions,
            "method": self.method.value,
            "target_audience": self.target_audience,
            "timeline_weeks": self.timeline_weeks,
            "budget_usd": self.budget_usd,
            "team_size": self.team_size,
            "start_date": self.start_date.isoformat() if self.start_date else None,
        }


@dataclass
class StudyPlan:
    brief: StudyBrief
    phases: list[Phase]
    resources: ResourceEstimate
    method_rationale: Optional[str] = None
    risks: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    llm_enriched: bool = False

    def to_dict(self) -> dict:
        return {
            "brief": self.brief.to_dict(),
            "phases": [p.to_dict() for p in self.phases],
            "resources": self.resources.to_dict(),
            "method_rationale": self.method_rationale,
            "risks": self.risks,
            "recommendations": self.recommendations,
            "llm_enriched": self.llm_enriched,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)
