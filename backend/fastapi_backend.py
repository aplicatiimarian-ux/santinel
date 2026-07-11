"""
SANTINEL Backend — FastAPI + Professional Psychology Coaching
Integrated: CBT, NLP, TA, Dual-Speaker Analysis, Goal-Based Coaching
Real-time AI coaching with professional frameworks
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
from datetime import datetime
import sys
import os

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from core_complete import SantinelCore
from anonimizare.anon_complete import Anonymizer
from module.llm_complete import LLMClient
from core.cbt_module import CBTAssessment
from core.nlp_module import NLPModule
from core.ta_module import TAModule
from core.dual_speaker_analyzer import DualSpeakerAnalyzer
from core.goal_coaching_engine import GoalCoachingEngine, GoalType

# Initialize FastAPI
app = FastAPI(title="SANTINEL", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
core = SantinelCore()
anonymizer = Anonymizer()
llm = LLMClient()

# Psychology framework modules
cbt = CBTAssessment()
nlp = NLPModule()
ta = TAModule()
dual_speaker = DualSpeakerAnalyzer()
goal_engine = GoalCoachingEngine()

# Session storage (SQLite in production)
sessions = {}
session_goals = {}

# ============== PYDANTIC MODELS ==============

class SessionCreate(BaseModel):
    contact_name: str
    company_name: str
    user_id: str

class CoachingRequest(BaseModel):
    session_id: str
    situation: str
    emotions: Optional[Dict[str, float]] = None
    is_reactive: bool = False

class GoalAdd(BaseModel):
    goal_type: str  # "price", "terms", "scope", "timeline", "relationship", "information", "custom"
    description: str
    target_value: str
    minimum_acceptable: str
    priority: int = 1

class AudioAnalysisRequest(BaseModel):
    session_id: str
    audio_path: str
    transcription: Optional[str] = None

# ============== ENDPOINTS ==============

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "🟢 SANTINEL operational", "timestamp": datetime.now()}

@app.post("/api/v1/sessions")
async def create_session(session: SessionCreate):
    """Create new negotiation session"""
    session_id = f"session_{datetime.now().timestamp()}"
    
    sessions[session_id] = {
        "contact_name": session.contact_name,
        "company_name": session.company_name,
        "user_id": session.user_id,
        "created_at": datetime.now(),
        "goals": [],
        "interactions": [],
    }
    
    session_goals[session_id] = GoalCoachingEngine()
    
    return {
        "session_id": session_id,
        "message": f"✅ Session created for {session.contact_name} @ {session.company_name}",
        "status": "active"
    }

@app.post("/api/v1/goals/add")
async def add_goal(session_id: str, goal: GoalAdd):
    """Add negotiation goal to session"""
    if session_id not in session_goals:
        raise HTTPException(status_code=404, detail="Session not found")
    
    goal_engine_instance = session_goals[session_id]
    
    # Map string to GoalType enum
    goal_type_map = {
        "price": GoalType.PRICE,
        "terms": GoalType.TERMS,
        "scope": GoalType.SCOPE,
        "timeline": GoalType.TIMELINE,
        "relationship": GoalType.RELATIONSHIP,
        "information": GoalType.INFORMATION,
        "custom": GoalType.CUSTOM,
    }
    
    goal_type = goal_type_map.get(goal.goal_type, GoalType.CUSTOM)
    
    new_goal = goal_engine_instance.add_goal(
        goal_type=goal_type,
        description=goal.description,
        target_value=goal.target_value,
        minimum_acceptable=goal.minimum_acceptable,
        priority=goal.priority
    )
    
    sessions[session_id]["goals"].append({
        "type": goal.goal_type,
        "description": goal.description,
        "target": goal.target_value,
        "minimum": goal.minimum_acceptable,
    })
    
    return {
        "goal_added": True,
        "goal_id": len(goal_engine_instance.goals) - 1,
        "message": f"✅ Goal added: {goal.description}"
    }

@app.post("/api/v1/audio/transcribe")
async def transcribe_audio(request: AudioAnalysisRequest):
    """Transcribe audio to text"""
    # Mock transcription (real would use Whisper API)
    mock_transcription = "Vendor wants 20% increase, we can afford 5%. Need better strategy."
    
    return {
        "session_id": request.session_id,
        "text": mock_transcription,
        "confidence": 0.92,
        "language": "en"
    }

@app.post("/api/v1/audio/emotions")
async def detect_emotions(request: AudioAnalysisRequest):
    """Detect emotions from audio"""
    # Mock emotion detection
    return {
        "session_id": request.session_id,
        "dominant_emotion": "assertive",
        "emotions": {
            "assertive": 0.8,
            "confident": 0.6,
            "calm": 0.5
        },
        "confidence": 0.85
    }

@app.post("/api/v1/coaching")
async def get_coaching(request: CoachingRequest):
    """
    Get professional coaching using ALL frameworks:
    CBT + NLP + TA + Dual-Speaker + Goal-Based
    """
    
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # ============ FRAMEWORK 1: CBT ASSESSMENT ============
    distortions = cbt.identify_distortions(request.situation)
    cbt_assessment = cbt.assess_emotional_state(
        request.situation,
        request.emotions or {}
    )
    
    # ============ FRAMEWORK 2: NLP ANALYSIS ============
    rep_system = nlp.detect_representation_system(request.situation)
    problem_frame = nlp.detect_problem_frame(request.situation)
    nlp_reframe = nlp.generate_nlp_reframe(
        request.situation,
        problem_frame,
        max(request.emotions or {}, key=lambda k: request.emotions[k]) if request.emotions else "neutral"
    )
    excellence_model = nlp.model_excellence(problem_frame)
    linguistic_analysis = nlp.linguistic_pattern_analysis(request.situation)
    
    # ============ FRAMEWORK 3: TA ANALYSIS ============
    ego_state_analysis = ta.detect_ego_state(request.situation)
    life_position = ta.detect_life_position(request.situation, "")
    game_analysis = ta.detect_psychological_game(request.situation)
    healthy_transaction = ta.prescribe_healthy_transaction(request.situation)
    
    # ============ FRAMEWORK 4: DUAL-SPEAKER ANALYSIS ============
    user_analysis = dual_speaker.analyze_user(
        request.situation,
        request.emotions or {},
        ego_state_analysis.get("primary_ego_state", "unknown"),
        life_position.value
    )
    counterparty_analysis = dual_speaker.infer_counterparty_state(request.situation)
    interaction_dynamics = dual_speaker.analyze_interaction_dynamics()
    dual_coaching = dual_speaker.generate_dual_coaching()
    
    # ============ FRAMEWORK 5: GOAL-BASED COACHING ============
    goal_engine_instance = session_goals.get(request.session_id, GoalCoachingEngine())
    
    if request.is_reactive:
        goal_based = goal_engine_instance.get_reactive_coaching(request.situation)
    else:
        goal_based = goal_engine_instance.get_goal_coaching()
    
    # ============ INTEGRATION: PROFESSIONAL COACHING ============
    # Use LLM to synthesize all frameworks into coherent coaching
    synthesis_prompt = f"""
You are an expert executive coach specializing in high-stakes negotiations.
Synthesize the following psychological frameworks into ONE coherent coaching response:

SITUATION: {request.situation}

CBT INSIGHT: {cbt_assessment.get('cbt_intervention', '')}
NLP STRATEGY: {nlp_reframe}
TA PRESCRIPTION: {healthy_transaction}
DUAL-PARTY COACHING: {dual_coaching}
GOAL-ALIGNED COACHING: {goal_based}

Generate a concise, actionable coaching response that:
1. Identifies the core issue (psychological insight)
2. Provides immediate tactical action
3. Maintains both parties' dignity
4. Moves toward mutual value creation
Keep response to 3-5 sentences maximum.
"""
    
    try:
        synthesized_response = llm.complete(synthesis_prompt)
    except:
        synthesized_response = f"""
PROFESSIONAL COACHING RESPONSE:

{cbt_assessment.get('therapeutic_insight', 'Maintain clarity and focus.')}

Recommended action: {nlp_reframe.split('ACTION:')[1].split('USE:')[0].strip() if 'ACTION:' in nlp_reframe else 'Stay in Adult ego state.'}

Remember: {healthy_transaction.split('🎯')[1].split('🗣️')[0].strip() if '🎯' in healthy_transaction else 'Focus on mutual value.'}
"""
    
    # Store interaction for session history
    sessions[request.session_id]["interactions"].append({
        "timestamp": datetime.now(),
        "situation": request.situation,
        "frameworks_used": ["CBT", "NLP", "TA", "Dual-Speaker", "Goal-Based"],
        "coaching_type": "reactive" if request.is_reactive else "goal-focused"
    })
    
    return {
        "session_id": request.session_id,
        "coaching": synthesized_response,
        "frameworks_applied": {
            "cbt": {
                "distortions_found": [d["distortion"] for d in distortions],
                "insight": cbt_assessment.get("therapeutic_insight", "")
            },
            "nlp": {
                "representation_system": rep_system.get("primary_system"),
                "reframe": nlp_reframe[:100] + "..."
            },
            "ta": {
                "ego_state": ego_state_analysis.get("primary_ego_state"),
                "life_position": life_position.value
            },
            "dual_speaker": {
                "user_state": user_analysis.get("emotional_state"),
                "counterparty_readiness": counterparty_analysis.get("readiness_to_agree", "")
            },
            "goal_aligned": "Yes" if goal_engine_instance.goals else "No goals set"
        },
        "detailed_assessment": {
            "cbt_assessment": cbt_assessment,
            "nlp_analysis": rep_system,
            "ta_analysis": ego_state_analysis,
            "dual_speaker": interaction_dynamics,
        }
    }

@app.post("/api/v1/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get complete session status and progress"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    goal_engine_instance = session_goals.get(session_id)
    
    return {
        "session_id": session_id,
        "contact": session_data["contact_name"],
        "company": session_data["company_name"],
        "created_at": session_data["created_at"],
        "interactions_count": len(session_data["interactions"]),
        "goals": session_data["goals"],
        "goal_count": len(session_data["goals"]),
        "status": "active"
    }

# ============== STARTUP ==============

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 SANTINEL Backend Starting...")
    print("✅ Psychology Frameworks Loaded:")
    print("   • CBT (Cognitive Behavioral Therapy)")
    print("   • NLP (Neuro-Linguistic Programming)")
    print("   • TA (Transactional Analysis)")
    print("   • Dual-Speaker Analysis")
    print("   • Goal-Based Coaching Engine")
    print("✅ FastAPI running on http://0.0.0.0:8000")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)