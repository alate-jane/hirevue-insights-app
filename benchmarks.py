"""Competency taxonomy, benchmark calculations, and role-fit scoring engine.

Provides mapping between HireVue competency IDs, industry benchmarks,
and candidate fit calculations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from hirevue_client import AssessmentScore

HIREVUE_THRESHOLD = 2.5

COMPETENCY_TAXONOMY: Dict[str, Dict[str, str]] = {
    # Interpersonal & Behavioral Competencies
    "team-orientation": {
        "name": "Team Orientation",
        "category": "Interpersonal & Behavioral",
        "description": "Collaborating effectively, supporting peers, and contributing to collective goals.",
    },
    "service-orientation": {
        "name": "Service Orientation",
        "category": "Interpersonal & Behavioral",
        "description": "Customer centricity, actively resolving patron needs, and exceeding service standards.",
    },
    "communication": {
        "name": "Communication",
        "category": "Interpersonal & Behavioral",
        "description": "Conveying ideas clearly, active listening, and structuring verbal responses.",
    },
    "adaptability": {
        "name": "Adaptability",
        "category": "Interpersonal & Behavioral",
        "description": "Handling shifting priorities, ambiguity, and changing workplace procedures.",
    },
    "agreeableness": {
        "name": "Agreeableness & Empathy",
        "category": "Interpersonal & Behavioral",
        "description": "Demonstrating patience, empathy, warmth, and conflict-de-escalating behavior.",
    },
    "compassion": {
        "name": "Compassion",
        "category": "Interpersonal & Behavioral",
        "description": "Understanding others' emotional context and responding with supportive care.",
    },
    "composure": {
        "name": "Composure & Resilience",
        "category": "Interpersonal & Behavioral",
        "description": "Staying calm, steady, and professional under peak pressure and customer conflict.",
    },
    "conscientiousness": {
        "name": "Conscientiousness",
        "category": "Interpersonal & Behavioral",
        "description": "Attention to detail, procedural adherence, accountability, and reliable quality.",
    },
    "dependability": {
        "name": "Dependability",
        "category": "Interpersonal & Behavioral",
        "description": "Punctuality, consistency in execution, and honoring commitments.",
    },
    "drive": {
        "name": "Drive & Motivation",
        "category": "Interpersonal & Behavioral",
        "description": "Personal initiative, ambition, energy, and proactive ownership of tasks.",
    },
    "tenacity": {
        "name": "Tenacity & Grit",
        "category": "Interpersonal & Behavioral",
        "description": "Persisting through setbacks and long-term problem solving.",
    },
    "negotiation": {
        "name": "Negotiation & Influence",
        "category": "Interpersonal & Behavioral",
        "description": "Persuading stakeholders, finding mutually beneficial compromises.",
    },

    # Cognitive & Game-based Competencies
    "think-agility": {
        "name": "Mental Agility",
        "category": "Cognitive & Game-Based",
        "description": "Fast cognitive switching, processing dynamic rules, and working memory.",
    },
    "think-numeracy": {
        "name": "Quantitative Numeracy",
        "category": "Cognitive & Game-Based",
        "description": "Numerical reasoning, calculation speed, and quantitative trend analysis.",
    },
    "think-problem-solving": {
        "name": "Problem Solving",
        "category": "Cognitive & Game-Based",
        "description": "Deductive logic, root cause discovery, and systematic reasoning.",
    },
    "think-visuospatial": {
        "name": "Visuospatial Reasoning",
        "category": "Cognitive & Game-Based",
        "description": "Mental 2D/3D spatial manipulation and pattern recognition.",
    },
}

ROLE_PROFILES: Dict[str, Dict[str, Any]] = {
    "retail": {
        "title": "Retail & Customer Service",
        "target_benchmark": 3.0,
        "weights": {
            "service-orientation": 0.30,
            "team-orientation": 0.20,
            "communication": 0.20,
            "agreeableness": 0.10,
            "dependability": 0.10,
            "composure": 0.10,
        },
    },
    "tech_analyst": {
        "title": "Data, Tech & Analytics",
        "target_benchmark": 3.2,
        "weights": {
            "think-problem-solving": 0.30,
            "think-numeracy": 0.25,
            "think-agility": 0.20,
            "conscientiousness": 0.15,
            "communication": 0.10,
        },
    },
    "banking": {
        "title": "Banking & Financial Services",
        "target_benchmark": 3.2,
        "weights": {
            "conscientiousness": 0.25,
            "think-numeracy": 0.25,
            "service-orientation": 0.20,
            "dependability": 0.15,
            "composure": 0.15,
        },
    },
    "graduate": {
        "title": "Graduate & Leadership Fast-Track",
        "target_benchmark": 3.4,
        "weights": {
            "drive": 0.25,
            "communication": 0.20,
            "think-agility": 0.20,
            "team-orientation": 0.20,
            "adaptability": 0.15,
        },
    },
}


@dataclass
class ScoredCompetency:
    id: str
    name: str
    category: str
    description: str
    score: float
    is_strength: bool
    status_label: str


@dataclass
class RoleFitResult:
    role_key: str
    role_title: str
    weighted_score: float
    fit_percentage: float
    target_benchmark: float
    met_count: int
    gap_count: int
    evaluated_competencies: List[ScoredCompetency]


def get_competency_meta(competency_id: str) -> Dict[str, str]:
    """Retrieves metadata for a competency id, falling back to clean formatted title."""
    clean_id = competency_id.lower().strip()
    if clean_id in COMPETENCY_TAXONOMY:
        return COMPETENCY_TAXONOMY[clean_id]

    # Generate friendly fallback
    pretty_name = clean_id.replace("think-", "").replace("-", " ").title()
    category = "Cognitive & Game-Based" if "think" in clean_id else "Interpersonal & Behavioral"
    return {
        "name": pretty_name,
        "category": category,
        "description": f"Assessment competency: {pretty_name}",
    }


def parse_scored_competencies(scores: List[AssessmentScore]) -> List[ScoredCompetency]:
    """Enriches raw assessment scores with names, categories, and strength classifications."""
    results: List[ScoredCompetency] = []
    for s in scores:
        meta = get_competency_meta(s.id)
        is_strength = s.score > HIREVUE_THRESHOLD
        if s.score >= 4.0:
            status_label = "Exceptional Strength"
        elif s.score > HIREVUE_THRESHOLD:
            status_label = "Proficient Strength"
        elif s.score >= 2.0:
            status_label = "Moderate Development Area"
        else:
            status_label = "Critical Development Area"

        results.append(
            ScoredCompetency(
                id=s.id,
                name=meta["name"],
                category=meta["category"],
                description=meta["description"],
                score=round(s.score, 2),
                is_strength=is_strength,
                status_label=status_label,
            )
        )
    return results


def calculate_role_fit(scores: List[AssessmentScore], role_key: str) -> RoleFitResult:
    """Calculates weighted role-fit score against a target role profile."""
    if role_key not in ROLE_PROFILES:
        raise KeyError(f"Invalid role profile key: '{role_key}'")

    role_cfg = ROLE_PROFILES[role_key]
    weights: Dict[str, float] = role_cfg["weights"]
    target_benchmark: float = role_cfg["target_benchmark"]

    scores_dict = {s.id.lower(): s.score for s in scores}
    evaluated_comps: List[ScoredCompetency] = []

    total_weight_present = 0.0
    weighted_sum = 0.0
    met_count = 0
    gap_count = 0

    for comp_id, weight in weights.items():
        score_val = scores_dict.get(comp_id)
        if score_val is not None:
            total_weight_present += weight
            weighted_sum += score_val * weight
            meta = get_competency_meta(comp_id)
            is_met = score_val >= target_benchmark
            if is_met:
                met_count += 1
            else:
                gap_count += 1

            evaluated_comps.append(
                ScoredCompetency(
                    id=comp_id,
                    name=meta["name"],
                    category=meta["category"],
                    description=meta["description"],
                    score=round(score_val, 2),
                    is_strength=is_met,
                    status_label="Above Benchmark" if is_met else "Below Benchmark",
                )
            )

    if total_weight_present > 0:
        final_weighted_score = weighted_sum / total_weight_present
    else:
        final_weighted_score = 0.0

    fit_percentage = min(100.0, max(0.0, (final_weighted_score / 5.0) * 100))

    return RoleFitResult(
        role_key=role_key,
        role_title=role_cfg["title"],
        weighted_score=round(final_weighted_score, 2),
        fit_percentage=round(fit_percentage, 1),
        target_benchmark=target_benchmark,
        met_count=met_count,
        gap_count=gap_count,
        evaluated_competencies=evaluated_comps,
    )
