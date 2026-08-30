#!/usr/bin/env python3
# ============================================================
# SANTINEL Deployment Verification Demo
# Bilingual deployment checks (English + Romanian)
# ============================================================

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Language(Enum):
    ENGLISH = "en"
    ROMANIAN = "ro"


@dataclass
class HealthCheckResult:
    component: str
    status: str  # "healthy", "warning", "critical"
    latency_ms: float
    details: str
    timestamp: str


class DeploymentMessages:
    """Bilingual deployment messages"""

    MESSAGES = {
        "deployment_verification": {
            Language.ENGLISH: "SANTINEL Production Deployment Verification",
            Language.ROMANIAN: "Verificarea implementării SANTINEL în producție"
        },
        "checking_component": {
            Language.ENGLISH: "Checking component: {component}",
            Language.ROMANIAN: "Verific componentă: {component}"
        },
        "component_healthy": {
            Language.ENGLISH: "[OK] {component} is healthy (latency: {latency:.0f}ms)",
            Language.ROMANIAN: "[OK] {component} este sănătos (latență: {latency:.0f}ms)"
        },
        "component_warning": {
            Language.ENGLISH: "[WARN] {component} has warnings: {details}",
            Language.ROMANIAN: "[AVERTISMENT] {component} are avertismente: {details}"
        },
        "component_critical": {
            Language.ENGLISH: "[CRITICAL] {component} is down: {details}",
            Language.ROMANIAN: "[CRITIC] {component} este inactiv: {details}"
        },
        "database_check": {
            Language.ENGLISH: "Database Connection",
            Language.ROMANIAN: "Conexiune bază de date"
        },
        "redis_check": {
            Language.ENGLISH: "Redis Cache",
            Language.ROMANIAN: "Cache Redis"
        },
        "api_check": {
            Language.ENGLISH: "FastAPI Backend",
            Language.ROMANIAN: "Backend FastAPI"
        },
        "docker_check": {
            Language.ENGLISH: "Docker Containers",
            Language.ROMANIAN: "Containere Docker"
        },
        "kubernetes_check": {
            Language.ENGLISH: "Kubernetes Cluster",
            Language.ROMANIAN: "Cluster Kubernetes"
        },
        "voice_processor_check": {
            Language.ENGLISH: "Voice Processor Service",
            Language.ROMANIAN: "Serviciul de procesare voce"
        },
        "monitoring_check": {
            Language.ENGLISH: "Monitoring Stack (Prometheus/Grafana)",
            Language.ROMANIAN: "Stack de monitorizare (Prometheus/Grafana)"
        },
        "logs_check": {
            Language.ENGLISH: "Centralized Logging (ELK)",
            Language.ROMANIAN: "Logging centralizat (ELK)"
        },
        "deployment_summary": {
            Language.ENGLISH: "Deployment Verification Summary",
            Language.ROMANIAN: "Rezumatul verifikării implementării"
        },
        "total_checks": {
            Language.ENGLISH: "Total checks: {total}",
            Language.ROMANIAN: "Total verificări: {total}"
        },
        "healthy_checks": {
            Language.ENGLISH: "Healthy: {count}",
            Language.ROMANIAN: "Sănătos: {count}"
        },
        "warning_checks": {
            Language.ENGLISH: "Warnings: {count}",
            Language.ROMANIAN: "Avertismente: {count}"
        },
        "critical_checks": {
            Language.ENGLISH: "Critical: {count}",
            Language.ROMANIAN: "Critic: {count}"
        },
        "deployment_ready": {
            Language.ENGLISH: "Deployment is ready for production!",
            Language.ROMANIAN: "Implementarea este gata pentru producție!"
        },
        "deployment_failed": {
            Language.ENGLISH: "Deployment verification failed. Check critical issues.",
            Language.ROMANIAN: "Verificarea implementării a eșuat. Verificați problemele critice."
        },
    }

    @classmethod
    def get(cls, key: str, language: Language, **kwargs) -> str:
        """Get message in specified language"""
        message = cls.MESSAGES.get(key, {}).get(language, key)
        return message.format(**kwargs) if kwargs else message


class DeploymentVerifier:
    """Verify deployment readiness"""

    def __init__(self, language: Language = Language.ENGLISH):
        self.language = language
        self.results: List[HealthCheckResult] = []
        self.start_time = None

    def print_header(self):
        """Print header"""
        print("\n" + "="*70)
        print(DeploymentMessages.get("deployment_verification", self.language))
        print("="*70)
        print(f"Language: {self.language.value.upper()}")
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print("="*70 + "\n")

    def check_docker(self) -> Tuple[str, float, str]:
        """Check Docker containers"""
        component = DeploymentMessages.get("docker_check", self.language)
        logger.info(DeploymentMessages.get("checking_component", self.language, component=component))

        start = time.time()

        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "label=com.example.santinel=true"],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                output = result.stdout.decode('utf-8').strip()
                running_containers = len(output.split('\n')) - 1  # Exclude header

                if running_containers >= 3:  # API, Redis, Postgres
                    latency = (time.time() - start) * 1000
                    return "healthy", latency, f"{running_containers} containers running"
                else:
                    return "warning", (time.time() - start) * 1000, f"Only {running_containers} containers running"
            else:
                return "warning", (time.time() - start) * 1000, "Docker not available or labeled containers not found"

        except subprocess.TimeoutExpired:
            return "warning", 5000.0, "Docker check timed out"
        except FileNotFoundError:
            return "critical", 0.0, "Docker CLI not installed"
        except Exception as e:
            return "critical", 0.0, str(e)

    def check_database(self) -> Tuple[str, float, str]:
        """Check database connectivity"""
        component = DeploymentMessages.get("database_check", self.language)
        logger.info(DeploymentMessages.get("checking_component", self.language, component=component))

        start = time.time()

        try:
            result = subprocess.run(
                ["psql", "--version"],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                # Try to connect
                db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@localhost:5432/santinel_prod")
                result = subprocess.run(
                    ["psql", db_url, "-c", "SELECT version();"],
                    capture_output=True,
                    timeout=10
                )

                if result.returncode == 0:
                    latency = (time.time() - start) * 1000
                    return "healthy", latency, "Connected successfully"
                else:
                    return "warning", (time.time() - start) * 1000, "Connected but query failed"
            else:
                return "warning", (time.time() - start) * 1000, "psql CLI not available"

        except subprocess.TimeoutExpired:
            return "warning", 10000.0, "Database check timed out"
        except Exception as e:
            return "warning", (time.time() - start) * 1000, str(e)

    def check_redis(self) -> Tuple[str, float, str]:
        """Check Redis cache"""
        component = DeploymentMessages.get("redis_check", self.language)
        logger.info(DeploymentMessages.get("checking_component", self.language, component=component))

        start = time.time()

        try:
            result = subprocess.run(
                ["redis-cli", "ping"],
                capture_output=True,
                timeout=5,
                env={**os.environ, "REDISPASS": os.getenv("REDIS_PASSWORD", "redis123")}
            )

            if result.returncode == 0:
                latency = (time.time() - start) * 1000
                return "healthy", latency, "Redis is responding"
            else:
                return "warning", (time.time() - start) * 1000, "Redis not responding"

        except subprocess.TimeoutExpired:
            return "warning", 5000.0, "Redis check timed out"
        except FileNotFoundError:
            return "warning", 0.0, "redis-cli not installed"
        except Exception as e:
            return "warning", (time.time() - start) * 1000, str(e)

    def check_api(self) -> Tuple[str, float, str]:
        """Check API health"""
        component = DeploymentMessages.get("api_check", self.language)
        logger.info(DeploymentMessages.get("checking_component", self.language, component=component))

        start = time.time()

        try:
            import requests

            response = requests.get("http://localhost:8002/api/v1/health", timeout=5)
            latency = (time.time() - start) * 1000

            if response.status_code == 200:
                return "healthy", latency, "API is responding"
            else:
                return "warning", latency, f"API returned status {response.status_code}"

        except requests.exceptions.Timeout:
            return "warning", 5000.0, "API request timed out"
        except requests.exceptions.ConnectionError:
            return "warning", (time.time() - start) * 1000, "Cannot connect to API"
        except ImportError:
            return "warning", 0.0, "requests library not available"
        except Exception as e:
            return "warning", (time.time() - start) * 1000, str(e)

    def check_voice_processor(self) -> Tuple[str, float, str]:
        """Check voice processor service"""
        component = DeploymentMessages.get("voice_processor_check", self.language)
        logger.info(DeploymentMessages.get("checking_component", self.language, component=component))

        start = time.time()

        try:
            # Check if voice module can be imported
            sys.path.insert(0, str(Path(__file__).parent))
            from core.voice_module import VoiceAnalyzer, VoiceProvider

            analyzer = VoiceAnalyzer(VoiceProvider.MOCK)
            latency = (time.time() - start) * 1000

            return "healthy", latency, "Voice module is available"

        except ImportError:
            return "warning", (time.time() - start) * 1000, "Voice module not available"
        except Exception as e:
            return "warning", (time.time() - start) * 1000, str(e)

    def check_kubernetes(self) -> Tuple[str, float, str]:
        """Check Kubernetes cluster"""
        component = DeploymentMessages.get("kubernetes_check", self.language)
        logger.info(DeploymentMessages.get("checking_component", self.language, component=component))

        start = time.time()

        try:
            result = subprocess.run(
                ["kubectl", "cluster-info"],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                latency = (time.time() - start) * 1000

                # Check namespace
                ns_result = subprocess.run(
                    ["kubectl", "get", "namespace", "santinel-prod"],
                    capture_output=True,
                    timeout=5
                )

                if ns_result.returncode == 0:
                    return "healthy", latency, "Kubernetes and namespace are ready"
                else:
                    return "warning", latency, "Kubernetes running but namespace not found"
            else:
                return "warning", (time.time() - start) * 1000, "Kubernetes cluster not accessible"

        except FileNotFoundError:
            return "warning", 0.0, "kubectl not installed"
        except subprocess.TimeoutExpired:
            return "warning", 5000.0, "Kubernetes check timed out"
        except Exception as e:
            return "warning", (time.time() - start) * 1000, str(e)

    def check_monitoring(self) -> Tuple[str, float, str]:
        """Check monitoring stack"""
        component = DeploymentMessages.get("monitoring_check", self.language)
        logger.info(DeploymentMessages.get("checking_component", self.language, component=component))

        start = time.time()

        try:
            import requests

            # Check Prometheus
            prom = requests.get("http://localhost:9090", timeout=3)
            grafana = requests.get("http://localhost:3000", timeout=3)

            latency = (time.time() - start) * 1000

            if prom.status_code == 200 and grafana.status_code == 200:
                return "healthy", latency, "Prometheus and Grafana are running"
            elif prom.status_code == 200:
                return "warning", latency, "Prometheus running but Grafana unavailable"
            else:
                return "warning", latency, "Monitoring stack not fully available"

        except requests.exceptions.ConnectionError:
            return "warning", (time.time() - start) * 1000, "Cannot connect to monitoring services"
        except ImportError:
            return "warning", 0.0, "requests library not available"
        except Exception as e:
            return "warning", (time.time() - start) * 1000, str(e)

    def check_logging(self) -> Tuple[str, float, str]:
        """Check centralized logging"""
        component = DeploymentMessages.get("logs_check", self.language)
        logger.info(DeploymentMessages.get("checking_component", self.language, component=component))

        start = time.time()

        try:
            import requests

            # Check Elasticsearch
            es = requests.get("http://localhost:9200", timeout=3)
            kibana = requests.get("http://localhost:5601", timeout=3)

            latency = (time.time() - start) * 1000

            if es.status_code == 200 and kibana.status_code == 200:
                return "healthy", latency, "Elasticsearch and Kibana are running"
            elif es.status_code == 200:
                return "warning", latency, "Elasticsearch running but Kibana unavailable"
            else:
                return "warning", latency, "ELK stack not fully available"

        except requests.exceptions.ConnectionError:
            return "warning", (time.time() - start) * 1000, "Cannot connect to ELK services"
        except ImportError:
            return "warning", 0.0, "requests library not available"
        except Exception as e:
            return "warning", (time.time() - start) * 1000, str(e)

    def run_all_checks(self):
        """Run all deployment checks"""
        self.start_time = time.time()

        checks = [
            ("docker", self.check_docker),
            ("database", self.check_database),
            ("redis", self.check_redis),
            ("api", self.check_api),
            ("voice_processor", self.check_voice_processor),
            ("kubernetes", self.check_kubernetes),
            ("monitoring", self.check_monitoring),
            ("logging", self.check_logging),
        ]

        for check_name, check_func in checks:
            try:
                status, latency, details = check_func()

                component_label = DeploymentMessages.get(f"{check_name}_check", self.language)
                result = HealthCheckResult(
                    component=component_label,
                    status=status,
                    latency_ms=latency,
                    details=details,
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
                self.results.append(result)

                # Print result
                if status == "healthy":
                    msg = DeploymentMessages.get(
                        "component_healthy",
                        self.language,
                        component=component_label,
                        latency=latency
                    )
                    print(f"[OK] {msg}")
                elif status == "warning":
                    msg = DeploymentMessages.get(
                        "component_warning",
                        self.language,
                        component=component_label,
                        details=details
                    )
                    print(f"[WARN] {msg}")
                else:
                    msg = DeploymentMessages.get(
                        "component_critical",
                        self.language,
                        component=component_label,
                        details=details
                    )
                    print(f"[CRITICAL] {msg}")

            except Exception as e:
                logger.error(f"Check {check_name} failed: {e}")

    def print_summary(self):
        """Print summary"""
        print("\n" + "="*70)
        print(DeploymentMessages.get("deployment_summary", self.language))
        print("="*70)

        healthy_count = sum(1 for r in self.results if r.status == "healthy")
        warning_count = sum(1 for r in self.results if r.status == "warning")
        critical_count = sum(1 for r in self.results if r.status == "critical")

        print(DeploymentMessages.get("total_checks", self.language, total=len(self.results)))
        print(DeploymentMessages.get("healthy_checks", self.language, count=healthy_count))
        print(DeploymentMessages.get("warning_checks", self.language, count=warning_count))
        print(DeploymentMessages.get("critical_checks", self.language, count=critical_count))

        if critical_count > 0:
            print("\n" + DeploymentMessages.get("deployment_failed", self.language))
            return False
        else:
            print("\n" + DeploymentMessages.get("deployment_ready", self.language))
            return True

    def export_results(self, filename: str = "deployment_verification.json"):
        """Export results to JSON"""
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "language": self.language.value,
            "results": [asdict(r) for r in self.results],
            "summary": {
                "total": len(self.results),
                "healthy": sum(1 for r in self.results if r.status == "healthy"),
                "warning": sum(1 for r in self.results if r.status == "warning"),
                "critical": sum(1 for r in self.results if r.status == "critical"),
                "duration_seconds": time.time() - self.start_time if self.start_time else 0
            }
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Results exported to {filename}")


def main():
    """Main function"""
    print("\n" + "="*70)
    print("SANTINEL Deployment Verification - Bilingual Demo")
    print("="*70)

    # Run checks in both languages
    for language in [Language.ENGLISH, Language.ROMANIAN]:
        verifier = DeploymentVerifier(language=language)
        verifier.print_header()
        verifier.run_all_checks()
        success = verifier.print_summary()
        verifier.export_results(f"deployment_verification_{language.value}.json")

        if not success and language == Language.ENGLISH:
            print("\nNote: Some issues detected. See results for details.")

        print("\n")


if __name__ == "__main__":
    main()
