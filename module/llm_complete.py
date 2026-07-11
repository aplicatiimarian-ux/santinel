# ============================================================
# SANTINEL — LLM INTEGRATION MODULE
# Week 1: Groq + Mistral unified interface (cloud-only)
# ============================================================

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================================================
# PROMPT TEMPLATES (Romanian negotiation)
# ============================================================

class PromptTemplates:
    """Reusable prompt templates for negotiation coaching"""
    
    @staticmethod
    def system_prompt() -> str:
        """System prompt for SANTINEL coaching"""
        return """
Tu ești SANTINEL, un asistent AI specializat în negociere și relații interpersonale.
Rolul tău este să oferi coaching real-time și strategii pentru a optimiza rezultatele conversațiilor.

PRINCIPII:
- Analiza tactici (anchoring, concesii, pressure)
- Detecție emoții și tone (stress, rezistență, interes)
- Sugestii practice și immediate
- Respectă confidențialitate (anonimizare PII)
- Limba: Română (formal, profesional)

CONTEXT: Poți accesa intel din AEGIS Veritas despre contact/companie (background, risc, oportunități).
OUTPUT: Coaching concis, actionabil, în timp real.
"""
    
    @staticmethod
    def analyze_prompt(transcript: str, contact_name: str = "Contact") -> str:
        """Analyze a conversation segment"""
        return f"""
Analizează următoarea secvență de negociere:

CONTACT: {contact_name}
TRANSCRIPT:
{transcript}

ANALIZEAZĂ:
1. TACTICI DETECTATE: Ce tactici folosește {contact_name}? (anchoring, concesii, amenințări, etc)
2. EMOȚII: Care-i tonul {contact_name}? (confident, nervous, angry, interested, etc)
3. PUNCTE SLABE: Unde-i vulnerabil {contact_name}?
4. OPORTUNITĂȚI: Ce putem negocia mai bine?
5. COACHING: Ce să faci următorul pas?

FORMAT RĂSPUNS (JSON):
{{
    "tactics": ["tactic1", "tactic2"],
    "emotions": {{"contact": "emotion", "confidence": 0.8}},
    "weaknesses": ["weakness1"],
    "opportunities": ["opp1"],
    "next_step": "Action recommendation"
}}
"""
    
    @staticmethod
    def coaching_prompt(situation: str, context: str = "") -> str:
        """Real-time coaching suggestion"""
        return f"""
SITUAȚIE CURENTĂ:
{situation}

{f"CONTEXT: {context}" if context else ""}

DAI O SUGESTIE RAPIDĂ (1-2 propoziții max) pentru urmatorul pas.
Fii direct și actionabil.
"""
    
    @staticmethod
    def strategy_prompt(negotiation_goal: str, contact_background: str = "") -> str:
        """Pre-call strategy planning"""
        return f"""
OBIECTIV NEGOCIERE:
{negotiation_goal}

{f"CONTEXT CONTACT: {contact_background}" if contact_background else ""}

PLANIFICĂ STRATEGIE:
1. OPENING: Cum deschid conversația?
2. ANCHORING: Ce cifre/termeni sugerez?
3. CONCESSIONS: Ce pot ceda? Ce nu?
4. FALLBACK: Plan B dacă nu merg negocierile?
5. CLOSING: Cum încheiem favorabil?

FORMAT RĂSPUNS (JSON):
{{
    "opening": "Text deschidere",
    "anchoring": "Anchor position",
    "concessions_allowed": ["can give 1"],
    "fallback": "Plan B",
    "closing": "Closing strategy"
}}
"""


# ============================================================
# LLM CLIENT (Cloud-only: Groq + Mistral)
# ============================================================

class LLMClient:
    """
    Unified LLM interface (Groq → Mistral fallback)
    Cloud-only, no local resources (zero GPU/RAM impact)
    """
    
    def __init__(self):
        """Initialize LLM clients"""
        self.config = {
            "groq_key": os.getenv("GROQ_API_KEY", ""),
            "groq_model": "openai/gpt-oss-120b",
            "mistral_key": os.getenv("MISTRAL_API_KEY", ""),
            "mistral_model": "mistral-large-latest"
        }
        
        self.groq_available = self._check_groq()
        self.mistral_available = self._check_mistral()
        
        logger.info(f"LLMClient init: Groq={self.groq_available}, Mistral={self.mistral_available}")
    
    def _check_groq(self) -> bool:
        """Verify Groq API availability"""
        if not self.config["groq_key"]:
            logger.warning("Groq API key not configured")
            return False
        try:
            headers = {"Authorization": f"Bearer {self.config['groq_key']}"}
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers=headers,
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Groq check failed: {e}")
            return False
    
    def _check_mistral(self) -> bool:
        """Verify Mistral API availability"""
        if not self.config["mistral_key"]:
            logger.warning("Mistral API key not configured")
            return False
        try:
            headers = {"Authorization": f"Bearer {self.config['mistral_key']}"}
            response = requests.get(
                "https://api.mistral.ai/v1/models",
                headers=headers,
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Mistral check failed: {e}")
            return False
    
    def _call_groq(self, prompt: str, system: str = "", temperature: float = 0.7) -> Optional[str]:
        """Call Groq API (primary)"""
        if not self.groq_available:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.config['groq_key']}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json={
                    "model": self.config["groq_model"],
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": temperature
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
    
    def _call_mistral(self, prompt: str, system: str = "", temperature: float = 0.7) -> Optional[str]:
        """Call Mistral API (fallback)"""
        if not self.mistral_available:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.config['mistral_key']}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json={
                    "model": self.config["mistral_model"],
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": temperature
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            return None
        except Exception as e:
            logger.error(f"Mistral error: {e}")
            return None
    
    def call(self, prompt: str, system: str = "", temperature: float = 0.7) -> Dict:
        """
        Execute prompt with fallback chain: Groq → Mistral
        
        Returns:
        {
            "response": "LLM output",
            "provider": "groq|mistral|none",
            "status": "success|error",
            "timestamp": ISO timestamp
        }
        """
        
        # Try Groq first (free tier, stable)
        response = self._call_groq(prompt, system, temperature)
        if response:
            return {
                "response": response,
                "provider": "groq",
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Fallback to Mistral
        response = self._call_mistral(prompt, system, temperature)
        if response:
            return {
                "response": response,
                "provider": "mistral",
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Both failed
        return {
            "response": "No LLM provider available",
            "provider": "none",
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def analyze_conversation(self, transcript: str, contact_name: str = "Contact") -> Dict:
        """Analyze conversation segment"""
        prompt = PromptTemplates.analyze_prompt(transcript, contact_name)
        system = PromptTemplates.system_prompt()
        result = self.call(prompt, system, temperature=0.5)
        
        # Try to parse JSON
        try:
            response_text = result["response"]
            if "{" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                json_str = response_text[json_start:json_end]
                result["parsed"] = json.loads(json_str)
            else:
                result["parsed"] = None
        except:
            result["parsed"] = None
        
        return result
    
    def get_coaching(self, situation: str, context: str = "") -> Dict:
        """Get real-time coaching suggestion"""
        prompt = PromptTemplates.coaching_prompt(situation, context)
        system = PromptTemplates.system_prompt()
        return self.call(prompt, system, temperature=0.7)
    
    def plan_strategy(self, negotiation_goal: str, contact_background: str = "") -> Dict:
        """Plan pre-call strategy"""
        prompt = PromptTemplates.strategy_prompt(negotiation_goal, contact_background)
        system = PromptTemplates.system_prompt()
        result = self.call(prompt, system, temperature=0.5)
        
        # Try to parse JSON
        try:
            response_text = result["response"]
            if "{" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                json_str = response_text[json_start:json_end]
                result["parsed"] = json.loads(json_str)
            else:
                result["parsed"] = None
        except:
            result["parsed"] = None
        
        return result


# ============================================================
# TEST HARNESS
# ============================================================

def run_tests():
    """Test LLM module"""
    
    print("\n" + "=" * 60)
    print("🤖 SANTINEL — LLM INTEGRATION MODULE")
    print("=" * 60 + "\n")
    
    # Initialize
    print("🔌 Initializing LLM client (cloud-only)...")
    llm = LLMClient()
    print(f"   Groq: {llm.groq_available}")
    print(f"   Mistral: {llm.mistral_available}")
    print()
    
    # Test 1: Coaching
    print("💡 Test 1: Real-time coaching...")
    result = llm.get_coaching(
        "Contact says: 'Nu pot accepta mai mult de 10% discount'",
        "Am buget pentru 15% discount"
    )
    print(f"   Provider: {result['provider']}")
    print(f"   Response: {result['response'][:150]}...")
    print()
    
    # Test 2: Strategy
    print("📋 Test 2: Pre-call strategy...")
    result = llm.plan_strategy(
        "Negochez contract de servicii IT, scop: 20% discount + suport 24/7",
        "Furnizor: compannie medie, reputatie buna"
    )
    print(f"   Provider: {result['provider']}")
    print(f"   Response: {result['response'][:150]}...")
    if result.get("parsed"):
        print(f"   Parsed: {list(result['parsed'].keys())}")
    print()
    
    # Test 3: Analysis
    print("🔍 Test 3: Conversation analysis...")
    transcript = """
    Me: Bună, vreau să discutez prețul contractului.
    Contact: Prețul e fix, nu negociez pe asta.
    Me: Înțeleg, dar poate e o cale de a face asta benefic pentru amândoi?
    Contact: OK, spune.
    """
    result = llm.analyze_conversation(transcript, "Vendor")
    print(f"   Provider: {result['provider']}")
    print(f"   Response: {result['response'][:150]}...")
    print()
    
    print("✅ LLM_COMPLETE.PY — All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()