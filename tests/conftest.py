# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures for SANTINEL framework testing.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path so we can import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ta_module import TAModule
from core.ei_module import EIModule
from core.attachment_module import AttachmentModule
from core.behavioral_econ_module import BehavioralEconomicsModule
from core.game_theory_module import GameTheoryModule
from core.neuroscience_module import NeuroscienceModule
from core.narrative_module import NarrativeModule
from core.somatic_module import SomaticModule
from core.feedback_extraction_module import FeedbackExtractionModule
from core.sales_scripts_module import SalesScriptsModule
from core.santinel_unified_coach import SantinelUnifiedCoach


# ============================================================================
# FIXTURES: Framework Instances
# ============================================================================

@pytest.fixture
def ta_module():
    """TA module instance."""
    return TAModule()


@pytest.fixture
def ei_module():
    """EI module instance."""
    return EIModule()


@pytest.fixture
def attachment_module():
    """Attachment module instance."""
    return AttachmentModule()


@pytest.fixture
def behavioral_econ_module():
    """Behavioral Economics module instance."""
    return BehavioralEconomicsModule()


@pytest.fixture
def game_theory_module():
    """Game Theory module instance."""
    return GameTheoryModule()


@pytest.fixture
def neuroscience_module():
    """Neuroscience module instance."""
    return NeuroscienceModule()


@pytest.fixture
def narrative_module():
    """Narrative module instance."""
    return NarrativeModule()


@pytest.fixture
def somatic_module():
    """Somatic module instance."""
    return SomaticModule()


@pytest.fixture
def feedback_module():
    """Feedback Extraction module instance."""
    return FeedbackExtractionModule()


@pytest.fixture
def sales_scripts_module():
    """Sales Scripts module instance."""
    return SalesScriptsModule()


@pytest.fixture
def unified_coach():
    """Unified Coach instance."""
    return SantinelUnifiedCoach()


# ============================================================================
# FIXTURES: Test Data (English)
# ============================================================================

@pytest.fixture
def sample_texts_en():
    """Sample English texts for testing."""
    return {
        "agreement": "Yes, I love this idea. Let's move forward. I'm excited!",
        "objection": "I don't think this will work. I'm not comfortable with this approach.",
        "doubt": "I'm not sure about this. I'm hesitant. Let me think about it.",
        "stalling": "Let me get back to you later. I need to discuss this with my team first.",
        "question": "How does this work? Can you explain the process?",
        "urgency": "We need to move quickly. The deadline is approaching. We must decide now!",
        "budget": "What's the cost? Can you negotiate on price? How much will this cost us?",
        "competitive": "We're looking at other vendors. Your competitor is cheaper.",
    }


@pytest.fixture
def sample_texts_ro():
    """Sample Romanian texts for testing."""
    return {
        "agreement": "Da, îmi place această idee. Să mergem mai departe. Sunt entuziasmat!",
        "objection": "Nu cred că va funcționa. Nu sunt confortabil cu această abordare.",
        "doubt": "Nu sunt sigur de asta. Sunt ezitant. Lasă-mă să mă gândesc.",
        "stalling": "Te sun mai târziu. Trebuie să discut asta cu echipa mea.",
        "question": "Cum funcționează? Poți explica procesul?",
        "urgency": "Trebuie să ne mișcăm rapid. Termen limită se apropie. Trebuie să decidem acum!",
        "budget": "Care este costul? Poți negocia prețul? Cât va costa pentru noi?",
        "competitive": "Ne uităm la alți furnizori. Competitorul tău este mai ieftin.",
    }


@pytest.fixture
def negotiation_scenarios_en():
    """Complex English negotiation scenarios."""
    return [
        {
            "name": "Anxious prospect with loss aversion",
            "text": "I'm worried about making the wrong choice. What if this doesn't work? I've seen other vendors fail. And honestly, they're cheaper. What if I'm throwing money away?",
            "expected_patterns": ["doubt", "objection", "budget_concern", "loss_aversion"],
        },
        {
            "name": "Dominant personality with zero-sum framing",
            "text": "I appreciate it, but frankly, I'm shopping around. Your competitor offered X and Y. They're also cheaper. I need to see why I should pick you. Why shouldn't I just go with them?",
            "expected_patterns": ["competitive", "zero_sum", "budget_concern"],
        },
        {
            "name": "Secure attachment ready to close",
            "text": "Yes, I'm excited about this. I trust you. I'm comfortable moving forward. I just want to make sure we have a clear implementation plan.",
            "expected_patterns": ["agreement", "trust", "clarification"],
        },
    ]


@pytest.fixture
def negotiation_scenarios_ro():
    """Complex Romanian negotiation scenarios."""
    return [
        {
            "name": "Prospect anxios cu aversiune la pierdere",
            "text": "Îmi este frică să fac o alegere greșită. Ce dacă nu funcționează? Am văzut că alți furnizori au eșuat. Și sunt mai ieftini. Ce dacă cheltuiesc bani degeaba?",
            "expected_patterns": ["doubt", "objection", "budget_concern", "loss_aversion"],
        },
        {
            "name": "Personalitate dominantă cu gândire zero-sum",
            "text": "Apreciez, dar cinstit vorbind, mă uit pe alte opțiuni. Competitorul tău a oferit X și Y. Sunt și mai ieftini. Trebuie să-mi arăți de ce ar trebui să te aleg pe tine.",
            "expected_patterns": ["competitive", "zero_sum", "budget_concern"],
        },
    ]


# ============================================================================
# FIXTURES: Expected Results
# ============================================================================

@pytest.fixture
def expected_ego_states():
    """Expected TA ego states."""
    return ["parent", "adult", "child"]


@pytest.fixture
def expected_attachment_styles():
    """Expected attachment styles."""
    return ["secure", "anxious", "avoidant", "fearful_avoidant"]


@pytest.fixture
def expected_emotional_states():
    """Expected EI emotional states."""
    return ["openness", "skepticism", "frustration", "curiosity", "fear", "acceptance"]


@pytest.fixture
def expected_biases():
    """Expected behavioral economics biases."""
    return ["loss_aversion", "anchoring", "sunk_cost", "framing", "status_quo", "availability"]


@pytest.fixture
def expected_game_archetypes():
    """Expected game theory archetypes."""
    return ["prisoners_dilemma", "zero_sum", "coordination", "battle_of_sexes"]


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "bilingual: mark test as testing bilingual capability"
    )
    config.addinivalue_line(
        "markers", "edge_case: mark test as testing edge cases"
    )
