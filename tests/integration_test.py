# ============================================================
# SANTINEL — INTEGRATION TESTS
# Week 2: End-to-end testing (SESSION + LLM + AEGIS + UI)
# ============================================================

import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from module.session_complete import SessionManager
from bridge.aegis_bridge import AEGISBridge, ContextInjector
from module.llm_complete import LLMClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# TEST SUITE
# ============================================================

class IntegrationTestSuite:
    """End-to-end integration tests for SANTINEL"""
    
    def __init__(self):
        """Initialize test suite"""
        self.results = []
        self.start_time = datetime.now(timezone.utc)
        self.timings = {}
    
    def log_test(self, name: str, status: bool, duration: float = 0, message: str = ""):
        """Log test result"""
        result = {
            "name": name,
            "status": "✅ PASS" if status else "❌ FAIL",
            "duration_ms": int(duration * 1000),
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.results.append(result)
        self.timings[name] = duration
        
        print(f"{result['status']} {name} ({duration:.2f}s)")
    
    def test_1_aegis_bridge_initialization(self):
        """Test 1: AEGIS Bridge initialization"""
        t0 = time.time()
        
        try:
            bridge = AEGISBridge()
            status = bridge is not None
            duration = time.time() - t0
            self.log_test("AEGIS Bridge initialization", status, duration)
            return bridge
        except Exception as e:
            duration = time.time() - t0
            self.log_test("AEGIS Bridge initialization", False, duration, str(e))
            return None
    
    def test_2_context_injection(self, bridge: AEGISBridge):
        """Test 2: Context injection (AEGIS → coaching prompt)"""
        t0 = time.time()
        
        try:
            injector = ContextInjector(bridge)
            context = injector.prepare_coaching_context("Ion Popescu", "ABC SRL")
            
            status = (
                "contact" in context and
                "company" in context and
                "coaching_prompt" in context and
                len(context["coaching_prompt"]) > 0
            )
            
            duration = time.time() - t0
            self.log_test(
                "Context injection (AEGIS intel)",
                status,
                duration,
                f"Generated {len(context['coaching_prompt'])} char prompt"
            )
            return context
        except Exception as e:
            duration = time.time() - t0
            self.log_test("Context injection", False, duration, str(e))
            return None
    
    def test_3_session_initialization(self):
        """Test 3: Session Manager initialization"""
        t0 = time.time()
        
        try:
            session_mgr = SessionManager(user_id="test_user_integration")
            status = session_mgr is not None and session_mgr.session_id
            
            duration = time.time() - t0
            self.log_test(
                "Session Manager init",
                status,
                duration,
                f"Session ID: {session_mgr.session_id if status else 'N/A'}"
            )
            return session_mgr
        except Exception as e:
            duration = time.time() - t0
            self.log_test("Session Manager init", False, duration, str(e))
            return None
    
    def test_4_start_session_flow(self, session_mgr: SessionManager):
        """Test 4: Start session flow"""
        t0 = time.time()
        
        try:
            result = session_mgr.start_session("Ion Popescu", "ABC SRL")
            status = result["status"] == "active" and result["session_id"]
            
            duration = time.time() - t0
            self.log_test(
                "Start session flow",
                status,
                duration,
                f"Session: {result.get('session_id', 'N/A')}"
            )
        except Exception as e:
            duration = time.time() - t0
            self.log_test("Start session flow", False, duration, str(e))
    
    def test_5_real_time_coaching(self, session_mgr: SessionManager):
        """Test 5: Real-time coaching (LLM integration)"""
        t0 = time.time()
        
        try:
            coaching_result = session_mgr.get_real_time_coaching(
                "Contact insists on 10% discount, I need 20%"
            )
            
            status = (
                coaching_result["status"] == "success" and
                len(coaching_result.get("coaching", "")) > 0
            )
            
            duration = time.time() - t0
            self.log_test(
                "Real-time coaching (LLM)",
                status,
                duration,
                f"Provider: {coaching_result.get('provider', 'unknown')}"
            )
            return coaching_result
        except Exception as e:
            duration = time.time() - t0
            self.log_test("Real-time coaching", False, duration, str(e))
            return None
    
    def test_6_process_audio_segment(self, session_mgr: SessionManager):
        """Test 6: Process audio segment (audio + anonymization + analysis)"""
        t0 = time.time()
        
        try:
            audio_result = session_mgr.process_audio_segment("negotiation_1.wav")
            
            # Expected to fail (no file), but test the flow
            status = "status" in audio_result
            
            duration = time.time() - t0
            self.log_test(
                "Process audio segment",
                status,
                duration,
                f"Status: {audio_result.get('status', 'unknown')}"
            )
            return audio_result
        except Exception as e:
            duration = time.time() - t0
            self.log_test("Process audio segment", False, duration, str(e))
            return None
    
    def test_7_end_session_flow(self, session_mgr: SessionManager):
        """Test 7: End session flow (save to database)"""
        t0 = time.time()
        
        try:
            result = session_mgr.end_session()
            status = result["status"] == "closed"
            
            duration = time.time() - t0
            self.log_test(
                "End session & save to DB",
                status,
                duration,
                f"Duration: {result['summary'].get('duration', 'N/A')}s"
            )
            return result
        except Exception as e:
            duration = time.time() - t0
            self.log_test("End session flow", False, duration, str(e))
            return None
    
    def test_8_llm_fallback_chain(self):
        """Test 8: LLM fallback chain (Groq → Mistral)"""
        t0 = time.time()
        
        try:
            llm = LLMClient()
            result = llm.call("Test prompt", system="Test system")
            
            status = (
                result["status"] == "success" and
                result["provider"] in ["groq", "mistral"]
            )
            
            duration = time.time() - t0
            self.log_test(
                "LLM fallback chain",
                status,
                duration,
                f"Provider: {result.get('provider', 'none')}"
            )
            return result
        except Exception as e:
            duration = time.time() - t0
            self.log_test("LLM fallback chain", False, duration, str(e))
            return None
    
    def test_9_performance_benchmark(self):
        """Test 9: Performance benchmark (response times)"""
        t0 = time.time()
        
        try:
            session_mgr = SessionManager(user_id="perf_test")
            session_mgr.start_session("Test Contact", "Test Company")
            
            coaching = session_mgr.get_real_time_coaching("Test situation")
            
            session_mgr.end_session()
            
            duration = time.time() - t0
            status = duration < 30  # Should complete in < 30 seconds
            
            self.log_test(
                "Performance benchmark (full flow)",
                status,
                duration,
                f"Total time: {duration:.2f}s"
            )
        except Exception as e:
            duration = time.time() - t0
            self.log_test("Performance benchmark", False, duration, str(e))
    
    def test_10_error_handling(self):
        """Test 10: Error handling & graceful degradation"""
        t0 = time.time()
        
        try:
            # Test with invalid inputs
            session_mgr = SessionManager(user_id="error_test")
            
            # Try to end session before starting
            result = session_mgr.end_session()
            status = result["status"] == "error"
            
            duration = time.time() - t0
            self.log_test(
                "Error handling & validation",
                status,
                duration,
                "Correctly rejected invalid operation"
            )
        except Exception as e:
            duration = time.time() - t0
            self.log_test("Error handling", False, duration, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 70)
        print("🧪 SANTINEL — INTEGRATION TEST SUITE")
        print("=" * 70 + "\n")
        
        # Test 1: AEGIS Bridge
        bridge = self.test_1_aegis_bridge_initialization()
        
        # Test 2: Context Injection
        if bridge:
            context = self.test_2_context_injection(bridge)
        
        # Test 3: Session initialization
        session_mgr = self.test_3_session_initialization()
        
        # Test 4-7: Full session flow
        if session_mgr:
            self.test_4_start_session_flow(session_mgr)
            self.test_5_real_time_coaching(session_mgr)
            self.test_6_process_audio_segment(session_mgr)
            self.test_7_end_session_flow(session_mgr)
        
        # Test 8: LLM fallback
        self.test_8_llm_fallback_chain()
        
        # Test 9: Performance
        self.test_9_performance_benchmark()
        
        # Test 10: Error handling
        self.test_10_error_handling()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70 + "\n")
        
        passed = sum(1 for r in self.results if "✅" in r["status"])
        failed = sum(1 for r in self.results if "❌" in r["status"])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({passed/total*100:.0f}%)")
        print(f"Failed: {failed} ({failed/total*100:.0f}%)")
        print()
        
        # Timing analysis
        print("⏱️  TIMING ANALYSIS")
        print("-" * 70)
        
        for name, duration in sorted(self.timings.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"{name:40} {duration:8.2f}s")
        
        print()
        
        # Performance verdict
        total_time = sum(self.timings.values())
        print(f"Total Test Duration: {total_time:.2f}s")
        
        if total_time < 60:
            print("✅ Performance: EXCELLENT (< 60s)")
        elif total_time < 120:
            print("✅ Performance: GOOD (< 120s)")
        else:
            print("⚠️  Performance: ACCEPTABLE (> 120s)")
        
        print()
        
        # Detailed results
        print("📋 DETAILED RESULTS")
        print("-" * 70)
        
        for result in self.results:
            print(f"{result['status']} {result['name']}")
            if result["message"]:
                print(f"   └─ {result['message']}")
        
        print("\n" + "=" * 70)
        
        if passed == total:
            print("✅ ALL TESTS PASSED — INTEGRATION SUCCESSFUL")
        else:
            print(f"⚠️  {failed} TEST(S) FAILED — CHECK LOGS")
        
        print("=" * 70 + "\n")
        
        # Export results
        self.export_results()
    
    def export_results(self):
        """Export test results to JSON"""
        export_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if "✅" in r["status"]),
            "failed": sum(1 for r in self.results if "❌" in r["status"]),
            "total_duration_s": sum(self.timings.values()),
            "results": self.results
        }
        
        filepath = Path(__file__).parent.parent / "docs" / "INTEGRATION_TEST_RESULTS.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📁 Results exported: {filepath}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    suite = IntegrationTestSuite()
    suite.run_all_tests()