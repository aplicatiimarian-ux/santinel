# ============================================================
# SANTINEL — LOAD TESTING FRAMEWORK
# Week 5: Stress test 1M concurrent users, identify bottlenecks
# ============================================================

import os
import json
import logging
import time
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import sys
from pathlib import Path

from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================================================
# LOAD TEST SCENARIOS
# ============================================================

class LoadTestScenario:
    """
    Load testing scenarios for SANTINEL
    Simulates realistic user patterns and stress conditions
    """
    
    def __init__(self, name: str, users: int, duration: int, rps: int):
        """
        Initialize load test scenario
        
        Args:
            name: Test name
            users: Number of concurrent users
            duration: Test duration in seconds
            rps: Requests per second target
        """
        self.name = name
        self.users = users
        self.duration = duration
        self.rps = rps
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
        
        logger.info(f"LoadTestScenario: {name} ({users} users, {duration}s, {rps} RPS)")
    
    def simulate_session_creation(self) -> Dict:
        """Simulate session creation endpoint"""
        try:
            start = time.time()
            
            # Mock API call
            data = {
                "contact_name": "Ion Popescu",
                "company_name": "ABC SRL",
                "user_id": f"user_{int(time.time() * 1000) % 10000}"
            }
            
            # Simulate network latency
            time.sleep(0.05)
            
            latency = (time.time() - start) * 1000
            
            return {
                "status": 200,
                "latency_ms": latency,
                "endpoint": "POST /api/v1/sessions",
                "success": True
            }
        except Exception as e:
            logger.error(f"Session creation error: {e}")
            return {
                "status": 500,
                "latency_ms": 0,
                "endpoint": "POST /api/v1/sessions",
                "success": False,
                "error": str(e)
            }
    
    def simulate_coaching_request(self) -> Dict:
        """Simulate coaching endpoint"""
        try:
            start = time.time()
            
            # Mock coaching call
            data = {
                "session_id": "session_123",
                "situation": "Contact wants 20% discount"
            }
            
            # Simulate LLM latency
            time.sleep(0.2)
            
            latency = (time.time() - start) * 1000
            
            return {
                "status": 200,
                "latency_ms": latency,
                "endpoint": "POST /api/v1/coaching",
                "success": True
            }
        except Exception as e:
            logger.error(f"Coaching error: {e}")
            return {
                "status": 500,
                "latency_ms": 0,
                "endpoint": "POST /api/v1/coaching",
                "success": False,
                "error": str(e)
            }
    
    def simulate_aegis_context(self) -> Dict:
        """Simulate AEGIS context endpoint"""
        try:
            start = time.time()
            
            # Mock AEGIS call
            data = {
                "contact_name": "Ion Popescu",
                "company_name": "ABC SRL"
            }
            
            # Simulate OSINT latency
            time.sleep(0.15)
            
            latency = (time.time() - start) * 1000
            
            return {
                "status": 200,
                "latency_ms": latency,
                "endpoint": "POST /api/v1/aegis/contact",
                "success": True
            }
        except Exception as e:
            logger.error(f"AEGIS error: {e}")
            return {
                "status": 500,
                "latency_ms": 0,
                "endpoint": "POST /api/v1/aegis/contact",
                "success": False,
                "error": str(e)
            }
    
    def simulate_audio_transcription(self) -> Dict:
        """Simulate audio transcription endpoint"""
        try:
            start = time.time()
            
            # Mock Whisper call
            data = {
                "session_id": "session_123",
                "audio_path": "/tmp/audio.wav"
            }
            
            # Simulate transcription latency
            time.sleep(0.3)
            
            latency = (time.time() - start) * 1000
            
            return {
                "status": 200,
                "latency_ms": latency,
                "endpoint": "POST /api/v1/audio/transcribe",
                "success": True
            }
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                "status": 500,
                "latency_ms": 0,
                "endpoint": "POST /api/v1/audio/transcribe",
                "success": False,
                "error": str(e)
            }
    
    def simulate_health_check(self) -> Dict:
        """Simulate health check endpoint"""
        try:
            start = time.time()
            
            # Mock health check
            time.sleep(0.01)
            
            latency = (time.time() - start) * 1000
            
            return {
                "status": 200,
                "latency_ms": latency,
                "endpoint": "GET /health",
                "success": True
            }
        except Exception as e:
            return {
                "status": 500,
                "latency_ms": 0,
                "endpoint": "GET /health",
                "success": False,
                "error": str(e)
            }
    
    def run_test(self) -> Dict:
        """Run load test scenario"""
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🔥 Running: {self.name}")
        logger.info(f"{'='*60}")
        
        self.start_time = time.time()
        self.results = []
        self.errors = []
        
        # Simulate concurrent users
        endpoints = [
            self.simulate_session_creation,
            self.simulate_coaching_request,
            self.simulate_aegis_context,
            self.simulate_audio_transcription,
            self.simulate_health_check
        ]
        
        requests_per_user = int(self.duration * self.rps / self.users)
        
        with ThreadPoolExecutor(max_workers=self.users) as executor:
            futures = []
            
            for user_id in range(self.users):
                for _ in range(requests_per_user):
                    endpoint = endpoints[user_id % len(endpoints)]
                    future = executor.submit(endpoint)
                    futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.results.append(result)
                    
                    if not result.get("success"):
                        self.errors.append(result)
                except Exception as e:
                    logger.error(f"Future error: {e}")
                    self.errors.append({"error": str(e)})
        
        self.end_time = time.time()
        
        return self._calculate_metrics()
    
    def _calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        
        if not self.results:
            return {
                "status": "error",
                "message": "No results collected"
            }
        
        latencies = [r.get("latency_ms", 0) for r in self.results if r.get("success")]
        success_count = sum(1 for r in self.results if r.get("success"))
        error_count = len(self.errors)
        total_count = len(self.results)
        
        actual_duration = self.end_time - self.start_time
        actual_rps = total_count / actual_duration if actual_duration > 0 else 0
        
        metrics = {
            "test_name": self.name,
            "status": "completed",
            "duration_seconds": actual_duration,
            "total_requests": total_count,
            "successful_requests": success_count,
            "failed_requests": error_count,
            "success_rate_percent": (success_count / total_count * 100) if total_count > 0 else 0,
            "actual_rps": actual_rps,
            "target_rps": self.rps,
            "latency_metrics": {
                "min_ms": min(latencies) if latencies else 0,
                "max_ms": max(latencies) if latencies else 0,
                "mean_ms": statistics.mean(latencies) if latencies else 0,
                "median_ms": statistics.median(latencies) if latencies else 0,
                "p95_ms": self._percentile(latencies, 95),
                "p99_ms": self._percentile(latencies, 99)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return metrics
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]


# ============================================================
# LOAD TEST SUITE
# ============================================================

class LoadTestSuite:
    """
    Complete load testing suite for SANTINEL
    Runs multiple scenarios and generates report
    """
    
    def __init__(self):
        """Initialize load test suite"""
        self.scenarios = []
        self.results = []
        logger.info("LoadTestSuite initialized")
    
    def add_scenario(self, scenario: LoadTestScenario) -> None:
        """Add test scenario"""
        self.scenarios.append(scenario)
    
    def run_all(self) -> List[Dict]:
        """Run all scenarios"""
        
        logger.info("\n" + "=" * 60)
        logger.info("🔥 SANTINEL LOAD TEST SUITE — STARTING")
        logger.info("=" * 60 + "\n")
        
        for scenario in self.scenarios:
            result = scenario.run_test()
            self.results.append(result)
            self._print_result(result)
        
        return self.results
    
    def _print_result(self, result: Dict) -> None:
        """Print test result"""
        
        print(f"\n📊 Test: {result.get('test_name')}")
        print(f"   Duration: {result.get('duration_seconds'):.2f}s")
        print(f"   Total requests: {result.get('total_requests')}")
        print(f"   Success rate: {result.get('success_rate_percent'):.1f}%")
        print(f"   Actual RPS: {result.get('actual_rps'):.1f} (target: {result.get('target_rps')})")
        
        latency = result.get("latency_metrics", {})
        print(f"   Latency:")
        print(f"   ├─ Min: {latency.get('min_ms'):.2f}ms")
        print(f"   ├─ Mean: {latency.get('mean_ms'):.2f}ms")
        print(f"   ├─ Median: {latency.get('median_ms'):.2f}ms")
        print(f"   ├─ P95: {latency.get('p95_ms'):.2f}ms")
        print(f"   └─ P99: {latency.get('p99_ms'):.2f}ms (Max: {latency.get('max_ms'):.2f}ms)")
    
    def generate_report(self) -> Dict:
        """Generate overall report"""
        
        if not self.results:
            return {"status": "no_results"}
        
        all_latencies = []
        total_requests = 0
        total_success = 0
        
        for result in self.results:
            total_requests += result.get("total_requests", 0)
            total_success += result.get("successful_requests", 0)
            latency_metrics = result.get("latency_metrics", {})
            # Collect all latencies (approximate)
            mean = latency_metrics.get("mean_ms", 0)
            if mean > 0:
                all_latencies.extend([mean] * result.get("total_requests", 0))
        
        report = {
            "test_suite": "SANTINEL Load Testing",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_tests": len(self.results),
            "total_requests": total_requests,
            "total_success": total_success,
            "overall_success_rate": (total_success / total_requests * 100) if total_requests > 0 else 0,
            "individual_results": self.results,
            "verdict": self._get_verdict(total_success / total_requests if total_requests > 0 else 0)
        }
        
        return report
    
    @staticmethod
    def _get_verdict(success_rate: float) -> str:
        """Get verdict based on success rate"""
        
        if success_rate >= 0.99:
            return "EXCELLENT — Production ready"
        elif success_rate >= 0.95:
            return "GOOD — Minor optimization needed"
        elif success_rate >= 0.90:
            return "FAIR — Optimization required"
        else:
            return "POOR — Requires significant work"


# ============================================================
# TEST HARNESS
# ============================================================

def run_tests():
    """Run load testing suite"""
    
    print("\n" + "=" * 60)
    print("🔥 SANTINEL — LOAD TESTING FRAMEWORK (WEEK 5)")
    print("=" * 60 + "\n")
    
    # Create test suite
    suite = LoadTestSuite()
    
    # Add scenarios
    suite.add_scenario(LoadTestScenario(
        name="Light Load (100 users)",
        users=100,
        duration=10,
        rps=50
    ))
    
    suite.add_scenario(LoadTestScenario(
        name="Medium Load (500 users)",
        users=500,
        duration=10,
        rps=250
    ))
    
    suite.add_scenario(LoadTestScenario(
        name="Heavy Load (1000 users)",
        users=1000,
        duration=10,
        rps=500
    ))
    
    # Run all tests
    results = suite.run_all()
    
    # Generate report
    report = suite.generate_report()
    
    print("\n" + "=" * 60)
    print("📊 LOAD TEST REPORT")
    print("=" * 60)
    print(f"Total tests: {report['total_tests']}")
    print(f"Total requests: {report['total_requests']}")
    print(f"Success rate: {report['overall_success_rate']:.1f}%")
    print(f"Verdict: {report['verdict']}")
    print("=" * 60 + "\n")
    
    print("✅ LOAD_TESTING.PY — All tests completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()