# ============================================================
# SANTINEL — PROMETHEUS METRICS CONFIGURATION
# ============================================================

import logging
import time
from typing import Callable, Optional
from datetime import datetime, timezone
import json

# Prometheus client (optional dependency)
try:
    from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
    from prometheus_client import CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Prometheus metrics collection"""

    def __init__(self):
        self.enabled = PROMETHEUS_AVAILABLE

        if not self.enabled:
            logger.info("Prometheus metrics disabled (prometheus_client not installed)")
            return

        # Create registry
        self.registry = CollectorRegistry()

        # Request metrics
        self.request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )

        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request latency in seconds',
            ['method', 'endpoint'],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
            registry=self.registry
        )

        # API metrics
        self.api_errors = Counter(
            'api_errors_total',
            'Total API errors',
            ['endpoint', 'error_type'],
            registry=self.registry
        )

        self.api_latency = Gauge(
            'api_request_latency_ms',
            'API request latency in milliseconds',
            ['endpoint'],
            registry=self.registry
        )

        # Voice module metrics
        self.voice_processes = Counter(
            'voice_processing_total',
            'Total voice processing events',
            ['operation'],
            registry=self.registry
        )

        self.voice_latency = Histogram(
            'voice_latency_seconds',
            'Voice processing latency in seconds',
            ['operation'],
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.3, 0.5, 1.0),
            registry=self.registry
        )

        self.voice_quality = Gauge(
            'voice_quality_score',
            'Voice signal quality score (0-1)',
            ['speaker_type'],
            registry=self.registry
        )

        # Database metrics
        self.db_queries = Counter(
            'db_queries_total',
            'Total database queries',
            ['query_type', 'table'],
            registry=self.registry
        )

        self.db_latency = Histogram(
            'db_query_latency_seconds',
            'Database query latency in seconds',
            ['query_type'],
            registry=self.registry
        )

        self.db_connections = Gauge(
            'db_active_connections',
            'Active database connections',
            registry=self.registry
        )

        # Cache metrics
        self.cache_hits = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_type'],
            registry=self.registry
        )

        self.cache_misses = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_type'],
            registry=self.registry
        )

        # Session metrics
        self.sessions_active = Gauge(
            'sessions_active',
            'Number of active sessions',
            registry=self.registry
        )

        self.sessions_total = Counter(
            'sessions_total',
            'Total sessions created',
            registry=self.registry
        )

        # Coaching metrics
        self.coaching_requests = Counter(
            'coaching_requests_total',
            'Total coaching requests',
            ['framework'],
            registry=self.registry
        )

        self.coaching_latency = Histogram(
            'coaching_latency_seconds',
            'Coaching generation latency in seconds',
            ['framework'],
            registry=self.registry
        )

        # System metrics
        self.errors_total = Counter(
            'errors_total',
            'Total errors',
            ['error_type', 'component'],
            registry=self.registry
        )

        self.queue_size = Gauge(
            'queue_size',
            'Size of processing queue',
            ['queue_type'],
            registry=self.registry
        )

        logger.info("Prometheus metrics initialized")

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request"""
        if not self.enabled:
            return

        self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_api_error(self, endpoint: str, error_type: str):
        """Record API error"""
        if not self.enabled:
            return

        self.api_errors.labels(endpoint=endpoint, error_type=error_type).inc()

    def record_api_latency(self, endpoint: str, latency_ms: float):
        """Record API latency"""
        if not self.enabled:
            return

        self.api_latency.labels(endpoint=endpoint).set(latency_ms)

    def record_voice_processing(self, operation: str, duration: float):
        """Record voice processing event"""
        if not self.enabled:
            return

        self.voice_processes.labels(operation=operation).inc()
        self.voice_latency.labels(operation=operation).observe(duration)

    def set_voice_quality(self, speaker_type: str, score: float):
        """Set voice quality score"""
        if not self.enabled:
            return

        self.voice_quality.labels(speaker_type=speaker_type).set(max(0, min(1, score)))

    def record_db_query(self, query_type: str, table: str, duration: float):
        """Record database query"""
        if not self.enabled:
            return

        self.db_queries.labels(query_type=query_type, table=table).inc()
        self.db_latency.labels(query_type=query_type).observe(duration)

    def set_db_connections(self, count: int):
        """Set active database connections"""
        if not self.enabled:
            return

        self.db_connections.set(count)

    def record_cache_hit(self, cache_type: str):
        """Record cache hit"""
        if not self.enabled:
            return

        self.cache_hits.labels(cache_type=cache_type).inc()

    def record_cache_miss(self, cache_type: str):
        """Record cache miss"""
        if not self.enabled:
            return

        self.cache_misses.labels(cache_type=cache_type).inc()

    def set_active_sessions(self, count: int):
        """Set active sessions count"""
        if not self.enabled:
            return

        self.sessions_active.set(count)

    def record_session_created(self):
        """Record session creation"""
        if not self.enabled:
            return

        self.sessions_total.inc()

    def record_coaching_request(self, framework: str, duration: float):
        """Record coaching request"""
        if not self.enabled:
            return

        self.coaching_requests.labels(framework=framework).inc()
        self.coaching_latency.labels(framework=framework).observe(duration)

    def record_error(self, error_type: str, component: str):
        """Record error"""
        if not self.enabled:
            return

        self.errors_total.labels(error_type=error_type, component=component).inc()

    def set_queue_size(self, queue_type: str, size: int):
        """Set queue size"""
        if not self.enabled:
            return

        self.queue_size.labels(queue_type=queue_type).set(size)

    def get_metrics(self) -> bytes:
        """Get metrics in Prometheus format"""
        if not self.enabled:
            return b""

        return generate_latest(self.registry)

    def get_metrics_text(self) -> str:
        """Get metrics as text"""
        return self.get_metrics().decode('utf-8')


class MetricsMiddleware:
    """FastAPI middleware for metrics collection"""

    def __init__(self, app, metrics: PrometheusMetrics):
        self.app = app
        self.metrics = metrics

    async def __call__(self, request, call_next):
        start = time.time()

        try:
            response = await call_next(request)
        except Exception as e:
            duration = time.time() - start
            self.metrics.record_request(
                request.method,
                request.url.path,
                500,
                duration
            )
            self.metrics.record_error(type(e).__name__, "fastapi")
            raise

        duration = time.time() - start
        self.metrics.record_request(
            request.method,
            request.url.path,
            response.status_code,
            duration
        )

        return response


class PerformanceTracker:
    """Performance tracking utility"""

    def __init__(self, metrics: Optional[PrometheusMetrics] = None):
        self.metrics = metrics
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time and self.metrics:
            duration = time.time() - self.start_time
            return duration
        return 0

    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds"""
        if self.start_time:
            return (time.time() - self.start_time) * 1000
        return 0


# Global metrics instance
metrics = PrometheusMetrics()


def get_metrics() -> PrometheusMetrics:
    """Get global metrics instance"""
    return metrics


def setup_metrics(app):
    """Setup metrics for FastAPI app"""
    if metrics.enabled:
        app.add_middleware(MetricsMiddleware, metrics=metrics)

        @app.get("/metrics")
        async def get_prometheus_metrics():
            return {
                "content": metrics.get_metrics_text(),
                "status": "ok"
            }

        logger.info("Metrics endpoint registered at /metrics")


if __name__ == "__main__":
    # Test metrics
    logging.basicConfig(level=logging.INFO)

    metrics.record_request("GET", "/api/v1/sessions", 200, 0.045)
    metrics.record_request("POST", "/api/v1/coaching", 201, 0.234)
    metrics.record_api_error("/api/v1/login", "AuthenticationError")
    metrics.record_voice_processing("transcription", 0.125)
    metrics.set_voice_quality("confident", 0.92)
    metrics.record_db_query("SELECT", "sessions", 0.012)
    metrics.record_cache_hit("redis")
    metrics.set_active_sessions(42)
    metrics.record_coaching_request("cbt", 0.156)

    print(metrics.get_metrics_text())
