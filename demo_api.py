#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SANTINEL API Gateway Demo
Comprehensive test calls for the advanced REST API and WebSocket server.

Demonstrates:
- /analyze endpoint (route through all 10 frameworks)
- /coach endpoint (unified coaching)
- /scripts endpoint (script matching for DISC personalities)
- /outcomes endpoint (effectiveness tracking)
- /stream-coaching WebSocket (real-time updates)

Bilingual support (EN + RO).
"""

import json
import asyncio
from datetime import datetime

# Import the API gateway
from core.api_gateway import (
    SantinelAPIGateway,
    AnalysisRequest,
    CoachingRequest,
    ScriptRequest,
    OutcomeRecord,
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title.upper()}")
    print(f"{'='*70}\n")


def demo_analysis_english():
    """Demo: /analyze endpoint in English."""
    print_section("DEMO 1: Analysis in English")

    gateway = SantinelAPIGateway()

    your_text = (
        "I believe we've built a strong relationship here. "
        "This partnership offers significant value for both of us. "
        "I'm confident we can succeed together."
    )

    their_text = (
        "I appreciate that, but I need to understand the pricing better. "
        "What's the breakdown of costs? Can you negotiate on the service level?"
    )

    req = AnalysisRequest(
        your_text=your_text,
        their_text=their_text,
        language="en",
    )

    print(f"YOUR TEXT: {your_text}\n")
    print(f"THEIR TEXT: {their_text}\n")

    response = gateway.analyze(req)

    print(f"REQUEST ID: {response.request_id}")
    print(f"TIMESTAMP: {response.timestamp}")
    print(f"\nFRAMEWORK SYNTHESIS:")
    for key, value in response.synthesis.items():
        print(f"  {key.upper()}: {value}")

    print(f"\nCONFLICTS: {len(response.conflicts)}")
    for conflict in response.conflicts:
        print(f"  - {conflict}")

    print(f"\nSYNERGIES: {len(response.synergies)}")
    for synergy in response.synergies:
        print(f"  - {synergy}")

    print(f"\nCLOSE PROBABILITY: {response.close_probability:.1f}/10")
    print(f"\nNEXT MOVES:")
    for i, move in enumerate(response.next_moves, 1):
        print(f"  {i}. {move}")


def demo_analysis_romanian():
    """Demo: /analyze endpoint in Romanian."""
    print_section("DEMO 2: Analysis in Romanian")

    gateway = SantinelAPIGateway()

    your_text = (
        "Cred că am construit o relație puternică. "
        "Acest parteneriat aduce valoare semnificativă pentru amândoi. "
        "Sunt încredințat că vom reuși împreună."
    )

    their_text = (
        "Apreciez asta, dar trebuie să înțeleg mai bine prețurile. "
        "Care e detalierea costurilor? Poți negocia pe nivelul de servicii?"
    )

    req = AnalysisRequest(
        your_text=your_text,
        their_text=their_text,
        language="ro",
    )

    print(f"YOUR TEXT: {your_text}\n")
    print(f"THEIR TEXT: {their_text}\n")

    response = gateway.analyze(req)

    print(f"CLOSE PROBABILITY: {response.close_probability:.1f}/10")
    print(f"NEXT MOVES: {response.next_moves}")


def demo_coaching_driver():
    """Demo: /coach endpoint for Driver personality."""
    print_section("DEMO 3: Coaching for Driver Personality")

    gateway = SantinelAPIGateway()

    your_text = "Let's focus on the bottom line. What's your decision?"

    their_text = (
        "I appreciate the directness. Here's what I need: "
        "faster implementation timeline, 15% discount, and dedicated support."
    )

    req = CoachingRequest(
        your_text=your_text,
        their_text=their_text,
        personality_type="driver",
        situation="negotiation",
        language="en",
    )

    print(f"PERSONALITY: Driver")
    print(f"SITUATION: Negotiation")
    print(f"THEIR TEXT: {their_text}\n")

    response = gateway.coach(req)

    print(f"COACHING SUMMARY:")
    print(response.coaching_summary)
    print(f"\nKEY MOVES:")
    for move in response.key_moves:
        print(f"  - {move}")
    print(f"\nNEXT BEST ACTION: {response.next_best_action}")
    print(f"CONFIDENCE: {response.confidence_score:.2f}")


def demo_coaching_amiable():
    """Demo: /coach endpoint for Amiable personality."""
    print_section("DEMO 4: Coaching for Amiable Personality")

    gateway = SantinelAPIGateway()

    your_text = "I want to make sure this works well for you."

    their_text = (
        "I do want to move forward, but I'm worried about the timeline. "
        "My team is already stretched thin. Can we phase this in?"
    )

    req = CoachingRequest(
        your_text=your_text,
        their_text=their_text,
        personality_type="amiable",
        situation="objection",
        language="en",
    )

    print(f"PERSONALITY: Amiable")
    print(f"SITUATION: Objection handling")
    print(f"THEIR TEXT: {their_text}\n")

    response = gateway.coach(req)

    print(f"COACHING SUMMARY:")
    print(response.coaching_summary)
    print(f"\nKEY MOVES:")
    for move in response.key_moves:
        print(f"  - {move}")


def demo_script_matching():
    """Demo: /scripts endpoint for various situations + personalities."""
    print_section("DEMO 5: Script Matching (DISC + Situation)")

    gateway = SantinelAPIGateway()

    scenarios = [
        ("cold_call", "driver"),
        ("discovery", "amiable"),
        ("objection", "analytical"),
        ("closing", "expressive"),
    ]

    for situation, personality in scenarios:
        print(f"\n--- {situation.upper()} + {personality.upper()} ---")

        req = ScriptRequest(
            situation=situation,
            personality_type=personality,
            language="en",
        )

        response = gateway.match_script(req)

        print(f"SCRIPT: {response.script}")
        print(f"FOLLOW-UP TACTICS:")
        for tactic in response.follow_up_tactics:
            print(f"  - {tactic}")


def demo_script_matching_romanian():
    """Demo: /scripts endpoint in Romanian."""
    print_section("DEMO 6: Script Matching in Romanian")

    gateway = SantinelAPIGateway()

    print("\n--- CLOSING + EXPRESSIVE (ROMANIAN) ---")

    req = ScriptRequest(
        situation="closing",
        personality_type="expressive",
        language="ro",
    )

    response = gateway.match_script(req)

    print(f"SCRIPT: {response.script}")
    print(f"CONFIDENCE: {response.confidence_score:.2f}")


def demo_outcomes_tracking():
    """Demo: /outcomes endpoint for tracking script effectiveness."""
    print_section("DEMO 7: Outcomes Tracking & Analytics")

    gateway = SantinelAPIGateway()

    outcomes = [
        OutcomeRecord(
            deal_id="DEAL-2024-001",
            lead_id="LEAD-ION-001",
            situation="closing",
            personality_type="driver",
            script_used="Let's finalize this deal now",
            result="won",
            coaching_effectiveness=0.94,
            duration_seconds=900,
            notes="Quick decision; responded well to direct approach",
        ),
        OutcomeRecord(
            deal_id="DEAL-2024-002",
            lead_id="LEAD-MARIA-001",
            situation="objection",
            personality_type="amiable",
            script_used="I understand your concerns. Let's find a solution together.",
            result="advanced",
            coaching_effectiveness=0.87,
            duration_seconds=1200,
            notes="Built rapport; needs more time to decide",
        ),
        OutcomeRecord(
            deal_id="DEAL-2024-003",
            lead_id="LEAD-ALEX-001",
            situation="discovery",
            personality_type="analytical",
            script_used="Here are the metrics that demonstrate ROI",
            result="stalled",
            coaching_effectiveness=0.65,
            duration_seconds=1800,
            notes="Needs more data; asked for deep-dive analysis",
        ),
        OutcomeRecord(
            deal_id="DEAL-2024-004",
            lead_id="LEAD-CRISTINA-001",
            situation="cold_call",
            personality_type="expressive",
            script_used="This is going to be amazing! Let me show you why...",
            result="won",
            coaching_effectiveness=0.89,
            duration_seconds=600,
            notes="Excited response; energy matched",
        ),
    ]

    print("RECORDING OUTCOMES BY PERSONALITY & EFFECTIVENESS:\n")

    effectiveness_by_type = {}

    for outcome in outcomes:
        result = gateway.record_outcome(outcome)

        print(f"DEAL: {outcome.deal_id}")
        print(f"  Personality: {outcome.personality_type}")
        print(f"  Situation: {outcome.situation}")
        print(f"  Result: {outcome.result.upper()}")
        print(f"  Effectiveness: {outcome.coaching_effectiveness:.2f}")
        print(f"  Duration: {outcome.duration_seconds}s")
        print(f"  Notes: {outcome.notes}\n")

        # Aggregate stats
        if outcome.personality_type not in effectiveness_by_type:
            effectiveness_by_type[outcome.personality_type] = []
        effectiveness_by_type[outcome.personality_type].append(outcome.coaching_effectiveness)

    print("\n--- EFFECTIVENESS BY PERSONALITY ---")
    for ptype, scores in effectiveness_by_type.items():
        avg = sum(scores) / len(scores)
        print(f"{ptype.upper()}: {avg:.2f} average effectiveness")


async def demo_streaming_coaching():
    """Demo: WebSocket /stream-coaching endpoint."""
    print_section("DEMO 8: Real-Time Coaching Stream (WebSocket)")

    gateway = SantinelAPIGateway()

    connection_id = "ws-conn-001"

    your_text = "I think we're close to agreement here."
    their_text = "I'm interested, but I need approval from my CFO first."

    print(f"STARTING COACHING STREAM: {connection_id}")
    print(f"YOUR TEXT: {your_text}")
    print(f"THEIR TEXT: {their_text}\n")

    # Start the stream
    gateway.stream_manager.start_stream(connection_id, your_text, their_text)

    # In production, this would be an actual WebSocket connection
    # For demo, simulate a few updates
    print("SIMULATING STREAM UPDATES (30-second intervals):\n")

    for i in range(3):
        coaching_req = CoachingRequest(
            your_text=your_text,
            their_text=their_text,
            language="en",
        )
        coaching = gateway.coach(coaching_req)

        print(f"[UPDATE {i+1} at {datetime.now().strftime('%H:%M:%S')}]")
        print(f"  Summary: {coaching.coaching_summary.split(chr(10))[0]}")
        print(f"  Confidence: {coaching.confidence_score:.2f}")
        print(f"  Next Action: {coaching.next_best_action}\n")

        if i < 2:
            await asyncio.sleep(1)  # Simulate 30-second interval

    gateway.stream_manager.stop_stream(connection_id)
    print(f"STREAM STOPPED: {connection_id}")


def demo_health_check():
    """Demo: GET /health endpoint."""
    print_section("DEMO 9: Health Check")

    gateway = SantinelAPIGateway()

    health = gateway.health_check()

    print(f"STATUS: {health['status'].upper()}")
    print(f"VERSION: {health['version']}")
    print(f"FRAMEWORKS: {health['frameworks']}")
    print(f"TIMESTAMP: {health['timestamp']}")


def demo_bilingual_coaching_flow():
    """Demo: Complete coaching flow in both languages."""
    print_section("DEMO 10: Bilingual Coaching Flow (EN + RO)")

    gateway = SantinelAPIGateway()

    # English scenario
    print("--- ENGLISH SCENARIO ---\n")
    en_your = "Our solution is built for companies like yours."
    en_their = "What kind of support do you provide during implementation?"

    en_req = CoachingRequest(
        your_text=en_your,
        their_text=en_their,
        language="en",
    )

    en_coaching = gateway.coach(en_req)
    print(f"YOUR: {en_your}")
    print(f"THEIR: {en_their}")
    print(f"RECOMMENDATION: {en_coaching.next_best_action}\n")

    # Romanian scenario
    print("--- ROMANIAN SCENARIO ---\n")
    ro_your = "Soluția noastră este construită pentru companii ca a ta."
    ro_their = "Ce fel de suport oferiți în timpul implementării?"

    ro_req = CoachingRequest(
        your_text=ro_your,
        their_text=ro_their,
        language="ro",
    )

    ro_coaching = gateway.coach(ro_req)
    print(f"YOUR: {ro_your}")
    print(f"THEIR: {ro_their}")
    print(f"RECOMMENDATION: {ro_coaching.next_best_action}\n")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("  SANTINEL API GATEWAY DEMO")
    print("  Advanced REST API + WebSocket Coaching Platform")
    print("="*70)

    # Run synchronous demos
    demo_analysis_english()
    demo_analysis_romanian()
    demo_coaching_driver()
    demo_coaching_amiable()
    demo_script_matching()
    demo_script_matching_romanian()
    demo_outcomes_tracking()
    demo_health_check()
    demo_bilingual_coaching_flow()

    # Run async demo
    print("\nStarting async streaming demo...\n")
    asyncio.run(demo_streaming_coaching())

    print_section("All Demos Complete")
    print("API Gateway is ready for production deployment.")
    print("\nEndpoints Summary:")
    print("  POST   /analyze          - Route through all 10 frameworks")
    print("  POST   /coach            - Synthesize unified coaching")
    print("  POST   /scripts          - Match scripts by personality + situation")
    print("  POST   /outcomes         - Record and track outcomes")
    print("  WS     /stream-coaching  - Real-time coaching updates (30sec)")
    print("  GET    /health           - Health check")
    print("\nLanguages Supported: EN, RO (bilingual)")
    print("Personalities Supported: DRIVER, EXPRESSIVE, AMIABLE, ANALYTICAL")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
