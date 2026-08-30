# -*- coding: utf-8 -*-
"""
Unit tests for Feedback Extraction framework.
Tests verbal signals, vocal signals, and close probability scoring.
"""

import pytest


class TestFeedbackExtractionFramework:
    """Tests for Feedback Extraction framework."""

    # ========================================================================
    # VERBAL SIGNALS TESTS
    # ========================================================================

    @pytest.mark.unit
    def test_agreement_signal_detection_en(self, feedback_module):
        """Test agreement signal detection in English."""
        agreement_text = "Yes, absolutely! That sounds perfect. Let's move forward!"
        result = feedback_module.detect_verbal_signals(agreement_text)
        assert result is not None
        assert "agreement" in result or "signals" in result

    @pytest.mark.unit
    def test_agreement_signal_detection_ro(self, feedback_module):
        """Test agreement signal detection in Romanian."""
        agreement_text = "Da, absolut! Sună perfect. Să mergem mai departe!"
        result = feedback_module.detect_verbal_signals(agreement_text)
        assert result is not None

    @pytest.mark.unit
    def test_doubt_signal_detection(self, feedback_module):
        """Test doubt signal detection."""
        doubt_text = "I'm not sure about this. I'm hesitant. Let me think."
        result = feedback_module.detect_verbal_signals(doubt_text)
        assert result is not None
        assert "doubt" in result or "signals" in result

    @pytest.mark.unit
    def test_objection_signal_detection(self, feedback_module):
        """Test objection signal detection."""
        objection_text = "But I don't agree with that. I have concerns. That's not right."
        result = feedback_module.detect_verbal_signals(objection_text)
        assert result is not None
        assert "objection" in result or "signals" in result

    @pytest.mark.unit
    def test_stalling_signal_detection(self, feedback_module):
        """Test stalling signal detection."""
        stalling_text = "Let me think about it. I need to consult with my team. Maybe later."
        result = feedback_module.detect_verbal_signals(stalling_text)
        assert result is not None
        assert "stalling" in result or "signals" in result

    @pytest.mark.unit
    def test_question_signal_detection(self, feedback_module):
        """Test question signal detection."""
        question_text = "How does this work? Can you explain? Tell me more?"
        result = feedback_module.detect_verbal_signals(question_text)
        assert result is not None

    @pytest.mark.unit
    def test_urgency_signal_detection(self, feedback_module):
        """Test urgency signal detection."""
        urgency_text = "We need to move fast! The deadline is approaching. We must decide now!"
        result = feedback_module.detect_verbal_signals(urgency_text)
        assert result is not None

    @pytest.mark.unit
    def test_budget_signal_detection(self, feedback_module):
        """Test budget signal detection."""
        budget_text = "What's the cost? Can you negotiate on price? How much will it be?"
        result = feedback_module.detect_verbal_signals(budget_text)
        assert result is not None

    @pytest.mark.unit
    def test_competitive_signal_detection(self, feedback_module):
        """Test competitive signal detection."""
        competitive_text = "We're looking at other vendors. Your competitor offered more."
        result = feedback_module.detect_verbal_signals(competitive_text)
        assert result is not None

    # ========================================================================
    # VOCAL SIGNALS TESTS
    # ========================================================================

    @pytest.mark.unit
    def test_high_energy_detection(self, feedback_module):
        """Test high energy vocal signal detection."""
        # High energy would have words like excited, enthusiastic
        high_energy_text = "I'm excited! Absolutely! This is amazing!"
        result = feedback_module.detect_vocal_signals(high_energy_text)
        assert result is not None

    @pytest.mark.unit
    def test_low_energy_detection(self, feedback_module):
        """Test low energy vocal signal detection."""
        low_energy_text = "I guess so. Maybe. I don't know. Whatever."
        result = feedback_module.detect_vocal_signals(low_energy_text)
        assert result is not None

    @pytest.mark.unit
    def test_hesitation_detection(self, feedback_module):
        """Test hesitation/pause detection."""
        hesitation_text = "Um... well... I think... maybe..."
        result = feedback_module.detect_vocal_signals(hesitation_text)
        assert result is not None

    @pytest.mark.unit
    def test_warm_tone_detection(self, feedback_module):
        """Test warm/friendly tone detection."""
        warm_text = "I really appreciate your help! You're wonderful. Thank you so much!"
        result = feedback_module.detect_vocal_signals(warm_text)
        assert result is not None

    @pytest.mark.unit
    def test_cold_tone_detection(self, feedback_module):
        """Test cold/dismissive tone detection."""
        cold_text = "That's fine. Whatever works. I don't really care."
        result = feedback_module.detect_vocal_signals(cold_text)
        assert result is not None

    # ========================================================================
    # CLOSE PROBABILITY SCORING TESTS
    # ========================================================================

    @pytest.mark.unit
    def test_close_probability_high_agreement(self, feedback_module):
        """Test close probability with high agreement signals."""
        your_text = "I believe we have an agreement. Shall we confirm?"
        their_text = "Yes! Let's do it. I'm in. This works perfectly!"
        result = feedback_module.analyze_real_time(your_text, their_text)

        assert result is not None
        assert "close_probability_score" in result
        assert result["close_probability_score"] > 7

    @pytest.mark.unit
    def test_close_probability_low_objection(self, feedback_module):
        """Test close probability with strong objections."""
        your_text = "This solution will solve your problem."
        their_text = "I don't think this will work. I have major concerns."
        result = feedback_module.analyze_real_time(your_text, their_text)

        assert result is not None
        assert "close_probability_score" in result
        assert result["close_probability_score"] < 4

    @pytest.mark.unit
    def test_close_probability_mixed_signals(self, feedback_module):
        """Test close probability with mixed signals."""
        your_text = "Let me clarify our value proposition."
        their_text = "That's interesting. I'm somewhat interested but hesitant."
        result = feedback_module.analyze_real_time(your_text, their_text)

        assert result is not None
        assert "close_probability_score" in result
        assert 3 <= result["close_probability_score"] <= 7

    @pytest.mark.unit
    def test_close_probability_scale_range(self, feedback_module):
        """Test that close probability stays within 0-10 scale."""
        test_cases = [
            ("Yes!", "Perfect!"),
            ("No.", "Terrible."),
            ("Maybe?", "I don't know."),
            ("Excellent!", "Wonderful!"),
            ("Awful!", "Horrible!"),
        ]

        for your_text, their_text in test_cases:
            result = feedback_module.analyze_real_time(your_text, their_text)
            assert 0 <= result["close_probability_score"] <= 10

    # ========================================================================
    # DUAL-SPEAKER ANALYSIS TESTS
    # ========================================================================

    @pytest.mark.unit
    def test_dual_speaker_engagement_analysis(self, feedback_module):
        """Test analyzing both speakers' engagement levels."""
        your_text = "I'm very excited about this partnership!"
        their_text = "I'm somewhat interested but not fully convinced."
        result = feedback_module.analyze_real_time(your_text, their_text)

        assert result is not None
        assert "your_verbals" in result
        assert "their_verbals" in result

    @pytest.mark.unit
    def test_dual_speaker_momentum_tracking(self, feedback_module):
        """Test momentum tracking across speakers."""
        your_text = "Great! I think we're making progress."
        their_text = "I see where you're going. This is helpful."
        result = feedback_module.analyze_real_time(your_text, their_text)

        assert result is not None
        # Both should show positive signals
        assert result["close_probability_score"] > 5

    # ========================================================================
    # INTERPRETATION TESTS
    # ========================================================================

    @pytest.mark.unit
    def test_interpretation_labels(self, feedback_module):
        """Test that interpretations are clear and actionable."""
        scenarios = [
            ("Perfect! Let's go!", "I agree completely!"),
            ("Let me pitch this.", "I don't think so."),
            ("Here's my offer.", "Interesting. Tell me more."),
        ]

        for your_text, their_text in scenarios:
            result = feedback_module.analyze_real_time(your_text, their_text)
            assert "interpretation" in result
            assert isinstance(result["interpretation"], str)
            assert len(result["interpretation"]) > 0

    # ========================================================================
    # REAL-TIME COACHING TESTS
    # ========================================================================

    @pytest.mark.unit
    def test_real_time_coaching_provided(self, feedback_module):
        """Test that real-time coaching is provided."""
        your_text = "Does this work for you?"
        their_text = "I'm not sure. Let me think about it."
        result = feedback_module.analyze_real_time(your_text, their_text)

        assert result is not None
        assert "coaching" in result
        assert isinstance(result["coaching"], str)

    @pytest.mark.unit
    def test_coaching_actionable(self, feedback_module):
        """Test that coaching is actionable."""
        your_text = "Here's our offer."
        their_text = "That's good, but I need to compare with others."
        result = feedback_module.analyze_real_time(your_text, their_text)

        coaching = result["coaching"]
        # Coaching should mention specific next steps
        assert len(coaching) > 10

    # ========================================================================
    # EDGE CASES AND ERROR HANDLING
    # ========================================================================

    @pytest.mark.edge_case
    def test_empty_text_feedback(self, feedback_module):
        """Test feedback extraction with empty text."""
        result = feedback_module.analyze_real_time("", "")
        assert result is not None

    @pytest.mark.edge_case
    def test_single_speaker_feedback(self, feedback_module):
        """Test feedback extraction with only one speaker."""
        result = feedback_module.analyze_real_time("Hello there", "")
        assert result is not None

    @pytest.mark.edge_case
    def test_very_long_text_feedback(self, feedback_module):
        """Test feedback extraction with very long text."""
        long_text = "word " * 500
        result = feedback_module.analyze_real_time(long_text, long_text)
        assert result is not None
        assert 0 <= result["close_probability_score"] <= 10

    @pytest.mark.edge_case
    def test_special_characters_feedback(self, feedback_module):
        """Test feedback extraction with special characters."""
        special_text = "I'm 100% YES!!! #AMAZING @mention $$$"
        result = feedback_module.analyze_real_time(special_text, "OK!")
        assert result is not None

    @pytest.mark.edge_case
    def test_repeated_words_feedback(self, feedback_module):
        """Test feedback extraction with repeated words."""
        repeated_text = "no no no no no I don't want this"
        result = feedback_module.analyze_real_time("yes yes yes", repeated_text)
        assert result is not None
        # Strong negative should show low close probability
        assert result["close_probability_score"] < 4

    # ========================================================================
    # BILINGUAL TESTS
    # ========================================================================

    @pytest.mark.bilingual
    def test_romanian_agreement_signals(self, feedback_module):
        """Test Romanian agreement signal detection."""
        ro_agreement = "Da! Absolut! E perfect! Să mergem mai departe!"
        result = feedback_module.detect_verbal_signals(ro_agreement)
        assert result is not None

    @pytest.mark.bilingual
    def test_romanian_objection_signals(self, feedback_module):
        """Test Romanian objection signal detection."""
        ro_objection = "Nu sunt de acord. Am îngrijorări. Asta nu e bună."
        result = feedback_module.detect_verbal_signals(ro_objection)
        assert result is not None

    @pytest.mark.bilingual
    def test_mixed_language_feedback(self, feedback_module):
        """Test feedback extraction with mixed languages."""
        mixed = "Yes, da! I agree, sunt de acord!"
        result = feedback_module.analyze_real_time(mixed, "OK, bine!")
        assert result is not None

    # ========================================================================
    # COMPREHENSIVE SCENARIOS
    # ========================================================================

    @pytest.mark.integration
    def test_scenario_ready_to_close(self, feedback_module):
        """Test complete ready-to-close scenario."""
        your_text = "I think we've covered everything. You've said yes to features, pricing, and timeline. Ready?"
        their_text = "Yes! I'm excited. I trust you. Let's do this!"

        result = feedback_module.analyze_real_time(your_text, their_text)

        assert result["close_probability_score"] > 8
        assert "agreement" in result["their_verbals"] or result["their_verbals"]["agreement"] > 0

    @pytest.mark.integration
    def test_scenario_early_stage(self, feedback_module):
        """Test complete early-stage discovery scenario."""
        your_text = "Let me ask you some questions to understand your needs better."
        their_text = "Sure, I'm open to learning more. What would you like to know?"

        result = feedback_module.analyze_real_time(your_text, their_text)

        assert 4 <= result["close_probability_score"] <= 7

    @pytest.mark.integration
    def test_scenario_objection_stage(self, feedback_module):
        """Test complete objection-handling scenario."""
        your_text = "I understand your concern about price. Let me address that."
        their_text = "I'm not comfortable with that cost. It's too expensive."

        result = feedback_module.analyze_real_time(your_text, their_text)

        assert 2 <= result["close_probability_score"] <= 5

    @pytest.mark.integration
    def test_scenario_budget_discussion(self, feedback_module):
        """Test budget negotiation scenario."""
        your_text = "Our pricing is $50K per year."
        their_text = "What's included? Can you negotiate? Can you offer payment terms?"

        result = feedback_module.analyze_real_time(your_text, their_text)

        # Budget questions show interest but not full commitment
        assert 4 <= result["close_probability_score"] <= 7
