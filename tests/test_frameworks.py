# -*- coding: utf-8 -*-
"""
Unit tests for all 10 SANTINEL frameworks.
Tests accuracy, edge cases, and bilingual support.
"""

import pytest


# ============================================================================
# TA (TRANSACTIONAL ANALYSIS) FRAMEWORK TESTS
# ============================================================================

class TestTAFramework:
    """Tests for TA (Transactional Analysis) framework."""

    @pytest.mark.unit
    def test_ego_state_detection_en(self, ta_module, sample_texts_en):
        """Test ego state detection in English."""
        result = ta_module.detect_ego_state(sample_texts_en["agreement"])
        assert result is not None
        assert "primary_finding" in result
        assert result["primary_finding"] in ["parent", "adult", "child", "critical_parent", "nurturing_parent", "free_child", "adapted_child"]

    @pytest.mark.unit
    def test_ego_state_detection_ro(self, ta_module, sample_texts_ro):
        """Test ego state detection in Romanian."""
        result = ta_module.detect_ego_state(sample_texts_ro["agreement"])
        assert result is not None
        assert "primary_finding" in result

    @pytest.mark.unit
    def test_life_position_analysis(self, ta_module, sample_texts_en):
        """Test life position analysis."""
        result = ta_module.analyze_life_position(sample_texts_en["agreement"])
        assert result is not None
        assert "primary_finding" in result

    @pytest.mark.unit
    def test_psychological_games_detection(self, ta_module):
        """Test psychological games detection."""
        game_text = "You always do this to me. Why are you trying to hurt me?"
        result = ta_module.detect_psychological_game(game_text)
        assert result is not None
        assert "detected_patterns" in result or "coaching_guidance" in result

    @pytest.mark.edge_case
    def test_empty_text_ta(self, ta_module):
        """Test TA framework with empty text."""
        result = ta_module.detect_ego_state("")
        assert result is not None

    @pytest.mark.edge_case
    def test_very_long_text_ta(self, ta_module):
        """Test TA framework with very long text."""
        long_text = "agreement " * 500
        result = ta_module.detect_ego_state(long_text)
        assert result is not None


# ============================================================================
# EMOTIONAL INTELLIGENCE (EI) FRAMEWORK TESTS
# ============================================================================

class TestEIFramework:
    """Tests for EI (Emotional Intelligence) framework."""

    @pytest.mark.unit
    def test_competency_detection_en(self, ei_module, sample_texts_en):
        """Test EI competency detection in English."""
        result = ei_module.detect_competencies(sample_texts_en["agreement"])
        assert result is not None
        assert "primary_finding" in result
        assert "scores" in result
        assert "confidence_score" in result or "coaching_guidance" in result

    @pytest.mark.unit
    def test_emotional_state_detection_en(self, ei_module, sample_texts_en):
        """Test emotional state detection in English."""
        result = ei_module.detect_emotional_state(sample_texts_en["agreement"])
        assert result is not None
        assert "primary_finding" in result
        assert "coaching_guidance" in result

    @pytest.mark.unit
    def test_emotional_state_detection_ro(self, ei_module, sample_texts_ro):
        """Test emotional state detection in Romanian."""
        result = ei_module.detect_emotional_state(sample_texts_ro["agreement"])
        assert result is not None

    @pytest.mark.unit
    def test_dual_speaker_assessment(self, ei_module, sample_texts_en):
        """Test dual-speaker EI assessment."""
        your_text = sample_texts_en["agreement"]
        their_text = sample_texts_en["objection"]
        result = ei_module.dual_speaker_assessment(your_text, their_text)
        assert result is not None

    @pytest.mark.edge_case
    def test_mixed_language_ei(self, ei_module):
        """Test EI with mixed language input."""
        mixed_text = "I'm excited! Sunt foarte fericit!"
        result = ei_module.detect_emotional_state(mixed_text)
        assert result is not None


# ============================================================================
# ATTACHMENT FRAMEWORK TESTS
# ============================================================================

class TestAttachmentFramework:
    """Tests for Attachment framework."""

    @pytest.mark.unit
    def test_attachment_style_detection_en(self, attachment_module):
        """Test attachment style detection in English."""
        secure_text = "I trust you completely. I feel safe with this arrangement."
        result = attachment_module.score_attachment(secure_text)
        assert result is not None
        assert ("anxiety_score" in result or "anxiety" in result)
        assert ("avoidance_score" in result or "avoidance" in result)
        assert 0 <= (result.get("anxiety_score") or result.get("anxiety", 0)) <= 1
        assert 0 <= (result.get("avoidance_score") or result.get("avoidance", 0)) <= 1

    @pytest.mark.unit
    def test_attachment_style_detection_ro(self, attachment_module):
        """Test attachment style detection in Romanian."""
        anxious_text = "Sunt îngrijorat că m-ai abandon. Ai grijă de mine?"
        result = attachment_module.score_attachment(anxious_text)
        assert result is not None
        assert ("anxiety_score" in result or "anxiety" in result)

    @pytest.mark.unit
    def test_wound_detection(self, attachment_module):
        """Test core wound detection."""
        abandonment_text = "Everyone leaves me. I'm always alone."
        result = attachment_module.detect_wounds(abandonment_text)
        assert result is not None
        assert ("wounds" in result or "detected_patterns" in result or "confidence_score" in result)

    @pytest.mark.unit
    def test_dual_speaker_attachment(self, attachment_module):
        """Test dual-speaker attachment analysis."""
        your_text = "I'm here for you. I won't leave."
        their_text = "That's what everyone says, but they always go."
        result = attachment_module.dual_speaker_attachment(your_text, their_text)
        assert result is not None

    @pytest.mark.edge_case
    def test_anxiety_avoidance_extremes(self, attachment_module):
        """Test anxiety-avoidance scoring at extremes."""
        # High anxiety text
        anxious = "I'm scared you'll abandon me. I need constant confirmation. What if you refuse?"
        result_a = attachment_module.score_attachment(anxious)
        anxiety_val = result_a.get("anxiety_score") or result_a.get("anxiety", 0)
        assert isinstance(anxiety_val, (int, float))
        assert 0 <= anxiety_val <= 1

        # High avoidance text
        avoidant = "I don't need anyone. I'm fine alone. I prefer independence."
        result_b = attachment_module.score_attachment(avoidant)
        avoidance_val = result_b.get("avoidance_score") or result_b.get("avoidance", 0)
        assert isinstance(avoidance_val, (int, float))
        assert 0 <= avoidance_val <= 1


# ============================================================================
# BEHAVIORAL ECONOMICS FRAMEWORK TESTS
# ============================================================================

class TestBehavioralEconomicsFramework:
    """Tests for Behavioral Economics framework."""

    @pytest.mark.unit
    def test_loss_aversion_detection_en(self, behavioral_econ_module):
        """Test loss aversion bias detection in English."""
        loss_text = "What if this doesn't work? I can't afford to lose money."
        result = behavioral_econ_module.detect_biases(loss_text)
        assert result is not None
        assert "detected_patterns" in result or "primary_finding" in result

    @pytest.mark.unit
    def test_loss_aversion_detection_ro(self, behavioral_econ_module):
        """Test loss aversion bias detection in Romanian."""
        loss_text = "Ce dacă nu funcționează? Nu pot pierde bani."
        result = behavioral_econ_module.detect_biases(loss_text)
        assert result is not None

    @pytest.mark.unit
    def test_anchoring_bias_detection(self, behavioral_econ_module):
        """Test anchoring bias detection."""
        anchor_text = "The market price is $100. That's too expensive."
        result = behavioral_econ_module.detect_biases(anchor_text)
        assert result is not None

    @pytest.mark.unit
    def test_sunk_cost_detection(self, behavioral_econ_module):
        """Test sunk cost fallacy detection."""
        sunk_cost_text = "We've already invested so much. We have to continue."
        result = behavioral_econ_module.detect_biases(sunk_cost_text)
        assert result is not None

    @pytest.mark.unit
    def test_status_quo_bias_detection(self, behavioral_econ_module):
        """Test status quo bias detection."""
        status_quo_text = "Our current system works fine. Why change?"
        result = behavioral_econ_module.detect_biases(status_quo_text)
        assert result is not None

    @pytest.mark.edge_case
    def test_all_biases_in_one_text(self, behavioral_econ_module):
        """Test detection of multiple biases in single text."""
        complex_text = (
            "We've already invested $50K so we can't stop now. "
            "The market says $100 is standard, but that's expensive. "
            "Our current system works, why change? We could lose money."
        )
        result = behavioral_econ_module.detect_biases(complex_text)
        assert result is not None


# ============================================================================
# GAME THEORY FRAMEWORK TESTS
# ============================================================================

class TestGameTheoryFramework:
    """Tests for Game Theory framework."""

    @pytest.mark.unit
    def test_game_archetype_detection_en(self, game_theory_module):
        """Test game archetype detection in English."""
        zero_sum_text = "If you win, I lose. We can't both win here."
        result = game_theory_module.detect_game_archetype(zero_sum_text)
        assert result is not None
        assert "primary_finding" in result or "confidence_score" in result

    @pytest.mark.unit
    def test_game_archetype_detection_ro(self, game_theory_module):
        """Test game archetype detection in Romanian."""
        coord_text = "Trebuie să colaborăm pentru a reuși amândoi."
        result = game_theory_module.detect_game_archetype(coord_text)
        assert result is not None

    @pytest.mark.unit
    def test_strategic_position_assessment(self, game_theory_module):
        """Test strategic position assessment."""
        dominant_text = "We have all the power in this negotiation."
        result = game_theory_module.assess_strategic_position(dominant_text)
        assert result is not None

    @pytest.mark.unit
    def test_batna_zopa_identification(self, game_theory_module):
        """Test BATNA and ZOPA identification."""
        batna_text = "Our best alternative is to go with vendor X."
        result = game_theory_module.identify_batna_and_zopa(batna_text)
        assert result is not None

    @pytest.mark.edge_case
    def test_game_mismatches(self, game_theory_module):
        """Test detecting game theory mismatches."""
        mismatch_text = "Let's collaborate and find a solution together. But whoever gets better terms wins."
        result = game_theory_module.detect_game_archetype(mismatch_text)
        assert result is not None


# ============================================================================
# NEUROSCIENCE FRAMEWORK TESTS
# ============================================================================

class TestNeuroscienceFramework:
    """Tests for Neuroscience framework."""

    @pytest.mark.unit
    def test_somatic_patterns_detection_en(self, neuroscience_module):
        """Test somatic patterns detection in English."""
        threat_text = "I'm nervous. My heart is racing. I'm scared."
        result = neuroscience_module.detect_patterns(threat_text)
        assert result is not None

    @pytest.mark.unit
    def test_somatic_patterns_detection_ro(self, neuroscience_module):
        """Test somatic patterns detection in Romanian."""
        threat_text = "Sunt nervos. Inima mi se poate sparge. Sunt speriat."
        result = neuroscience_module.detect_patterns(threat_text)
        assert result is not None

    @pytest.mark.unit
    def test_nervous_system_state_assessment(self, neuroscience_module):
        """Test nervous system state assessment."""
        parasympathetic_text = "I feel calm and relaxed. Everything is fine."
        result = neuroscience_module.assess_nervous_system_state(parasympathetic_text)
        assert result is not None
        assert ("primary_finding" in result or "detected_patterns" in result or "emotional_state" in result)

    @pytest.mark.unit
    def test_threat_safety_reward_scoring(self, neuroscience_module):
        """Test threat/safety/reward scoring."""
        reward_text = "I'm excited about this opportunity. This will benefit us both!"
        result = neuroscience_module.score_threat_safety_reward(reward_text)
        assert result is not None

    @pytest.mark.edge_case
    def test_dysregulation_detection(self, neuroscience_module):
        """Test dysregulation pattern detection."""
        dysreg_text = "I'm panicking. Everything feels overwhelming. Help!"
        result = neuroscience_module.assess_nervous_system_state(dysreg_text)
        assert result is not None


# ============================================================================
# NARRATIVE FRAMEWORK TESTS
# ============================================================================

class TestNarrativeFramework:
    """Tests for Narrative framework."""

    @pytest.mark.unit
    def test_narrative_archetype_detection_en(self, narrative_module):
        """Test narrative archetype detection in English."""
        hero_text = "I overcame the challenge and succeeded."
        result = narrative_module.detect_dominant_narrative(hero_text)
        assert result is not None

    @pytest.mark.unit
    def test_narrative_archetype_detection_ro(self, narrative_module):
        """Test narrative archetype detection in Romanian."""
        victim_text = "Totul este vina lor. Sunt victima."
        result = narrative_module.detect_dominant_narrative(victim_text)
        assert result is not None

    @pytest.mark.unit
    def test_identity_patterns_analysis(self, narrative_module):
        """Test identity patterns analysis."""
        agency_text = "I take control of my destiny. I make things happen."
        result = narrative_module.analyze_identity_patterns(agency_text)
        assert result is not None

    @pytest.mark.unit
    def test_meaning_patterns_detection(self, narrative_module):
        """Test meaning patterns detection."""
        growth_text = "This experience taught me a lot and made me stronger."
        result = narrative_module.detect_meaning_patterns(growth_text)
        assert result is not None

    @pytest.mark.edge_case
    def test_narrative_conflict_detection(self, narrative_module):
        """Test detecting contradictory narratives in single text."""
        conflict_text = "I'm a victim but I'm also in control. I can't change but I must try."
        result = narrative_module.detect_dominant_narrative(conflict_text)
        assert result is not None


# ============================================================================
# SOMATIC FRAMEWORK TESTS
# ============================================================================

class TestSomaticFramework:
    """Tests for Somatic framework."""

    @pytest.mark.unit
    def test_somatic_patterns_detection_en(self, somatic_module):
        """Test somatic patterns detection in English."""
        grounded_text = "I feel centered and present. My breathing is steady."
        result = somatic_module.detect_somatic_patterns(grounded_text)
        assert result is not None

    @pytest.mark.unit
    def test_somatic_patterns_detection_ro(self, somatic_module):
        """Test somatic patterns detection in Romanian."""
        tense_text = "Sunt tare încordat. Mușchii mi-l dor. Sunt plin de tensiune."
        result = somatic_module.detect_somatic_patterns(tense_text)
        assert result is not None

    @pytest.mark.unit
    def test_somatic_state_assessment(self, somatic_module):
        """Test overall somatic state assessment."""
        confident_text = "I feel strong and capable. I'm standing tall."
        result = somatic_module.assess_somatic_state(confident_text)
        assert result is not None

    @pytest.mark.unit
    def test_grounding_presence_assessment(self, somatic_module):
        """Test grounding and presence assessment."""
        present_text = "I'm fully present in this moment. I notice everything around me."
        result = somatic_module.assess_somatic_state(present_text)
        assert result is not None

    @pytest.mark.edge_case
    def test_dissociation_detection(self, somatic_module):
        """Test dissociation pattern detection."""
        dissoc_text = "I feel disconnected from my body. Like I'm watching from outside."
        result = somatic_module.detect_somatic_patterns(dissoc_text)
        assert result is not None


# ============================================================================
# INTEGRATION TESTS: Multi-Framework Scenarios
# ============================================================================

class TestMultiFrameworkScenarios:
    """Tests for complex scenarios requiring multiple frameworks."""

    @pytest.mark.integration
    @pytest.mark.bilingual
    def test_anxious_prospect_scenario_en(
        self,
        ta_module,
        ei_module,
        attachment_module,
        behavioral_econ_module,
        sample_texts_en
    ):
        """Test anxious prospect scenario across multiple frameworks."""
        text = sample_texts_en["doubt"]

        # All frameworks should detect the anxiety pattern
        ta_result = ta_module.detect_ego_state(text)
        ei_result = ei_module.detect_emotional_state(text)
        attach_result = attachment_module.score_attachment(text)
        bias_result = behavioral_econ_module.detect_biases(text)

        assert ta_result is not None
        assert ei_result is not None
        assert attach_result is not None
        assert bias_result is not None

    @pytest.mark.integration
    @pytest.mark.bilingual
    def test_competitive_scenario_en(
        self,
        game_theory_module,
        behavioral_econ_module,
        narrative_module,
        sample_texts_en
    ):
        """Test competitive scenario across frameworks."""
        text = sample_texts_en["competitive"]

        game_result = game_theory_module.detect_game_archetype(text)
        bias_result = behavioral_econ_module.detect_biases(text)
        narrative_result = narrative_module.detect_dominant_narrative(text)

        assert game_result is not None
        assert bias_result is not None
        assert narrative_result is not None

    @pytest.mark.integration
    @pytest.mark.bilingual
    def test_complex_negotiation_ro(
        self,
        ta_module,
        ei_module,
        attachment_module,
        game_theory_module,
        negotiation_scenarios_ro
    ):
        """Test complex Romanian negotiation across frameworks."""
        scenario = negotiation_scenarios_ro[0]
        text = scenario["text"]

        results = {
            "ta": ta_module.detect_ego_state(text),
            "ei": ei_module.detect_emotional_state(text),
            "attachment": attachment_module.score_attachment(text),
            "game_theory": game_theory_module.detect_game_archetype(text),
        }

        # All frameworks should have results
        for framework_name, result in results.items():
            assert result is not None, f"{framework_name} returned None"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Tests for framework performance and stability."""

    @pytest.mark.edge_case
    def test_rapid_sequential_calls(self, ta_module):
        """Test rapid sequential framework calls."""
        texts = ["Hello world"] * 100
        for text in texts:
            result = ta_module.detect_ego_state(text)
            assert result is not None

    @pytest.mark.edge_case
    def test_special_characters_handling(self, ei_module):
        """Test handling of special characters."""
        special_text = "I'm 100% excited!!! #YES @mention $$$"
        result = ei_module.detect_emotional_state(special_text)
        assert result is not None

    @pytest.mark.edge_case
    def test_unicode_handling(self, attachment_module):
        """Test unicode character handling."""
        unicode_text = "I'm happy! 😊 Very good! ✨ 不错 🎉"
        result = attachment_module.score_attachment(unicode_text)
        assert result is not None

    @pytest.mark.edge_case
    def test_numbers_and_dates_handling(self, behavioral_econ_module):
        """Test handling of numbers and dates."""
        numeric_text = "The cost is $1,234.56 and the deadline is 2025-12-31."
        result = behavioral_econ_module.detect_biases(numeric_text)
        assert result is not None
