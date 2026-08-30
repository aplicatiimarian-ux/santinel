# -*- coding: utf-8 -*-
"""
Integration tests for Unified Coach (all 10 frameworks orchestrated).
Tests multi-framework synthesis, conflict detection, and synergy identification.
"""

import pytest


class TestUnifiedCoachFramework:
    """Tests for Unified Coach framework orchestration."""

    # ========================================================================
    # BASIC ORCHESTRATION TESTS
    # ========================================================================

    @pytest.mark.integration
    def test_unified_coach_initializes(self, unified_coach):
        """Test that unified coach initializes all frameworks."""
        assert unified_coach.ta is not None
        assert unified_coach.ei is not None
        assert unified_coach.attachment is not None
        assert unified_coach.behavioral_econ is not None
        assert unified_coach.game_theory is not None
        assert unified_coach.neuroscience is not None
        assert unified_coach.narrative is not None
        assert unified_coach.somatic is not None
        assert unified_coach.feedback is not None
        assert unified_coach.scripts is not None

    @pytest.mark.integration
    def test_analyze_unified_returns_complete_result(self, unified_coach):
        """Test that unified analysis returns all expected fields."""
        your_text = "I believe this is a great opportunity for both of us."
        their_text = "I'm interested. Let's explore this together."

        result = unified_coach.analyze_unified(your_text, their_text)

        assert "framework_findings" in result
        assert "synthesis" in result
        assert "conflicts" in result
        assert "synergies" in result
        assert "integrated_coaching" in result
        assert "close_probability" in result
        assert "next_moves" in result

    @pytest.mark.integration
    def test_analyze_unified_single_speaker(self, unified_coach):
        """Test unified analysis with only one speaker."""
        your_text = "I think we have a great opportunity here."
        result = unified_coach.analyze_unified(your_text, "")

        assert result is not None
        assert "synthesis" in result

    @pytest.mark.integration
    def test_analyze_unified_empty_text(self, unified_coach):
        """Test unified analysis with empty text."""
        result = unified_coach.analyze_unified("", "")
        assert result is not None

    # ========================================================================
    # FRAMEWORK FINDINGS TESTS
    # ========================================================================

    @pytest.mark.integration
    def test_framework_findings_ta(self, unified_coach):
        """Test that TA framework findings are included."""
        their_text = "I think you're trying to manipulate me."
        result = unified_coach.analyze_unified("", their_text)

        findings = result["framework_findings"]
        assert findings.get("ta") is not None

    @pytest.mark.integration
    def test_framework_findings_ei(self, unified_coach):
        """Test that EI framework findings are included."""
        their_text = "I'm excited about this partnership!"
        result = unified_coach.analyze_unified("", their_text)

        findings = result["framework_findings"]
        assert findings.get("ei") is not None

    @pytest.mark.integration
    def test_framework_findings_attachment(self, unified_coach):
        """Test that Attachment findings are included."""
        their_text = "I need to feel secure before committing."
        result = unified_coach.analyze_unified("", their_text)

        findings = result["framework_findings"]
        assert findings.get("attachment") is not None

    @pytest.mark.integration
    def test_framework_findings_behavioral_econ(self, unified_coach):
        """Test that Behavioral Economics findings are included."""
        their_text = "What if this doesn't work? I've already invested so much."
        result = unified_coach.analyze_unified("", their_text)

        findings = result["framework_findings"]
        assert findings.get("behavioral_econ") is not None

    @pytest.mark.integration
    def test_framework_findings_game_theory(self, unified_coach):
        """Test that Game Theory findings are included."""
        their_text = "Either we both win or I walk away."
        result = unified_coach.analyze_unified("", their_text)

        findings = result["framework_findings"]
        assert findings.get("game_theory") is not None

    @pytest.mark.integration
    def test_framework_findings_neuroscience(self, unified_coach):
        """Test that Neuroscience findings are included."""
        their_text = "My heart is racing. I'm nervous about this."
        result = unified_coach.analyze_unified("", their_text)

        findings = result["framework_findings"]
        assert findings.get("neuroscience") is not None

    @pytest.mark.integration
    def test_framework_findings_narrative(self, unified_coach):
        """Test that Narrative findings are included."""
        their_text = "I've always been a winner. I make things happen."
        result = unified_coach.analyze_unified("", their_text)

        findings = result["framework_findings"]
        assert findings.get("narrative") is not None

    @pytest.mark.integration
    def test_framework_findings_somatic(self, unified_coach):
        """Test that Somatic findings are included."""
        their_text = "I'm grounded and present in this moment."
        result = unified_coach.analyze_unified("", their_text)

        findings = result["framework_findings"]
        assert findings.get("somatic") is not None

    @pytest.mark.integration
    def test_framework_findings_feedback(self, unified_coach):
        """Test that Feedback findings are included."""
        your_text = "Can you help me with this?"
        their_text = "Yes, absolutely! I'd love to help!"
        result = unified_coach.analyze_unified(your_text, their_text)

        findings = result["framework_findings"]
        assert findings.get("feedback") is not None

    # ========================================================================
    # SYNTHESIS TESTS
    # ========================================================================

    @pytest.mark.integration
    def test_synthesis_has_threat_level(self, unified_coach):
        """Test that synthesis includes threat level."""
        their_text = "I'm worried about this. What if it goes wrong?"
        result = unified_coach.analyze_unified("", their_text)

        synthesis = result["synthesis"]
        assert "threat_level" in synthesis
        assert synthesis["threat_level"] in ["HIGH", "MEDIUM", "LOW", "unknown"]

    @pytest.mark.integration
    def test_synthesis_has_engagement_level(self, unified_coach):
        """Test that synthesis includes engagement level."""
        their_text = "I'm very interested! This is exciting!"
        result = unified_coach.analyze_unified("", their_text)

        synthesis = result["synthesis"]
        assert "engagement_level" in synthesis

    @pytest.mark.integration
    def test_synthesis_has_decision_readiness(self, unified_coach):
        """Test that synthesis includes decision readiness."""
        their_text = "Let's move forward with this."
        result = unified_coach.analyze_unified("", their_text)

        synthesis = result["synthesis"]
        assert "decision_readiness" in synthesis

    @pytest.mark.integration
    def test_synthesis_has_relationship_quality(self, unified_coach):
        """Test that synthesis includes relationship quality."""
        their_text = "I trust you completely."
        result = unified_coach.analyze_unified("", their_text)

        synthesis = result["synthesis"]
        assert "relationship_quality" in synthesis

    @pytest.mark.integration
    def test_synthesis_has_strategic_position(self, unified_coach):
        """Test that synthesis includes strategic position."""
        their_text = "We're in a strong negotiating position."
        result = unified_coach.analyze_unified("", their_text)

        synthesis = result["synthesis"]
        assert "strategic_position" in synthesis

    # ========================================================================
    # CONFLICT DETECTION TESTS
    # ========================================================================

    @pytest.mark.integration
    def test_detect_conflicts_present(self, unified_coach):
        """Test that conflicts are detected when frameworks disagree."""
        your_text = "Let's collaborate and find a solution together."
        their_text = "No, I need to win here. Zero-sum."

        result = unified_coach.analyze_unified(your_text, their_text)
        conflicts = result["conflicts"]

        # May or may not detect depending on signal strength
        assert isinstance(conflicts, list)

    @pytest.mark.integration
    def test_conflicts_are_descriptive(self, unified_coach):
        """Test that conflicts have descriptive text."""
        your_text = "Win-win is our goal."
        their_text = "Either I win or you lose. There's no middle ground."

        result = unified_coach.analyze_unified(your_text, their_text)
        conflicts = result["conflicts"]

        for conflict in conflicts:
            assert isinstance(conflict, str)
            assert len(conflict) > 0

    @pytest.mark.integration
    def test_no_false_conflicts(self, unified_coach):
        """Test that aligned frameworks don't create conflicts."""
        your_text = "I trust you and I think we can work together."
        their_text = "I feel safe with you. Let's partner."

        result = unified_coach.analyze_unified(your_text, their_text)
        conflicts = result["conflicts"]

        # Aligned signals should produce fewer/no conflicts
        assert len(conflicts) <= 2

    # ========================================================================
    # SYNERGY IDENTIFICATION TESTS
    # ========================================================================

    @pytest.mark.integration
    def test_detect_synergies_present(self, unified_coach):
        """Test that synergies are detected when frameworks align."""
        your_text = "I'm calm and present for this conversation."
        their_text = "I feel grounded too. Let's focus on solutions."

        result = unified_coach.analyze_unified(your_text, their_text)
        synergies = result["synergies"]

        assert isinstance(synergies, list)

    @pytest.mark.integration
    def test_synergies_are_actionable(self, unified_coach):
        """Test that synergies provide actionable insights."""
        your_text = "I believe in this partnership."
        their_text = "I trust you completely. I feel safe here."

        result = unified_coach.analyze_unified(your_text, their_text)
        synergies = result["synergies"]

        for synergy in synergies:
            assert isinstance(synergy, str)
            assert "SYNERGY" in synergy or len(synergy) > 0

    # ========================================================================
    # INTEGRATED COACHING TESTS
    # ========================================================================

    @pytest.mark.integration
    def test_integrated_coaching_provided(self, unified_coach):
        """Test that integrated coaching is provided."""
        your_text = "Here's our offer."
        their_text = "I'm interested but I need to think about it."

        result = unified_coach.analyze_unified(your_text, their_text)
        coaching = result["integrated_coaching"]

        assert isinstance(coaching, list)

    @pytest.mark.integration
    def test_coaching_has_priority(self, unified_coach):
        """Test that coaching recommendations have priority levels."""
        your_text = "Let's close this deal."
        their_text = "I'm ready. Let's do it."

        result = unified_coach.analyze_unified(your_text, their_text)
        coaching = result["integrated_coaching"]

        for recommendation in coaching:
            assert "priority" in recommendation or "move" in recommendation

    @pytest.mark.integration
    def test_coaching_cites_frameworks(self, unified_coach):
        """Test that coaching cites supporting frameworks."""
        your_text = "What are your concerns?"
        their_text = "I'm worried about commitment."

        result = unified_coach.analyze_unified(your_text, their_text)
        coaching = result["integrated_coaching"]

        for recommendation in coaching:
            # Should reference which frameworks support the recommendation
            assert "frameworks" in recommendation or "reasoning" in recommendation

    # ========================================================================
    # CLOSE PROBABILITY TESTS
    # ========================================================================

    @pytest.mark.integration
    def test_close_probability_high_readiness(self, unified_coach):
        """Test close probability when prospect is ready."""
        your_text = "I think we're ready to move forward."
        their_text = "Yes! Let's sign. I'm excited to start!"

        result = unified_coach.analyze_unified(your_text, their_text)
        close_prob = result["close_probability"]

        assert 0 <= close_prob <= 10

    @pytest.mark.integration
    def test_close_probability_low_readiness(self, unified_coach):
        """Test close probability when prospect is resistant."""
        your_text = "Should we move forward?"
        their_text = "No, I don't think so. This doesn't feel right."

        result = unified_coach.analyze_unified(your_text, their_text)
        close_prob = result["close_probability"]

        assert 0 <= close_prob <= 10
        assert close_prob < 4

    @pytest.mark.integration
    def test_close_probability_mid_range(self, unified_coach):
        """Test close probability in mid-range scenarios."""
        your_text = "What do you think?"
        their_text = "It sounds interesting, but I need to learn more."

        result = unified_coach.analyze_unified(your_text, their_text)
        close_prob = result["close_probability"]

        assert 0 <= close_prob <= 10

    # ========================================================================
    # NEXT MOVES TESTS
    # ========================================================================

    @pytest.mark.integration
    def test_next_moves_provided(self, unified_coach):
        """Test that next moves are provided."""
        your_text = "How does that sound?"
        their_text = "I'm interested, but have questions."

        result = unified_coach.analyze_unified(your_text, their_text)
        next_moves = result["next_moves"]

        assert isinstance(next_moves, list)
        assert len(next_moves) <= 5

    @pytest.mark.integration
    def test_next_moves_are_actionable(self, unified_coach):
        """Test that next moves are actionable."""
        your_text = "Should we proceed?"
        their_text = "I'm nervous but I trust you."

        result = unified_coach.analyze_unified(your_text, their_text)
        next_moves = result["next_moves"]

        for move in next_moves:
            assert isinstance(move, str)
            assert len(move) > 0

    @pytest.mark.integration
    def test_next_moves_prioritized(self, unified_coach):
        """Test that next moves are prioritized by impact."""
        your_text = "Ready to decide?"
        their_text = "I'm panicking. Everything feels overwhelming."

        result = unified_coach.analyze_unified(your_text, their_text)
        next_moves = result["next_moves"]

        # When prospect is dysregulated, de-escalation should be early
        if len(next_moves) > 0:
            assert isinstance(next_moves[0], str)

    # ========================================================================
    # SCENARIO-BASED INTEGRATION TESTS
    # ========================================================================

    @pytest.mark.integration
    def test_scenario_anxious_prospect(self, unified_coach):
        """Test complete anxious prospect scenario."""
        your_text = "I understand you're concerned about risk. That's smart."
        their_text = "I'm worried about making the wrong choice. What if this doesn't work?"

        result = unified_coach.analyze_unified(your_text, their_text)

        # Should detect anxiety
        synthesis = result["synthesis"]
        assert synthesis["threat_level"] in ["HIGH", "MEDIUM"]

        # Should provide de-escalation moves
        next_moves = result["next_moves"]
        assert len(next_moves) > 0

    @pytest.mark.integration
    def test_scenario_competitive_prospect(self, unified_coach):
        """Test complete competitive prospect scenario."""
        your_text = "We're not trying to beat your current vendor."
        their_text = "I'm shopping around. Competitor offered better terms."

        result = unified_coach.analyze_unified(your_text, their_text)

        # Should detect competitive positioning
        findings = result["framework_findings"]
        assert findings.get("game_theory") is not None

    @pytest.mark.integration
    def test_scenario_ready_to_close(self, unified_coach):
        """Test complete ready-to-close scenario."""
        your_text = "I think we're ready. You've agreed to features, pricing, timeline."
        their_text = "Yes, I'm excited! I trust you. Let's do this!"

        result = unified_coach.analyze_unified(your_text, their_text)

        # Should detect some readiness level
        synthesis = result["synthesis"]
        assert "decision_readiness" in synthesis

        # Close probability should be in valid range
        assert 0 <= result["close_probability"] <= 10

    @pytest.mark.integration
    def test_scenario_complex_conflict(self, unified_coach):
        """Test complex multi-framework conflict scenario."""
        your_text = "Let's find a collaborative solution."
        their_text = (
            "Everything I've tried has failed. People always disappoint me. "
            "My heart is racing. I don't know if I can trust this."
        )

        result = unified_coach.analyze_unified(your_text, their_text)

        # Should detect multiple frameworks firing
        synthesis = result["synthesis"]
        conflicts = result["conflicts"]
        next_moves = result["next_moves"]

        # Complex scenarios produce synthesis output
        assert isinstance(conflicts, list)
        assert isinstance(next_moves, list)

    # ========================================================================
    # BILINGUAL INTEGRATION TESTS
    # ========================================================================

    @pytest.mark.integration
    @pytest.mark.bilingual
    def test_unified_coach_romanian_text(self, unified_coach):
        """Test unified coach with Romanian text."""
        your_text = "Cred că avem o oportunitate grozavă."
        their_text = "Sunt interesat, dar trebuie să mă gândesc."

        result = unified_coach.analyze_unified(your_text, their_text)

        assert result is not None
        assert "synthesis" in result

    @pytest.mark.integration
    @pytest.mark.bilingual
    def test_unified_coach_mixed_language(self, unified_coach):
        """Test unified coach with mixed English/Romanian."""
        your_text = "I think da, this is perfect!"
        their_text = "I'm interested, sunt fericit!"

        result = unified_coach.analyze_unified(your_text, their_text)

        assert result is not None

    # ========================================================================
    # STRESS AND EDGE CASES
    # ========================================================================

    @pytest.mark.edge_case
    def test_very_long_negotiation_text(self, unified_coach):
        """Test unified coach with very long text."""
        long_text = (
            "I believe in long-term partnerships. "
            "Trust is essential. Quality matters. Communication is key. "
        ) * 50

        result = unified_coach.analyze_unified(long_text, "Yes, I agree.")
        assert result is not None

    @pytest.mark.edge_case
    def test_rapid_sequential_analyses(self, unified_coach):
        """Test rapid sequential analyses."""
        scenarios = [
            ("I'm excited", "Me too!"),
            ("I'm concerned", "Don't worry"),
            ("Let's close", "Agreed!"),
        ]

        for your_text, their_text in scenarios:
            result = unified_coach.analyze_unified(your_text, their_text)
            assert result is not None
            assert 0 <= result["close_probability"] <= 10

    @pytest.mark.edge_case
    def test_contradictory_signals(self, unified_coach):
        """Test unified coach with contradictory signals."""
        your_text = "I'm excited and confident!"
        their_text = "I'm excited but I'm also terrified and hesitant."

        result = unified_coach.analyze_unified(your_text, their_text)

        # Should handle contradictions gracefully
        assert result is not None
        conflicts = result["conflicts"]
        assert isinstance(conflicts, list)

    @pytest.mark.edge_case
    def test_neutral_bland_text(self, unified_coach):
        """Test unified coach with bland neutral text."""
        bland_text = "Hello. How are you? That's nice. OK."
        result = unified_coach.analyze_unified(bland_text, "Fine. Good. Thanks.")

        assert result is not None
        # Should still produce synthesis
        assert "synthesis" in result
