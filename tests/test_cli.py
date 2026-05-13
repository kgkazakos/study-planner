"""Tests for study_planner CLI commands."""
import json

import pytest
from click.testing import CliRunner

from study_planner.cli import main


@pytest.fixture()
def runner():
    return CliRunner()


def test_plan_basic(runner):
    result = runner.invoke(
        main,
        [
            "plan",
            "--title", "Onboarding Study",
            "--questions", "Why do users drop off?|What is confusing?",
            "--audience", "New users aged 25-35",
            "--method", "qualitative",
            "--weeks", "8",
        ],
    )
    assert result.exit_code == 0
    assert "Onboarding Study" in result.output


def test_plan_json_output(runner):
    result = runner.invoke(
        main,
        [
            "plan",
            "--title", "JSON Test",
            "--questions", "What?",
            "--audience", "Users",
            "--method", "quantitative",
            "--weeks", "6",
            "--json-output",
        ],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["brief"]["method"] == "quantitative"
    assert len(data["phases"]) >= 4
    assert data["resources"]["researcher_hours"] > 0


def test_plan_mixed_method(runner):
    result = runner.invoke(
        main,
        [
            "plan",
            "--title", "Mixed Study",
            "--questions", "How?",
            "--audience", "Enterprise users",
            "--method", "mixed",
            "--weeks", "12",
            "--json-output",
        ],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["brief"]["method"] == "mixed"


def test_plan_with_start_date(runner):
    result = runner.invoke(
        main,
        [
            "plan",
            "--title", "Dated Study",
            "--questions", "Why?",
            "--audience", "All users",
            "--method", "qualitative",
            "--weeks", "8",
            "--start", "2026-09-01",
            "--json-output",
        ],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    phases = data["phases"]
    assert phases[0]["start_date"] is not None


def test_timeline_command(runner):
    result = runner.invoke(main, ["timeline", "--method", "qualitative", "--weeks", "8"])
    assert result.exit_code == 0
    assert "Planning" in result.output or "Recruit" in result.output


def test_timeline_with_start(runner):
    result = runner.invoke(
        main,
        ["timeline", "--method", "quantitative", "--weeks", "6", "--start", "2026-07-01"],
    )
    assert result.exit_code == 0


def test_estimate_command(runner):
    result = runner.invoke(main, ["estimate", "--method", "qualitative"])
    assert result.exit_code == 0
    assert "$" in result.output


def test_estimate_json(runner):
    result = runner.invoke(main, ["estimate", "--method", "quantitative", "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "researcher_hours" in data
    assert "total_cost_estimate_usd" in data


def test_plan_file_command(tmp_path, runner):
    brief_file = tmp_path / "brief.txt"
    brief_file.write_text(
        "title: File-based Study\n"
        "method: qualitative\n"
        "audience: Product teams\n"
        "weeks: 8\n"
        "questions:\n"
        "What is the core problem?\n"
        "How do users work around it?\n"
    )
    result = runner.invoke(main, ["plan-file", str(brief_file), "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "File-based Study" in data["brief"]["title"]
    assert len(data["brief"]["research_questions"]) == 2
