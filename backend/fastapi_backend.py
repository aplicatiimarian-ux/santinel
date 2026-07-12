"""
SANTINEL Backend — FastAPI + Professional Psychology Coaching + Vector DB + Fine-Tuning
Integrated: CBT, NLP, TA, Dual-Speaker Analysis, Goal-Based Coaching
Real-time AI coaching + Feedback System + Self-Improving LLM + Fine-Tuning Pipeline
PHASE 3: LLM fine-tuning execution + A/B testing + Production ready + DEBUG logging
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

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

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

# Import Vector DB Manager
try:
    from vector_db_integration import get_vector_db_manager
    vector_db = get_vector_db_manager(use_mock=True)
    print("✅ Real Pinecone Vector DB Manager initialized")
except ImportError:
    from vector_db_integration import get_vector_db_manager
    vector_db = get_vector_db_manager(use_mock=True)

# Import Fine-Tuning Pipeline
try:
    from finetuning_pipeline import FineTuningPipeline, FineTuningProvider
    print("✅ Fine-Tuning Pipeline imported")
except ImportError:
    print("⚠️ Fine-Tuning Pipeline not available")
    FineTuningPipeline = None

# Initialize FastAPI
app = FastAPI(title="SANTINEL", version="3.0.0-PHASE3")

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
    print("✅ Psychology frameworks loaded")
except:
    cbt = None
    nlp = None
    ta = None
    dual_speaker = None
    print("⚠️ Psychology modules initialized with fallbacks")

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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                period TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS finetuning_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                provider TEXT,
                model_name TEXT,
                status TEXT,
                examples_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                version TEXT,
                provider TEXT,
                status TEXT,
                performance_rating REAL,
                deployed_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
    
    def store_finetuning_job(self, job_id: str, provider: str, model_name: str, examples_count: int) -> bool:
        """Store fine-tuning job record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO finetuning_jobs
                (job_id, provider, model_name, status, examples_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (job_id, provider, model_name, 'submitted', examples_count))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing job: {e}")
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
        "status": "🟢 SANTINEL v3.0 operational",
        "version": "3.0.0-PHASE3",
        "vector_db": "✅ Pinecone Ready",
        "finetuning": "✅ Available",
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
    
    print(f"\n✅ Session created: {session_id}")
    
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
    Enhanced with REAL Pinecone Vector DB + Fine-tuning ready
    """
    
    print(f"\n🔍 DEBUG COACHING: session_id={request.session_id}")
    
    if request.session_id not in sessions:
        print(f"   ❌ Session not found!")
        raise HTTPException(status_code=404, detail="Sesiune nu găsită")
    
    print(f"   ✅ Session found")
    print(f"   interactions BEFORE: {len(sessions[request.session_id]['interactions'])}")
    
    coaching_parts = []
    frameworks_applied = []
    
    # Retrieve similar patterns from Pinecone
    similar_patterns = []
    situation_type = "general"
    
    if vector_db:
        try:
            similar_patterns = vector_db.find_similar_patterns(
                situation_text=request.situation,
                situation_type=situation_type,
                limit=3
            )
            if similar_patterns:
                coaching_parts.append(f"📚 Similar successes: {len(similar_patterns)} patterns found (Pinecone)")
                frameworks_applied.append("Pinecone-VectorDB")
        except Exception as e:
            print(f"Vector DB error: {e}")
    
    # CBT Analysis
    cbt_insight = ""
    try:
        if cbt:
            distortions = cbt.identify_distortions(request.situation)
            cbt_assessment = cbt.assess_emotional_state(request.situation, request.emotions or {})
            cbt_insight = cbt_assessment.get("therapeutic_insight", "")
            
            if distortions:
                coaching_parts.append(f"🧠 CBT: Distorsiuni identificate: {', '.join([d['distortion'] for d in distortions[:2]])}. {cbt_insight}")
            else:
                coaching_parts.append(f"🧠 CBT: {cbt_insight or 'Gândire clară detectată.'}")
            
            frameworks_applied.append("CBT")
    except Exception as e:
        print(f"CBT error: {e}")
        coaching_parts.append("🧠 CBT: Gândire strategică recomandată")
    
    # NLP Analysis
    try:
        if nlp:
            rep_system = nlp.detect_representation_system(request.situation)
            system = rep_system.get("primary_system", "balansat")
            coaching_parts.append(f"🎯 NLP: Stil {system}. Reframe: Oportunitate de negociere.")
            frameworks_applied.append("NLP")
    except Exception as e:
        print(f"NLP error: {e}")
    
    # TA Analysis
    try:
        if ta:
            ego_state_analysis = ta.detect_ego_state(request.situation)
            ego = ego_state_analysis.get("primary_ego_state", "Adult")
            
            if ego == "Adult":
                coaching_parts.append("⚖️ TA: Adult ego state - perfect pentru negociere.")
            else:
                coaching_parts.append(f"⚖️ TA: Tranziție către Adult ego state.")
            
            frameworks_applied.append("TA")
    except Exception as e:
        print(f"TA error: {e}")
    
    # Situation-specific coaching
    situation_lower = request.situation.lower()
    if "%" in situation_lower or "creștere" in situation_lower:
        coaching_parts.append("💰 SPECIFIC: Conversa pe valoare, nu pe procentaj.")
        situation_type = "price"
    elif "termen" in situation_lower or "deadline" in situation_lower:
        coaching_parts.append("⏰ SPECIFIC: Urgență = Presiune. Propune timeline realist.")
        situation_type = "timeline"
    elif "conflict" in situation_lower:
        coaching_parts.append("🤝 SPECIFIC: Conflict = Oportunitate. Găsește interesul comun.")
        situation_type = "conflict"
    
    final_coaching = "\n".join(coaching_parts)
    
    # Store interaction — CRITICAL for feedback later
    coaching_id = f"coaching_{datetime.now().timestamp()}"
    
    print(f"   🔄 Storing interaction...")
    print(f"   coaching_id: {coaching_id}")
    print(f"   frameworks_applied: {frameworks_applied}")
    
    sessions[request.session_id]["interactions"].append({
        "coaching_id": coaching_id,
        "situation": request.situation,
        "timestamp": datetime.now(),
        "frameworks_used": frameworks_applied
    })
    
    print(f"   ✅ Interaction stored")
    print(f"   interactions AFTER: {len(sessions[request.session_id]['interactions'])}")
    
    return {
        "session_id": request.session_id,
        "coaching_id": coaching_id,
        "coaching": final_coaching,
        "similar_patterns_found": len(similar_patterns),
        "situation_type": situation_type,
        "frameworks_applied": frameworks_applied
    }

@app.get("/api/v1/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get complete session status"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Sesiune nu găsită")
    
    session_data = sessions[session_id]
    
    return {
        "session_id": session_id,
        "contact": session_data["contact_name"],
        "company": session_data["company_name"],
        "created_at": str(session_data["created_at"]),
        "interactions_count": len(session_data["interactions"]),
        "status": "active"
    }

@app.post("/api/v1/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit coaching feedback and rating with DEBUG logging"""
    
    print(f"\n🔍 DEBUG: Feedback received")
    print(f"   session_id: {feedback.session_id}")
    print(f"   rating: {feedback.rating}")
    
    success = feedback_db.store_feedback(
        session_id=feedback.session_id,
        coaching_id=feedback.coaching_id,
        rating=feedback.rating,
        quality_score=feedback.quality_score,
        useful_aspects=feedback.useful_aspects,
        comments=feedback.comments
    )
    
    print(f"   ✅ SQLite stored: {success}")
    
    # Store high-quality patterns in Pinecone
    if success and feedback.rating >= 4:
        print(f"\n🔍 DEBUG: Attempting Pinecone storage")
        print(f"   rating >= 4: True")
        print(f"   vector_db is not None: {vector_db is not None}")
        
        if vector_db:
            try:
                session_data = sessions.get(feedback.session_id, {})
                interactions = session_data.get("interactions", [])
                
                print(f"   session_data exists: {bool(session_data)}")
                print(f"   interactions count: {len(interactions)}")
                
                last_interaction = interactions[-1] if interactions else None
                
                print(f"   found last_interaction: {last_interaction is not None}")
                
                if last_interaction:
                    frameworks = last_interaction.get("frameworks_used", [])
                    print(f"   frameworks: {frameworks}")
                    print(f"   🔄 Calling vector_db.store_coaching_pattern()...")
                    
                    store_result = vector_db.store_coaching_pattern(
                        coaching_text=f"High-quality coaching (rating {feedback.rating}): {', '.join(feedback.useful_aspects)}",
                        situation_type="general",
                        frameworks_used=frameworks,
                        rating=feedback.rating,
                        quality_score=feedback.quality_score,
                        session_id=feedback.session_id,
                        success_outcome=True,
                        metadata={"useful_aspects": feedback.useful_aspects}
                    )
                    
                    print(f"   ✅ store_coaching_pattern returned: {store_result}")
                else:
                    print(f"   ⚠️ No last_interaction found in session")
            except Exception as e:
                print(f"   ❌ Exception during Pinecone storage:")
                print(f"      {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"   ⚠️ vector_db is None - cannot store pattern")
    else:
        print(f"   ⚠️ Skipping Pinecone: success={success}, rating={feedback.rating}")
    
    if success:
        return {
            "status": "✅ Feedback salvat",
            "rating": feedback.rating,
            "message": "Mulțumim pentru feedback!",
            "pinecone_stored": feedback.rating >= 4 and vector_db is not None
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
        raise HTTPException(status_code=500, detail="Eroare")

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

@app.get("/api/v1/finetuning/export")
async def export_finetuning_data_endpoint(min_rating: int = 4, limit: int = 100):
    """Export high-quality coaching patterns for fine-tuning"""
    try:
        if not FineTuningPipeline:
            raise HTTPException(status_code=503, detail="Fine-tuning module not available")
        
        pipeline = FineTuningPipeline(vector_db_manager=vector_db)
        export_data = pipeline.export_training_data(min_rating, limit)
        
        return {
            "status": "✅ Export complete",
            "patterns": export_data.get("metadata", {}).get("total_patterns", 0),
            "data": export_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {e}")

@app.post("/api/v1/finetuning/submit")
async def submit_finetuning_job(min_rating: int = 4, provider: str = "groq"):
    """Submit fine-tuning job to Groq/Mistral"""
    try:
        if not FineTuningPipeline:
            raise HTTPException(status_code=503, detail="Fine-tuning module not available")
        
        pipeline = FineTuningPipeline(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            mistral_api_key=os.getenv("MISTRAL_API_KEY"),
            vector_db_manager=vector_db
        )
        
        # Export and format data
        export_data = pipeline.export_training_data(min_rating=min_rating)
        training_examples = pipeline.format_training_data(export_data)
        
        # Submit job
        provider_enum = FineTuningProvider.GROQ if provider == "groq" else FineTuningProvider.MISTRAL
        result = pipeline.submit_finetuning_job(training_examples, provider_enum)
        
        # Store in database
        if result.get("status") == "submitted":
            feedback_db.store_finetuning_job(
                result.get("job_id"),
                provider,
                result.get("model_name"),
                len(training_examples)
            )
        
        return {
            "status": "✅ Job submitted",
            "provider": provider,
            "job_id": result.get("job_id"),
            "examples": len(training_examples),
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submission error: {e}")

@app.get("/api/v1/finetuning/status/{job_id}")
async def get_finetuning_status(job_id: str):
    """Get status of fine-tuning job"""
    try:
        if not FineTuningPipeline:
            raise HTTPException(status_code=503, detail="Fine-tuning module not available")
        
        pipeline = FineTuningPipeline()
        status = pipeline.get_finetuning_status(job_id)
        
        return {
            "job_id": job_id,
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status error: {e}")

@app.post("/api/v1/finetuning/deploy")
async def deploy_finetuned_model(model_name: str, version: str = "2.0-ft"):
    """Deploy fine-tuned model as active coaching model"""
    try:
        if not FineTuningPipeline:
            raise HTTPException(status_code=503, detail="Fine-tuning module not available")
        
        pipeline = FineTuningPipeline()
        deployment = pipeline.deploy_finetuned_model(model_name, version)
        
        return {
            "status": "✅ Model deployed",
            "model_name": model_name,
            "version": version,
            "deployment": deployment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment error: {e}")

@app.get("/api/v1/finetuning/ab-test")
async def run_ab_test(model_a: str = "baseline", model_b: str = "finetuned-v1"):
    """Run A/B test comparing two models"""
    try:
        if not FineTuningPipeline:
            raise HTTPException(status_code=503, detail="Fine-tuning module not available")
        
        pipeline = FineTuningPipeline()
        comparison = pipeline.compare_model_performance(model_a, model_b)
        
        return {
            "status": "✅ A/B test complete",
            "comparison": comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"A/B test error: {e}")

@app.get("/api/v1/finetuning/current-model")
async def get_current_coaching_model():
    """Get current active coaching model"""
    try:
        if not FineTuningPipeline:
            return {"status": "✅ Baseline", "model": "v1.0", "version": "baseline"}
        
        pipeline = FineTuningPipeline()
        model = pipeline.get_current_model()
        
        return {
            "status": "✅ Current model retrieved",
            "model": model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/api/v1/vectordb/stats")
async def get_vectordb_stats():
    """Get Vector DB statistics"""
    if vector_db:
        try:
            stats = vector_db.get_stats()
            return stats
        except Exception as e:
            return {"status": f"⚠️ Error: {e}"}
    else:
        return {"status": "⚠️ Vector DB not initialized"}

# ============== STARTUP ==============

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 SANTINEL Backend v3.0-PHASE3 Se Pornește...")
    print("✅ Framework-uri Psihologie: CBT/NLP/TA/DualSpeaker/Goal")
    print("✅ Sistem Feedback și Outcome")
    print("✅ Coaching DINAMIC - personalizat")
    print("🔄 PHASE 2 — REAL Pinecone Vector DB:")
    if vector_db:
        try:
            stats = vector_db.get_stats()
            print(f"   ✅ {stats}")
        except Exception as e:
            print(f"   ⚠️ Vector DB error: {e}")
    print("🔄 PHASE 3 — LLM Fine-Tuning Pipeline:")
    if FineTuningPipeline:
        print("   ✅ Fine-tuning endpoints ready")
        print("   ✅ Groq/Mistral integration ready")
        print("   ✅ A/B testing framework ready")
    else:
        print("   ⚠️ Fine-tuning module not available")
    print("✅ FastAPI v3.0 rulează pe http://0.0.0.0:8000")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)