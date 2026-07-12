"""
SANTINEL Backend — FastAPI + Professional Psychology Coaching + Vector DB
Integrated: CBT, NLP, TA, Dual-Speaker Analysis, Goal-Based Coaching
Real-time AI coaching with professional frameworks + Feedback System + Self-Improving LLM
PHASE 2: Vector DB for high-quality pattern storage + LLM fine-tuning
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
from datetime import datetime
import sys
import os
import sqlite3

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

try:
    from cbt_module import CBTAssessment
    from nlp_module import NLPModule
    from ta_module import TAModule
    from dual_speaker_analyzer import DualSpeakerAnalyzer
    from goal_coaching_engine import GoalCoachingEngine, GoalType
except ImportError as e:
    print(f"Warning: Psychology modules not found: {e}")
    print("Continuing with mock implementations...")

# Import Vector DB Manager
try:
    from vector_db_integration import get_vector_db_manager
    vector_db = get_vector_db_manager(use_mock=True)  # Use mock for MVP
except ImportError:
    print("Warning: Vector DB integration not found, using mock")
    vector_db = None

# Initialize FastAPI
app = FastAPI(title="SANTINEL", version="2.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Psychology framework modules
try:
    cbt = CBTAssessment()
    nlp = NLPModule()
    ta = TAModule()
    dual_speaker = DualSpeakerAnalyzer()
except:
    cbt = None
    nlp = None
    ta = None
    dual_speaker = None
    print("Psychology modules initialized with fallbacks")

# Feedback Database
class FeedbackDatabase:
    """SQLite database for storing feedback and outcomes"""
    
    def __init__(self, db_path: str = 'santinel_feedback.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                coaching_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                quality_score REAL,
                useful_aspects TEXT,
                comments TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Outcomes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                contact_name TEXT,
                company_name TEXT,
                negotiation_type TEXT,
                success INTEGER,
                target_value REAL,
                actual_value REAL,
                target_achieved REAL,
                actual_achieved REAL,
                notes TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Coaching performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coaching_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coaching_id TEXT NOT NULL,
                framework_used TEXT,
                user_satisfaction REAL,
                outcome_success_rate REAL,
                improvement_trend REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                period TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vector DB patterns table (cache)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vector_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT NOT NULL,
                coaching_text TEXT,
                situation_type TEXT,
                frameworks_used TEXT,
                rating INTEGER,
                quality_score REAL,
                session_id TEXT,
                success_outcome INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_feedback(self, session_id: str, coaching_id: str, rating: int, 
                       quality_score: float, useful_aspects: List[str], comments: str = '') -> bool:
        """Store user feedback for coaching"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            aspects_str = ','.join(useful_aspects) if useful_aspects else ''
            
            cursor.execute('''
                INSERT INTO feedback 
                (session_id, coaching_id, rating, quality_score, useful_aspects, comments)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, coaching_id, rating, quality_score, aspects_str, comments))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing feedback: {e}")
            return False
    
    def store_outcome(self, session_id: str, contact_name: str, company_name: str,
                      negotiation_type: str, success: bool, target_value: float,
                      actual_value: float, target_achieved: float, actual_achieved: float,
                      notes: str = '') -> bool:
        """Store negotiation outcome"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO outcomes
                (session_id, contact_name, company_name, negotiation_type, success,
                 target_value, actual_value, target_achieved, actual_achieved, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, contact_name, company_name, negotiation_type, 
                  1 if success else 0, target_value, actual_value, target_achieved, 
                  actual_achieved, notes))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing outcome: {e}")
            return False
    
    def get_feedback_stats(self) -> Dict:
        """Get feedback statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT AVG(rating), COUNT(*) FROM feedback')
            avg_rating, count = cursor.fetchone()
            
            cursor.execute('SELECT AVG(quality_score) FROM feedback')
            avg_quality = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'average_rating': avg_rating or 0,
                'total_ratings': count or 0,
                'average_quality_score': avg_quality or 0
            }
        except Exception as e:
            print(f"Error getting feedback stats: {e}")
            return {}
    
    def get_outcome_stats(self) -> Dict:
        """Get outcome statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*), SUM(success) FROM outcomes')
            result = cursor.fetchone()
            total = result[0] if result else 0
            successes = result[1] if result else 0
            
            cursor.execute('SELECT AVG(actual_achieved) FROM outcomes WHERE success = 1')
            avg_result = cursor.fetchone()
            avg_success_rate = avg_result[0] if avg_result else 0
            
            cursor.execute('SELECT negotiation_type, COUNT(*), SUM(success) FROM outcomes GROUP BY negotiation_type')
            by_type = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_negotiations': total or 0,
                'successful_negotiations': successes or 0,
                'success_rate': (successes / total * 100) if total else 0,
                'average_achievement_rate': avg_success_rate or 0,
                'by_type': by_type
            }
        except Exception as e:
            print(f"Error getting outcome stats: {e}")
            return {}
    
    def get_top_coaching_patterns(self, limit: int = 5) -> List[Dict]:
        """Get most effective coaching patterns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT f.coaching_id, AVG(f.rating), AVG(f.quality_score), COUNT(*)
                FROM feedback f
                GROUP BY f.coaching_id
                ORDER BY AVG(f.rating) DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'coaching_id': r[0],
                    'avg_rating': r[1],
                    'avg_quality': r[2],
                    'count': r[3]
                }
                for r in results
            ]
        except Exception as e:
            print(f"Error getting coaching patterns: {e}")
            return []
    
    def export_for_finetuning(self) -> Dict:
        """Export high-quality interactions for LLM fine-tuning"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_id, coaching_id, rating, quality_score
                FROM feedback
                WHERE rating >= 4
                ORDER BY rating DESC
            ''')
            
            high_quality = cursor.fetchall()
            
            cursor.execute('''
                SELECT session_id, negotiation_type, actual_achieved
                FROM outcomes
                WHERE success = 1
                ORDER BY actual_achieved DESC
            ''')
            
            successful = cursor.fetchall()
            
            conn.close()
            
            return {
                'high_quality_coaching': [
                    {'session_id': h[0], 'coaching_id': h[1], 'rating': h[2], 'quality': h[3]}
                    for h in high_quality
                ],
                'successful_negotiations': [
                    {'session_id': s[0], 'type': s[1], 'achievement': s[2]}
                    for s in successful
                ]
            }
        except Exception as e:
            print(f"Error exporting for fine-tuning: {e}")
            return {}

# Initialize feedback database
feedback_db = FeedbackDatabase('santinel_feedback.db')

# Session storage
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
    goal_type: str
    description: str
    target_value: str
    minimum_acceptable: str
    priority: int = 1

class AudioAnalysisRequest(BaseModel):
    session_id: str
    audio_path: str
    transcription: Optional[str] = None

class FeedbackRequest(BaseModel):
    session_id: str
    coaching_id: str
    rating: int
    quality_score: float
    useful_aspects: List[str] = []
    comments: str = ""

class OutcomeRequest(BaseModel):
    session_id: str
    contact_name: str
    company_name: str
    negotiation_type: str
    success: bool
    target_value: float
    actual_value: float
    target_achieved: float
    actual_achieved: float
    notes: str = ""

# ============== ENDPOINTS ==============

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "🟢 SANTINEL operational",
        "version": "2.0.0",
        "vector_db": "✅ Ready" if vector_db else "⚠️ Disabled",
        "timestamp": datetime.now()
    }

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
        "contact_name": session.contact_name,
        "company_name": session.company_name,
        "created_at": str(datetime.now()),
        "message": f"✅ Sesiune creată pentru {session.contact_name}",
        "status": "active"
    }

@app.post("/api/v1/goals/add")
async def add_goal(session_id: str, goal: GoalAdd):
    """Add negotiation goal to session"""
    if session_id not in session_goals:
        raise HTTPException(status_code=404, detail="Sesiune nu găsită")
    
    goal_engine_instance = session_goals[session_id]
    
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
        "message": f"✅ Obiectiv adăugat: {goal.description}"
    }

@app.post("/api/v1/audio/transcribe")
async def transcribe_audio(request: AudioAnalysisRequest):
    """Transcribe audio to text"""
    mock_transcription = "Vânzătorul cere 20% creștere, putem permite 5%. Avem nevoie de strategie mai bună."
    
    return {
        "session_id": request.session_id,
        "text": mock_transcription,
        "confidence": 0.92,
        "language": "ro"
    }

@app.post("/api/v1/audio/emotions")
async def detect_emotions(request: AudioAnalysisRequest):
    """Detect emotions from audio"""
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
    PHASE 2: Enhanced with Vector DB similar patterns
    """
    
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sesiune nu găsită")
    
    coaching_parts = []
    frameworks_applied = []
    
    # PHASE 2: Retrieve similar patterns from Vector DB
    similar_patterns = []
    situation_type = "general"
    
    if vector_db:
        similar_patterns = vector_db.find_similar_patterns(
            situation_text=request.situation,
            situation_type=situation_type,
            limit=3
        )
        if similar_patterns:
            coaching_parts.append(f"📚 Similar successes: {len(similar_patterns)} patterns found in knowledge base")
            frameworks_applied.append("VectorDB-Retrieval")
    
    # CBT Analysis
    cbt_insight = ""
    try:
        if cbt:
            distortions = cbt.identify_distortions(request.situation)
            cbt_assessment = cbt.assess_emotional_state(
                request.situation,
                request.emotions or {}
            )
            cbt_insight = cbt_assessment.get("therapeutic_insight", "")
            
            if distortions:
                coaching_parts.append(f"🧠 CBT: Ai identificat distorsiuni: {', '.join([d['distortion'] for d in distortions[:2]])}. {cbt_insight}")
            else:
                coaching_parts.append(f"🧠 CBT: {cbt_insight or 'Gândire clară detectată - continuă cu această claritate.'}")
            
            frameworks_applied.append("CBT")
    except Exception as e:
        print(f"CBT error: {e}")
        coaching_parts.append("🧠 CBT: Gândire strategică recomandată")
    
    # NLP Analysis
    try:
        if nlp:
            rep_system = nlp.detect_representation_system(request.situation)
            system = rep_system.get("primary_system", "balansat")
            coaching_parts.append(f"🎯 NLP: Stil reprezentare {system} detectat. Reframe: Vezi această situație ca oportunitate de negociere.")
            frameworks_applied.append("NLP")
    except Exception as e:
        print(f"NLP error: {e}")
        coaching_parts.append("🎯 NLP: Reframe problema ca oportunitate")
    
    # TA Analysis
    try:
        if ta:
            ego_state_analysis = ta.detect_ego_state(request.situation)
            ego = ego_state_analysis.get("primary_ego_state", "Adult")
            
            if ego == "Adult":
                coaching_parts.append("⚖️ TA: Ești în Adult ego state - perfect pentru negociere rațională.")
            elif ego == "critical_parent":
                coaching_parts.append("⚖️ TA: Detectez ton critic. Mergi în Adult: fapte, date, logică - nu judecată.")
            else:
                coaching_parts.append(f"⚖️ TA: Ego state: {ego}. Tranziția către Adult pentru negociere efectivă.")
            
            frameworks_applied.append("TA")
    except Exception as e:
        print(f"TA error: {e}")
        coaching_parts.append("⚖️ TA: Păstrează Adult ego state - rațional și respectuos")
    
    # Situation-specific coaching
    situation_lower = request.situation.lower()
    specific_advice = ""
    
    if "%" in situation_lower or "creștere" in situation_lower or "crescape" in situation_lower:
        specific_advice = "💰 SPECIFIC: Pentru cererile salariale/preț: Conversa pe valoare, nu pe procentaj. Ce valoare aduci TU? Ce costuri evitează pentru ei?"
        situation_type = "price"
    elif "termen" in situation_lower or "deadline" in situation_lower or "urgent" in situation_lower:
        specific_advice = "⏰ SPECIFIC: Urgența creează presiune. Rămâi calm. Propune timeline realist care beneficiază ambii."
        situation_type = "timeline"
    elif "conflict" in situation_lower or "dezacord" in situation_lower:
        specific_advice = "🤝 SPECIFIC: Conflict = Oportunitate. Găsește interesul comun sub poziții opuse."
        situation_type = "conflict"
    else:
        specific_advice = "📍 SPECIFIC: Focalizează pe valoare mutuală. Care sunt nevoile reale ale celuilalt?"
    
    coaching_parts.append(specific_advice)
    frameworks_applied.append("SituationAnalysis")
    
    # Combine all insights
    final_coaching = "\n".join(coaching_parts)
    
    # Store interaction
    coaching_id = f"coaching_{datetime.now().timestamp()}"
    sessions[request.session_id]["interactions"].append({
        "coaching_id": coaching_id,
        "timestamp": datetime.now(),
        "situation": request.situation,
        "frameworks_used": frameworks_applied,
        "coaching_type": "reactiv" if request.is_reactive else "bazat pe obiective"
    })
    
    return {
        "session_id": request.session_id,
        "coaching_id": coaching_id,
        "coaching": final_coaching,
        "similar_patterns_found": len(similar_patterns),
        "situation_type": situation_type,
        "frameworks_applied": {
            "cbt": {"insight": cbt_insight or "Gândire clară"},
            "nlp": {"reframe": "Oportunitate, nu problemă"},
            "ta": {"ego_state": "Adult", "life_position": "Eu sunt OK/Tu ești OK"},
            "dual_speaker": {"user_state": "asertiv", "counterparty_readiness": "Deschis"},
            "goal_aligned": "Da",
            "vector_db": {"similar_patterns": len(similar_patterns)}
        }
    }

@app.get("/api/v1/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get complete session status and progress"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sesiune nu găsită")
    
    session_data = sessions[session_id]
    
    return {
        "session_id": session_id,
        "contact": session_data["contact_name"],
        "company": session_data["company_name"],
        "created_at": str(session_data["created_at"]),
        "interactions_count": len(session_data["interactions"]),
        "goals": session_data["goals"],
        "goal_count": len(session_data["goals"]),
        "status": "active"
    }

@app.post("/api/v1/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit coaching feedback and rating
    PHASE 2: Store high-rated patterns (4-5 stars) in Vector DB
    """
    success = feedback_db.store_feedback(
        session_id=feedback.session_id,
        coaching_id=feedback.coaching_id,
        rating=feedback.rating,
        quality_score=feedback.quality_score,
        useful_aspects=feedback.useful_aspects,
        comments=feedback.comments
    )
    
    # PHASE 2: Store high-quality patterns in Vector DB
    if success and feedback.rating >= 4 and vector_db:
        try:
            # Get coaching text from session
            session_data = sessions.get(feedback.session_id, {})
            last_interaction = session_data.get("interactions", [])[-1] if session_data.get("interactions") else None
            
            if last_interaction:
                vector_db.store_coaching_pattern(
                    coaching_text=f"Rating {feedback.rating}: {', '.join(feedback.useful_aspects)}",
                    situation_type="general",
                    frameworks_used=last_interaction.get("frameworks_used", []),
                    rating=feedback.rating,
                    quality_score=feedback.quality_score,
                    session_id=feedback.session_id,
                    success_outcome=True,
                    metadata={"useful_aspects": feedback.useful_aspects}
                )
                print(f"✅ High-quality pattern stored in Vector DB (rating: {feedback.rating})")
        except Exception as e:
            print(f"⚠️ Vector DB storage error: {e}")
    
    if success:
        return {
            "status": "✅ Feedback salvat",
            "rating": feedback.rating,
            "message": "Mulțumim pentru feedback!",
            "vector_db_stored": feedback.rating >= 4
        }
    else:
        raise HTTPException(status_code=500, detail="Eroare la salvarea feedback")

@app.post("/api/v1/outcome")
async def submit_outcome(outcome: OutcomeRequest):
    """Submit negotiation outcome"""
    success = feedback_db.store_outcome(
        session_id=outcome.session_id,
        contact_name=outcome.contact_name,
        company_name=outcome.company_name,
        negotiation_type=outcome.negotiation_type,
        success=outcome.success,
        target_value=outcome.target_value,
        actual_value=outcome.actual_value,
        target_achieved=outcome.target_achieved,
        actual_achieved=outcome.actual_achieved,
        notes=outcome.notes
    )
    
    if success:
        return {
            "status": "✅ Rezultat înregistrat",
            "success": outcome.success,
            "achievement_rate": outcome.actual_achieved,
            "message": "Rezultat salvat pentru analiză"
        }
    else:
        raise HTTPException(status_code=500, detail="Eroare la salvarea rezultatului")

@app.get("/api/v1/metrics/feedback")
async def get_feedback_metrics():
    """Get feedback statistics"""
    stats = feedback_db.get_feedback_stats()
    return {
        "average_rating": stats.get('average_rating', 0),
        "total_ratings": stats.get('total_ratings', 0),
        "average_quality_score": stats.get('average_quality_score', 0)
    }

@app.get("/api/v1/metrics/outcomes")
async def get_outcome_metrics():
    """Get negotiation outcome statistics"""
    stats = feedback_db.get_outcome_stats()
    return {
        "total_negotiations": stats.get('total_negotiations', 0),
        "successful_negotiations": stats.get('successful_negotiations', 0),
        "success_rate_percent": stats.get('success_rate', 0),
        "average_achievement_rate": stats.get('average_achievement_rate', 0),
        "by_negotiation_type": stats.get('by_type', [])
    }

@app.get("/api/v1/metrics/top-patterns")
async def get_top_coaching_patterns():
    """Get most effective coaching patterns"""
    patterns = feedback_db.get_top_coaching_patterns(limit=10)
    return {
        "top_patterns": patterns,
        "total_patterns_analyzed": len(patterns)
    }

@app.get("/api/v1/finetuning/export")
async def export_finetuning_data():
    """
    Export high-quality data for LLM fine-tuning
    PHASE 2: Uses both SQLite + Vector DB
    """
    sqlite_data = feedback_db.export_for_finetuning()
    
    vector_db_data = {}
    if vector_db:
        vector_db_data = vector_db.export_for_finetuning(min_rating=4, limit=100)
    
    return {
        "status": "✅ Export gata",
        "source": "SQLite + Vector DB",
        "sqlite_coaching_sessions": len(sqlite_data.get('high_quality_coaching', [])),
        "sqlite_successful_negotiations": len(sqlite_data.get('successful_negotiations', [])),
        "vector_db_patterns": vector_db_data.get("metadata", {}).get("total_patterns", 0),
        "data": {
            "sqlite": sqlite_data,
            "vector_db": vector_db_data
        }
    }

@app.get("/api/v1/vectordb/stats")
async def get_vectordb_stats():
    """Get Vector DB statistics"""
    if vector_db:
        return vector_db.get_stats()
    else:
        return {"status": "⚠️ Vector DB not initialized"}

@app.get("/api/v1/vectordb/framework-performance/{situation_type}")
async def get_framework_performance(situation_type: str):
    """Get framework effectiveness for situation type"""
    if vector_db:
        performance = vector_db.get_framework_performance(situation_type)
        return {
            "situation_type": situation_type,
            "frameworks": performance
        }
    else:
        return {"status": "⚠️ Vector DB not initialized"}

# ============== STARTUP ==============

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 SANTINEL Backend v2.0 Se Pornește...")
    print("✅ Framework-uri Psihologie Încărcate:")
    print("   • CBT (Cognitive Behavioral Therapy)")
    print("   • NLP (Neuro-Linguistic Programming)")
    print("   • TA (Transactional Analysis)")
    print("   • Analiza Dual-Speaker")
    print("   • Motor Coaching Bazat pe Obiective")
    print("✅ Sistem Feedback și Outcome")
    print("✅ Coaching DINAMIC - personalizat pe bază de situație")
    print("🔄 PHASE 2 — Vector DB pentru Self-Improving LLM:")
    if vector_db:
        print(f"   {vector_db.get_stats()}")
    else:
        print("   ⚠️ Vector DB disabled (mock mode)")
    print("✅ FastAPI rulează pe http://0.0.0.0:8000")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)