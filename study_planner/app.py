"""Streamlit UI for study-planner — CPR Orbital #24."""
from __future__ import annotations

from datetime import date
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from study_planner.models import ResearchMethod, StudyBrief
from study_planner.planner import generate_plan

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="study-planner · CPR Orbital #24",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { background: #0f1117; }
    [data-testid="stSidebar"] * { color: #e8eaf0 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stTextArea label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stNumberInput label,
    [data-testid="stSidebar"] .stDateInput label,
    [data-testid="stSidebar"] .stRadio label { color: #9ca3af !important; font-size: 12px; font-weight: 500; letter-spacing: 0.03em; }
    [data-testid="stSidebar"] .stRadio > div { gap: 6px; }
    div[data-testid="metric-container"] { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; }
    .st-emotion-cache-1wivap2 { font-size: 13px; }
    .badge { display: inline-block; padding: 2px 10px; border-radius: 99px; font-size: 11px; font-weight: 600; }
    .badge-llm { background: #dcfce7; color: #166534; }
    .badge-rule { background: #f1f5f9; color: #475569; }
    .phase-card { background: #fff; border: 1px solid #e2e8f0; border-left: 4px solid; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; }
    .risk-item { background: #fefce8; border-left: 3px solid #fbbf24; border-radius: 0 6px 6px 0; padding: 8px 12px; margin-bottom: 6px; font-size: 13px; }
    .rec-item { background: #f0fdf4; border-left: 3px solid #22c55e; border-radius: 0 6px 6px 0; padding: 8px 12px; margin-bottom: 6px; font-size: 13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Colour palette for phases
# ---------------------------------------------------------------------------

PHASE_COLOURS = [
    "#6366f1",  # indigo
    "#8b5cf6",  # violet
    "#ec4899",  # pink
    "#f59e0b",  # amber
    "#10b981",  # emerald
]

METHOD_ACCENT = {
    "qualitative": "#6366f1",
    "quantitative": "#0ea5e9",
    "mixed": "#f59e0b",
}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 📋 study-planner")
    st.markdown(
        '<p style="font-size:11px;color:#6b7280;margin-top:-8px;">CPR Orbital #24 · S4 · MIT</p>',
        unsafe_allow_html=True,
    )
    st.divider()

    title = st.text_input(
        "STUDY TITLE",
        value="Mobile Checkout UX Study",
        placeholder="e.g. Onboarding friction discovery",
    )

    questions_raw = st.text_area(
        "RESEARCH QUESTIONS (one per line)",
        value="Why do users abandon the checkout flow?\nWhat is the biggest friction point in onboarding?\nHow do power users differ from new users?",
        height=110,
    )

    audience = st.text_input(
        "TARGET AUDIENCE",
        value="Mobile app users aged 25–45, purchased in last 6 months",
    )

    method_label = st.radio(
        "RESEARCH METHOD",
        options=["Qualitative", "Quantitative", "Mixed"],
        horizontal=True,
    )
    method_value = method_label.lower()

    col_a, col_b = st.columns(2)
    with col_a:
        weeks = st.slider("TIMELINE (weeks)", min_value=4, max_value=20, value=8, step=1)
    with col_b:
        team_size = st.slider("TEAM SIZE", min_value=1, max_value=6, value=1, step=1)

    start_date = st.date_input("START DATE", value=date.today())
    budget_raw = st.number_input(
        "BUDGET USD (optional, 0 = not set)",
        min_value=0.0,
        max_value=500_000.0,
        step=500.0,
        value=0.0,
        format="%.0f",
    )
    budget: Optional[float] = float(budget_raw) if budget_raw > 0 else None

    st.divider()
    st.markdown(
        '<p style="font-size:11px;color:#6b7280;">LLM ENRICHMENT (optional)</p>',
        unsafe_allow_html=True,
    )
    llm_choice = st.selectbox(
        "BACKEND",
        options=[
            "none (rule-based only)",
            "── Anthropic ──",
            "anthropic/claude-opus-4-6",
            "anthropic/claude-sonnet-4-6",
            "── OpenAI ──",
            "openai/gpt-5.5",
            "openai/gpt-5.4-mini",
            "── Google ──",
            "gemini/gemini-3.1-pro-preview",
            "gemini/gemini-2.5-flash",
        ],
        label_visibility="collapsed",
    )
    llm_backend: Optional[str] = (
        None if (llm_choice.startswith("none") or llm_choice.startswith("──")) else llm_choice
    )

    st.divider()
    generate_btn = st.button(
        "⚡ Generate Plan", type="primary", use_container_width=True
    )

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "plan" not in st.session_state:
    st.session_state.plan = None
if "error" not in st.session_state:
    st.session_state.error = None

# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

if generate_btn:
    questions = [q.strip() for q in questions_raw.splitlines() if q.strip()]
    if not questions:
        st.session_state.error = "Please enter at least one research question."
    else:
        st.session_state.error = None
        brief = StudyBrief(
            title=title,
            research_questions=questions,
            method=ResearchMethod(method_value),
            target_audience=audience,
            timeline_weeks=weeks,
            budget_usd=budget,
            team_size=team_size,
            start_date=start_date,
        )
        with st.spinner("Building your study plan…"):
            try:
                plan = generate_plan(brief, llm_backend=llm_backend)
                st.session_state.plan = plan
            except Exception as exc:
                st.session_state.error = str(exc)

# ---------------------------------------------------------------------------
# Error display
# ---------------------------------------------------------------------------

if st.session_state.error:
    st.error(st.session_state.error)

# ---------------------------------------------------------------------------
# Welcome screen
# ---------------------------------------------------------------------------

if st.session_state.plan is None and not st.session_state.error:
    st.markdown(
        """
        <div style="text-align:center;padding:60px 20px 40px;">
            <div style="font-size:48px;">📋</div>
            <h2 style="font-weight:600;margin:12px 0 8px;">study-planner</h2>
            <p style="color:#6b7280;font-size:15px;max-width:480px;margin:0 auto;">
                AI-assisted research study scoping, timeline generation, and resource estimation.
                Fill in the sidebar and click <strong>Generate Plan</strong> to get started.
            </p>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;max-width:700px;margin:0 auto;">
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:18px;">
                <div style="font-size:22px;">🗂</div>
                <div style="font-weight:600;margin:6px 0 4px;font-size:14px;">Study Scoping</div>
                <div style="color:#6b7280;font-size:12px;">Method-aware phase generation for qual, quant, and mixed studies</div>
            </div>
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:18px;">
                <div style="font-size:22px;">📅</div>
                <div style="font-weight:600;margin:6px 0 4px;font-size:14px;">Timeline</div>
                <div style="color:#6b7280;font-size:12px;">Working-day Gantt chart with proportional phase scaling</div>
            </div>
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:18px;">
                <div style="font-size:22px;">💰</div>
                <div style="font-weight:600;margin:6px 0 4px;font-size:14px;">Resources</div>
                <div style="color:#6b7280;font-size:12px;">Participant count, researcher hours, incentive budget, and cost estimate</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------------------------------------------------------------------
# Main output
# ---------------------------------------------------------------------------

plan = st.session_state.plan
b = plan.brief
accent = METHOD_ACCENT.get(b.method.value, "#6366f1")
enriched = plan.llm_enriched

# Header
badge_html = (
    '<span class="badge badge-llm">✦ LLM enriched</span>'
    if enriched
    else '<span class="badge badge-rule">rule-based</span>'
)
st.markdown(
    f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
        <h1 style="margin:0;font-size:22px;font-weight:700;">{b.title}</h1>
        {badge_html}
    </div>
    <p style="color:#6b7280;margin:0 0 20px;font-size:13px;">
        {b.method.value.capitalize()} · {b.timeline_weeks} weeks · Team {b.team_size} · {b.target_audience}
    </p>
    """,
    unsafe_allow_html=True,
)

# Metrics row
r = plan.resources
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Participants", f"{r.participant_count}")
col2.metric("Researcher hours", f"{r.researcher_hours}h")
col3.metric("Incentive budget", f"${r.incentive_budget_usd:,.0f}")
col4.metric("Researcher cost", f"${r.estimated_researcher_cost_usd:,.0f}")
col5.metric("Total estimate", f"${r.total_cost_estimate_usd:,.0f}")

st.divider()

tab_overview, tab_timeline, tab_phases, tab_resources, tab_export = st.tabs(
    ["Overview", "Timeline", "Phases", "Resources", "Export"]
)

# ── Overview ────────────────────────────────────────────────────────────────

with tab_overview:
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Method Rationale")
        if plan.method_rationale:
            st.markdown(
                f'<div style="background:#f8fafc;border-left:4px solid {accent};'
                f'border-radius:0 8px 8px 0;padding:14px 16px;font-size:14px;line-height:1.65;">'
                f"{plan.method_rationale}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("&nbsp;")
        st.subheader("Research Questions")
        for i, q in enumerate(b.research_questions, 1):
            st.markdown(
                f'<div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;'
                f'padding:10px 14px;margin-bottom:8px;font-size:13px;">'
                f'<strong style="color:{accent};">Q{i}</strong> &nbsp; {q}</div>',
                unsafe_allow_html=True,
            )

    with col_right:
        st.subheader("⚠ Risks")
        for risk in plan.risks:
            st.markdown(
                f'<div class="risk-item">{risk}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("&nbsp;")
        st.subheader("→ Recommendations")
        for rec in plan.recommendations:
            st.markdown(
                f'<div class="rec-item">{rec}</div>',
                unsafe_allow_html=True,
            )

# ── Timeline ────────────────────────────────────────────────────────────────

with tab_timeline:
    phases_with_dates = [p for p in plan.phases if p.start_date and p.end_date]

    if phases_with_dates:
        df = pd.DataFrame(
            [
                {
                    "Phase": p.name,
                    "Start": pd.Timestamp(p.start_date),
                    "End": pd.Timestamp(p.end_date) + pd.Timedelta(days=1),
                    "Owner": p.owner,
                    "Days": p.duration_days,
                    "Deliverables": " · ".join(p.deliverables[:2]),
                }
                for p in phases_with_dates
            ]
        )

        colour_map = {
            p.name: PHASE_COLOURS[i % len(PHASE_COLOURS)]
            for i, p in enumerate(phases_with_dates)
        }

        fig = px.timeline(
            df,
            x_start="Start",
            x_end="End",
            y="Phase",
            color="Phase",
            color_discrete_map=colour_map,
            hover_data={"Owner": True, "Days": True, "Deliverables": True, "Start": False, "End": False},
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            showlegend=False,
            height=320,
            margin=dict(l=10, r=10, t=10, b=30),
            plot_bgcolor="white",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#f0f0f0", title=""),
            yaxis=dict(title=""),
            font=dict(family="Inter, system-ui, sans-serif", size=12),
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

        # Phase summary table
        tdf = df[["Phase", "Start", "End", "Days", "Owner"]].copy()
        tdf["Start"] = tdf["Start"].dt.strftime("%b %-d, %Y")
        tdf["End"] = (tdf["End"] - pd.Timedelta(days=1)).dt.strftime("%b %-d, %Y")
        st.dataframe(tdf, use_container_width=True, hide_index=True)
    else:
        st.info("No start date set — timeline dates are unavailable.")

# ── Phases ──────────────────────────────────────────────────────────────────

with tab_phases:
    for i, p in enumerate(plan.phases):
        colour = PHASE_COLOURS[i % len(PHASE_COLOURS)]
        date_str = ""
        if p.start_date and p.end_date:
            date_str = f" &nbsp;·&nbsp; {p.start_date.strftime('%b %-d')} – {p.end_date.strftime('%b %-d, %Y')}"

        with st.expander(f"{p.name}  ({p.duration_days} days{date_str.replace('&nbsp;', ' ').replace('·', '·')})", expanded=(i == 0)):
            cols = st.columns([1, 1])
            with cols[0]:
                st.markdown("**Tasks**")
                for task in p.tasks:
                    st.markdown(f"- {task}")
            with cols[1]:
                st.markdown("**Deliverables**")
                for d in p.deliverables:
                    st.markdown(f"- {d}")

            if p.notes:
                st.markdown(
                    f'<div style="background:#f0f9ff;border-left:3px solid #0ea5e9;'
                    f'border-radius:0 6px 6px 0;padding:8px 12px;margin-top:10px;font-size:13px;">'
                    f"✦ {p.notes}</div>",
                    unsafe_allow_html=True,
                )
            st.caption(f"Owner: {p.owner}")

# ── Resources ───────────────────────────────────────────────────────────────

with tab_resources:
    col_l, col_r = st.columns([2, 3])

    with col_l:
        st.subheader("Cost Breakdown")
        fig_pie = go.Figure(
            go.Pie(
                labels=["Researcher time", "Participant incentives", "15% buffer"],
                values=[
                    r.estimated_researcher_cost_usd,
                    r.incentive_budget_usd,
                    round(
                        (r.estimated_researcher_cost_usd + r.incentive_budget_usd) * 0.15,
                        2,
                    ),
                ],
                hole=0.5,
                marker_colors=["#6366f1", "#10b981", "#f59e0b"],
                textinfo="label+percent",
                textfont_size=12,
            )
        )
        fig_pie.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, system-ui, sans-serif"),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_r:
        st.subheader("Resource Summary")
        rows = [
            ("Participants", str(r.participant_count)),
            ("Sessions per participant", str(r.sessions_per_participant)),
            ("Researcher hours", f"{r.researcher_hours}h"),
            ("Incentive budget", f"${r.incentive_budget_usd:,.0f}"),
            ("Researcher cost (est. @ $85/h)", f"${r.estimated_researcher_cost_usd:,.0f}"),
            ("Total (+ 15% buffer)", f"${r.total_cost_estimate_usd:,.0f}"),
        ]
        if b.budget_usd:
            remaining = b.budget_usd - r.total_cost_estimate_usd
            rows.append(
                (
                    "Budget variance",
                    f"{'✅ +' if remaining >= 0 else '⚠ –'}${abs(remaining):,.0f}",
                )
            )

        for label, value in rows:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'border-bottom:1px solid #f1f5f9;padding:8px 0;font-size:13px;">'
                f"<span style='color:#6b7280;'>{label}</span>"
                f"<span style='font-weight:600;'>{value}</span></div>",
                unsafe_allow_html=True,
            )

        st.markdown("&nbsp;")
        st.subheader("Tooling Checklist")
        for note in r.tooling_notes:
            st.markdown(f"☐ {note}")

# ── Export ───────────────────────────────────────────────────────────────────

with tab_export:
    st.subheader("JSON Export")
    json_str = plan.to_json()
    st.download_button(
        label="⬇ Download study-plan.json",
        data=json_str,
        file_name="study-plan.json",
        mime="application/json",
        use_container_width=True,
    )
    st.code(json_str, language="json")
