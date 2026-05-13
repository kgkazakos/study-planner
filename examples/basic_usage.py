"""Basic usage examples for study-planner."""
from datetime import date

from study_planner.models import ResearchMethod, StudyBrief
from study_planner.planner import generate_plan

# ---------------------------------------------------------------------------
# 1. Qualitative study — rule-based (no API key required)
# ---------------------------------------------------------------------------

brief = StudyBrief(
    title="Mobile Checkout UX Study",
    research_questions=[
        "Why do users abandon the checkout flow?",
        "What is the biggest friction point in the payment step?",
        "How do first-time buyers differ from repeat purchasers?",
    ],
    method=ResearchMethod.QUALITATIVE,
    target_audience="Mobile app users aged 25–45, purchased in last 6 months",
    timeline_weeks=8,
    budget_usd=12_000,
    team_size=2,
    start_date=date(2026, 9, 1),
)

plan = generate_plan(brief)

print(f"Study: {plan.brief.title}")
print(f"Method rationale: {plan.method_rationale[:80]}…")
print(f"\nPhases ({len(plan.phases)} total):")
for p in plan.phases:
    print(f"  {p.start_date} – {p.end_date}  {p.name}  ({p.duration_days}d)")

print(f"\nResources:")
print(f"  Participants:  {plan.resources.participant_count}")
print(f"  Researcher h:  {plan.resources.researcher_hours}h")
print(f"  Total est.:    ${plan.resources.total_cost_estimate_usd:,.0f}")

print(f"\nRisks:")
for r in plan.risks:
    print(f"  ⚠  {r[:70]}…")

# ---------------------------------------------------------------------------
# 2. Mixed-methods study — JSON output
# ---------------------------------------------------------------------------

mixed_brief = StudyBrief(
    title="Product Discovery — Mixed Methods",
    research_questions=[
        "How do teams currently plan their work?",
        "What percentage of users use the advanced filter feature?",
    ],
    method=ResearchMethod.MIXED,
    target_audience="Enterprise product teams (20+ seats)",
    timeline_weeks=12,
    start_date=date(2026, 10, 1),
)

mixed_plan = generate_plan(mixed_brief)
print("\n--- Mixed plan JSON (truncated) ---")
import json

data = json.loads(mixed_plan.to_json())
print(f"Phases: {[p['name'] for p in data['phases']]}")
print(f"Total cost estimate: ${data['resources']['total_cost_estimate_usd']:,.0f}")

# ---------------------------------------------------------------------------
# 3. CLI equivalents
# ---------------------------------------------------------------------------

print("""
--- CLI equivalents ---

# Rule-based plan
study-planner plan \\
  --title "Mobile Checkout UX Study" \\
  --questions "Why do users abandon?|What is the friction point?" \\
  --audience "Mobile app users aged 25-45" \\
  --method qualitative \\
  --weeks 8 \\
  --start 2026-09-01

# From brief file
study-planner plan-file tests/fixtures/sample_brief.txt

# Timeline only
study-planner timeline --method qualitative --weeks 8 --start 2026-09-01

# Resource estimate only
study-planner estimate --method mixed

# With LLM enrichment
study-planner plan \\
  --title "My Study" \\
  --questions "Why?" \\
  --audience "Users" \\
  --method qualitative \\
  --llm-backend openai/gpt-4o-mini \\
  --json-output

# Streamlit UI
streamlit run study_planner/app.py
""")
