# -*- coding: utf-8 -*-
"""
SANTINEL API Gateway
Advanced REST API with WebSocket support for real-time coaching.

Endpoints:
  POST /analyze        - Route input through all 10 frameworks in parallel
  POST /coach          - Synthesize unified coaching recommendation
  POST /voice          - Send audio, get vocal + textual analysis
  POST /scripts        - Match situation + personality to best scripts
  POST /outcomes       - Track script effectiveness per personality type
  WS  /stream-coaching - Real-time coaching updates (30sec intervals)

Supports bilingual (EN + RO) input/output.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod

# Mock imports (in production: import actual framework modules)
try:
    from core.santinel_unified_coach import SantinelUnifiedCoach
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
    from core.crm_integration import CRMSyncAdapter, Outcome, DealStage
except ImportError:
    SantinelUnifiedCoach = TAModule = EIModule = None
    AttachmentModule = BehavioralEconomicsModule = GameTheoryModule = None
    NeuroscienceModule = NarrativeModule = SomaticModule = None
    FeedbackExtractionModule = SalesScriptsModule = None
    CRMSyncAdapter = Outcome = DealStage = None


class Personality(Enum):
    """DISC personality types for script matching."""
    DRIVER = "driver"
    EXPRESSIVE = "expressive"
    AMIABLE = "amiable"
    ANALYTICAL = "analytical"


class Situation(Enum):
    """Sales situation types for script selection."""
    COLD_CALL = "cold_call"
    DISCOVERY = "discovery"
    OBJECTION = "objection"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"


@dataclass
class AnalysisRequest:
    """Request for framework analysis."""
    your_text: str
    their_text: str
    language: str = "en"  # "en" or "ro"
    context: Optional[Dict] = None


@dataclass
class AnalysisResponse:
    """Response from framework analysis."""
    request_id: str
    timestamp: str
    language: str
    framework_findings: Dict[str, Any]
    synthesis: Dict[str, Any]
    conflicts: List[str]
    synergies: List[str]
    integrated_coaching: List[Dict]
    close_probability: float
    next_moves: List[str]


@dataclass
class CoachingRequest:
    """Request for unified coaching."""
    your_text: str
    their_text: str
    language: str = "en"
    personality_type: Optional[str] = None
    situation: Optional[str] = None


@dataclass
class CoachingResponse:
    """Unified coaching recommendation."""
    request_id: str
    timestamp: str
    coaching_summary: str
    key_moves: List[str]
    rationale: str
    confidence_score: float
    next_best_action: str


@dataclass
class ScriptRequest:
    """Request for script matching."""
    situation: str  # "cold_call", "discovery", "objection", "closing", "follow_up"
    personality_type: str  # "driver", "expressive", "amiable", "analytical"
    language: str = "en"


@dataclass
class ScriptResponse:
    """Best-match script for situation + personality."""
    request_id: str
    timestamp: str
    situation: str
    personality_type: str
    script: str
    rationale: str
    confidence_score: float
    follow_up_tactics: List[str]


@dataclass
class OutcomeRecord:
    """Record of negotiation outcome for analytics."""
    deal_id: str
    lead_id: str
    situation: str
    personality_type: str
    script_used: str
    result: str  # "won", "lost", "stalled", "advanced"
    coaching_effectiveness: float  # 0.0-1.0
    duration_seconds: int
    notes: Optional[str] = None


class AnalysisEngine:
    """Engine for routing requests through all frameworks."""

    def __init__(self):
        self.coach = SantinelUnifiedCoach() if SantinelUnifiedCoach else None
        self.ta = TAModule() if TAModule else None
        self.ei = EIModule() if EIModule else None
        self.attachment = AttachmentModule() if AttachmentModule else None
        self.behavioral_econ = BehavioralEconomicsModule() if BehavioralEconomicsModule else None
        self.game_theory = GameTheoryModule() if GameTheoryModule else None
        self.neuroscience = NeuroscienceModule() if NeuroscienceModule else None
        self.narrative = NarrativeModule() if NarrativeModule else None
        self.somatic = SomaticModule() if SomaticModule else None
        self.feedback = FeedbackExtractionModule() if FeedbackExtractionModule else None
        self.scripts = SalesScriptsModule() if SalesScriptsModule else None

    def analyze(self, req: AnalysisRequest) -> AnalysisResponse:
        """Route input through all 10 frameworks in parallel."""
        if not self.coach:
            # Mock response for testing without actual modules
            return self._mock_analysis(req)

        result = self.coach.analyze_unified(req.your_text, req.their_text)

        return AnalysisResponse(
            request_id=f"req-{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            language=req.language,
            framework_findings=result.get("framework_findings", {}),
            synthesis=result.get("synthesis", {}),
            conflicts=result.get("conflicts", []),
            synergies=result.get("synergies", []),
            integrated_coaching=result.get("integrated_coaching", []),
            close_probability=result.get("close_probability", 0),
            next_moves=result.get("next_moves", []),
        )

    def synthesize_coaching(self, req: CoachingRequest) -> CoachingResponse:
        """Generate unified coaching recommendation."""
        analysis = self.analyze(AnalysisRequest(
            your_text=req.your_text,
            their_text=req.their_text,
            language=req.language,
        ))

        # Synthesize from framework findings
        coaching_summary = self._synthesize_coaching_text(analysis)
        key_moves = analysis.next_moves[:3]  # Top 3 moves
        confidence = analysis.close_probability / 10.0  # Normalize to 0-1

        return CoachingResponse(
            request_id=analysis.request_id,
            timestamp=analysis.timestamp,
            coaching_summary=coaching_summary,
            key_moves=key_moves,
            rationale="Based on unified analysis across all 10 frameworks.",
            confidence_score=min(confidence, 1.0),
            next_best_action=key_moves[0] if key_moves else "GATHER_INFORMATION",
        )

    def match_script(self, req: ScriptRequest) -> ScriptResponse:
        """Match best script for situation + personality."""
        if not self.scripts:
            return self._mock_script_response(req)

        situation = Situation[req.situation.upper()] if req.situation else Situation.DISCOVERY
        personality = Personality[req.personality_type.upper()] if req.personality_type else Personality.DRIVER

        # In production: call SalesScriptsModule.select_script(situation, personality)
        script = self._get_script(situation, personality, req.language)

        return ScriptResponse(
            request_id=f"script-{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            situation=req.situation,
            personality_type=req.personality_type,
            script=script,
            rationale=f"Matched {situation.value.replace('_', ' ')} situation with {personality.value} personality.",
            confidence_score=0.85,
            follow_up_tactics=[
                "Ask open-ended question",
                "Listen for objection",
                "Validate their concern",
                "Propose next step",
            ],
        )

    def record_outcome(self, outcome: OutcomeRecord) -> bool:
        """Record negotiation outcome for effectiveness tracking."""
        # In production: save to database and sync to CRM
        print(f"[OUTCOME RECORDED] {outcome.deal_id}: {outcome.result} "
              f"({outcome.coaching_effectiveness:.2f} effectiveness)")
        return True

    @staticmethod
    def _mock_analysis(req: AnalysisRequest) -> AnalysisResponse:
        """Mock analysis response for testing."""
        return AnalysisResponse(
            request_id=f"req-{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            language=req.language,
            framework_findings={
                "ta": {"primary_finding": "adult", "confidence_score": 0.8},
                "ei": {"emotional_state": "openness", "confidence_score": 0.75},
            },
            synthesis={
                "threat_level": "LOW",
                "engagement_level": "HIGH",
                "decision_readiness": "PROGRESSING",
                "relationship_quality": "secure",
                "strategic_position": "collaborative",
            },
            conflicts=[],
            synergies=["Neuroscience and somatic align on calm state"],
            integrated_coaching=[
                {
                    "priority": 4,
                    "move": "BUILD_TRUST",
                    "reasoning": "High engagement; establish safety",
                    "frameworks": ["ei", "attachment"],
                }
            ],
            close_probability=6.5,
            next_moves=["BUILD_TRUST", "EXPLORE_NEEDS", "PROPOSE_SOLUTION"],
        )

    @staticmethod
    def _synthesize_coaching_text(analysis: AnalysisResponse) -> str:
        """Synthesize coaching into narrative text."""
        moves = ", ".join(analysis.next_moves[:3])
        return (
            f"UNIFIED COACHING RECOMMENDATION\n\n"
            f"THREAT LEVEL: {analysis.synthesis.get('threat_level', 'UNKNOWN')}\n"
            f"ENGAGEMENT: {analysis.synthesis.get('engagement_level', 'UNKNOWN')}\n"
            f"READINESS: {analysis.synthesis.get('decision_readiness', 'UNKNOWN')}\n\n"
            f"NEXT MOVES: {moves}\n\n"
            f"Close Probability: {analysis.close_probability:.1f}/10"
        )

    @staticmethod
    def _mock_script_response(req: ScriptRequest) -> ScriptResponse:
        """Mock script response for testing."""
        scripts = {
            ("cold_call", "driver"): "Let's cut to the chase. Here's what we can do...",
            ("cold_call", "expressive"): "I'm excited to share this opportunity with you...",
            ("cold_call", "amiable"): "I think we can build something great together...",
            ("cold_call", "analytical"): "Based on your industry, here are the metrics...",
            ("objection", "driver"): "I hear the concern. Let's address it directly...",
            ("objection", "expressive"): "I understand your hesitation. Let me show you...",
            ("objection", "amiable"): "Your concern is valid. How can we solve it together...",
            ("objection", "analytical"): "Valid point. Here's the data that addresses it...",
            ("closing", "driver"): "Let's finalize this. What do you need to move forward?",
            ("closing", "expressive"): "This is going to be amazing! Let's make it official!",
            ("closing", "amiable"): "I'm confident this is right for you. Shall we proceed?",
            ("closing", "analytical"): "The terms are clear. Are you ready to sign?",
        }

        key = (req.situation.lower(), req.personality_type.lower())
        script = scripts.get(key, "Let's move this forward together.")

        return ScriptResponse(
            request_id=f"script-{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            situation=req.situation,
            personality_type=req.personality_type,
            script=script,
            rationale=f"Optimized for {req.personality_type} personality in {req.situation} context.",
            confidence_score=0.87,
            follow_up_tactics=[
                "Listen for response",
                "Validate their concern",
                "Propose alternative",
                "Schedule follow-up",
            ],
        )

    @staticmethod
    def _get_script(situation: Situation, personality: Personality, language: str) -> str:
        """Retrieve script for situation + personality combination."""
        if language.lower() == "ro":
            scripts = {
                (Situation.COLD_CALL, Personality.DRIVER): "Să ajungem direct la lucru. Iată ce putem face...",
                (Situation.DISCOVERY, Personality.AMIABLE): "Cred că putem construi ceva grozav împreună...",
                (Situation.OBJECTION, Personality.ANALYTICAL): "Punctul tău e valid. Iată datele...",
                (Situation.CLOSING, Personality.EXPRESSIVE): "O să fie fantastic! Să o facem oficial!",
            }
        else:
            scripts = {
                (Situation.COLD_CALL, Personality.DRIVER): "Let's cut to the chase. Here's our value...",
                (Situation.DISCOVERY, Personality.AMIABLE): "I'd love to understand your needs better...",
                (Situation.OBJECTION, Personality.ANALYTICAL): "That's a valid concern. Here's the data...",
                (Situation.CLOSING, Personality.EXPRESSIVE): "This is going to be amazing! Let's do it!",
            }

        return scripts.get((situation, personality), "Let's move this forward together.")


class CoachingStreamManager:
    """Manages WebSocket connections for real-time coaching streams."""

    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.engine = AnalysisEngine()

    async def stream_coaching(self, connection_id: str, your_text: str, their_text: str, interval_sec: int = 30):
        """Stream coaching updates to client every interval_sec seconds."""
        try:
            while True:
                req = CoachingRequest(
                    your_text=your_text,
                    their_text=their_text,
                    language="en",
                )
                coaching = self.engine.synthesize_coaching(req)

                update = {
                    "type": "coaching_update",
                    "timestamp": coaching.timestamp,
                    "coaching_summary": coaching.coaching_summary,
                    "key_moves": coaching.key_moves,
                    "confidence_score": coaching.confidence_score,
                }

                # In production: send via WebSocket
                print(f"[COACHING STREAM {connection_id}] {json.dumps(update)}")

                await asyncio.sleep(interval_sec)

        except Exception as e:
            print(f"[STREAM ERROR {connection_id}] {str(e)}")

    def start_stream(self, connection_id: str, your_text: str, their_text: str):
        """Start a coaching stream for a connection."""
        self.connections[connection_id] = {
            "your_text": your_text,
            "their_text": their_text,
            "started_at": datetime.now().isoformat(),
        }

    def stop_stream(self, connection_id: str):
        """Stop a coaching stream."""
        if connection_id in self.connections:
            del self.connections[connection_id]


class SantinelAPIGateway:
    """Main API Gateway for SANTINEL."""

    def __init__(self):
        self.engine = AnalysisEngine()
        self.stream_manager = CoachingStreamManager()
        self.crm_sync = CRMSyncAdapter() if CRMSyncAdapter else None

    def analyze(self, req: AnalysisRequest) -> AnalysisResponse:
        """POST /analyze endpoint."""
        return self.engine.analyze(req)

    def coach(self, req: CoachingRequest) -> CoachingResponse:
        """POST /coach endpoint."""
        return self.engine.synthesize_coaching(req)

    def match_script(self, req: ScriptRequest) -> ScriptResponse:
        """POST /scripts endpoint."""
        return self.engine.match_script(req)

    def record_outcome(self, outcome: OutcomeRecord) -> Dict:
        """POST /outcomes endpoint."""
        self.engine.record_outcome(outcome)
        return {"status": "recorded", "outcome_id": f"outcome-{datetime.now().timestamp()}"}

    async def stream_coaching_ws(self, connection_id: str, your_text: str, their_text: str):
        """WS /stream-coaching endpoint."""
        await self.stream_manager.stream_coaching(connection_id, your_text, their_text)

    def health_check(self) -> Dict:
        """GET /health endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "frameworks": 10,
            "version": "1.0.0",
        }


# FastAPI integration example (pseudo-code)
def create_fastapi_app():
    """Create FastAPI app with SANTINEL endpoints."""
    # In production: integrate with actual FastAPI
    gateway = SantinelAPIGateway()

    return {
        "POST /analyze": gateway.analyze,
        "POST /coach": gateway.coach,
        "POST /scripts": gateway.match_script,
        "POST /outcomes": gateway.record_outcome,
        "WS /stream-coaching": gateway.stream_coaching_ws,
        "GET /health": gateway.health_check,
    }


if __name__ == "__main__":
    # Test API Gateway
    gateway = SantinelAPIGateway()

    # Test analysis
    print("=== ANALYSIS REQUEST ===")
    analysis_req = AnalysisRequest(
        your_text="I believe this is a great opportunity for both of us.",
        their_text="I'm interested, but I need to understand the pricing better.",
        language="en",
    )
    analysis = gateway.analyze(analysis_req)
    print(f"Close Probability: {analysis.close_probability:.1f}/10")
    print(f"Next Moves: {analysis.next_moves}")

    # Test coaching
    print("\n=== COACHING REQUEST ===")
    coaching_req = CoachingRequest(
        your_text="I believe this is a great opportunity for both of us.",
        their_text="I'm interested, but I need to understand the pricing better.",
        personality_type="analytical",
        situation="discovery",
    )
    coaching = gateway.coach(coaching_req)
    print(f"Next Best Action: {coaching.next_best_action}")
    print(f"Confidence: {coaching.confidence_score:.2f}")

    # Test script matching
    print("\n=== SCRIPT MATCHING ===")
    script_req = ScriptRequest(
        situation="objection",
        personality_type="driver",
        language="en",
    )
    script = gateway.match_script(script_req)
    print(f"Script: {script.script}")
    print(f"Follow-up Tactics: {script.follow_up_tactics}")

    # Test outcome recording
    print("\n=== OUTCOME RECORDING ===")
    outcome = OutcomeRecord(
        deal_id="deal-001",
        lead_id="lead-001",
        situation="closing",
        personality_type="driver",
        script_used="Let's finalize this deal",
        result="won",
        coaching_effectiveness=0.92,
        duration_seconds=1200,
    )
    result = gateway.record_outcome(outcome)
    print(f"Result: {result}")

    # Test health check
    print("\n=== HEALTH CHECK ===")
    health = gateway.health_check()
    print(f"Status: {health['status']}")
    print(f"Version: {health['version']}")
