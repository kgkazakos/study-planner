# study-planner

**AI-assisted research study scoping, timeline generation, and resource estimation.**

CPR Orbital #24 · S4 — Research Ops · MIT License

---

## The problem

Most research studies get scoped in a slide deck or a rough estimate in someone's head. There is no systematic way to translate a research brief into a phased timeline, resource estimate, and risk register — so studies start with unrealistic timelines, under-resourced teams, and no documented rationale for the method choice.

`study-planner` is a practitioner-facing tool that converts a study brief into a structured plan in seconds. It runs fully offline with rule-based defaults; optionally enrich every output with LLM-generated rationale, phase guidance, and tailored risk analysis.

---

## Features

- **Study scoping** — Method-aware phase generation for qualitative, quantitative, and mixed-methods studies, with proportional duration scaling across 4–20 week timelines
- **Working-day timeline** — Phase start/end dates assigned with proper Mon–Fri scheduling; visual Gantt chart in the Streamlit UI
- **Resource estimation** — Participant counts, researcher hours, incentive budgets, and total cost estimates (with 15% buffer) per method
- **Risk register** — Three pre-built risks per method; LLM enrichment generates study-specific risks and strategic recommendations
- **LLM enrichment via DSPy** — One flag activates ChainOfThought enrichment: per-phase guidance notes, methodological rationale, and tailored recommendations
- **Three LLM backends** — `openai/gpt-4o-mini`, `anthropic/claude-sonnet-4-6`, `gemini/gemini-2.0-flash`
- **Streamlit UI** — Full multi-tab interface with Gantt chart, phase detail cards, cost breakdown donut, and JSON download
- **CLI** — `plan`, `plan-file`, `timeline`, and `estimate` commands with `--json-output` for CI integration
- **Zero API key required** — Core runs entirely offline; LLM enrichment is opt-in

---

## Install

```bash
pip install -e .
```

With Streamlit UI:
```bash
pip install -e ".[ui]"
```

---

## CLI usage

```bash
# Generate a full study plan
study-planner plan \
  --title "Mobile Checkout UX Study" \
  --questions "Why do users abandon checkout?|What is the friction point?" \
  --audience "Mobile app users aged 25-45" \
  --method qualitative \
  --weeks 8 \
  --start 2026-09-01

# From a brief file
study-planner plan-file tests/fixtures/sample_brief.txt

# Timeline only
study-planner timeline --method qualitative --weeks 8 --start 2026-09-01

# Resource estimate only
study-planner estimate --method mixed

# With LLM enrichment
study-planner plan \
  --title "My Study" \
  --questions "Why?" \
  --audience "Users" \
  --method qualitative \
  --llm-backend openai/gpt-4o-mini \
  --json-output
```

### Brief file format

```
title: Mobile Checkout UX Study
method: qualitative
audience: Mobile app users aged 25-45
weeks: 8
team: 2
budget: 12000
questions:
Why do users abandon the checkout flow?
What is the biggest friction point?
```

---

## Streamlit UI

```bash
streamlit run study_planner/app.py
```

The UI provides:
- **Overview tab** — method rationale, research questions, risk register, recommendations
- **Timeline tab** — interactive Gantt chart with phase dates
- **Phases tab** — expandable cards with tasks, deliverables, and LLM guidance notes
- **Resources tab** — cost breakdown donut, resource summary table, tooling checklist
- **Export tab** — JSON download of the complete study plan

---

## Python API

```python
from datetime import date
from study_planner.models import ResearchMethod, StudyBrief
from study_planner.planner import generate_plan

brief = StudyBrief(
    title="Mobile Checkout UX Study",
    research_questions=[
        "Why do users abandon the checkout flow?",
        "What is the biggest friction point?",
    ],
    method=ResearchMethod.QUALITATIVE,
    target_audience="Mobile app users aged 25–45",
    timeline_weeks=8,
    start_date=date(2026, 9, 1),
    team_size=2,
    budget_usd=12_000,
)

# Rule-based (offline, no API key)
plan = generate_plan(brief)

# LLM-enriched
plan = generate_plan(brief, llm_backend="openai/gpt-4o-mini")

print(plan.to_json())
```

---

## LLM enrichment

When `--llm-backend` is set, DSPy `ChainOfThought` adds:

| Field | Without LLM | With LLM |
|---|---|---|
| `method_rationale` | Rule-based template | Study-specific rationale |
| `risks` | Method-level defaults | Study-specific risks |
| `recommendations` | Method-level defaults | Tailored recommendations |
| `phase.notes` | `null` | Phase-specific guidance |

Set the appropriate environment variable before running:

```bash
export ANTHROPIC_API_KEY="..."       # anthropic/claude-opus-4-6, claude-sonnet-4-6
export OPENAI_API_KEY="..."          # openai/gpt-5.5, gpt-5.4-mini
export GEMINI_API_KEY="..."          # gemini/gemini-4-argon, gemini-2.5-flash
```

---

## JSON output schema

```json
{
  "brief": {
    "title": "...",
    "research_questions": ["..."],
    "method": "qualitative",
    "target_audience": "...",
    "timeline_weeks": 8,
    "budget_usd": 12000,
    "team_size": 2,
    "start_date": "2026-09-01"
  },
  "phases": [
    {
      "name": "Planning & Guide Design",
      "duration_days": 6,
      "tasks": ["..."],
      "deliverables": ["..."],
      "owner": "Lead Researcher",
      "notes": null,
      "start_date": "2026-09-01",
      "end_date": "2026-09-08"
    }
  ],
  "resources": {
    "researcher_hours": 56.5,
    "participant_count": 15,
    "incentive_budget_usd": 1125.0,
    "estimated_researcher_cost_usd": 4802.5,
    "total_cost_estimate_usd": 6813.88,
    "tooling_notes": ["..."]
  },
  "method_rationale": "...",
  "risks": ["..."],
  "recommendations": ["..."],
  "llm_enriched": false
}
```

---

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check study_planner/ tests/
```

---

## Part of the CPR Ecosystem

`study-planner` is **Orbital #24** in the [CPR Orbital Series](https://github.com/kgkazakos) — 40 open-source tools for AI-native product research infrastructure, shipped at an almost daily cadence through December 2026.

**Related tools in this series:**

| Tool | Role |
|---|---|
| [qual-sniffer](https://github.com/kgkazakos/qual-sniffer) (#3) | Detects methodological weaknesses in discussion guides — run before finalising the guide in Planning phase |
| [survey-cleaner](https://github.com/kgkazakos/survey-cleaner) (#4) | Removes speeders and straight-liners from raw survey exports — essential for the Data Cleaning phase |
| [power-analyst](https://github.com/kgkazakos/power-analyst) (#4.9) | Validates sample size against effect sizes — pair with the Resource Estimate output |
| [saturation-meter](https://github.com/kgkazakos/saturation-meter) (#8) | Estimates thematic saturation — use during Analysis phase to know when to stop |
| [bias-audit](https://github.com/kgkazakos/bias-audit) (#14) | Detects interviewer bias patterns — run during Analysis to validate qual findings |
| [sample-sizer](https://github.com/kgkazakos/sample-sizer) (#21) | AI-assisted sample size calculator — cross-reference with resource estimates |
| [evidence-chain](https://github.com/kgkazakos/evidence-chain) (#23) | Tracks claim-to-evidence provenance — use during Synthesis & Reporting |

The broader [Computational Product Research](https://github.com/kgkazakos) discipline is documented at the CPR GitHub organisation.

---

## What this is and what it is not

**What it is:** A planning and scoping aid that helps researchers translate a brief into a structured timeline and resource estimate. It is opinionated but overridable — all defaults are based on industry-standard research practice and can be adapted for your context.

**What it is not:** A guarantee that the generated plan will work for your specific study. Research timelines are affected by factors this tool cannot know (organisational dependencies, participant availability, stakeholder review cycles). Use the output as a starting point, not a final commitment.

---

## License

MIT © 2026 Kostas Kazakos
