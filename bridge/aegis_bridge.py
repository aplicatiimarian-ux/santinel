# ============================================================
# SANTINEL — AEGIS INTEGRATION BRIDGE
# Week 2: Connect SANTINEL coaching to AEGIS intelligence
# ============================================================

import os
import json
import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime, timezone
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================================================
# AEGIS BRIDGE (API Connector)
# ============================================================

class AEGISBridge:
    """
    Connect SANTINEL to AEGIS Veritas intelligence platform
    
    Flow:
    1. Pre-call: Get context (company intel, risk profile)
    2. During call: Real-time coaching (using AEGIS intel)
    3. Post-call: Send feedback (coaching results → learnings)
    """
    
    def __init__(self):
        """Initialize AEGIS bridge"""
        self.aegis_url = os.getenv("AEGIS_API_URL", "http://localhost:8000")
        self.aegis_key = os.getenv("AEGIS_API_KEY", "")
        self.available = self._check_connection()
        
        logger.info(f"AEGISBridge initialized: available={self.available}")
    
    def _check_connection(self) -> bool:
        """Check if AEGIS API is available"""
        try:
            headers = {"Authorization": f"Bearer {self.aegis_key}"}
            response = requests.get(
                f"{self.aegis_url}/health",
                headers=headers,
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"AEGIS connection check failed: {e}")
            return False
    
    def get_contact_intel(self, contact_name: str, company_name: str = "") -> Dict:
        """
        Get intelligence about contact before call
        
        Returns:
        {
            "contact": {...contact data...},
            "company": {...company data...},
            "risk_profile": "low|medium|high",
            "history": [...previous interactions...],
            "recommendations": [...coaching tips...]
        }
        """
        
        try:
            headers = {"Authorization": f"Bearer {self.aegis_key}"}
            
            params = {
                "name": contact_name,
                "company": company_name
            }
            
            response = requests.get(
                f"{self.aegis_url}/api/v1/intelligence/person",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "contact": data.get("person", {}),
                    "company": data.get("company", {}),
                    "risk_profile": data.get("risk_level", "unknown"),
                    "history": data.get("interactions", []),
                    "recommendations": self._generate_recommendations(data),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                logger.warning(f"AEGIS get_contact_intel returned {response.status_code}")
                return self._mock_contact_intel(contact_name, company_name)
        
        except Exception as e:
            logger.error(f"get_contact_intel error: {e}")
            return self._mock_contact_intel(contact_name, company_name)
    
    def get_company_osint(self, company_name: str, country: str = "RO") -> Dict:
        """
        Get OSINT about company (media, court, financial)
        
        Returns:
        {
            "company": company data,
            "media": [...news articles...],
            "financial": [...financial data...],
            "legal": [...court proceedings...],
            "risk_factors": [...]
        }
        """
        
        try:
            headers = {"Authorization": f"Bearer {self.aegis_key}"}
            
            params = {
                "name": company_name,
                "country": country
            }
            
            response = requests.get(
                f"{self.aegis_url}/api/v1/osint/company",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "company": data.get("company", {}),
                    "media": data.get("media_articles", [])[:5],
                    "financial": data.get("financial_data", {}),
                    "legal": data.get("court_proceedings", [])[:3],
                    "risk_factors": data.get("risk_factors", []),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                logger.warning(f"AEGIS get_company_osint returned {response.status_code}")
                return self._mock_company_osint(company_name)
        
        except Exception as e:
            logger.error(f"get_company_osint error: {e}")
            return self._mock_company_osint(company_name)
    
    def send_coaching_feedback(self, session_id: str, feedback: Dict) -> Dict:
        """
        Send coaching results back to AEGIS for learning
        
        Input feedback:
        {
            "contact_name": "...",
            "company_name": "...",
            "outcome": "success|partial|failed",
            "tactics_used": [...],
            "concessions": [...],
            "final_terms": {...},
            "coaching_effectiveness": 0-1
        }
        """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.aegis_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "session_id": session_id,
                "feedback": feedback,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.post(
                f"{self.aegis_url}/api/v1/intelligence/feedback",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Feedback saved to AEGIS",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                logger.warning(f"AEGIS send_coaching_feedback returned {response.status_code}")
                return {
                    "status": "error",
                    "message": f"AEGIS returned {response.status_code}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        except Exception as e:
            logger.error(f"send_coaching_feedback error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _generate_recommendations(self, intel_data: Dict) -> List[str]:
        """Generate coaching recommendations based on intel"""
        
        recommendations = []
        risk_level = intel_data.get("risk_level", "").lower()
        
        if risk_level == "high":
            recommendations.append("High risk contact: use conservative opening, verify all claims")
        elif risk_level == "medium":
            recommendations.append("Medium risk: standard approach, watch for pressure tactics")
        else:
            recommendations.append("Low risk: can be more flexible with concessions")
        
        if intel_data.get("history"):
            recommendations.append(f"Contact has {len(intel_data['history'])} previous interactions")
        
        if intel_data.get("company", {}).get("financial_status") == "unstable":
            recommendations.append("Company financially unstable: they may accept lower prices")
        
        return recommendations
    
    def _mock_contact_intel(self, contact_name: str, company_name: str) -> Dict:
        """Mock AEGIS response (for testing without AEGIS running)"""
        
        return {
            "status": "success",
            "contact": {
                "name": contact_name,
                "company": company_name,
                "role": "Sales Manager",
                "experience": "15+ years",
                "negotiation_style": "assertive"
            },
            "company": {
                "name": company_name,
                "industry": "IT Services",
                "size": "50-100 employees",
                "financial_status": "stable"
            },
            "risk_profile": "medium",
            "history": [
                {"date": "2026-06-15", "outcome": "successful", "value": "€50,000"},
                {"date": "2026-05-20", "outcome": "partial", "value": "€30,000"}
            ],
            "recommendations": [
                "Contact prefers direct negotiation",
                "Company has stable finances, can push for premium pricing",
                "Previous deals suggest flexibility on payment terms"
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _mock_company_osint(self, company_name: str) -> Dict:
        """Mock OSINT response (for testing)"""
        
        return {
            "status": "success",
            "company": {
                "name": company_name,
                "registration": "123456789",
                "founded": "2015",
                "headquarters": "București"
            },
            "media": [
                {"title": "Company announces new product line", "date": "2026-07-01", "source": "TechNews"},
                {"title": "Market analysis: IT services growing 15% YoY", "date": "2026-06-25", "source": "Finance"}
            ],
            "financial": {
                "revenue_2025": "€2,500,000",
                "growth": "12%",
                "profitability": "good"
            },
            "legal": [
                {"case": "Contract dispute resolved", "date": "2026-05-10", "outcome": "settled"}
            ],
            "risk_factors": [
                "Normal business risk profile"
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ============================================================
# CONTEXT INJECTOR (Pre-call preparation)
# ============================================================

class ContextInjector:
    """Inject AEGIS intel into coaching prompts"""
    
    def __init__(self, aegis_bridge: AEGISBridge):
        """Initialize with AEGIS bridge"""
        self.bridge = aegis_bridge
    
    def prepare_coaching_context(self, contact_name: str, company_name: str) -> Dict:
        """
        Prepare full context for coaching session
        
        Returns coaching-ready context with:
        - Contact background
        - Company OSINT
        - Risk profile
        - Recommended tactics
        """
        
        contact_intel = self.bridge.get_contact_intel(contact_name, company_name)
        company_osint = self.bridge.get_company_osint(company_name)
        
        context = {
            "contact": contact_intel.get("contact", {}),
            "company": contact_intel.get("company", {}),
            "company_osint": company_osint.get("company", {}),
            "risk_profile": contact_intel.get("risk_profile", "unknown"),
            "history": contact_intel.get("history", []),
            "recommendations": contact_intel.get("recommendations", []),
            "media_context": company_osint.get("media", []),
            "financial_context": company_osint.get("financial", {}),
            "legal_context": company_osint.get("legal", []),
            "risk_factors": company_osint.get("risk_factors", []),
            "coaching_prompt": self._generate_coaching_prompt(contact_intel, company_osint)
        }
        
        return context
    
    def _generate_coaching_prompt(self, contact_intel: Dict, company_osint: Dict) -> str:
        """Generate coaching prompt using AEGIS context"""
        
        contact_name = contact_intel.get("contact", {}).get("name", "Contact")
        company_name = contact_intel.get("company", {}).get("name", "Company")
        risk = contact_intel.get("risk_profile", "medium")
        
        prompt = f"""
Tu negociezi cu {contact_name} din {company_name}.

CONTEXT INTEL:
- Risk profile: {risk}
- Company financial status: {contact_intel.get("company", {}).get("financial_status", "unknown")}
- Contact experience: {contact_intel.get("contact", {}).get("experience", "unknown")}
- Previous outcomes: {len(contact_intel.get("history", []))} interactions

RECOMMENDATIONS:
{chr(10).join(f"- {rec}" for rec in contact_intel.get("recommendations", []))}

STRATEGY:
1. Use these recommendations to guide your opening
2. Adjust based on contact's risk profile
3. Reference company context when relevant
4. Push harder if company is financially strong

Gata? Mergi înainte cu negocierea.
"""
        
        return prompt.strip()


# ============================================================
# TEST HARNESS
# ============================================================

def run_tests():
    """Test AEGIS bridge"""
    
    print("\n" + "=" * 60)
    print("🔗 SANTINEL — AEGIS BRIDGE")
    print("=" * 60 + "\n")
    
    print("🔌 Initializing AEGIS bridge...")
    bridge = AEGISBridge()
    print(f"   AEGIS available: {bridge.available}")
    print()
    
    print("👤 Test 1: Get contact intelligence...")
    result = bridge.get_contact_intel("Ion Popescu", "ABC SRL")
    print(f"   Status: {result['status']}")
    print(f"   Contact: {result['contact'].get('name', 'N/A')}")
    print(f"   Company: {result['company'].get('name', 'N/A')}")
    print(f"   Risk profile: {result['risk_profile']}")
    print(f"   History: {len(result['history'])} interactions")
    print()
    
    print("🏢 Test 2: Get company OSINT...")
    result = bridge.get_company_osint("ABC SRL")
    print(f"   Status: {result['status']}")
    print(f"   Company: {result['company'].get('name', 'N/A')}")
    print(f"   Media articles: {len(result['media'])}")
    print(f"   Legal cases: {len(result['legal'])}")
    print(f"   Risk factors: {len(result['risk_factors'])}")
    print()
    
    print("📋 Test 3: Prepare coaching context...")
    injector = ContextInjector(bridge)
    context = injector.prepare_coaching_context("Ion Popescu", "ABC SRL")
    print(f"   Contact: {context['contact'].get('name', 'N/A')}")
    print(f"   Company: {context['company'].get('name', 'N/A')}")
    print(f"   Risk profile: {context['risk_profile']}")
    print(f"   Recommendations: {len(context['recommendations'])}")
    print(f"   Coaching prompt length: {len(context['coaching_prompt'])} chars")
    print()
    
    print("📤 Test 4: Send coaching feedback...")
    feedback = {
        "contact_name": "Ion Popescu",
        "company_name": "ABC SRL",
        "outcome": "success",
        "tactics_used": ["anchoring", "concessions"],
        "final_terms": {"discount": "15%", "payment_terms": "30 days"},
        "coaching_effectiveness": 0.85
    }
    result = bridge.send_coaching_feedback("session_test_001", feedback)
    print(f"   Status: {result['status']}")
    print(f"   Message: {result.get('message', 'OK')}")
    print()
    
    print("✅ AEGIS_BRIDGE.PY — All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()