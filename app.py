"""HireVue Candidate Score & Insights App.

Streamlit dashboard to reveal raw quantitative competency scores,
compare performance against role-specific benchmarks, and generate
personalized STAR-method interview improvement action plans.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from benchmarks import (
    HIREVUE_THRESHOLD,
    ROLE_PROFILES,
    calculate_role_fit,
    parse_scored_competencies,
)
from coach import filter_development_areas, generate_coaching_advice
from hirevue_client import fetch_interview_status
from mock_data import get_demo_profile, get_demo_profile_names

st.set_page_config(
    page_title="HireVue Candidate Score & Insights",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for card elements and metrics
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .badge-strength {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85em;
    }
    .badge-dev {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85em;
    }
    .badge-neutral {
        background-color: #e2e8f0;
        color: #334155;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def create_radar_chart(scored_comps, role_fit):
    """Builds interactive radar chart comparing candidate scores vs role benchmark."""
    categories = [c.name for c in scored_comps]
    scores = [c.score for c in scored_comps]

    if not categories:
        return None

    # Close the radar loop
    radar_categories = categories + [categories[0]]
    radar_scores = scores + [scores[0]]
    benchmark_line = [role_fit.target_benchmark] * len(radar_categories)
    threshold_line = [HIREVUE_THRESHOLD] * len(radar_categories)

    fig = go.Figure()

    # Candidate Score Trace
    fig.add_trace(
        go.Scatterpolar(
            r=radar_scores,
            theta=radar_categories,
            fill="toself",
            name="Your Score",
            line=dict(color="#2563eb", width=2.5),
            fillcolor="rgba(37, 99, 235, 0.25)",
        )
    )

    # Role Benchmark Trace
    fig.add_trace(
        go.Scatterpolar(
            r=benchmark_line,
            theta=radar_categories,
            name=f"{role_fit.role_title} Target ({role_fit.target_benchmark})",
            line=dict(color="#10b981", width=2, dash="dash"),
        )
    )

    # HireVue Pass Threshold Trace
    fig.add_trace(
        go.Scatterpolar(
            r=threshold_line,
            theta=radar_categories,
            name="HireVue Pass Line (2.5)",
            line=dict(color="#f59e0b", width=1.5, dash="dot"),
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 2.5, 3, 4, 5],
                ticktext=["1", "2", "2.5 (Mid)", "3", "4", "5"],
            )
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=30, b=50),
        height=480,
    )
    return fig


def create_bar_chart(scored_comps):
    """Builds categorized horizontal bar chart with color-coded strengths."""
    df = pd.DataFrame(
        [
            {
                "Competency": c.name,
                "Score": c.score,
                "Category": c.category,
                "Status": "Strength (> 2.5)" if c.is_strength else "Dev Area (<= 2.5)",
            }
            for c in scored_comps
        ]
    )

    fig = go.Figure()

    colors = ["#10b981" if s > HIREVUE_THRESHOLD else "#ef4444" for s in df["Score"]]

    fig.add_trace(
        go.Bar(
            x=df["Score"],
            y=df["Competency"],
            orientation="h",
            marker=dict(color=colors),
            text=[f"{s:.1f} / 5.0" for s in df["Score"]],
            textposition="auto",
        )
    )

    # Vertical threshold line at 2.5
    fig.add_vline(
        x=2.5,
        line_width=2,
        line_dash="dash",
        line_color="#f59e0b",
        annotation_text="HireVue Threshold (2.5)",
        annotation_position="top right",
    )

    fig.update_layout(
        xaxis=dict(range=[0, 5.2], title="Score (out of 5.0)"),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=20, t=30, b=40),
        height=max(380, len(df) * 35),
    )
    return fig


# --- SIDEBAR CONTROLS ---
st.sidebar.title("🎯 HireVue Insights")
st.sidebar.caption("Revealing candidate scores & automated assessment feedback")

input_mode = st.sidebar.radio(
    "Data Source Mode",
    ["Demo Profiles (Instant Preview)", "Live Interview Link / Code"],
    index=0,
)

target_role = st.sidebar.selectbox(
    "Target Benchmark Role",
    options=list(ROLE_PROFILES.keys()),
    format_func=lambda k: ROLE_PROFILES[k]["title"],
    index=0,
)

interview_data = None

if input_mode == "Demo Profiles (Instant Preview)":
    demo_options = get_demo_profile_names()
    chosen_demo = st.sidebar.selectbox(
        "Select Sample Profile",
        options=list(demo_options.keys()),
        format_func=lambda k: demo_options[k],
    )
    interview_data = get_demo_profile(chosen_demo)
    st.sidebar.success(f"Loaded: {interview_data.company_name} sample")

else:
    url_input = st.sidebar.text_input(
        "HireVue Status Link or Code",
        placeholder="https://eu.hirevue.com/ui/interview-status/#/CODE/",
        help="Paste the link from your interview completion email or SMS.",
    )
    fetch_btn = st.sidebar.button("Reveal Scores", type="primary", use_container_width=True)

    if fetch_btn:
        if not url_input.strip():
            st.sidebar.error("Please enter a valid link or interview code.")
        else:
            with st.spinner("Connecting to HireVue API..."):
                try:
                    interview_data = fetch_interview_status(url_input)
                    st.session_state["cached_data"] = interview_data
                    st.sidebar.success("Successfully fetched scores!")
                except Exception as err:
                    st.sidebar.error(f"Error: {str(err)}")

    if "cached_data" in st.session_state and interview_data is None:
        interview_data = st.session_state["cached_data"]

st.sidebar.divider()
st.sidebar.markdown(
    "🔒 **Privacy Guarantee**\n"
    "Your interview link is queried in real-time. No interview codes, names, or scores are saved to any database."
)


# --- MAIN CONTENT DASHBOARD ---
st.title("🎯 HireVue Candidate Score & Insights")
st.caption(
    "Demystify automated video & cognitive assessments: see raw scores, role benchmarks, and STAR improvement coaching."
)

if not interview_data:
    st.info("👈 Select a demo profile or paste your HireVue interview link in the sidebar to get started.")
    st.stop()

# Header Information
col_info1, col_info2, col_info3 = st.columns([3, 2, 2])
with col_info1:
    st.subheader(f"{interview_data.company_name} — {interview_data.position_title}")
    st.caption(f"Interview Code: `{interview_data.interview_code}`")

with col_info2:
    status_color = "badge-strength" if interview_data.status == "COMPLETED" else "badge-neutral"
    st.markdown(
        f"**Assessment Status:** <span class='{status_color}'>{interview_data.status}</span>",
        unsafe_allow_html=True,
    )

with col_info3:
    expired_label = "Expired" if interview_data.is_expired else "Active"
    st.markdown(
        f"**Availability:** <span class='badge-neutral'>{expired_label}</span>",
        unsafe_allow_html=True,
    )

st.divider()

# Check for empty scores (e.g. pending/in-progress)
if not interview_data.assessment_scores:
    st.warning(
        "⏳ **Scores Pending:** This interview is currently in progress or the automated evaluation has not finished processing yet. Please check back after scoring completes."
    )
    st.stop()

# Enriched Competency Calculations
scored_competencies = parse_scored_competencies(interview_data.assessment_scores)
role_fit = calculate_role_fit(interview_data.assessment_scores, target_role)
all_advice = generate_coaching_advice(scored_competencies)
dev_advice = filter_development_areas(all_advice)

# Metric Summary Cards
scores_list = [c.score for c in scored_competencies]
avg_score = sum(scores_list) / len(scores_list) if scores_list else 0.0
strengths_count = sum(1 for c in scored_competencies if c.is_strength)
dev_count = sum(1 for c in scored_competencies if not c.is_strength)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Overall Average Score", f"{avg_score:.2f} / 5.0", delta=f"{avg_score - 2.5:+.2f} vs Midpoint")
m2.metric("Strengths (> 2.5)", f"{strengths_count} competencies")
m3.metric("Development Areas (≤ 2.5)", f"{dev_count} flagged", delta_color="inverse")
m4.metric(
    f"{role_fit.role_title} Fit",
    f"{role_fit.fit_percentage}%",
    delta=f"{role_fit.met_count} / {len(role_fit.evaluated_competencies)} Met",
)

st.write("")

# Navigation Tabs
tab_charts, tab_table, tab_coach = st.tabs(
    ["📊 Score Dashboard & Radar", "📋 Detailed Scorecard", "💡 AI Interview Coach & Action Plan"]
)

with tab_charts:
    col_chart_left, col_chart_right = st.columns([1, 1])

    with col_chart_left:
        st.markdown("#### 🕸️ Competency Radar vs Role Benchmark")
        radar_fig = create_radar_chart(scored_competencies, role_fit)
        if radar_fig:
            st.plotly_chart(radar_fig, use_container_width=True)

    with col_chart_right:
        st.markdown("#### 📊 Score Distribution vs HireVue Threshold")
        bar_fig = create_bar_chart(scored_competencies)
        if bar_fig:
            st.plotly_chart(bar_fig, use_container_width=True)

with tab_table:
    st.markdown("#### 📋 Comprehensive Competency Breakdown")
    table_rows = []
    for c in scored_competencies:
        table_rows.append(
            {
                "Competency": c.name,
                "Category": c.category,
                "Score": f"{c.score:.2f} / 5.0",
                "Classification": c.status_label,
                "Description": c.description,
            }
        )
    df_table = pd.DataFrame(table_rows)
    st.dataframe(df_table, use_container_width=True, hide_index=True)

with tab_coach:
    st.markdown("### 💡 Targeted Interview Coach & Action Plan")
    st.write(
        "HireVue automated systems flag competencies scored **2.5 or lower** as risk areas. "
        "Review these tailored STAR responses and game strategies to lift your scores in subsequent interviews."
    )

    if not dev_advice:
        st.success(
            "🎉 **Outstanding Result!** All your competencies scored above HireVue's 2.5 pass threshold. "
            "You demonstrated strong proficiency across both behavioral and cognitive dimensions."
        )
    else:
        st.error(f"⚠️ **{len(dev_advice)} Development Area(s) Detected:**")

        for item in dev_advice:
            with st.expander(
                f"🚨 **{item.competency_name}** — Score: {item.score:.2f} / 5.0 ({item.category})",
                expanded=True,
            ):
                st.markdown(f"**Why HireVue evaluates this:**\n{item.why_it_matters}")
                st.markdown(f"**Common Pitfalls:**\n{item.typical_mistakes}")

                if "Cognitive" in item.category or "think" in item.competency_id:
                    st.info(f"🎮 **Cognitive Game Assessment Strategy:**\n\n{item.game_tips}")
                else:
                    st.markdown(f"**🎯 Targeted Practice Question:**\n*{item.practice_question}*")
                    st.markdown("**⭐ Recommended STAR Framework:**")
                    st.code(item.star_framework_guide, language="markdown")
                    st.markdown("**🏆 Exemplary Response Template:**")
                    st.success(item.sample_strong_response)
