#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SANTINEL Mobile Shared Logic
Shared audio, Bluetooth, offline, and sync logic for iOS/Android apps."""

import json
import os
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib


class ConnectionState(Enum):
    """Network connection states."""
    ONLINE = "online"
    OFFLINE = "offline"
    SYNCING = "syncing"


@dataclass
class AudioFile:
    """Audio recording metadata."""
    id: str
    filename: str
    path: str
    duration_seconds: float
    created_at: str  # ISO timestamp
    sample_rate: int  # Hz
    channels: int
    format: str  # m4a, wav


@dataclass
class BluetoothDevice:
    """Bluetooth earpiece metadata."""
    id: str
    name: str
    mac_address: str
    connected: bool
    battery_level: Optional[int]  # 0-100


@dataclass
class OfflineCall:
    """Call recorded in offline mode."""
    id: str
    audio_file: AudioFile
    timestamp: str
    sync_status: str  # pending, synced, failed
    retry_count: int


class AudioManager:
    """Cross-platform audio recording management."""

    def __init__(self, storage_path: str = "./audio_cache"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def start_recording(self) -> AudioFile:
        """Start recording audio session."""
        timestamp = datetime.utcnow().isoformat()
        audio_id = f"audio_{datetime.utcnow().timestamp()}"
        filename = f"{audio_id}.m4a"
        path = os.path.join(self.storage_path, filename)

        audio_file = AudioFile(
            id=audio_id,
            filename=filename,
            path=path,
            duration_seconds=0.0,
            created_at=timestamp,
            sample_rate=16000,
            channels=1,
            format="m4a"
        )

        return audio_file

    def stop_recording(self, audio_file: AudioFile, duration_seconds: float) -> bool:
        """Stop recording and save audio file."""
        try:
            # In real impl, file is saved by OS audio recorder
            # Here we just update metadata
            audio_file.duration_seconds = duration_seconds
            return os.path.exists(audio_file.path)
        except Exception as e:
            print(f"Error stopping recording: {e}")
            return False

    def get_recording(self, audio_id: str) -> Optional[AudioFile]:
        """Get recording by ID."""
        for file in os.listdir(self.storage_path):
            if audio_id in file:
                return AudioFile(
                    id=audio_id,
                    filename=file,
                    path=os.path.join(self.storage_path, file),
                    duration_seconds=0.0,
                    created_at=datetime.utcnow().isoformat(),
                    sample_rate=16000,
                    channels=1,
                    format="m4a"
                )
        return None

    def delete_recording(self, audio_id: str) -> bool:
        """Delete recording after sync."""
        try:
            audio_file = self.get_recording(audio_id)
            if audio_file and os.path.exists(audio_file.path):
                os.remove(audio_file.path)
                return True
        except Exception as e:
            print(f"Error deleting recording: {e}")
        return False

    def list_recordings(self) -> List[AudioFile]:
        """List all local recordings."""
        recordings = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".m4a"):
                path = os.path.join(self.storage_path, filename)
                recordings.append(AudioFile(
                    id=filename.replace(".m4a", ""),
                    filename=filename,
                    path=path,
                    duration_seconds=0.0,
                    created_at=datetime.utcnow().isoformat(),
                    sample_rate=16000,
                    channels=1,
                    format="m4a"
                ))
        return recordings


class BluetoothManager:
    """Cross-platform Bluetooth earpiece management."""

    def __init__(self):
        self.paired_devices: Dict[str, BluetoothDevice] = {}
        self.connected_device: Optional[BluetoothDevice] = None

    def scan_devices(self) -> List[BluetoothDevice]:
        """Scan for available Bluetooth devices."""
        # In real impl, uses iOS/Android BLE APIs
        return list(self.paired_devices.values())

    def connect(self, device_id: str) -> bool:
        """Connect to Bluetooth device."""
        if device_id in self.paired_devices:
            device = self.paired_devices[device_id]
            device.connected = True
            self.connected_device = device
            return True
        return False

    def disconnect(self) -> bool:
        """Disconnect from current device."""
        if self.connected_device:
            self.connected_device.connected = False
            self.connected_device = None
            return True
        return False

    def get_battery_level(self) -> Optional[int]:
        """Get connected device battery level."""
        if self.connected_device:
            return self.connected_device.battery_level
        return None

    def is_connected(self) -> bool:
        """Check if any device is connected."""
        return self.connected_device is not None


class OfflineSyncManager:
    """Manage offline calls and sync when online."""

    def __init__(self, db_path: str = "./offline_sync.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize offline sync database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS offline_calls (
                id TEXT PRIMARY KEY,
                audio_file_id TEXT,
                audio_filename TEXT,
                audio_path TEXT,
                timestamp TEXT,
                sync_status TEXT,
                retry_count INTEGER,
                last_retry TEXT
            )
        """)
        conn.commit()
        conn.close()

    def record_offline_call(self, audio_file: AudioFile) -> OfflineCall:
        """Record a call that was made offline."""
        call_id = f"call_{datetime.utcnow().timestamp()}"
        offline_call = OfflineCall(
            id=call_id,
            audio_file=audio_file,
            timestamp=datetime.utcnow().isoformat(),
            sync_status="pending",
            retry_count=0
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO offline_calls (id, audio_file_id, audio_filename, audio_path, timestamp, sync_status, retry_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            call_id,
            audio_file.id,
            audio_file.filename,
            audio_file.path,
            offline_call.timestamp,
            "pending",
            0
        ))
        conn.commit()
        conn.close()

        return offline_call

    def get_pending_calls(self) -> List[OfflineCall]:
        """Get all calls pending sync."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM offline_calls WHERE sync_status = 'pending'
        """)
        rows = cursor.fetchall()
        conn.close()

        pending_calls = []
        for row in rows:
            pending_calls.append(OfflineCall(
                id=row[0],
                audio_file=AudioFile(
                    id=row[1],
                    filename=row[2],
                    path=row[3],
                    duration_seconds=0.0,
                    created_at=row[4],
                    sample_rate=16000,
                    channels=1,
                    format="m4a"
                ),
                timestamp=row[4],
                sync_status=row[5],
                retry_count=row[6]
            ))

        return pending_calls

    def mark_synced(self, call_id: str) -> bool:
        """Mark a call as successfully synced."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE offline_calls SET sync_status = 'synced' WHERE id = ?
        """, (call_id,))
        conn.commit()
        conn.close()
        return True

    def mark_sync_failed(self, call_id: str) -> bool:
        """Mark a call as failed sync (will retry)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE offline_calls
            SET sync_status = 'pending', retry_count = retry_count + 1, last_retry = ?
            WHERE id = ?
        """, (datetime.utcnow().isoformat(), call_id))
        conn.commit()
        conn.close()
        return True

    def clear_synced_calls(self) -> int:
        """Delete synced calls from local storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM offline_calls WHERE sync_status = 'synced'")
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted


class ConnectionManager:
    """Monitor network connectivity state."""

    def __init__(self):
        self.state = ConnectionState.ONLINE
        self.is_wifi = False
        self.is_cellular = False

    def set_online(self, wifi: bool = True) -> None:
        """Set connection state to online."""
        self.state = ConnectionState.ONLINE
        self.is_wifi = wifi
        self.is_cellular = not wifi

    def set_offline(self) -> None:
        """Set connection state to offline."""
        self.state = ConnectionState.OFFLINE
        self.is_wifi = False
        self.is_cellular = False

    def set_syncing(self) -> None:
        """Set connection state to syncing."""
        self.state = ConnectionState.SYNCING

    def get_state(self) -> ConnectionState:
        """Get current connection state."""
        return self.state

    def is_online(self) -> bool:
        """Check if online."""
        return self.state == ConnectionState.ONLINE


class SyncEngine:
    """Orchestrate offline sync when connectivity returns."""

    def __init__(
        self,
        audio_manager: AudioManager,
        sync_db: OfflineSyncManager,
        connection_mgr: ConnectionManager
    ):
        self.audio_manager = audio_manager
        self.sync_db = sync_db
        self.connection_mgr = connection_mgr
        self.api_base = "http://localhost:8002/api/v1"

    def sync_pending_calls(self, api_key: str) -> Dict[str, Any]:
        """Sync all pending offline calls to backend."""
        if not self.connection_mgr.is_online():
            return {"status": "offline", "synced": 0, "failed": 0}

        self.connection_mgr.set_syncing()
        pending = self.sync_db.get_pending_calls()
        synced_count = 0
        failed_count = 0

        for call in pending:
            try:
                # In real impl, upload audio to backend
                # POST /api/v1/sessions with audio file
                # Then mark as synced
                self.sync_db.mark_synced(call.id)
                synced_count += 1
            except Exception as e:
                print(f"Sync failed for {call.id}: {e}")
                self.sync_db.mark_sync_failed(call.id)
                failed_count += 1

        self.connection_mgr.set_online()
        self.sync_db.clear_synced_calls()

        return {
            "status": "completed",
            "synced": synced_count,
            "failed": failed_count,
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  SANTINEL MOBILE SHARED LOGIC DEMO")
    print("="*60 + "\n")

    # Audio Management
    print("1. AUDIO RECORDING:")
    audio_mgr = AudioManager("./test_audio")
    audio = audio_mgr.start_recording()
    print(f"   ✓ Started recording: {audio.id}")
    audio_mgr.stop_recording(audio, 30.0)
    print(f"   ✓ Stopped recording: {audio.duration_seconds}s")

    # Bluetooth Management
    print("\n2. BLUETOOTH EARPIECE:")
    bt_mgr = BluetoothManager()
    bt_mgr.paired_devices["airpods"] = BluetoothDevice(
        id="airpods",
        name="AirPods Pro",
        mac_address="A1:B2:C3:D4:E5:F6",
        connected=False,
        battery_level=85
    )
    print(f"   ✓ Found device: {bt_mgr.scan_devices()[0].name}")
    bt_mgr.connect("airpods")
    print(f"   ✓ Connected: {bt_mgr.is_connected()}")
    print(f"   ✓ Battery: {bt_mgr.get_battery_level()}%")

    # Offline Sync
    print("\n3. OFFLINE SYNC:")
    sync_db = OfflineSyncManager("./test_offline.db")
    offline_call = sync_db.record_offline_call(audio)
    print(f"   ✓ Recorded offline call: {offline_call.id}")
    pending = sync_db.get_pending_calls()
    print(f"   ✓ Pending calls: {len(pending)}")

    # Connection Management
    print("\n4. CONNECTION STATE:")
    conn_mgr = ConnectionManager()
    print(f"   ✓ Initial state: {conn_mgr.get_state().value}")
    conn_mgr.set_offline()
    print(f"   ✓ Offline: {conn_mgr.get_state().value}")
    conn_mgr.set_online()
    print(f"   ✓ Back online: {conn_mgr.get_state().value}")

    # Sync Engine
    print("\n5. SYNC ENGINE:")
    sync_engine = SyncEngine(audio_mgr, sync_db, conn_mgr)
    result = sync_engine.sync_pending_calls("api_key_123")
    print(f"   ✓ Sync result: {result['status']}")
    print(f"   ✓ Synced: {result['synced']}, Failed: {result['failed']}")

    print("\n" + "="*60 + "\n")
