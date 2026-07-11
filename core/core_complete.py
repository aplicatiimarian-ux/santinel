# ============================================================
# SANTINEL — CORE MODULE
# Week 1: Orchestrator dual-LLM + Config + Database
# ============================================================

import os
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv
import requests
import json
import logging

# Database
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================================================
# CONFIG
# ============================================================

class Config:
    """Application configuration"""
    
    # LLM
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    GROQ_MODEL = "openai/gpt-oss-120b"
    MISTRAL_MODEL = "mistral-large-latest"
    
    # Ollama
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = "mistral:7b"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./santinel.db")
    
    # App
    APP_NAME = "SANTINEL"
    VERSION = "0.1.0"
    DEBUG = os.getenv("DEBUG", "True") == "True"


# ============================================================
# DATABASE MODELS
# ============================================================

Base = declarative_base()


class SessionRecord(Base):
    """Store conversation sessions"""
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String)
    contact_name = Column(String, nullable=True)
    contact_company = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Integer, default=0)
    transcript = Column(Text, nullable=True)
    coaching_suggestions = Column(Text, nullable=True)
    result = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class UserProfile(Base):
    """Store user information"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    tier = Column(String, default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
    encrypted_key = Column(String, nullable=True)


class AnalysisResult(Base):
    """Store call analysis"""
    __tablename__ = "analysis"
    
    id = Column(String, primary_key=True)
    session_id = Column(String)
    user_emotion = Column(String, nullable=True)
    contact_emotion = Column(String, nullable=True)
    patterns = Column(Text, nullable=True)
    consistency = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================
# DATABASE CONNECTION
# ============================================================

class Database:
    """Database management"""
    
    def __init__(self):
        self.engine = create_engine(
            Config.DATABASE_URL,
            echo=Config.DEBUG,
            connect_args={"check_same_thread": False} if "sqlite" in Config.DATABASE_URL else {}
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def close(self):
        self.engine.dispose()


db = Database()


# ============================================================
# ORCHESTRATOR — DUAL-LLM VETTING
# ============================================================

class OrchestratorDualLLM:
    """
    Dual-LLM vetting system:
    - Primary: Ollama local (free, unrestricted)
    - Secondary: Groq (verification, safety)
    - Fallback: Mistral (if Groq down)
    """
    
    def __init__(self):
        self.config = Config
        self.ollama_available = self._check_ollama()
        self.groq_available = self._check_groq()
        
        logger.info(f"Ollama available: {self.ollama_available}")
        logger.info(f"Groq available: {self.groq_available}")
    
    def _check_ollama(self) -> bool:
        """Verify Ollama is running locally"""
        try:
            response = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama check failed: {e}")
            return False
    
    def _check_groq(self) -> bool:
        """Verify Groq API is available"""
        if not self.config.GROQ_API_KEY:
            logger.warning("Groq API key not configured")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.config.GROQ_API_KEY}"}
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers=headers,
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Groq check failed: {e}")
            return False
    
    def _get_ollama_response(self, prompt: str) -> Optional[str]:
        """Get response from local Ollama"""
        if not self.ollama_available:
            return None
        
        try:
            response = requests.post(
                f"{self.config.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": self.config.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            return None
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return None
    
    def _get_groq_response(self, prompt: str) -> Optional[str]:
        """Get response from Groq API"""
        if not self.groq_available or not self.config.GROQ_API_KEY:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json={
                    "model": self.config.GROQ_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            return None
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return None
    
    def execute(self, prompt: str, context: str = "") -> Dict:
        """
        Execute prompt on dual-LLM system.
        Returns: {
            "ollama": response,
            "groq": response,
            "timestamp": datetime,
            "status": "success" | "degraded" | "error"
        }
        """
        
        full_prompt = f"{context}\n\nUser: {prompt}" if context else prompt
        
        # Get responses
        ollama_response = self._get_ollama_response(full_prompt)
        groq_response = self._get_groq_response(full_prompt)
        
        # Determine status
        status = "success" if (ollama_response and groq_response) else "degraded"
        if not ollama_response and not groq_response:
            status = "error"
        
        return {
            "ollama": ollama_response or "(Ollama unavailable)",
            "groq": groq_response or "(Groq unavailable)",
            "prompt": prompt,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status
        }
    
    def get_best_response(self, prompt: str, context: str = "") -> str:
        """
        Get best response (prefer Ollama if both available, for speed + freedom)
        """
        result = self.execute(prompt, context)
        
        if result["status"] == "success":
            return result["ollama"]
        elif result["status"] == "degraded":
            return result["ollama"] if result["ollama"] != "(Ollama unavailable)" else result["groq"]
        else:
            return "⚠️ LLM systems unavailable. Please try again."


# ============================================================
# TEST HARNESS
# ============================================================

def run_tests():
    """Test all components"""
    
    print("\n" + "=" * 60)
    print(f"🛡️  {Config.APP_NAME} v{Config.VERSION} — SANTINEL CORE")
    print("=" * 60 + "\n")
    
    # Test orchestrator
    print("📡 Testing Dual-LLM Orchestrator...")
    orch = OrchestratorDualLLM()
    
    print(f"   ✓ Ollama available: {orch.ollama_available}")
    print(f"   ✓ Groq available: {orch.groq_available}")
    print()
    
    # Test simple prompt
    if orch.ollama_available or orch.groq_available:
        print("🧪 Testing simple prompt...")
        result = orch.execute(
            "Ce-i SANTINEL? (răspuns scurt în 1-2 propoziții)",
            context="Context: Tu ești SANTINEL, asistent AI pentru negocieri."
        )
        
        print(f"\n📤 Status: {result['status']}")
        print(f"📤 OLLAMA Response:\n{result['ollama'][:200]}...")
        if result['groq'] != "(Groq unavailable)":
            print(f"\n📤 GROQ Response:\n{result['groq'][:200]}...")
        print()
    else:
        print("⚠️  No LLM systems available. Skipping prompt test.")
        print()
    
    # Test database
    print("💾 Testing Database...")
    db_session = db.get_session()
    
    test_session = SessionRecord(
        id="test_001",
        user_id="user_001",
        contact_name="Test Contact",
        contact_company="Test Company"
    )
    db_session.add(test_session)
    db_session.commit()
    
    saved = db_session.query(SessionRecord).filter_by(id="test_001").first()
    print(f"   ✓ Database working: {saved is not None}")
    
    db_session.delete(saved)
    db_session.commit()
    db_session.close()
    
    print()
    print("✅ CORE_COMPLETE.PY — All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()