"""AI Interview Coach & Action Plan Generator.

Generates structured improvement strategies, STAR-method interview templates,
and cognitive game tips tailored specifically to candidate development areas (scores <= 2.5).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from benchmarks import HIREVUE_THRESHOLD, ScoredCompetency, get_competency_meta

# Structured knowledge base for targeted interview coaching
COACHING_KNOWLEDGE_BASE: Dict[str, Dict[str, str]] = {
    "service-orientation": {
        "why_it_matters": "HireVue looks for proactive customer empathy, active ownership of complaints, and going beyond minimum duties.",
        "typical_mistakes": "Focusing solely on store policy rather than candidate empathy; blaming the customer; not showing follow-through.",
        "practice_question": "Tell me about a time you had to deal with an upset or demanding customer. How did you resolve the situation?",
        "star_framework_guide": "• Situation: Set the scene with a difficult customer expectation.\n• Task: Your personal responsibility to protect customer relationship.\n• Action: De-escalate with active listening, offer genuine options within policy.\n• Result: Customer satisfaction metric or positive feedback received.",
        "sample_strong_response": "At my previous role, a customer was frustrated that an advertised promotional item was out of stock. Instead of simply saying 'we're sold out', I apologized for the inconvenience, checked nearby store inventories on our handheld scanner, and arranged a complimentary home dispatch. The customer praised our swift resolution and became a regular store visitor.",
        "game_tips": "N/A (Behavioral competency)",
    },
    "team-orientation": {
        "why_it_matters": "Assesses willingness to share credit, support overwhelmed colleagues, and put team goals before individual ego.",
        "typical_mistakes": "Using only 'I' instead of 'we'; criticizing teammates; presenting yourself as a solo hero who fixed everything alone.",
        "practice_question": "Describe a situation where a team member wasn't pulling their weight or a project was falling behind. How did you handle it?",
        "star_framework_guide": "• Situation: Describe the group deadline or store rush.\n• Task: The collective objective.\n• Action: Proactively checked in with the teammate privately, redistributed tasks without judgment.\n• Result: Team delivered on time, strengthened peer trust.",
        "sample_strong_response": "During peak holiday trading, our restocking team was falling two hours behind schedule. I noticed a junior colleague was struggling with inventory scanning. I paired up with them for 30 minutes to share efficient batching techniques and divided aisle responsibilities. We cleared the backlog 15 minutes before store opening.",
        "game_tips": "N/A (Behavioral competency)",
    },
    "communication": {
        "why_it_matters": "HireVue models evaluate speech rate, filler words, coherence, and structured message delivery.",
        "typical_mistakes": "Rambling answers; jumping back and forth across timeline; lacking clear takeaways.",
        "practice_question": "Explain a complex situation or procedure to someone who had no prior background knowledge.",
        "star_framework_guide": "• Situation: Technical or procedural concept needing delivery.\n• Task: Make it immediately actionable for the audience.\n• Action: Broke down into 3 simple milestones, used relatable analogies, paused for comprehension checks.\n• Result: Audience successfully performed task without error.",
        "sample_strong_response": "When onboarding a new cashier, I explained our refund and exchange policy by breaking it into three simple steps: verify receipt, inspect item condition, and process payment method reversal. I gave a live demonstration and observed their first two transactions, ensuring 100% procedural compliance.",
        "game_tips": "N/A (Behavioral competency)",
    },
    "composure": {
        "why_it_matters": "Evaluates vocal tone consistency, steady breathing, and emotional equilibrium under pressure.",
        "typical_mistakes": "Visibly panicking on video, speed-talking, or admitting to feeling overwhelmed.",
        "practice_question": "Tell me about a high-stress emergency or sudden crisis at work. How did you keep your composure?",
        "star_framework_guide": "• Situation: Sudden unexpected bottleneck or emergency.\n• Task: Maintain calmness and prioritize safety / customer flow.\n• Action: Paused for 5 seconds to assess priorities, communicated steady steps to peers.\n• Result: Crisis de-escalated smoothly without panic.",
        "sample_strong_response": "During a black Friday sale, our POS terminal system went offline for 10 minutes. Rather than allowing panic in the queue, I stepped to the front of the registers, clearly briefed waiting customers on the technical glitch, and organized queue marshaling while our manager restarted the router. Customers appreciated the prompt transparency.",
        "game_tips": "N/A (Behavioral competency)",
    },
    "negotiation": {
        "why_it_matters": "Measures persuasion, finding common ground, and resolving differing agendas positively.",
        "typical_mistakes": "Being overly aggressive or passively giving up without proposing alternative solutions.",
        "practice_question": "Describe a time when you had to convince a team member or client who initially disagreed with your perspective.",
        "star_framework_guide": "• Situation: Disagreement on approach or terms.\n• Task: Reach alignment without damaging rapport.\n• Action: Listened to their underlying constraints first, proposed a compromise addressing their core concern.\n• Result: Agreement reached and implemented successfully.",
        "sample_strong_response": "When our team was debating whether to prioritize website bug fixes or new feature development, I organized a 15-minute sync with the design lead. By highlighting customer drop-off data from checkout bugs, I persuaded them to allocate 70% of sprint capacity to critical fixes and 30% to high-priority UI updates.",
        "game_tips": "N/A (Behavioral competency)",
    },
    "think-numeracy": {
        "why_it_matters": "Tests mental arithmetic accuracy, statistical literacy, and speed in quantitative decision making.",
        "typical_mistakes": "Over-calculating exact decimal points instead of using rapid mental estimation and bounding.",
        "practice_question": "Cognitive Game: Digit / Math Assessment modules.",
        "star_framework_guide": "Cognitive assessment: Practice mental math estimation shortcuts (rounding numbers to nearest 10 or 5 to eliminate wrong answers rapidly).",
        "sample_strong_response": "N/A (Cognitive Game Assessment)",
        "game_tips": "• Practice 10 minutes daily on mental arithmetic apps (e.g. arithmetic speed drills).\n• In game tests, eliminate obvious wrong answers with order-of-magnitude estimation (e.g. 48 x 52 ≈ 50 x 50 = 2500).\n• Never get stuck on one difficult question: make an educated guess and maintain pacing.",
    },
    "think-agility": {
        "why_it_matters": "Measures task-switching efficiency, cognitive flexibility, and response inhibition in game modules.",
        "typical_mistakes": "Fixating on previous game rules when rule shifts happen; rushing without reading changing stimuli.",
        "practice_question": "Cognitive Game: Shape switching, color-word Stroop tasks, symbol matching.",
        "star_framework_guide": "Cognitive assessment: Train rapid dual-tasking and cognitive inhibition.",
        "sample_strong_response": "N/A (Cognitive Game Assessment)",
        "game_tips": "• Ensure you are fully rested with zero distractions before starting HireVue game assessments.\n• Read test tutorials carefully: practice rounds do not count towards your score, so use them to master the mechanics.\n• Stay focused on the primary sorting rule (e.g., color vs shape) and keep fingers hovering over arrow keys.",
    },
    "think-problem-solving": {
        "why_it_matters": "Evaluates deductive reasoning, finding pattern sequences, and logical deduction under time limits.",
        "typical_mistakes": "Guessing randomly before analyzing pattern transformations (rotation, color inversion, count changes).",
        "practice_question": "Cognitive Game: Matrix reasoning, progressive patterns, and system diagnosis.",
        "star_framework_guide": "Cognitive assessment: Analyze pattern changes systematically by one dimension at a time.",
        "sample_strong_response": "N/A (Cognitive Game Assessment)",
        "game_tips": "• Isolate one feature at a time: check shape movement, then shading/color, then element count.\n• Use process of elimination to discard choices that violate any single detected pattern rule.\n• Keep a small piece of scratch paper nearby to quickly jot down pattern codes.",
    },
}


@dataclass
class CoachingAdvice:
    competency_id: str
    competency_name: str
    category: str
    score: float
    is_development_area: bool
    why_it_matters: str
    typical_mistakes: str
    practice_question: str
    star_framework_guide: str
    sample_strong_response: str
    game_tips: str


def generate_coaching_advice(competencies: List[ScoredCompetency]) -> List[CoachingAdvice]:
    """Generates detailed coaching advice for all competencies, prioritizing development areas (scores <= 2.5)."""
    # Sort with lowest scores first (most urgent gaps)
    sorted_comps = sorted(competencies, key=lambda c: c.score)

    advice_list: List[CoachingAdvice] = []
    for comp in sorted_comps:
        kb_entry = COACHING_KNOWLEDGE_BASE.get(comp.id.lower())
        if not kb_entry:
            # Fallback for unmapped competencies
            is_game = "Cognitive" in comp.category or "think" in comp.id.lower()
            kb_entry = {
                "why_it_matters": f"Assesses core workplace capability in {comp.name}.",
                "typical_mistakes": "Giving generic answers without verifiable metrics or actions.",
                "practice_question": f"Give an example where you demonstrated high proficiency in {comp.name}.",
                "star_framework_guide": "Structure response using Situation, Task, Action, and Measurable Result.",
                "sample_strong_response": f"In my recent project, I took ownership of {comp.name} by setting clear benchmarks, collaborating with peers, and improving overall throughput by 20%.",
                "game_tips": "Review instructions thoroughly, maintain steady pacing, and avoid rushed guesses." if is_game else "N/A",
            }

        advice_list.append(
            CoachingAdvice(
                competency_id=comp.id,
                competency_name=comp.name,
                category=comp.category,
                score=comp.score,
                is_development_area=comp.score <= HIREVUE_THRESHOLD,
                why_it_matters=kb_entry["why_it_matters"],
                typical_mistakes=kb_entry["typical_mistakes"],
                practice_question=kb_entry["practice_question"],
                star_framework_guide=kb_entry["star_framework_guide"],
                sample_strong_response=kb_entry["sample_strong_response"],
                game_tips=kb_entry["game_tips"],
            )
        )

    return advice_list


def filter_development_areas(advice_list: List[CoachingAdvice]) -> List[CoachingAdvice]:
    """Filters advice list to only include development areas (<= 2.5)."""
    return [a for a in advice_list if a.is_development_area]
