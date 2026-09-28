"""Unit tests for coach.py."""

from benchmarks import ScoredCompetency
from coach import filter_development_areas, generate_coaching_advice


def test_generate_coaching_advice_sorting_and_content():
    competencies = [
        ScoredCompetency(
            id="service-orientation",
            name="Service Orientation",
            category="Interpersonal & Behavioral",
            description="",
            score=4.2,
            is_strength=True,
            status_label="Exceptional",
        ),
        ScoredCompetency(
            id="negotiation",
            name="Negotiation & Influence",
            category="Interpersonal & Behavioral",
            description="",
            score=2.1,
            is_strength=False,
            status_label="Moderate Development Area",
        ),
        ScoredCompetency(
            id="think-numeracy",
            name="Quantitative Numeracy",
            category="Cognitive & Game-Based",
            description="",
            score=2.4,
            is_strength=False,
            status_label="Moderate Development Area",
        ),
    ]

    advice = generate_coaching_advice(competencies)
    assert len(advice) == 3

    # Lowest score should come first (negotiation at 2.1)
    assert advice[0].competency_id == "negotiation"
    assert advice[0].is_development_area is True
    assert "Situation:" in advice[0].star_framework_guide

    # Second lowest should be think-numeracy at 2.4
    assert advice[1].competency_id == "think-numeracy"
    assert advice[1].is_development_area is True
    assert "mental arithmetic" in advice[1].game_tips.lower()

    # Highest score last
    assert advice[2].competency_id == "service-orientation"
    assert advice[2].is_development_area is False


def test_filter_development_areas():
    competencies = [
        ScoredCompetency(
            id="communication",
            name="Communication",
            category="Interpersonal & Behavioral",
            description="",
            score=3.5,
            is_strength=True,
            status_label="Proficient",
        ),
        ScoredCompetency(
            id="composure",
            name="Composure",
            category="Interpersonal & Behavioral",
            description="",
            score=2.2,
            is_strength=False,
            status_label="Development Area",
        ),
    ]

    all_advice = generate_coaching_advice(competencies)
    dev_only = filter_development_areas(all_advice)

    assert len(dev_only) == 1
    assert dev_only[0].competency_id == "composure"
    assert dev_only[0].score == 2.2
