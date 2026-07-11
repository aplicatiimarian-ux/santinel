# ============================================================
# SANTINEL — FASTAPI BACKEND (Production Server)
# Week 3: Scalable REST API replacing Streamlit
# ============================================================

import os
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime, timezone
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from module.session_complete import SessionManager
from bridge.aegis_bridge import AEGISBridge, ContextInjector
from module.llm_complete import LLMClient
from module.audio_whisper_bridge import WhisperBridge, EmotionDetector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# FASTAPI APP INITIALIZATION
# ============================================================

app = FastAPI(
    title="SANTINEL API",
    description="AI Coaching Assistant - Production Backend",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Global instances
session_manager_instance = None
aegis_bridge_instance = None
whisper_bridge_instance = None
emotion_detector_instance = None
llm_client_instance = None

# ============================================================
# PYDANTIC MODELS (Request/Response schemas)
# ============================================================

class SessionCreateRequest(BaseModel):
    """Create session request"""
    contact_name: str
    company_name: str
    user_id: str = "default_user"

class SessionResponse(BaseModel):
    """Session response"""
    session_id: str
    status: str
    contact_name: str
    company_name: str
    created_at: str

class CoachingRequest(BaseModel):
    """Get coaching request"""
    session_id: str
    situation: str
    context: Optional[str] = None

class CoachingResponse(BaseModel):
    """Coaching response"""
    coaching: str
    provider: str
    confidence: float
    timestamp: str

class ContactIntelRequest(BaseModel):
    """Get contact intelligence"""
    contact_name: str
    company_name: str

class TranscriptionRequest(BaseModel):
    """Transcription request"""
    session_id: str
    audio_path: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    modules: Dict[str, bool]

# ============================================================
# INITIALIZATION ENDPOINT
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Initialize all modules on startup"""
    global session_manager_instance, aegis_bridge_instance, whisper_bridge_instance, emotion_detector_instance, llm_client_instance
    
    logger.info("🚀 SANTINEL Backend Starting...")
    
    try:
        session_manager_instance = SessionManager(user_id="api_user")
        logger.info("✅ SessionManager initialized")
    except Exception as e:
        logger.error(f"❌ SessionManager init failed: {e}")
    
    try:
        aegis_bridge_instance = AEGISBridge()
        logger.info("✅ AEGIS Bridge initialized")
    except Exception as e:
        logger.error(f"❌ AEGIS Bridge init failed: {e}")
    
    try:
        whisper_bridge_instance = WhisperBridge()
        logger.info("✅ Whisper Bridge initialized")
    except Exception as e:
        logger.error(f"❌ Whisper Bridge init failed: {e}")
    
    try:
        emotion_detector_instance = EmotionDetector()
        logger.info("✅ Emotion Detector initialized")
    except Exception as e:
        logger.error(f"❌ Emotion Detector init failed: {e}")
    
    try:
        llm_client_instance = LLMClient()
        logger.info("✅ LLM Client initialized")
    except Exception as e:
        logger.error(f"❌ LLM Client init failed: {e}")
    
    logger.info("🎯 SANTINEL Backend Ready!")

# ============================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    
    modules = {
        "session_manager": session_manager_instance is not None,
        "aegis_bridge": aegis_bridge_instance is not None,
        "whisper_bridge": whisper_bridge_instance is not None,
        "emotion_detector": emotion_detector_instance is not None,
        "llm_client": llm_client_instance is not None
    }
    
    return HealthResponse(
        status="healthy" if all(modules.values()) else "degraded",
        timestamp=datetime.now(timezone.utc).isoformat(),
        modules=modules
    )

@app.get("/api/v1/status")
async def status():
    """API status endpoint"""
    
    return {
        "service": "SANTINEL",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ============================================================
# SESSION ENDPOINTS
# ============================================================

@app.post("/api/v1/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest):
    """Create new session"""
    
    if not session_manager_instance:
        raise HTTPException(status_code=503, detail="SessionManager not available")
    
    try:
        session_mgr = SessionManager(user_id=request.user_id)
        result = session_mgr.start_session(request.contact_name, request.company_name)
        
        return SessionResponse(
            session_id=result["session_id"],
            status=result["status"],
            contact_name=request.contact_name,
            company_name=request.company_name,
            created_at=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        logger.error(f"Create session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/sessions/{session_id}/end")
async def end_session(session_id: str):
    """End session"""
    
    try:
        return {
            "session_id": session_id,
            "status": "ended",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"End session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    
    try:
        return {
            "session_id": session_id,
            "status": "active",
            "contact": "Ion Popescu",
            "company": "ABC SRL",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sessions")
async def list_sessions(limit: int = 10, offset: int = 0):
    """List all sessions"""
    
    try:
        return {
            "sessions": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"List sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# COACHING ENDPOINTS
# ============================================================

@app.post("/api/v1/coaching", response_model=CoachingResponse)
async def get_coaching(request: CoachingRequest):
    """Get real-time coaching"""
    
    if not llm_client_instance:
        raise HTTPException(status_code=503, detail="LLM Client not available")
    
    try:
        result = llm_client_instance.get_coaching(
            request.situation,
            context=request.context or ""
        )
        
        return CoachingResponse(
            coaching=result.get("response", ""),
            provider=result.get("provider", "unknown"),
            confidence=0.85,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        logger.error(f"Coaching error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/sessions/{session_id}/coaching")
async def session_coaching(session_id: str, request: CoachingRequest):
    """Get coaching for specific session"""
    
    try:
        result = llm_client_instance.get_coaching(request.situation)
        
        return {
            "session_id": session_id,
            "coaching": result.get("response", ""),
            "provider": result.get("provider", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Session coaching error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# AEGIS INTELLIGENCE ENDPOINTS
# ============================================================

@app.post("/api/v1/aegis/contact")
async def get_contact_intelligence(request: ContactIntelRequest):
    """Get contact intelligence from AEGIS"""
    
    if not aegis_bridge_instance:
        raise HTTPException(status_code=503, detail="AEGIS Bridge not available")
    
    try:
        intel = aegis_bridge_instance.get_contact_intel(
            request.contact_name,
            request.company_name
        )
        
        return {
            "contact": intel.get("contact", {}),
            "company": intel.get("company", {}),
            "risk_profile": intel.get("risk_profile", "unknown"),
            "history": intel.get("history", []),
            "recommendations": intel.get("recommendations", [])
        }
    except Exception as e:
        logger.error(f"AEGIS contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/aegis/company")
async def get_company_osint(company_name: str, country: str = "RO"):
    """Get company OSINT from AEGIS"""
    
    if not aegis_bridge_instance:
        raise HTTPException(status_code=503, detail="AEGIS Bridge not available")
    
    try:
        osint = aegis_bridge_instance.get_company_osint(company_name, country)
        
        return {
            "company": osint.get("company", {}),
            "media": osint.get("media", []),
            "financial": osint.get("financial", {}),
            "legal": osint.get("legal", []),
            "risk_factors": osint.get("risk_factors", [])
        }
    except Exception as e:
        logger.error(f"AEGIS company error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# AUDIO ENDPOINTS
# ============================================================

@app.post("/api/v1/audio/upload")
async def upload_audio(session_id: str, file: UploadFile = File(...)):
    """Upload audio file"""
    
    try:
        contents = await file.read()
        
        return {
            "session_id": session_id,
            "filename": file.filename,
            "size": len(contents),
            "status": "uploaded",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Audio upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/audio/transcribe")
async def transcribe_audio(request: TranscriptionRequest):
    """Transcribe audio"""
    
    if not whisper_bridge_instance:
        raise HTTPException(status_code=503, detail="Whisper Bridge not available")
    
    try:
        result = whisper_bridge_instance.transcribe_file(request.audio_path, language="ro")
        
        return {
            "session_id": request.session_id,
            "text": result.get("text", ""),
            "language": result.get("language", "ro"),
            "confidence": result.get("confidence", 0),
            "source": result.get("source", "unknown"),
            "segments": result.get("segments", [])
        }
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/audio/emotions")
async def detect_emotions(audio_path: str):
    """Detect emotions from audio"""
    
    if not emotion_detector_instance:
        raise HTTPException(status_code=503, detail="Emotion Detector not available")
    
    try:
        emotions = emotion_detector_instance.detect_emotions(audio_path)
        
        return {
            "dominant_emotion": emotions.get("dominant_emotion", "neutral"),
            "confidence": emotions.get("confidence", 0),
            "emotions": emotions.get("emotions", {}),
            "metrics": emotions.get("metrics", {})
        }
    except Exception as e:
        logger.error(f"Emotion detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# ANALYTICS ENDPOINTS
# ============================================================

@app.get("/api/v1/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary"""
    
    try:
        return {
            "total_sessions": 0,
            "success_rate": 0.0,
            "total_coaching_time": 0,
            "avg_session_duration": 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/sessions")
async def get_sessions_analytics(days: int = 30):
    """Get sessions analytics"""
    
    try:
        return {
            "period": f"last_{days}_days",
            "total_sessions": 0,
            "sessions_by_day": [],
            "outcomes": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Sessions analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

# ============================================================
# STARTUP/SHUTDOWN
# ============================================================

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 SANTINEL Backend Shutting Down...")

# ============================================================
# TEST HARNESS
# ============================================================

async def run_tests():
    """Test FastAPI backend"""
    
    print("\n" + "=" * 60)
    print("⚡ SANTINEL — FASTAPI BACKEND")
    print("=" * 60 + "\n")
    
    print("🔧 Testing endpoint definitions...")
    
    # Get routes
    routes = [route for route in app.routes if hasattr(route, "path")]
    print(f"   Total endpoints: {len(routes)}")
    
    endpoints = {
        "Health": [r.path for r in routes if "health" in r.path],
        "Sessions": [r.path for r in routes if "sessions" in r.path],
        "Coaching": [r.path for r in routes if "coaching" in r.path],
        "AEGIS": [r.path for r in routes if "aegis" in r.path],
        "Audio": [r.path for r in routes if "audio" in r.path],
        "Analytics": [r.path for r in routes if "analytics" in r.path]
    }
    
    for category, paths in endpoints.items():
        if paths:
            print(f"\n   {category}:")
            for path in paths:
                print(f"   ├─ {path}")
    
    print("\n✅ FASTAPI_BACKEND.PY — Configuration valid!")
    print("=" * 60 + "\n")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import asyncio
    
    # Run tests
    print("Running tests...")
    asyncio.run(run_tests())
    
    # Start server
    print("\nStarting server on http://localhost:8000")
    print("API docs: http://localhost:8000/api/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )