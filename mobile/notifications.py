#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Firebase Cloud Messaging (FCM) notifications for mobile apps."""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import requests


@dataclass
class NotificationPayload:
    """Push notification content."""
    title: str
    body: str
    notification_type: str  # coaching, alert, update
    data: Dict[str, Any]
    deep_link: Optional[str] = None


@dataclass
class FCMMessage:
    """Firebase Cloud Messaging message."""
    token: str  # Device registration token
    notification: NotificationPayload
    priority: str  # high, normal
    ttl: int  # Time to live in seconds


class FCMNotificationManager:
    """Manage Firebase Cloud Messaging notifications."""

    def __init__(self, server_key: str, project_id: str):
        """Initialize FCM manager.

        Args:
            server_key: Firebase Cloud Messaging server key
            project_id: Firebase project ID
        """
        self.server_key = server_key
        self.project_id = project_id
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        self.device_tokens: Dict[str, str] = {}  # user_id -> device_token

    def register_device(self, user_id: str, device_token: str) -> bool:
        """Register device token for push notifications.

        Args:
            user_id: User ID
            device_token: FCM device registration token
        """
        self.device_tokens[user_id] = device_token
        return True

    def unregister_device(self, user_id: str) -> bool:
        """Unregister device token."""
        if user_id in self.device_tokens:
            del self.device_tokens[user_id]
            return True
        return False

    def send_notification(self, fcm_message: FCMMessage) -> bool:
        """Send push notification via FCM.

        In real implementation, this calls Firebase FCM API.
        For demo, returns True.
        """
        payload = {
            "to": fcm_message.token,
            "priority": fcm_message.priority,
            "time_to_live": fcm_message.ttl,
            "notification": {
                "title": fcm_message.notification.title,
                "body": fcm_message.notification.body,
                "click_action": fcm_message.notification.deep_link or "FLUTTER_NOTIFICATION_CLICK"
            },
            "data": {
                "notification_type": fcm_message.notification.notification_type,
                **fcm_message.notification.data
            }
        }

        headers = {
            "Authorization": f"key={self.server_key}",
            "Content-Type": "application/json"
        }

        try:
            # In real impl: response = requests.post(self.fcm_url, json=payload, headers=headers)
            # For demo: just log and return success
            print(f"[FCM] Sending notification: {fcm_message.notification.title}")
            return True
        except Exception as e:
            print(f"[FCM] Error sending notification: {e}")
            return False

    def send_coaching_alert(self, user_id: str, coaching_insight: Dict[str, Any]) -> bool:
        """Send live coaching alert notification.

        Called when real-time coaching insight is available during call.
        """
        if user_id not in self.device_tokens:
            return False

        notification = NotificationPayload(
            title="Live Coaching Alert",
            body=coaching_insight.get("summary", "New coaching insight available"),
            notification_type="coaching",
            data={
                "situation": coaching_insight.get("situation", ""),
                "personality": coaching_insight.get("personality", ""),
                "confidence": str(coaching_insight.get("confidence", 0)),
                "timestamp": datetime.utcnow().isoformat()
            },
            deep_link="santinel://coaching/live"
        )

        fcm_message = FCMMessage(
            token=self.device_tokens[user_id],
            notification=notification,
            priority="high",
            ttl=300  # 5 minutes
        )

        return self.send_notification(fcm_message)

    def send_call_ready_alert(self, user_id: str) -> bool:
        """Send alert when ready for call."""
        if user_id not in self.device_tokens:
            return False

        notification = NotificationPayload(
            title="Ready to Coach",
            body="Your negotiation call is starting. Tap to begin coaching.",
            notification_type="alert",
            data={
                "event": "call_starting",
                "timestamp": datetime.utcnow().isoformat()
            },
            deep_link="santinel://call/start"
        )

        fcm_message = FCMMessage(
            token=self.device_tokens[user_id],
            notification=notification,
            priority="high",
            ttl=60
        )

        return self.send_notification(fcm_message)

    def send_sync_complete_alert(self, user_id: str, synced_calls: int) -> bool:
        """Send alert when offline calls sync to backend."""
        if user_id not in self.device_tokens:
            return False

        notification = NotificationPayload(
            title="Sync Complete",
            body=f"✓ {synced_calls} call(s) synced successfully",
            notification_type="update",
            data={
                "event": "sync_complete",
                "synced_calls": str(synced_calls),
                "timestamp": datetime.utcnow().isoformat()
            },
            deep_link="santinel://analytics"
        )

        fcm_message = FCMMessage(
            token=self.device_tokens[user_id],
            notification=notification,
            priority="normal",
            ttl=3600
        )

        return self.send_notification(fcm_message)

    def send_script_recommendation(self, user_id: str, script: Dict[str, Any]) -> bool:
        """Send script recommendation during call."""
        if user_id not in self.device_tokens:
            return False

        notification = NotificationPayload(
            title="Script Recommendation",
            body=script.get("summary", "New script available"),
            notification_type="coaching",
            data={
                "script_id": script.get("id", ""),
                "situation": script.get("situation", ""),
                "effectiveness": str(script.get("effectiveness", 0)),
                "timestamp": datetime.utcnow().isoformat()
            },
            deep_link="santinel://scripts"
        )

        fcm_message = FCMMessage(
            token=self.device_tokens[user_id],
            notification=notification,
            priority="high",
            ttl=300
        )

        return self.send_notification(fcm_message)

    def send_batch_notifications(
        self,
        user_ids: List[str],
        notification: NotificationPayload
    ) -> Dict[str, bool]:
        """Send notification to multiple users."""
        results = {}
        for user_id in user_ids:
            if user_id in self.device_tokens:
                fcm_message = FCMMessage(
                    token=self.device_tokens[user_id],
                    notification=notification,
                    priority="normal",
                    ttl=3600
                )
                results[user_id] = self.send_notification(fcm_message)
            else:
                results[user_id] = False

        return results


class NotificationCenter:
    """Centralized notification management for the app."""

    def __init__(self, fcm_manager: FCMNotificationManager):
        self.fcm = fcm_manager
        self.notification_history: List[Dict[str, Any]] = []

    def log_notification(self, user_id: str, notification: NotificationPayload) -> None:
        """Log sent notification for analytics."""
        self.notification_history.append({
            "user_id": user_id,
            "type": notification.notification_type,
            "title": notification.title,
            "timestamp": datetime.utcnow().isoformat()
        })

    def handle_coaching_stream_update(
        self,
        user_id: str,
        coaching_data: Dict[str, Any]
    ) -> bool:
        """Handle real-time coaching stream update."""
        success = self.fcm.send_coaching_alert(user_id, coaching_data)
        if success:
            notification = NotificationPayload(
                title="Live Coaching",
                body=coaching_data.get("summary", ""),
                notification_type="coaching",
                data=coaching_data
            )
            self.log_notification(user_id, notification)

        return success

    def handle_call_start(self, user_id: str) -> bool:
        """Handle call start event."""
        return self.fcm.send_call_ready_alert(user_id)

    def handle_offline_sync(self, user_id: str, synced_calls: int) -> bool:
        """Handle offline sync completion."""
        return self.fcm.send_sync_complete_alert(user_id, synced_calls)

    def handle_script_recommendation(
        self,
        user_id: str,
        script: Dict[str, Any]
    ) -> bool:
        """Handle script recommendation."""
        return self.fcm.send_script_recommendation(user_id, script)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  FIREBASE CLOUD MESSAGING (FCM) DEMO")
    print("="*70 + "\n")

    # Initialize FCM
    fcm = FCMNotificationManager(
        server_key="AAAA1a1a1a:XXXXXXXXXXXX",
        project_id="santinel-mobile"
    )

    # Register devices
    print("1. DEVICE REGISTRATION:")
    fcm.register_device("user_1", "device_token_ios_1")
    fcm.register_device("user_2", "device_token_android_1")
    print("   ✓ Registered 2 devices")

    # Send coaching alert
    print("\n2. LIVE COACHING ALERT:")
    coaching = {
        "situation": "closing",
        "personality": "driver",
        "summary": "Lead showing urgency - respond with directness",
        "confidence": 0.92
    }
    fcm.send_coaching_alert("user_1", coaching)
    print(f"   ✓ Sent coaching alert: {coaching['summary']}")

    # Send call ready alert
    print("\n3. CALL READY ALERT:")
    fcm.send_call_ready_alert("user_1")
    print("   ✓ Sent call start notification")

    # Send script recommendation
    print("\n4. SCRIPT RECOMMENDATION:")
    script = {
        "id": "script_closing_001",
        "situation": "closing",
        "summary": "Try the direct close: 'Let's move forward with...'",
        "effectiveness": 0.87
    }
    fcm.send_script_recommendation("user_2", script)
    print(f"   ✓ Sent script: {script['summary']}")

    # Send sync complete alert
    print("\n5. OFFLINE SYNC ALERT:")
    fcm.send_sync_complete_alert("user_2", 3)
    print("   ✓ Sent sync completion notification")

    # Notification Center
    print("\n6. NOTIFICATION CENTER:")
    center = NotificationCenter(fcm)
    center.handle_coaching_stream_update("user_1", coaching)
    print(f"   ✓ Notification history: {len(center.notification_history)} entries")

    # Batch notifications
    print("\n7. BATCH NOTIFICATIONS:")
    notification = NotificationPayload(
        title="Weekly Tips",
        body="Check out this week's negotiation tips",
        notification_type="update",
        data={"link": "santinel://tips/weekly"}
    )
    results = fcm.send_batch_notifications(["user_1", "user_2"], notification)
    print(f"   ✓ Sent to {sum(1 for v in results.values() if v)}/2 users")

    print("\n" + "="*70 + "\n")
