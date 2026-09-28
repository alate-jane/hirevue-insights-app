"""Mock data generator providing realistic HireVue candidate assessment payloads.

Used for offline portfolio demonstrations, fallback testing, and UI preview
when users do not possess an active HireVue interview link.
"""

from typing import Dict
from hirevue_client import AssessmentScore, InterviewData

DEMO_PROFILES: Dict[str, InterviewData] = {
    "retail_candidate": InterviewData(
        interview_code="DEMO-RETAIL-01",
        company_name="Officeworks",
        position_title="Customer Service Team Member",
        status="COMPLETED",
        is_available=True,
        is_expired=False,
        interview_type="ON_DEMAND",
        candidate_insights_report_enabled=True,
        assessment_scores=[
            AssessmentScore(id="service-orientation", score=4.2, score_type="COMPETENCY"),
            AssessmentScore(id="team-orientation", score=3.9, score_type="COMPETENCY"),
            AssessmentScore(id="adaptability", score=3.6, score_type="COMPETENCY"),
            AssessmentScore(id="agreeableness", score=4.0, score_type="COMPETENCY"),
            AssessmentScore(id="communication", score=3.2, score_type="COMPETENCY"),
            AssessmentScore(id="dependability", score=3.8, score_type="COMPETENCY"),
            AssessmentScore(id="composure", score=2.8, score_type="COMPETENCY"),
            AssessmentScore(id="negotiation", score=2.3, score_type="COMPETENCY"),  # Dev area
            AssessmentScore(id="think-agility", score=3.1, score_type="COMPETENCY"),
            AssessmentScore(id="think-numeracy", score=2.2, score_type="COMPETENCY"),  # Dev area
            AssessmentScore(id="think-problem-solving", score=3.0, score_type="COMPETENCY"),
        ],
    ),
    "analyst_candidate": InterviewData(
        interview_code="DEMO-ANALYST-02",
        company_name="Commonwealth Bank / Tech",
        position_title="Junior Data & Analytics Associate",
        status="COMPLETED",
        is_available=True,
        is_expired=False,
        interview_type="ON_DEMAND",
        candidate_insights_report_enabled=True,
        assessment_scores=[
            AssessmentScore(id="think-problem-solving", score=4.7, score_type="COMPETENCY"),
            AssessmentScore(id="think-numeracy", score=4.6, score_type="COMPETENCY"),
            AssessmentScore(id="think-agility", score=4.2, score_type="COMPETENCY"),
            AssessmentScore(id="think-visuospatial", score=4.0, score_type="COMPETENCY"),
            AssessmentScore(id="drive", score=3.8, score_type="COMPETENCY"),
            AssessmentScore(id="conscientiousness", score=3.9, score_type="COMPETENCY"),
            AssessmentScore(id="tenacity", score=3.5, score_type="COMPETENCY"),
            AssessmentScore(id="communication", score=3.0, score_type="COMPETENCY"),
            AssessmentScore(id="team-orientation", score=3.1, score_type="COMPETENCY"),
            AssessmentScore(id="negotiation", score=2.1, score_type="COMPETENCY"),  # Dev area
            AssessmentScore(id="composure", score=2.4, score_type="COMPETENCY"),  # Dev area
        ],
    ),
    "high_performer": InterviewData(
        interview_code="DEMO-TOP-03",
        company_name="Macquarie Group",
        position_title="Graduate Consultant",
        status="COMPLETED",
        is_available=True,
        is_expired=False,
        interview_type="ON_DEMAND",
        candidate_insights_report_enabled=True,
        assessment_scores=[
            AssessmentScore(id="communication", score=4.5, score_type="COMPETENCY"),
            AssessmentScore(id="service-orientation", score=4.2, score_type="COMPETENCY"),
            AssessmentScore(id="team-orientation", score=4.4, score_type="COMPETENCY"),
            AssessmentScore(id="adaptability", score=4.1, score_type="COMPETENCY"),
            AssessmentScore(id="drive", score=4.6, score_type="COMPETENCY"),
            AssessmentScore(id="think-agility", score=4.3, score_type="COMPETENCY"),
            AssessmentScore(id="think-numeracy", score=4.2, score_type="COMPETENCY"),
            AssessmentScore(id="think-problem-solving", score=4.6, score_type="COMPETENCY"),
            AssessmentScore(id="negotiation", score=3.8, score_type="COMPETENCY"),
            AssessmentScore(id="composure", score=4.0, score_type="COMPETENCY"),
        ],
    ),
    "pending_candidate": InterviewData(
        interview_code="DEMO-PENDING-04",
        company_name="Woolworths Group",
        position_title="Team Member",
        status="IN_PROGRESS",
        is_available=True,
        is_expired=False,
        interview_type="ON_DEMAND",
        candidate_insights_report_enabled=False,
        assessment_scores=[],
    ),
}


def get_demo_profile_names() -> Dict[str, str]:
    """Returns human-friendly labels for demo selection."""
    return {
        "retail_candidate": "Retail & Customer Service (Officeworks Sample)",
        "analyst_candidate": "Junior Data Analyst / Tech (Finance Sample)",
        "high_performer": "High Performing Graduate Candidate",
        "pending_candidate": "In-Progress / Pending Assessment",
    }


def get_demo_profile(profile_key: str) -> InterviewData:
    """Returns a copy of the demo profile data."""
    if profile_key not in DEMO_PROFILES:
        raise KeyError(f"Unknown demo profile key: '{profile_key}'")
    return DEMO_PROFILES[profile_key]
