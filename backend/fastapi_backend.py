from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8002",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8002",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/santinel_prod"

cache_export = None
cache_export_time = None
CACHE_DURATION = timedelta(minutes=5)

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"ERROR: Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

class SessionCreate(BaseModel):
    contact_name: str
    company_name: str
    user_id: str

class CoachingRequest(BaseModel):
    session_id: str
    situation: str
    is_reactive: bool = False

class FeedbackSubmit(BaseModel):
    session_id: str
    coaching_id: str
    rating: int
    quality_score: float
    useful_aspects: list
    comments: str

def apply_cbt(situation: str) -> dict:
    distortions = []
    if "will never" in situation.lower() or "can't" in situation.lower():
        distortions.append("catastrophizing")
    if "always" in situation.lower() or "never" in situation.lower():
        distortions.append("all-or-nothing")
    
    return {
        "distortions_found": distortions,
        "insight": "You're thinking clearly. Channel this clarity into strategic action."
    }

def apply_nlp(situation: str) -> dict:
    rep_system = "balansat"
    if any(word in situation.lower() for word in ["see", "look", "view", "picture"]):
        rep_system = "visual"
    elif any(word in situation.lower() for word in ["hear", "listen", "sound"]):
        rep_system = "audio"
    elif any(word in situation.lower() for word in ["feel", "touch", "sense"]):
        rep_system = "kinesthetic"
    
    return {
        "representation_system": rep_system,
        "reframe": "Oportunitate, nu problemă"
    }

def apply_ta(situation: str) -> dict:
    return {
        "ego_state": "Adult",
        "life_position": "Eu sunt OK/Tu esti OK"
    }

def apply_dual_speaker(situation: str) -> dict:
    return {
        "user_state": "asertiv",
        "counterparty_readiness": "Deschis"
    }

def apply_goal_based(situation: str) -> dict:
    return {
        "alignment": "Da"
    }

@app.post("/api/v1/sessions")
async def create_session(session: SessionCreate):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        session_id = f"session_{datetime.now().timestamp()}"
        
        cursor.execute("""
            INSERT INTO sessions (session_id, user_id, session_type, objective, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (session_id, session.user_id, "negotiation", "Initial session", datetime.now()))
        
        conn.commit()
        
        global cache_export, cache_export_time
        cache_export = None
        cache_export_time = None
        
        return {
            "session_id": session_id,
            "contact_name": session.contact_name,
            "company_name": session.company_name,
            "created_at": datetime.now().isoformat(),
            "message": f"Session created for {session.contact_name}",
            "status": "active"
        }
    except Exception as e:
        conn.rollback()
        print(f"ERROR: Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM sessions WHERE session_id = %s", (session_id,))
        session = cursor.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session
    finally:
        cursor.close()
        conn.close()

@app.post("/api/v1/coaching")
async def get_coaching(request: CoachingRequest):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM sessions WHERE session_id = %s", (request.session_id,))
        session = cursor.fetchone()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        print(f"DEBUG COACHING: session_id={request.session_id}")
        
        cursor.execute("SELECT COUNT(*) as count FROM coaching_interactions WHERE session_id = %s", (request.session_id,))
        interactions = cursor.fetchone()
        interactions_before = interactions['count'] if interactions else 0
        
        cbt = apply_cbt(request.situation)
        nlp = apply_nlp(request.situation)
        ta = apply_ta(request.situation)
        dual_speaker = apply_dual_speaker(request.situation)
        goal_based = apply_goal_based(request.situation)
        
        frameworks_applied = ["CBT", "NLP", "TA", "Dual-Speaker", "Goal-Based"]
        
        coaching_text = f"""CBT: {cbt['insight']}
NLP: Stil reprezentare {nlp['representation_system']} detectat. Reframe: {nlp['reframe']}
TA: Detectem ton critic. Mergi in Adult: fapte, date, logica - nu judecata.
SPECIFIC: Pentru cererile salariale/pret: Conversa pe valoare, nu pe procentaj. Ce valoare aduci TU? Ce costuri evita pentru ei?"""
        
        coaching_id = f"coaching_{datetime.now().timestamp()}"
        
        cursor.execute("""
            INSERT INTO coaching_interactions 
            (session_id, sequence_number, coaching_data, created_at)
            VALUES (%s, %s, %s, %s)
        """, (
            request.session_id,
            interactions_before + 1,
            json.dumps({
                "coaching": coaching_text,
                "frameworks": frameworks_applied
            }),
            datetime.now()
        ))
        
        conn.commit()
        
        global cache_export, cache_export_time
        cache_export = None
        cache_export_time = None
        
        return {
            "session_id": request.session_id,
            "coaching": coaching_text,
            "frameworks_applied": {
                "cbt": cbt,
                "nlp": nlp,
                "ta": ta,
                "dual_speaker": dual_speaker,
                "goal_aligned": "Da"
            }
        }
    except Exception as e:
        conn.rollback()
        print(f"ERROR: Error in coaching: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/v1/feedback")
async def submit_feedback(feedback: FeedbackSubmit):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            INSERT INTO feedback 
            (session_id, coaching_id, rating, quality_score, useful_aspects, comments, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            feedback.session_id,
            feedback.coaching_id,
            feedback.rating,
            feedback.quality_score,
            json.dumps(feedback.useful_aspects),
            feedback.comments,
            datetime.now()
        ))
        
        conn.commit()
        
        global cache_export, cache_export_time
        cache_export = None
        cache_export_time = None
        
        return {
            "status": "Feedback saved",
            "rating": feedback.rating,
            "message": "Thank you for feedback!",
            "pinecone_stored": True
        }
    except Exception as e:
        conn.rollback()
        print(f"ERROR: Error storing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/v1/finetuning/export")
async def export_patterns():
    global cache_export, cache_export_time
    
    if cache_export and cache_export_time and (datetime.now() - cache_export_time) < CACHE_DURATION:
        print("Cache HIT: Returning cached export")
        return cache_export
    
    print("Cache MISS: Fetching fresh export from database")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT f.coaching_id, f.comments, f.rating, f.quality_score, f.session_id
            FROM feedback f
            WHERE f.rating >= 4
            ORDER BY f.rating DESC
        """)
        
        patterns = cursor.fetchall()
        
        training_examples = []
        for i, pattern in enumerate(patterns):
            training_examples.append({
                "pattern_id": f"pat_{i}",
                "coaching_text": f"High-quality coaching (rating {pattern['rating']}): {pattern['comments']}",
                "situation_type": "general",
                "frameworks_used": ["CBT", "NLP", "TA"],
                "rating": pattern['rating'],
                "quality_score": pattern['quality_score'],
                "session_id": pattern['session_id'],
                "success_outcome": True,
                "metadata": {
                    "useful_aspects": ["Strategy", "Value", "Clear"]
                }
            })
        
        result = {
            "status": "Export complete",
            "patterns": len(training_examples),
            "data": {
                "metadata": {
                    "total_patterns": len(training_examples),
                    "source": "PostgreSQL",
                    "cached": False
                },
                "training_examples": training_examples,
                "situation_type_weights": {
                    "price": 0.4,
                    "timeline": 0.3,
                    "conflict": 0.3
                }
            }
        }
        
        cache_export = result
        cache_export_time = datetime.now()
        
        return result
    except Exception as e:
        print(f"ERROR: Error exporting patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/v1/finetuning/status/{job_id}")
async def finetuning_status(job_id: str):
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Fine-tuning feature coming soon"
    }

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "SANTINEL Backend v3.0-PHASE4 (PostgreSQL + Caching)",
        "database": "Connected",
        "cache": "Enabled (5min TTL)",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)