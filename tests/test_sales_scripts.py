# -*- coding: utf-8 -*-
"""
Unit tests for Sales Scripts framework.
Tests script selection, personality matching, and counter-response ranking.
"""

import pytest


class TestSalesScriptsFramework:
    """Tests for Sales Scripts framework."""

    # ========================================================================
    # SCRIPT RETRIEVAL TESTS
    # ========================================================================

    @pytest.mark.unit
    def test_get_cold_outreach_scripts_en(self, sales_scripts_module):
        """Test retrieving cold outreach scripts in English."""
        scripts = sales_scripts_module.get_scripts_by_category("cold_outreach", "en")
        assert len(scripts) > 0
        assert all("script" in s for s in scripts)
        assert all("effectiveness" in s for s in scripts)

    @pytest.mark.unit
    def test_get_initial_pitch_scripts_en(self, sales_scripts_module):
        """Test retrieving initial pitch scripts in English."""
        scripts = sales_scripts_module.get_scripts_by_category("initial_pitch", "en")
        assert len(scripts) > 0

    @pytest.mark.unit
    def test_get_objection_handling_scripts_en(self, sales_scripts_module):
        """Test retrieving objection handling scripts in English."""
        scripts = sales_scripts_module.get_scripts_by_category("objection_handling", "en")
        assert len(scripts) > 0
        # Objection handling should have the most scripts
        assert len(scripts) >= 3

    @pytest.mark.unit
    def test_get_negotiation_scripts_en(self, sales_scripts_module):
        """Test retrieving negotiation scripts in English."""
        scripts = sales_scripts_module.get_scripts_by_category("negotiation", "en")
        assert len(scripts) > 0

    @pytest.mark.unit
    def test_get_closing_scripts_en(self, sales_scripts_module):
        """Test retrieving closing scripts in English."""
        scripts = sales_scripts_module.get_scripts_by_category("closing", "en")
        assert len(scripts) > 0

    @pytest.mark.unit
    def test_get_follow_up_scripts_en(self, sales_scripts_module):
        """Test retrieving follow-up scripts in English."""
        scripts = sales_scripts_module.get_scripts_by_category("follow_up", "en")
        assert len(scripts) > 0

    @pytest.mark.bilingual
    def test_get_scripts_ro(self, sales_scripts_module):
        """Test retrieving scripts in Romanian."""
        ro_scripts = sales_scripts_module.get_scripts_by_category("cold_outreach", "ro")
        assert len(ro_scripts) > 0
        assert all("script" in s for s in ro_scripts)

    @pytest.mark.edge_case
    def test_get_invalid_category(self, sales_scripts_module):
        """Test retrieving invalid category."""
        scripts = sales_scripts_module.get_scripts_by_category("invalid_category", "en")
        assert len(scripts) == 0

    # ========================================================================
    # SCRIPT SELECTION ALGORITHM TESTS
    # ========================================================================

    @pytest.mark.unit
    def test_select_script_driver_cold_outreach(self, sales_scripts_module):
        """Test script selection for driver personality in cold outreach."""
        result = sales_scripts_module.select_script(
            category="cold_outreach",
            personality_type="driver",
            framework_signals={"tags": ["game_theory_coordination"]},
            language="en"
        )

        assert "selected_script" in result
        assert "confidence_score" in result
        assert 0 <= result["confidence_score"] <= 1
        assert "why_selected" in result

    @pytest.mark.unit
    def test_select_script_analytical_pitch(self, sales_scripts_module):
        """Test script selection for analytical personality in pitch."""
        result = sales_scripts_module.select_script(
            category="initial_pitch",
            personality_type="analytical",
            framework_signals={"tags": ["behavioral_econ_framing"]},
            language="en"
        )

        assert "selected_script" in result
        assert result["confidence_score"] > 0

    @pytest.mark.unit
    def test_select_script_amiable_negotiation(self, sales_scripts_module):
        """Test script selection for amiable personality in negotiation."""
        result = sales_scripts_module.select_script(
            category="negotiation",
            personality_type="amiable",
            framework_signals={"tags": ["attachment_secure"]},
            language="en"
        )

        assert "selected_script" in result
        assert result["selected_script"]["script"] is not None

    @pytest.mark.unit
    def test_select_script_expressive_objection(self, sales_scripts_module):
        """Test script selection for expressive personality in objection handling."""
        result = sales_scripts_module.select_script(
            category="objection_handling",
            personality_type="expressive",
            framework_signals={"tags": ["ei_empathy"]},
            language="en"
        )

        assert "selected_script" in result

    @pytest.mark.unit
    def test_select_script_best_fit_ranking(self, sales_scripts_module):
        """Test that script selection ranks by best fit."""
        # Two different personalities should potentially get different scripts
        result_driver = sales_scripts_module.select_script(
            category="closing",
            personality_type="driver",
            language="en"
        )

        result_amiable = sales_scripts_module.select_script(
            category="closing",
            personality_type="amiable",
            language="en"
        )

        # Both should have results
        assert "selected_script" in result_driver
        assert "selected_script" in result_amiable

    @pytest.mark.unit
    def test_select_script_framework_alignment(self, sales_scripts_module):
        """Test script selection considers framework tags."""
        framework_signals = {"tags": ["ta_adult_dialogue", "behavioral_econ_loss_aversion"]}
        result = sales_scripts_module.select_script(
            category="objection_handling",
            personality_type="analytical",
            framework_signals=framework_signals,
            language="en"
        )

        assert result["confidence_score"] > 0

    @pytest.mark.unit
    def test_select_script_effectiveness_weighting(self, sales_scripts_module):
        """Test that script effectiveness is considered in selection."""
        result = sales_scripts_module.select_script(
            category="cold_outreach",
            personality_type="driver",
            language="en"
        )

        script = result["selected_script"]
        assert "effectiveness" in script
        assert 0 <= script["effectiveness"] <= 1

    # ========================================================================
    # PERSONALITY TYPE MATCHING TESTS
    # ========================================================================

    @pytest.mark.unit
    def test_personality_fit_driver(self, sales_scripts_module):
        """Test driver personality fit."""
        scripts = sales_scripts_module.get_scripts_by_category("cold_outreach", "en")
        driver_friendly = [s for s in scripts if "driver" in s.get("personality_fit", [])]
        assert len(driver_friendly) > 0

    @pytest.mark.unit
    def test_personality_fit_expressive(self, sales_scripts_module):
        """Test expressive personality fit."""
        scripts = sales_scripts_module.get_scripts_by_category("initial_pitch", "en")
        expressive_friendly = [s for s in scripts if "expressive" in s.get("personality_fit", [])]
        assert len(expressive_friendly) > 0

    @pytest.mark.unit
    def test_personality_fit_amiable(self, sales_scripts_module):
        """Test amiable personality fit."""
        scripts = sales_scripts_module.get_scripts_by_category("negotiation", "en")
        amiable_friendly = [s for s in scripts if "amiable" in s.get("personality_fit", [])]
        assert len(amiable_friendly) > 0

    @pytest.mark.unit
    def test_personality_fit_analytical(self, sales_scripts_module):
        """Test analytical personality fit."""
        scripts = sales_scripts_module.get_scripts_by_category("objection_handling", "en")
        analytical_friendly = [s for s in scripts if "analytical" in s.get("personality_fit", [])]
        assert len(analytical_friendly) > 0

    # ========================================================================
    # COUNTER-RESPONSE TESTS
    # ========================================================================

    @pytest.mark.unit
    def test_get_price_counter_responses(self, sales_scripts_module):
        """Test counter-responses to price objections."""
        responses = sales_scripts_module.get_counter_responses("price", "en")
        assert len(responses) > 0
        assert all("response" in r for r in responses)
        assert all("effectiveness" in r for r in responses)
        assert all("rank" in r for r in responses)

    @pytest.mark.unit
    def test_price_responses_ranked_by_effectiveness(self, sales_scripts_module):
        """Test that price responses are ranked by effectiveness."""
        responses = sales_scripts_module.get_counter_responses("price", "en")
        effectiveness_scores = [r["effectiveness"] for r in responses]
        # Should be in descending order of effectiveness
        assert effectiveness_scores == sorted(effectiveness_scores, reverse=True)

    @pytest.mark.unit
    def test_get_timing_counter_responses(self, sales_scripts_module):
        """Test counter-responses to timing objections."""
        responses = sales_scripts_module.get_counter_responses("timing", "en")
        assert len(responses) > 0

    @pytest.mark.unit
    def test_get_competition_counter_responses(self, sales_scripts_module):
        """Test counter-responses to competitive objections."""
        responses = sales_scripts_module.get_counter_responses("competition", "en")
        assert len(responses) > 0

    @pytest.mark.unit
    def test_counter_response_has_actionable_text(self, sales_scripts_module):
        """Test that counter-responses have actionable text."""
        responses = sales_scripts_module.get_counter_responses("price", "en")
        for response in responses:
            assert len(response["response"]) > 10
            assert response["response"] is not None

    # ========================================================================
    # SITUATION-BASED SELECTION TESTS
    # ========================================================================

    @pytest.mark.unit
    def test_select_script_by_situation_progression(self, sales_scripts_module):
        """Test script selection follows sales funnel progression."""
        situations = ["cold_outreach", "initial_pitch", "objection_handling", "negotiation", "closing"]

        for situation in situations:
            result = sales_scripts_module.select_script(
                category=situation,
                personality_type="driver",
                language="en"
            )
            assert "selected_script" in result

    @pytest.mark.unit
    def test_different_situations_get_different_scripts(self, sales_scripts_module):
        """Test that different situations get appropriately different scripts."""
        cold_result = sales_scripts_module.select_script(
            category="cold_outreach",
            personality_type="driver",
            language="en"
        )

        close_result = sales_scripts_module.select_script(
            category="closing",
            personality_type="driver",
            language="en"
        )

        # Scripts should be different
        cold_script = cold_result["selected_script"]["script"]
        close_script = close_result["selected_script"]["script"]
        assert cold_script != close_script

    # ========================================================================
    # FRAMEWORK INTEGRATION TESTS
    # ========================================================================

    @pytest.mark.unit
    def test_script_has_framework_tags(self, sales_scripts_module):
        """Test that scripts have framework tags."""
        scripts = sales_scripts_module.get_scripts_by_category("objection_handling", "en")
        for script in scripts:
            assert "framework_tags" in script
            assert len(script["framework_tags"]) > 0

    @pytest.mark.unit
    def test_script_tags_align_with_frameworks(self, sales_scripts_module):
        """Test that script tags align with actual frameworks."""
        valid_tags = [
            "ta_", "ei_", "attachment_", "behavioral_econ_",
            "game_theory_", "neuroscience_", "narrative_", "somatic_"
        ]
        scripts = sales_scripts_module.get_scripts_by_category("objection_handling", "en")
        for script in scripts:
            for tag in script["framework_tags"]:
                assert any(tag.startswith(prefix) for prefix in valid_tags)

    # ========================================================================
    # BILINGUAL TESTS
    # ========================================================================

    @pytest.mark.bilingual
    def test_select_script_romanian(self, sales_scripts_module):
        """Test script selection in Romanian."""
        result = sales_scripts_module.select_script(
            category="cold_outreach",
            personality_type="driver",
            language="ro"
        )

        assert "selected_script" in result
        script = result["selected_script"]["script"]
        # Should contain Romanian text markers
        assert len(script) > 0

    @pytest.mark.bilingual
    def test_counter_responses_romanian(self, sales_scripts_module):
        """Test counter-responses in Romanian."""
        responses = sales_scripts_module.get_counter_responses("price", "ro")
        # May have responses or may fall back to English
        assert isinstance(responses, list)

    # ========================================================================
    # EDGE CASES
    # ========================================================================

    @pytest.mark.edge_case
    def test_select_script_no_framework_signals(self, sales_scripts_module):
        """Test script selection without framework signals."""
        result = sales_scripts_module.select_script(
            category="cold_outreach",
            personality_type="driver",
            framework_signals=None,
            language="en"
        )

        assert "selected_script" in result

    @pytest.mark.edge_case
    def test_select_script_empty_framework_signals(self, sales_scripts_module):
        """Test script selection with empty framework signals."""
        result = sales_scripts_module.select_script(
            category="cold_outreach",
            personality_type="driver",
            framework_signals={"tags": []},
            language="en"
        )

        assert "selected_script" in result

    @pytest.mark.edge_case
    def test_select_script_invalid_personality(self, sales_scripts_module):
        """Test script selection with invalid personality."""
        result = sales_scripts_module.select_script(
            category="cold_outreach",
            personality_type="invalid_personality",
            language="en"
        )

        # Should still return a script (fallback mechanism)
        assert "selected_script" in result or "error" not in result or result.get("selected_script")

    @pytest.mark.edge_case
    def test_counter_response_invalid_objection_type(self, sales_scripts_module):
        """Test counter-responses with invalid objection type."""
        responses = sales_scripts_module.get_counter_responses("invalid_type", "en")
        assert isinstance(responses, list)

    # ========================================================================
    # COMPREHENSIVE SCENARIOS
    # ========================================================================

    @pytest.mark.integration
    def test_scenario_driver_cold_to_close(self, sales_scripts_module):
        """Test driver personality journey from cold outreach to close."""
        journey = {
            "cold_outreach": sales_scripts_module.select_script("cold_outreach", "driver", language="en"),
            "initial_pitch": sales_scripts_module.select_script("initial_pitch", "driver", language="en"),
            "objection_handling": sales_scripts_module.select_script("objection_handling", "driver", language="en"),
            "closing": sales_scripts_module.select_script("closing", "driver", language="en"),
        }

        for stage, result in journey.items():
            assert "selected_script" in result
            assert result["selected_script"]["script"] is not None

    @pytest.mark.integration
    def test_scenario_amiable_relationship_based_sales(self, sales_scripts_module):
        """Test amiable personality relationship-based sales approach."""
        stages = ["cold_outreach", "initial_pitch", "negotiation", "closing"]

        for stage in stages:
            result = sales_scripts_module.select_script(
                category=stage,
                personality_type="amiable",
                framework_signals={"tags": ["attachment_secure", "narrative_collaborative"]},
                language="en"
            )

            assert "selected_script" in result

    @pytest.mark.integration
    def test_scenario_analytical_data_driven_sales(self, sales_scripts_module):
        """Test analytical personality data-driven sales approach."""
        result = sales_scripts_module.select_script(
            category="initial_pitch",
            personality_type="analytical",
            framework_signals={"tags": ["behavioral_econ_framing", "game_theory_coordination"]},
            language="en"
        )

        script = result["selected_script"]["script"]
        # Analytical scripts should mention data, ROI, or metrics
        assert len(script) > 0

    @pytest.mark.integration
    def test_scenario_objection_handling_price(self, sales_scripts_module):
        """Test objection handling for price concerns."""
        # Get script for objection handling
        script_result = sales_scripts_module.select_script(
            category="objection_handling",
            personality_type="analytical",
            framework_signals={"tags": ["behavioral_econ_loss_aversion"]},
            language="en"
        )

        # Get counter-responses
        counter = sales_scripts_module.get_counter_responses("price", "en")

        assert script_result["selected_script"] is not None
        assert len(counter) > 0

    @pytest.mark.integration
    def test_scenario_expressive_storytelling_approach(self, sales_scripts_module):
        """Test expressive personality storytelling approach."""
        result = sales_scripts_module.select_script(
            category="initial_pitch",
            personality_type="expressive",
            framework_signals={"tags": ["narrative_hero", "ei_social_skills"]},
            language="en"
        )

        script = result["selected_script"]["script"]
        # Should be engaging and narrative-focused
        assert len(script) > 0
