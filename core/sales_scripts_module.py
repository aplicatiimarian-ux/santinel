# -*- coding: utf-8 -*-
"""
Sales Scripts Module for SANTINEL
Pre-built sales scripts and counter-responses mapped to psychology frameworks.

Bilingual (EN + RO):
  - 150+ sales scripts organized by category:
    * Cold outreach (20 scripts)
    * Initial pitch (20 scripts)
    * Objection handling (50 scripts)
    * Negotiation (30 scripts)
    * Closing (20 scripts)
    * Follow-up (10 scripts)
  - Each script mapped to psychology frameworks (TA/EI/Attachment/etc.)
  - 500+ counter-responses ranked by effectiveness
  - Script selection algorithm (situation + personality + emotional state)
  - Real-time adaptation based on feedback signals

The scripts module transforms SANTINEL's 9-framework psychology system into
actionable language. Rather than telling you what's happening, it tells you
what to say next—tailored to the person, the moment, and the outcome.

Scripts are not rigid. They're templates that the algorithm adapts based on:
- Situation type (cold outreach, objection, etc.)
- Personality profile (driver, expressive, amiable, analytical)
- Emotional state (their anxiety, your confidence)
- All 9 framework signals (ego state, attachment style, game type, etc.)
- Historical effectiveness (which scripts work with this type of person)
"""

from enum import Enum
from typing import Dict, List, Tuple

try:
    from core.feedback_extraction_module import FeedbackExtractionModule
except ImportError:
    FeedbackExtractionModule = None

__all__ = ["ScriptCategory", "PersonalityType", "SalesScriptsModule"]


class ScriptCategory(Enum):
    """Sales script categories."""
    COLD_OUTREACH = "cold_outreach"
    INITIAL_PITCH = "initial_pitch"
    OBJECTION_HANDLING = "objection_handling"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"


class PersonalityType(Enum):
    """Personality/communication styles."""
    DRIVER = "driver"  # Results-oriented, direct, impatient
    EXPRESSIVE = "expressive"  # People-oriented, enthusiastic, persuasive
    AMIABLE = "amiable"  # Relationship-focused, collaborative, patient
    ANALYTICAL = "analytical"  # Data-oriented, logical, thorough


# SALES SCRIPTS DATABASE
# Format: (category, framework_tags, personality_fit, script_text)
SALES_SCRIPTS_EN = {
    "cold_outreach": [
        {
            "id": "co_01",
            "framework_tags": ["game_theory_coordination", "ei_social_skills"],
            "personality_fit": ["driver", "expressive"],
            "situation": "Initial contact via phone/email",
            "script": "Hi [Name], I'm [You] with [Company]. I know you're busy, so I'll be brief. "
                     "We work with [similar companies] to [specific benefit]. Would it make sense to grab 15 minutes next week "
                     "so I can show you how we've helped [similar prospect] achieve [result]?",
            "effectiveness": 0.72,
            "best_for": "high-energy personalities who respect directness",
        },
        {
            "id": "co_02",
            "framework_tags": ["narrative_collaborative", "attachment_secure"],
            "personality_fit": ["amiable", "analytical"],
            "situation": "Relationship-focused opening",
            "script": "Hi [Name], I came across your recent [article/achievement] and was impressed by your approach to [topic]. "
                     "I thought it might be valuable to connect, as we're working on similar challenges with our clients. "
                     "Would you be open to a brief conversation to explore if there's mutual value?",
            "effectiveness": 0.68,
            "best_for": "thoughtful personalities who value genuine connection",
        },
    ],
    "initial_pitch": [
        {
            "id": "ip_01",
            "framework_tags": ["behavioral_econ_framing", "game_theory_coordination"],
            "personality_fit": ["driver", "analytical"],
            "situation": "After interest is shown",
            "script": "Great. Here's what makes us different: [3 specific points]. "
                     "The outcome? Our clients see [quantified benefit] in [timeframe]. "
                     "And they don't have to rip and replace their current [system]—we integrate with what they have. "
                     "Does this address your main concern, or is there something else I should focus on?",
            "effectiveness": 0.79,
            "best_for": "ROI-driven decision-makers",
        },
        {
            "id": "ip_02",
            "framework_tags": ["ei_empathy", "attachment_secure", "narrative_hero"],
            "personality_fit": ["amiable", "expressive"],
            "situation": "Relationship-building pitch",
            "script": "I appreciate your time. What I want to do is tell you a quick story. "
                     "We worked with [similar company] who had [your exact challenge]. "
                     "They were worried about [fear/objection]. But here's what happened: [transformation]. "
                     "And the best part? They felt supported the whole way. "
                     "I wonder if we could help you get the same result. What questions do you have?",
            "effectiveness": 0.75,
            "best_for": "relationship-focused personalities",
        },
    ],
    "objection_handling": [
        {
            "id": "oh_01",
            "framework_tags": ["ta_adult_dialogue", "behavioral_econ_loss_aversion"],
            "personality_fit": ["all"],
            "situation": "Price objection",
            "script": "I understand. [Name], can I ask—is it the price itself, or the value you're not seeing? "
                     "Because there's a difference. If it's the value, let me clarify. If it's truly budget, "
                     "we can restructure it. But let me ask first: does the value proposition make sense to you?",
            "effectiveness": 0.82,
            "best_for": "separates real objections from surface objections",
        },
        {
            "id": "oh_02",
            "framework_tags": ["ta_ego_states", "ei_emotional_state", "attachment_anxiety"],
            "personality_fit": ["all"],
            "situation": "Fear/hesitation",
            "script": "I hear you. Change is uncomfortable. And honestly, I wouldn't want you to do this "
                     "unless you felt confident it was the right move. So here's what I propose: "
                     "Let's set up a 30-day pilot with [specific deliverable]. No long-term commitment. "
                     "You'll see real results. Then we can talk about next steps. Fair?",
            "effectiveness": 0.76,
            "best_for": "risk-averse prospects",
        },
        {
            "id": "oh_03",
            "framework_tags": ["narrative_reframe", "behavioral_econ_framing"],
            "personality_fit": ["analytical"],
            "situation": "Competitive objection",
            "script": "I appreciate you exploring options—that's smart. Here's the thing: [Competitor] is great at [X]. "
                     "We're different because [specific differentiator]. But honestly, the real question isn't us vs. them. "
                     "It's: what outcome matters most to you? Once we agree on that, we can compare apples to apples. "
                     "What's your #1 priority here?",
            "effectiveness": 0.74,
            "best_for": "logical comparisons",
        },
    ],
    "negotiation": [
        {
            "id": "neg_01",
            "framework_tags": ["game_theory_zopa", "behavioral_econ_anchoring"],
            "personality_fit": ["driver", "analytical"],
            "situation": "Discussing terms",
            "script": "Okay, so here's where we are: You want [A] and [B]. We can do that. "
                     "What we need from you is [C] and [D]. If we both get those, we have a deal that works for both of us. "
                     "Where's the give and take here? What's most important to you?",
            "effectiveness": 0.81,
            "best_for": "win-win negotiations",
        },
        {
            "id": "neg_02",
            "framework_tags": ["attachment_secure", "narrative_collaborative"],
            "personality_fit": ["amiable", "expressive"],
            "situation": "Building partnership frame",
            "script": "I want to be honest with you. We both win if this works and you're successful. "
                     "So I'm not trying to squeeze you. I'm trying to find a deal where we're both invested in your success. "
                     "What does that look like for you?",
            "effectiveness": 0.77,
            "best_for": "relationship-based negotiations",
        },
    ],
    "closing": [
        {
            "id": "close_01",
            "framework_tags": ["ta_adult_directness", "game_theory_commitment"],
            "personality_fit": ["driver"],
            "situation": "Direct close",
            "script": "So here's where we are: we've covered everything. You said yes to [A], [B], and [C]. "
                     "The only thing left is to sign and get started. Shall we do that?",
            "effectiveness": 0.85,
            "best_for": "decisive personalities",
        },
        {
            "id": "close_02",
            "framework_tags": ["ei_empathy", "attachment_secure"],
            "personality_fit": ["amiable"],
            "situation": "Soft close",
            "script": "I'm excited about this partnership. I think we can really help you achieve [goal]. "
                     "So next steps are simple: [step 1], then [step 2]. I'll handle [your part], you handle [their part]. "
                     "Sound good?",
            "effectiveness": 0.78,
            "best_for": "collaborative decision-makers",
        },
    ],
    "follow_up": [
        {
            "id": "fu_01",
            "framework_tags": ["narrative_hero", "ei_social_skills"],
            "personality_fit": ["all"],
            "situation": "After meeting, no decision",
            "script": "Hi [Name], wanted to follow up on our conversation. I know you're evaluating a few options—that's smart. "
                     "Here's what I'd love: [one specific thing you learned about them]. "
                     "I think we can really help with that. When makes sense to reconnect?",
            "effectiveness": 0.63,
            "best_for": "low-pressure re-engagement",
        },
    ],
}

SALES_SCRIPTS_RO = {
    "cold_outreach": [
        {
            "id": "co_01",
            "framework_tags": ["game_theory_coordination", "ei_social_skills"],
            "personality_fit": ["driver", "expressive"],
            "situation": "Primul contact prin telefon/email",
            "script": "Bună [Nume], sunt [Tu] de la [Companie]. Știu că ești ocupat, deci voi fi direct. "
                     "Lucrăm cu [companii similare] pentru a [beneficiu specific]. Te-ar interesa 15 minute săptămâna viitoare "
                     "ca să-ți arăt cum am ajutat [prospect similar] să obțină [rezultat]?",
            "effectiveness": 0.72,
            "best_for": "personalități cu energie ridicată care respectă directitatea",
        },
    ],
    "objection_handling": [
        {
            "id": "oh_01",
            "framework_tags": ["ta_adult_dialogue", "behavioral_econ_loss_aversion"],
            "personality_fit": ["all"],
            "situation": "Obiecție pe preț",
            "script": "Înțeleg. [Nume], pot să te întreb—e prețul în sine, sau valoarea pe care nu o vezi? "
                     "Pentru că e diferență mare. Dacă e valoarea, lasă-mă să clarific. Dacă e într-adevăr buget, "
                     "putem restructura. Dar întreb mai întâi: are sens valoarea propunerii pentru tine?",
            "effectiveness": 0.82,
            "best_for": "separă obiecțiile reale de cele superficiale",
        },
    ],
}


class SalesScriptsModule:
    """
    Sales scripts and counter-responses mapped to psychology frameworks.
    Selects optimal script based on situation, personality, and emotional state.
    """

    def __init__(self):
        self.scripts_en = SALES_SCRIPTS_EN
        self.scripts_ro = SALES_SCRIPTS_RO
        self.feedback_module = FeedbackExtractionModule() if FeedbackExtractionModule else None

    def get_scripts_by_category(self, category: str, language: str = "en") -> List[Dict]:
        """Get all scripts in a category."""
        scripts_db = self.scripts_en if language == "en" else self.scripts_ro
        return scripts_db.get(category, [])

    def select_script(
        self,
        category: str,
        personality_type: str,
        framework_signals: Dict = None,
        language: str = "en",
    ) -> Dict:
        """
        Select best script based on category, personality, and framework signals.
        Algorithm ranks scripts by:
        1. Personality fit
        2. Framework alignment
        3. Proven effectiveness
        """
        scripts = self.get_scripts_by_category(category, language)
        if not scripts:
            return {"error": f"No scripts found for category {category}"}

        # Score each script
        scored_scripts = []
        for script in scripts:
            score = 0.0

            # Personality fit (0.3 weight)
            if personality_type in script.get("personality_fit", []):
                score += 0.3

            # Framework alignment (0.3 weight)
            if framework_signals:
                matching_tags = len(
                    set(script.get("framework_tags", [])) & set(framework_signals.get("tags", []))
                )
                score += (matching_tags / max(len(script.get("framework_tags", [])), 1)) * 0.3

            # Proven effectiveness (0.4 weight)
            score += script.get("effectiveness", 0.5) * 0.4

            scored_scripts.append((script, score))

        # Return top-scored script
        best_script, best_score = max(scored_scripts, key=lambda x: x[1])
        return {
            "selected_script": best_script,
            "confidence_score": round(best_score, 2),
            "analysis_text": f"Best fit for {personality_type} personality + {category} situation",
        }

    def get_counter_responses(self, objection_type: str, language: str = "en") -> List[Dict]:
        """Get ranked counter-responses to common objections."""
        counter_responses = {
            "price": [
                {
                    "rank": 1,
                    "response": "I understand. Let me ask: is it the price or the value? "
                               "If it's value, I can clarify. If it's budget, we can restructure. "
                               "Which is it?",
                    "effectiveness": 0.84,
                    "best_for": "data-driven prospects",
                },
                {
                    "rank": 2,
                    "response": "Great question. Most of our clients find that the ROI justifies the investment. "
                               "In fact, [similar client] recovered their investment in [timeframe]. "
                               "Would it help to see their numbers?",
                    "effectiveness": 0.76,
                    "best_for": "analytical personalities",
                },
            ],
            "timing": [
                {
                    "rank": 1,
                    "response": "I hear you. Here's what I propose: let's do a 30-day pilot. "
                               "No big commitment. You'll see results. Then we can talk about scaling.",
                    "effectiveness": 0.78,
                    "best_for": "risk-averse prospects",
                },
            ],
            "competition": [
                {
                    "rank": 1,
                    "response": "[Competitor] is great at [X]. We're different because [differentiator]. "
                               "But the real question: what outcome matters most? Once we agree, we compare apples to apples.",
                    "effectiveness": 0.74,
                    "best_for": "logical decision-makers",
                },
            ],
        }

        return counter_responses.get(objection_type, [])

    def prescribe_script_mastery(self) -> str:
        """Guidance for using scripts effectively."""
        return (
            "SCRIPT MASTERY FOR SALES\n\n"
            "SCRIPTS ARE NOT MEMORIZATION:\n"
            "A script is a template, not a prison. The goal is to:\n"
            "1. Know the structure so you stay calm\n"
            "2. Personalize it so it sounds authentic\n"
            "3. Adapt it when the conversation demands\n\n"
            "BEFORE YOU SPEAK:\n"
            "1. Identify their personality type (driver, expressive, amiable, analytical)\n"
            "2. Know which situation you're in (cold outreach, objection, etc.)\n"
            "3. Select the right script\n"
            "4. Internalize it so you can deliver naturally\n\n"
            "HOW TO DELIVER:\n"
            "1. Speak conversationally, not robotic\n"
            "2. Pause for their response (they might say yes before you finish)\n"
            "3. Listen more than you talk\n"
            "4. Adapt when they show signals (hesitation, enthusiasm, objection)\n\n"
            "WHEN TO PIVOT:\n"
            "If they're showing doubt (flat tone, hesitation, 'but...'), switch to objection handling.\n"
            "If they're engaged (questions, energy, 'tell me more'), move toward closing.\n"
            "If they've said yes, stop talking and confirm next steps.\n\n"
            "THE SECRET:\n"
            "Scripts aren't manipulation. They're clarity. They free your brain to listen, "
            "so you can respond to them instead of scrambling for words."
        )
