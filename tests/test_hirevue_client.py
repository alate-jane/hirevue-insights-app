"""Unit tests for hirevue_client.py."""

from unittest.mock import MagicMock, patch
import pytest
import requests

from hirevue_client import (
    extract_interview_code_and_region,
    fetch_interview_status,
    AssessmentScore,
    InterviewData,
)


def test_extract_interview_code_eu_url():
    url = "https://eu.hirevue.com/ui/interview-status/#/ABC123XYZ/"
    code, endpoint = extract_interview_code_and_region(url)
    assert code == "ABC123XYZ"
    assert endpoint == "https://eu.hirevue.com/ui/graphql"


def test_extract_interview_code_us_url():
    url = "https://hirevue.com/ui/interview-status/#/DEF456UVW"
    code, endpoint = extract_interview_code_and_region(url)
    assert code == "DEF456UVW"
    assert endpoint == "https://hirevue.com/ui/graphql"


def test_extract_interview_code_bare_code():
    code, endpoint = extract_interview_code_and_region("CODE987")
    assert code == "CODE987"
    assert endpoint == "https://eu.hirevue.com/ui/graphql"


def test_extract_interview_code_empty_fails():
    with pytest.raises(ValueError, match="cannot be empty"):
        extract_interview_code_and_region("   ")


def test_extract_interview_code_invalid_fails():
    with pytest.raises(ValueError, match="Could not parse"):
        extract_interview_code_and_region("not valid url with spaces @@")


@patch("requests.post")
def test_fetch_interview_status_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "interviewStatus": {
                "companyName": "Officeworks",
                "candidateInsightsReportEnabled": True,
                "isAvailable": True,
                "status": "COMPLETED",
                "position": {
                    "title": "Customer Service Team Member",
                    "isExpired": False,
                    "interviewType": "ON_DEMAND",
                },
                "assessmentScores": [
                    {"id": "service-orientation", "score": 3.8, "scoreType": "COMPETENCY", "error": None},
                    {"id": "team-orientation", "score": 2.1, "scoreType": "COMPETENCY", "error": None},
                ],
            }
        }
    }
    mock_post.return_value = mock_response

    result = fetch_interview_status("https://eu.hirevue.com/ui/interview-status/#/MOCK123/")

    assert isinstance(result, InterviewData)
    assert result.company_name == "Officeworks"
    assert result.position_title == "Customer Service Team Member"
    assert len(result.assessment_scores) == 2
    assert result.assessment_scores[0].id == "service-orientation"
    assert result.assessment_scores[0].score == 3.8
    assert result.assessment_scores[1].score == 2.1


@patch("requests.post")
def test_fetch_interview_status_graphql_error(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "errors": [{"message": "Interview code not found or expired"}]
    }
    mock_post.return_value = mock_response

    with pytest.raises(ValueError, match="HireVue API returned error"):
        fetch_interview_status("INVALID_CODE")


@patch("requests.post")
def test_fetch_interview_status_connection_error(mock_post):
    mock_post.side_effect = requests.exceptions.Timeout("Connection timed out")

    with pytest.raises(ConnectionError, match="Failed to query HireVue endpoint"):
        fetch_interview_status("MOCK_CODE")
