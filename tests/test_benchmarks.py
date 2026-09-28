"""Unit tests for benchmarks.py."""

import pytest
from benchmarks import (
    calculate_role_fit,
    get_competency_meta,
    parse_scored_competencies,
    ROLE_PROFILES,
    RoleFitResult,
)
from hirevue_client import AssessmentScore


def test_get_competency_meta_known():
    meta = get_competency_meta("service-orientation")
    assert meta["name"] == "Service Orientation"
    assert meta["category"] == "Interpersonal & Behavioral"


def test_get_competency_meta_fallback():
    meta = get_competency_meta("think-custom-skill")
    assert "Custom Skill" in meta["name"]
    assert meta["category"] == "Cognitive & Game-Based"


def test_parse_scored_competencies_thresholds():
    scores = [
        AssessmentScore(id="service-orientation", score=4.5),
        AssessmentScore(id="communication", score=2.8),
        AssessmentScore(id="negotiation", score=2.3),
        AssessmentScore(id="composure", score=1.8),
    ]
    parsed = parse_scored_competencies(scores)
    assert len(parsed) == 4

    # Exceptional Strength
    assert parsed[0].is_strength is True
    assert parsed[0].status_label == "Exceptional Strength"

    # Proficient Strength (above 2.5)
    assert parsed[1].is_strength is True
    assert parsed[1].status_label == "Proficient Strength"

    # Moderate Development Area (<= 2.5, >= 2.0)
    assert parsed[2].is_strength is False
    assert parsed[2].status_label == "Moderate Development Area"

    # Critical Development Area (< 2.0)
    assert parsed[3].is_strength is False
    assert parsed[3].status_label == "Critical Development Area"


def test_calculate_role_fit_retail():
    scores = [
        AssessmentScore(id="service-orientation", score=4.0),
        AssessmentScore(id="team-orientation", score=4.0),
        AssessmentScore(id="communication", score=3.0),
        AssessmentScore(id="agreeableness", score=3.5),
        AssessmentScore(id="dependability", score=3.0),
        AssessmentScore(id="composure", score=3.0),
    ]
    fit = calculate_role_fit(scores, "retail")
    assert isinstance(fit, RoleFitResult)
    assert fit.role_key == "retail"
    assert fit.weighted_score > 3.0
    assert fit.fit_percentage > 60.0
    assert fit.gap_count == 0
    assert fit.met_count == 6


def test_calculate_role_fit_invalid_role():
    scores = [AssessmentScore(id="service-orientation", score=4.0)]
    with pytest.raises(KeyError, match="Invalid role profile key"):
        calculate_role_fit(scores, "astronaut_role")
