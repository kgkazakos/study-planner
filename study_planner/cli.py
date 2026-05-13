"""Click CLI for study-planner."""
from __future__ import annotations

import json
import sys
from datetime import date
from typing import Optional

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from study_planner.models import ResearchMethod, StudyBrief
from study_planner.planner import generate_plan, parse_brief_file

console = Console()

LLM_BACKENDS = [
    # Anthropic
    "anthropic/claude-opus-4-6",
    "anthropic/claude-sonnet-4-6",
    # OpenAI
    "openai/gpt-5.5",
    "openai/gpt-5.4-mini",
    # Google
    "gemini/gemini-3.1-pro-preview",
    "gemini/gemini-2.5-flash",
]

METHOD_HELP = "Research method: qualitative | quantitative | mixed"
BACKEND_HELP = (
    "LLM backend for enrichment. One of: "
    + ", ".join(LLM_BACKENDS)
    + ". Omit for rule-based output only."
)


@click.group()
@click.version_option("0.1.0", prog_name="study-planner")
def main() -> None:
    """study-planner — AI-assisted research study scoping, timeline generation,
    and resource estimation. Part of the CPR Orbital toolkit."""


# ---------------------------------------------------------------------------
# plan command
# ---------------------------------------------------------------------------


@main.command("plan")
@click.option("--title", required=True, help="Study title")
@click.option(
    "--questions",
    "questions_str",
    required=True,
    help="Research question(s), pipe-separated. e.g. 'Why X?|How Y?'",
)
@click.option("--audience", required=True, help="Target participant audience")
@click.option(
    "--method",
    type=click.Choice(["qualitative", "quantitative", "mixed"]),
    default="qualitative",
    show_default=True,
    help=METHOD_HELP,
)
@click.option("--weeks", default=8, show_default=True, type=int, help="Total timeline in weeks")
@click.option("--team", default=1, show_default=True, type=int, help="Team size (researchers)")
@click.option("--budget", default=None, type=float, help="Optional budget in USD")
@click.option("--start", default=None, help="Start date (YYYY-MM-DD). Defaults to today")
@click.option("--llm-backend", default=None, help=BACKEND_HELP)
@click.option("--json-output", is_flag=True, help="Output JSON instead of Rich table")
def plan_cmd(
    title: str,
    questions_str: str,
    audience: str,
    method: str,
    weeks: int,
    team: int,
    budget: Optional[float],
    start: Optional[str],
    llm_backend: Optional[str],
    json_output: bool,
) -> None:
    """Generate a full study plan from parameters."""
    questions = [q.strip() for q in questions_str.split("|") if q.strip()]
    start_date = date.fromisoformat(start) if start else None

    brief = StudyBrief(
        title=title,
        research_questions=questions,
        method=ResearchMethod(method),
        target_audience=audience,
        timeline_weeks=weeks,
        budget_usd=budget,
        team_size=team,
        start_date=start_date,
    )

    with console.status("[bold blue]Generating study plan…[/bold blue]"):
        plan = generate_plan(brief, llm_backend=llm_backend)

    if json_output:
        click.echo(plan.to_json())
        return

    _render_plan(plan)


# ---------------------------------------------------------------------------
# plan-file command
# ---------------------------------------------------------------------------


@main.command("plan-file")
@click.argument("brief_path", type=click.Path(exists=True))
@click.option("--llm-backend", default=None, help=BACKEND_HELP)
@click.option("--json-output", is_flag=True, help="Output JSON instead of Rich table")
def plan_file_cmd(brief_path: str, llm_backend: Optional[str], json_output: bool) -> None:
    """Generate a study plan from a brief file (see examples/sample_brief.txt)."""
    data = parse_brief_file(brief_path)

    try:
        brief = StudyBrief(
            title=data.get("title", "Untitled Study"),
            research_questions=data.get("research_questions", []),
            method=ResearchMethod(data.get("method", "qualitative")),
            target_audience=data.get("audience", ""),
            timeline_weeks=int(data.get("weeks", 8)),
            budget_usd=float(data["budget"]) if "budget" in data else None,
            team_size=int(data.get("team", 1)),
        )
    except (KeyError, ValueError) as exc:
        console.print(f"[red]Error parsing brief file: {exc}[/red]")
        sys.exit(1)

    with console.status("[bold blue]Generating study plan…[/bold blue]"):
        plan = generate_plan(brief, llm_backend=llm_backend)

    if json_output:
        click.echo(plan.to_json())
        return

    _render_plan(plan)


# ---------------------------------------------------------------------------
# timeline command
# ---------------------------------------------------------------------------


@main.command("timeline")
@click.option(
    "--method",
    type=click.Choice(["qualitative", "quantitative", "mixed"]),
    default="qualitative",
    show_default=True,
)
@click.option("--weeks", default=8, show_default=True, type=int)
@click.option("--start", default=None, help="Start date (YYYY-MM-DD). Defaults to today")
def timeline_cmd(method: str, weeks: int, start: Optional[str]) -> None:
    """Print a phase timeline for a given method and duration."""
    from study_planner.scoper import scope_phases
    from study_planner.timeline import assign_dates

    start_date = date.fromisoformat(start) if start else date.today()
    phases = scope_phases(ResearchMethod(method), weeks)
    phases = assign_dates(phases, start_date)

    table = Table(
        title=f"Timeline — {method.capitalize()} · {weeks} weeks",
        box=box.SIMPLE_HEAVY,
        show_lines=True,
    )
    table.add_column("Phase", style="bold")
    table.add_column("Start", style="cyan")
    table.add_column("End", style="cyan")
    table.add_column("Days", justify="right")
    table.add_column("Owner")

    for p in phases:
        table.add_row(
            p.name,
            p.start_date.isoformat() if p.start_date else "—",
            p.end_date.isoformat() if p.end_date else "—",
            str(p.duration_days),
            p.owner,
        )

    console.print(table)


# ---------------------------------------------------------------------------
# estimate command
# ---------------------------------------------------------------------------


@main.command("estimate")
@click.option(
    "--method",
    type=click.Choice(["qualitative", "quantitative", "mixed"]),
    default="qualitative",
    show_default=True,
)
@click.option("--team", default=1, show_default=True, type=int)
@click.option("--json-output", is_flag=True)
def estimate_cmd(method: str, team: int, json_output: bool) -> None:
    """Print a resource estimate for a given method and team size."""
    brief = StudyBrief(
        title="Estimate",
        research_questions=[],
        method=ResearchMethod(method),
        target_audience="",
        team_size=team,
    )
    from study_planner.resources import estimate_resources

    r = estimate_resources(brief)

    if json_output:
        click.echo(json.dumps(r.to_dict(), indent=2))
        return

    table = Table(title=f"Resource Estimate — {method.capitalize()}", box=box.SIMPLE_HEAVY)
    table.add_column("Item", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Participants", str(r.participant_count))
    table.add_row("Researcher hours", f"{r.researcher_hours}h")
    table.add_row("Incentive budget", f"${r.incentive_budget_usd:,.0f}")
    table.add_row("Researcher cost (est.)", f"${r.estimated_researcher_cost_usd:,.0f}")
    table.add_row("Total (+ 15% buffer)", f"[bold green]${r.total_cost_estimate_usd:,.0f}[/bold green]")

    console.print(table)
    if r.tooling_notes:
        console.print("\n[bold]Tooling[/bold]")
        for note in r.tooling_notes:
            console.print(f"  • {note}")


# ---------------------------------------------------------------------------
# Internal rendering helpers
# ---------------------------------------------------------------------------


def _render_plan(plan) -> None:
    """Render a StudyPlan to the terminal using Rich."""
    b = plan.brief
    enriched_badge = " [green]✦ LLM enriched[/green]" if plan.llm_enriched else ""
    console.print()
    console.print(
        Panel(
            f"[bold]{b.title}[/bold]{enriched_badge}\n"
            f"Method: [cyan]{b.method.value.capitalize()}[/cyan]  ·  "
            f"Timeline: [cyan]{b.timeline_weeks}w[/cyan]  ·  "
            f"Team: [cyan]{b.team_size}[/cyan]\n"
            f"Audience: {b.target_audience}",
            title="Study Plan",
            border_style="blue",
        )
    )

    # Rationale
    if plan.method_rationale:
        console.print(Panel(plan.method_rationale, title="Method Rationale", border_style="dim"))

    # Phases
    phase_table = Table(title="Phases", box=box.SIMPLE_HEAVY, show_lines=True)
    phase_table.add_column("Phase", style="bold")
    phase_table.add_column("Days", justify="right")
    phase_table.add_column("Start", style="cyan")
    phase_table.add_column("End", style="cyan")
    phase_table.add_column("Deliverables")
    if plan.llm_enriched:
        phase_table.add_column("Guidance", style="dim")

    for p in plan.phases:
        row = [
            p.name,
            str(p.duration_days),
            p.start_date.isoformat() if p.start_date else "—",
            p.end_date.isoformat() if p.end_date else "—",
            " · ".join(p.deliverables[:2]),
        ]
        if plan.llm_enriched:
            row.append(p.notes or "")
        phase_table.add_row(*row)

    console.print(phase_table)

    # Resources
    r = plan.resources
    res_table = Table(title="Resources", box=box.SIMPLE_HEAVY)
    res_table.add_column("Item", style="bold")
    res_table.add_column("Value", justify="right")
    res_table.add_row("Participants", str(r.participant_count))
    res_table.add_row("Researcher hours", f"{r.researcher_hours}h")
    res_table.add_row("Incentive budget", f"${r.incentive_budget_usd:,.0f}")
    res_table.add_row("Researcher cost (est.)", f"${r.estimated_researcher_cost_usd:,.0f}")
    res_table.add_row("Total (+ 15% buffer)", f"[bold green]${r.total_cost_estimate_usd:,.0f}[/bold green]")
    console.print(res_table)

    # Risks
    if plan.risks:
        console.print("\n[bold]Risks[/bold]")
        for risk in plan.risks:
            console.print(f"  ⚠  {risk}")

    # Recommendations
    if plan.recommendations:
        console.print("\n[bold]Recommendations[/bold]")
        for rec in plan.recommendations:
            console.print(f"  → {rec}")

    console.print()
