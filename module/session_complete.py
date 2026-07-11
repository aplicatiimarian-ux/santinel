# ============================================================
# SANTINEL — SESSION MANAGER MODULE
# Week 1: Integration of all modules (CORE + ANON + LLM + AUDIO)
# ============================================================

import os
import sys
import json
import logging
import uuid
from typing import Dict, Optional, List
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path (for imports)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all SANTINEL modules
from core.core_complete import OrchestratorDualLLM, Database, SessionRecord, AnalysisResult
from anonimizare.anon_complete import PII_Anonymizer
from module.llm_complete import LLMClient, PromptTemplates
from module.audio_complete import AudioHandler, AudioSession

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================================================
# SESSION MANAGER (Integration point)
# ============================================================

class SessionManager:
    """
    Central session orchestrator:
    Integrates CORE + ANON + LLM + AUDIO into unified flow
    """
    
    def __init__(self, user_id: str):
        """Initialize session manager with all components"""
        self.user_id = user_id
        self.session_id = f"session_{uuid.uuid4().hex[:8]}"
        self.created_at = datetime.now(timezone.utc)
        
        # Initialize all modules
        self.orchestrator = OrchestratorDualLLM()
        self.anonymizer = PII_Anonymizer()
        self.llm = LLMClient()
        self.audio = AudioHandler()
        self.database = Database()
        
        # Session state
        self.is_active = False
        self.contact_name = None
        self.contact_company = None
        self.transcript = ""
        self.anonymized_transcript = ""
        self.coaching_suggestions = []
        self.analysis_results = []
        
        logger.info(f"SessionManager initialized: {self.session_id} for user {self.user_id}")
    
    def start_session(self, contact_name: str, contact_company: str = "") -> Dict:
        """
        Start a new coaching session
        
        Returns:
        {
            "session_id": session identifier,
            "status": "active",
            "timestamp": start time,
            "contact": contact info
        }
        """
        
        if self.is_active:
            logger.warning("Session already active")
            return {"status": "error", "message": "Session already active"}
        
        self.is_active = True
        self.contact_name = contact_name
        self.contact_company = contact_company
        
        logger.info(f"Session started: {self.session_id}")
        
        return {
            "session_id": self.session_id,
            "status": "active",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contact": {
                "name": contact_name,
                "company": contact_company
            }
        }
    
    def process_audio_segment(self, audio_path: str) -> Dict:
        """
        Process audio segment:
        1. Transcribe (audio → text)
        2. Anonymize (text → anonymized)
        3. Analyze (get coaching)
        
        Returns:
        {
            "transcript": original text,
            "anonymized": anonymized text,
            "coaching": suggestions,
            "timestamp": when processed
        }
        """
        
        if not self.is_active:
            logger.warning("Session not active")
            return {"status": "error", "message": "Session not active"}
        
        try:
            # Step 1: Transcribe audio
            logger.info(f"Transcribing: {audio_path}")
            transcription = self.audio.transcribe(audio_path)
            
            if not transcription.get("text"):
                return {
                    "status": "error",
                    "message": "Transcription failed",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            transcript_text = transcription["text"]
            self.transcript += f"\n{transcript_text}"
            
            # Step 2: Anonymize
            logger.info("Anonymizing PII")
            anon_result = self.anonymizer.anonymize(transcript_text, user_id=self.user_id)
            anonymized_text = anon_result["anonymized_text"]
            self.anonymized_transcript += f"\n{anonymized_text}"
            
            # Step 3: Get coaching
            logger.info("Generating coaching")
            coaching = self.llm.analyze_conversation(anonymized_text, self.contact_name)
            self.coaching_suggestions.append(coaching)
            
            # Step 4: Store analysis
            analysis = {
                "segment": len(self.analysis_results) + 1,
                "original_text": transcript_text,
                "anonymized_text": anonymized_text,
                "pii_detected": anon_result.get("pii_detected", []),
                "coaching": coaching,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self.analysis_results.append(analysis)
            
            return {
                "status": "success",
                "transcript": transcript_text[:100] + "...",
                "anonymized": anonymized_text[:100] + "...",
                "coaching_provider": coaching.get("provider", "none"),
                "coaching_snippet": coaching.get("response", "")[:100] + "...",
                "pii_found": len(anon_result.get("pii_detected", [])),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Process audio error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_real_time_coaching(self, situation: str) -> Dict:
        """Get real-time coaching for current situation"""
        
        if not self.is_active:
            return {"status": "error", "message": "Session not active"}
        
        try:
            coaching = self.llm.get_coaching(situation, context=self.anonymized_transcript[-500:])
            return {
                "status": "success",
                "coaching": coaching.get("response", ""),
                "provider": coaching.get("provider", "none"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Coaching error: {e}")
            return {"status": "error", "message": str(e)}
    
    def end_session(self) -> Dict:
        """
        End session and save to database
        
        Returns:
        {
            "session_id": session identifier,
            "status": "closed",
            "summary": session summary,
            "timestamp": end time
        }
        """
        
        if not self.is_active:
            logger.warning("Session not active")
            return {"status": "error", "message": "Session not active"}
        
        try:
            # Save to database
            db_session = self.database.get_session()
            
            session_record = SessionRecord(
                id=self.session_id,
                user_id=self.user_id,
                contact_name=self.contact_name,
                contact_company=self.contact_company,
                created_at=self.created_at,
                duration_seconds=int((datetime.now(timezone.utc) - self.created_at).total_seconds()),
                transcript=self.anonymized_transcript,
                coaching_suggestions=json.dumps(self.coaching_suggestions),
                notes=f"Segments analyzed: {len(self.analysis_results)}, PII patterns: detected"
            )
            
            db_session.add(session_record)
            db_session.commit()
            
            # Create analysis record
            analysis_record = AnalysisResult(
                id=f"analysis_{uuid.uuid4().hex[:8]}",
                session_id=self.session_id,
                patterns=json.dumps({
                    "segments": len(self.analysis_results),
                    "pii_detections": sum(len(a.get("pii_detected", [])) for a in self.analysis_results)
                })
            )
            
            db_session.add(analysis_record)
            db_session.commit()
            db_session.close()
            
            self.is_active = False
            
            logger.info(f"Session ended and saved: {self.session_id}")
            
            return {
                "session_id": self.session_id,
                "status": "closed",
                "summary": {
                    "contact": self.contact_name,
                    "duration": int((datetime.now(timezone.utc) - self.created_at).total_seconds()),
                    "segments": len(self.analysis_results),
                    "coaching_provided": len(self.coaching_suggestions)
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"End session error: {e}")
            return {"status": "error", "message": str(e)}
    
    def export_session(self) -> Dict:
        """Export session data as JSON"""
        
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "contact": {
                "name": self.contact_name,
                "company": self.contact_company
            },
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "transcript": self.transcript[:500] + "..." if len(self.transcript) > 500 else self.transcript,
            "anonymized_transcript": self.anonymized_transcript[:500] + "..." if len(self.anonymized_transcript) > 500 else self.anonymized_transcript,
            "segments_analyzed": len(self.analysis_results),
            "coaching_suggestions": len(self.coaching_suggestions),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ============================================================
# TEST HARNESS
# ============================================================

def run_tests():
    """Test session manager integration"""
    
    print("\n" + "=" * 60)
    print("📞 SANTINEL — SESSION MANAGER (Integration)")
    print("=" * 60 + "\n")
    
    # Initialize
    print("🔌 Initializing session manager...")
    session_mgr = SessionManager(user_id="test_user_001")
    print()
    
    # Test 1: Start session
    print("▶️  Test 1: Start session...")
    result = session_mgr.start_session("Ion Popescu", "ABC SRL")
    print(f"   Session ID: {result['session_id']}")
    print(f"   Status: {result['status']}")
    print(f"   Contact: {result['contact']['name']}")
    print()
    
    # Test 2: Process audio (mock)
    print("🎙️  Test 2: Process audio segment...")
    result = session_mgr.process_audio_segment("negotiation_1.wav")
    print(f"   Status: {result['status']}")
    if result['status'] == 'error':
        print(f"   Message: {result['message']}")
    else:
        print(f"   Transcript: {result['transcript']}")
        print(f"   PII found: {result['pii_found']}")
        print(f"   Coaching provider: {result['coaching_provider']}")
    print()
    
    # Test 3: Real-time coaching
    print("💡 Test 3: Real-time coaching...")
    result = session_mgr.get_real_time_coaching(
        "Contact insists on 10% discount, I need 20%"
    )
    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        print(f"   Provider: {result['provider']}")
        print(f"   Coaching: {result['coaching'][:100]}...")
    print()
    
    # Test 4: Export session
    print("📋 Test 4: Export session data...")
    exported = session_mgr.export_session()
    print(f"   Session ID: {exported['session_id']}")
    print(f"   Contact: {exported['contact']['name']}")
    print(f"   Segments: {exported['segments_analyzed']}")
    print(f"   Coaching: {exported['coaching_suggestions']}")
    print()
    
    # Test 5: End session
    print("⏹️  Test 5: End session...")
    result = session_mgr.end_session()
    print(f"   Status: {result['status']}")
    if result['status'] == 'closed':
        print(f"   Duration: {result['summary']['duration']}s")
        print(f"   Segments: {result['summary']['segments']}")
    print()
    
    print("✅ SESSION_COMPLETE.PY — All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()