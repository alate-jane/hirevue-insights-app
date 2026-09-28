"""HireVue GraphQL API Client and URL Parser.

Extracts interview codes from candidate status URLs and fetches
raw competency assessment scores from HireVue's public GraphQL endpoints.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import requests

GRAPHQL_QUERY = """
query InterviewStatus($interviewCode: String!) {
  interviewStatus(interviewCode: $interviewCode) {
    companyName
    candidateInsightsReportEnabled
    inlineReturnUrl
    isAvailable
    product
    status
    position {
      interviewType
      isExpired
      title
    }
    assessmentScores {
      id
      score
      scoreType
      error
    }
  }
}
"""

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}


@dataclass
class AssessmentScore:
    id: str
    score: float
    score_type: Optional[str] = None
    error: Optional[str] = None


@dataclass
class InterviewData:
    interview_code: str
    company_name: str
    position_title: str
    status: str
    is_available: bool
    is_expired: bool
    interview_type: Optional[str] = None
    candidate_insights_report_enabled: bool = False
    assessment_scores: List[AssessmentScore] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)


def extract_interview_code_and_region(input_text: str) -> tuple[str, str]:
    """Extracts the interview code and region endpoint from a link or raw string.

    Supports inputs like:
      - https://eu.hirevue.com/ui/interview-status/#/ABC123XYZ/
      - https://hirevue.com/ui/interview-status/#/ABC123XYZ
      - ABC123XYZ (plain code)
    """
    clean_input = input_text.strip()
    if not clean_input:
        raise ValueError("Interview code or URL cannot be empty.")

    # Detect region domain (e.g. hirevue.com, eu.hirevue.com, au.hirevue.com)
    region_match = re.search(r"https?://([a-zA-Z0-9.\-]*\bhirevue\.com)", clean_input, re.IGNORECASE)
    if region_match:
        base_domain = region_match.group(1).lower()
    else:
        # Default to EU region commonly used in APAC/UK/EU
        base_domain = "eu.hirevue.com"

    endpoint = f"https://{base_domain}/ui/graphql"

    # Match hash fragment or url path or bare alphanumeric code
    # e.g. #/CODE/ or /CODE or bare code
    code_match = re.search(r"#/([a-zA-Z0-9_-]+)/?", clean_input)
    if code_match:
        return code_match.group(1), endpoint

    # Check path ending like /interview-status/CODE
    path_match = re.search(r"hirevue\.com/.*/([a-zA-Z0-9_-]{6,})/?", clean_input)
    if path_match:
        return path_match.group(1), endpoint

    # If it's a bare code without URL characters
    bare_match = re.match(r"^[a-zA-Z0-9_-]{4,}$", clean_input)
    if bare_match:
        return bare_match.group(0), endpoint

    raise ValueError(f"Could not parse a valid HireVue interview code from: '{input_text}'")


def fetch_interview_status(
    interview_code_or_url: str,
    timeout: int = 15,
    session: Optional[requests.Session] = None,
) -> InterviewData:
    """Queries the HireVue GraphQL endpoint for interview status and raw scores."""
    code, endpoint = extract_interview_code_and_region(interview_code_or_url)

    payload = {
        "operationName": "InterviewStatus",
        "variables": {"interviewCode": code},
        "query": GRAPHQL_QUERY,
    }

    requester = session or requests
    try:
        response = requester.post(
            endpoint,
            json=payload,
            headers=DEFAULT_HEADERS,
            timeout=timeout,
        )
        response.raise_for_status()
        res_json = response.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to query HireVue endpoint ({endpoint}): {str(e)}") from e

    errors = res_json.get("errors")
    if errors:
        error_msg = "; ".join(err.get("message", "Unknown error") for err in errors)
        raise ValueError(f"HireVue API returned error: {error_msg}")

    data = res_json.get("data", {})
    status_data = data.get("interviewStatus")
    if not status_data:
        raise ValueError(f"No interview status found for code '{code}'. Check if the code is correct.")

    position = status_data.get("position") or {}
    raw_scores = status_data.get("assessmentScores") or []

    parsed_scores: List[AssessmentScore] = []
    for s in raw_scores:
        if isinstance(s, dict) and "score" in s and s["score"] is not None:
            parsed_scores.append(
                AssessmentScore(
                    id=s.get("id", "unknown"),
                    score=float(s.get("score", 0.0)),
                    score_type=s.get("scoreType"),
                    error=s.get("error"),
                )
            )

    return InterviewData(
        interview_code=code,
        company_name=status_data.get("companyName") or "Unknown Company",
        position_title=position.get("title") or "Unknown Position",
        status=status_data.get("status") or "UNKNOWN",
        is_available=bool(status_data.get("isAvailable", False)),
        is_expired=bool(position.get("isExpired", False)),
        interview_type=position.get("interviewType"),
        candidate_insights_report_enabled=bool(status_data.get("candidateInsightsReportEnabled", False)),
        assessment_scores=parsed_scores,
        raw_response=res_json,
    )
