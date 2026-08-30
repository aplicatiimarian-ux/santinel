# ============================================================
# SANTINEL — SENTRY ERROR TRACKING CONFIGURATION
# ============================================================

import os
import logging
from typing import Optional
from datetime import datetime, timezone
import json

# Sentry SDK (optional dependency)
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlAlchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

logger = logging.getLogger(__name__)


class SentryConfig:
    """Sentry error tracking configuration"""

    def __init__(self):
        self.dsn = os.getenv("SENTRY_DSN")
        self.enabled = bool(self.dsn) and SENTRY_AVAILABLE
        self.environment = os.getenv("APP_ENV", "development")
        self.version = os.getenv("APP_VERSION", "1.0.0")
        self.debug = os.getenv("DEBUG", "False") == "True"

    def initialize(self):
        """Initialize Sentry SDK"""
        if not self.enabled:
            logger.info("Sentry error tracking disabled (no DSN configured)")
            return

        if not SENTRY_AVAILABLE:
            logger.warning("Sentry SDK not installed. Error tracking unavailable.")
            return

        try:
            sentry_sdk.init(
                dsn=self.dsn,
                integrations=[
                    FastApiIntegration(),
                    SqlAlchemyIntegration(),
                    RedisIntegration(),
                ],
                environment=self.environment,
                release=f"santinel@{self.version}",
                debug=self.debug,
                traces_sample_rate=0.1,  # 10% of transactions
                profiles_sample_rate=0.1 if self.environment == "production" else 1.0,
                attach_stacktrace=True,
                max_breadcrumbs=50,
                include_local_variables=not self.environment == "production",
            )

            logger.info(
                f"Sentry initialized (env={self.environment}, traces_sample_rate=0.1)"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")

    def set_user(self, user_id: str, email: Optional[str] = None):
        """Set current user context"""
        if not self.enabled:
            return

        try:
            sentry_sdk.set_user({
                "id": user_id,
                "email": email,
            })
        except Exception as e:
            logger.debug(f"Failed to set Sentry user: {e}")

    def set_tag(self, key: str, value: str):
        """Set a tag for categorization"""
        if not self.enabled:
            return

        try:
            sentry_sdk.set_tag(key, value)
        except Exception as e:
            logger.debug(f"Failed to set Sentry tag: {e}")

    def set_context(self, name: str, context: dict):
        """Set detailed context information"""
        if not self.enabled:
            return

        try:
            sentry_sdk.set_context(name, context)
        except Exception as e:
            logger.debug(f"Failed to set Sentry context: {e}")

    def add_breadcrumb(self, message: str, category: str = "default", level: str = "info"):
        """Add breadcrumb for debugging"""
        if not self.enabled:
            return

        try:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                timestamp=datetime.now(timezone.utc)
            )
        except Exception as e:
            logger.debug(f"Failed to add Sentry breadcrumb: {e}")

    def capture_exception(self, exception: Exception, **kwargs):
        """Manually capture an exception"""
        if not self.enabled:
            return None

        try:
            return sentry_sdk.capture_exception(exception)
        except Exception as e:
            logger.debug(f"Failed to capture Sentry exception: {e}")
            return None

    def capture_message(self, message: str, level: str = "info", **kwargs):
        """Manually capture a message"""
        if not self.enabled:
            return None

        try:
            return sentry_sdk.capture_message(message, level=level)
        except Exception as e:
            logger.debug(f"Failed to capture Sentry message: {e}")
            return None


class ErrorMetrics:
    """Error tracking metrics"""

    def __init__(self):
        self.errors_by_type = {}
        self.errors_by_endpoint = {}
        self.errors_by_hour = {}

    def record_error(self, error_type: str, endpoint: str = "unknown"):
        """Record an error occurrence"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:00")

        # By type
        if error_type not in self.errors_by_type:
            self.errors_by_type[error_type] = 0
        self.errors_by_type[error_type] += 1

        # By endpoint
        key = f"{error_type}:{endpoint}"
        if key not in self.errors_by_endpoint:
            self.errors_by_endpoint[key] = 0
        self.errors_by_endpoint[key] += 1

        # By hour
        if timestamp not in self.errors_by_hour:
            self.errors_by_hour[timestamp] = 0
        self.errors_by_hour[timestamp] += 1

    def get_summary(self) -> dict:
        """Get error summary"""
        return {
            "total_errors": sum(self.errors_by_type.values()),
            "errors_by_type": self.errors_by_type,
            "top_errors": sorted(
                self.errors_by_type.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "errors_by_hour": self.errors_by_hour,
            "endpoint_errors": sorted(
                self.errors_by_endpoint.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
        }

    def export_metrics(self) -> str:
        """Export metrics as JSON"""
        return json.dumps(self.get_summary(), indent=2, default=str)


# Global instances
sentry_config = SentryConfig()
error_metrics = ErrorMetrics()


def setup_error_tracking():
    """Initialize error tracking"""
    sentry_config.initialize()
    logger.info("Error tracking setup complete")


if __name__ == "__main__":
    # Test configuration
    logging.basicConfig(level=logging.INFO)
    setup_error_tracking()

    # Test metrics
    error_metrics.record_error("ValueError", "/api/v1/sessions")
    error_metrics.record_error("KeyError", "/api/v1/coaching")
    error_metrics.record_error("ValueError", "/api/v1/sessions")

    summary = error_metrics.get_summary()
    print(json.dumps(summary, indent=2))
