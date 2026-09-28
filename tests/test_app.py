"""Unit tests for app.py chart functions and dashboard logic."""

import plotly.graph_objects as go
from app import create_bar_chart, create_radar_chart
from benchmarks import calculate_role_fit, parse_scored_competencies
from mock_data import get_demo_profile


def test_create_radar_chart():
    demo_profile = get_demo_profile("retail_candidate")
    scored = parse_scored_competencies(demo_profile.assessment_scores)
    role_fit = calculate_role_fit(demo_profile.assessment_scores, "retail")

    fig = create_radar_chart(scored, role_fit)
    assert fig is not None
    assert isinstance(fig, go.Figure)
    # Ensure there are 3 traces: Candidate, Target, and Pass line
    assert len(fig.data) == 3


def test_create_bar_chart():
    demo_profile = get_demo_profile("retail_candidate")
    scored = parse_scored_competencies(demo_profile.assessment_scores)

    fig = create_bar_chart(scored)
    assert fig is not None
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
