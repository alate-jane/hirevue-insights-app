"""Unit tests for mock_data.py."""

import pytest
from mock_data import DEMO_PROFILES, get_demo_profile, get_demo_profile_names
from hirevue_client import InterviewData


def test_get_demo_profile_names():
    names = get_demo_profile_names()
    assert len(names) >= 4
    assert "retail_candidate" in names
    assert "analyst_candidate" in names


def test_get_demo_profile_valid():
    profile = get_demo_profile("retail_candidate")
    assert isinstance(profile, InterviewData)
    assert profile.company_name == "Officeworks"
    assert len(profile.assessment_scores) > 0
    # Validate score range 1.0 to 5.0
    for score in profile.assessment_scores:
        assert 1.0 <= score.score <= 5.0


def test_get_demo_profile_invalid():
    with pytest.raises(KeyError, match="Unknown demo profile"):
        get_demo_profile("non_existent_key")


def test_pending_candidate_profile():
    profile = get_demo_profile("pending_candidate")
    assert profile.status == "IN_PROGRESS"
    assert len(profile.assessment_scores) == 0
