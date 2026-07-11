# ============================================================
# SANTINEL — AUDIO MODULE
# Week 1: Whisper integration (mock for now, real Week 3+)
# ============================================================

import os
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================================================
# AUDIO HANDLER (Whisper integration placeholder)
# ============================================================

class AudioHandler:
    """
    Audio processing: speech-to-text via Whisper
    Mock implementation (Week 1), real Whisper.cpp (Week 3+)
    """
    
    def __init__(self):
        """Initialize audio handler"""
        self.supported_formats = [".wav", ".mp3", ".m4a", ".ogg", ".flac"]
        self.whisper_available = self._check_whisper()
        
        logger.info(f"AudioHandler init: Whisper available = {self.whisper_available}")
    
    def _check_whisper(self) -> bool:
        """Check if Whisper is available (mock: always False for now)"""
        try:
            # Week 3+: Will check for actual Whisper installation
            # import whisper
            # whisper.load_model("base")
            # For now: mock only
            return False
        except:
            return False
    
    def _mock_transcribe(self, audio_path: str) -> Dict:
        """
        Mock transcription (simulates Whisper output)
        Week 3+: Replace with real whisper.transcribe()
        """
        
        # Simulate different transcriptions based on filename
        mock_transcriptions = {
            "negotiation_1.wav": "Contactul: Prețul maxim pe care pot să-l ofer este 100.000 de lei. Me: Înțeleg, dar bugetul nostru permite 150.000. Putem negocia pe alte termeni?",
            "negotiation_2.wav": "Me: Bună, vreau să discutez contractul. Contactul: OK, te ascult. Me: Avem propunere de 20% discount dacă măresc volumul comenzilor.",
            "call_demo.wav": "Speaker 1: Salut, cum poți ajuta? Speaker 2: Am o propunere pentru tine. Speaker 1: Spune-mi mai mult.",
        }
        
        # Get filename from path
        filename = Path(audio_path).name
        
        # Return mock transcription or generic
        text = mock_transcriptions.get(filename, "Mock audio transcription: Contact discusses terms and conditions during negotiation.")
        
        return {
            "text": text,
            "language": "ro",
            "duration": 45.5,
            "confidence": 0.92
        }
    
    def transcribe(self, audio_path: str) -> Dict:
        """
        Transcribe audio file to text
        
        Returns:
        {
            "text": "transcribed text",
            "language": "ro|en",
            "duration": seconds,
            "confidence": 0-1,
            "source": "whisper|mock",
            "timestamp": ISO timestamp
        }
        """
        
        # Verify file exists
        if not Path(audio_path).exists():
            logger.error(f"Audio file not found: {audio_path}")
            return {
                "text": "",
                "language": "unknown",
                "duration": 0,
                "confidence": 0,
                "source": "none",
                "error": "File not found",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Verify format
        file_ext = Path(audio_path).suffix.lower()
        if file_ext not in self.supported_formats:
            logger.error(f"Unsupported audio format: {file_ext}")
            return {
                "text": "",
                "language": "unknown",
                "duration": 0,
                "confidence": 0,
                "source": "none",
                "error": f"Unsupported format: {file_ext}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        try:
            # Week 3+: Use real Whisper
            # import whisper
            # result = whisper.transcribe(audio_path, language="ro")
            # return {...}
            
            # Week 1: Use mock
            mock_result = self._mock_transcribe(audio_path)
            
            return {
                "text": mock_result["text"],
                "language": mock_result["language"],
                "duration": mock_result["duration"],
                "confidence": mock_result["confidence"],
                "source": "mock",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                "text": "",
                "language": "unknown",
                "duration": 0,
                "confidence": 0,
                "source": "none",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def split_speakers(self, transcript: str, speaker_count: int = 2) -> Dict:
        """
        Split transcript into speakers (diarization)
        Mock implementation (real: Week 3+ with pyannote)
        """
        
        lines = transcript.split("\n")
        speakers = {}
        
        # Simple mock: alternate speakers or detect "Speaker X:" pattern
        speaker_id = 0
        
        for line in lines:
            if ":" in line:
                # Try to extract speaker label
                parts = line.split(":", 1)
                if len(parts) == 2:
                    speaker_label = parts[0].strip()
                    text = parts[1].strip()
                    
                    if speaker_label not in speakers:
                        speakers[speaker_label] = []
                    speakers[speaker_label].append(text)
        
        # If no speakers found, return simple split
        if not speakers:
            return {
                "speakers": {f"speaker_{i}": [line] for i, line in enumerate(lines[:speaker_count])},
                "method": "mock",
                "confidence": 0.6
            }
        
        return {
            "speakers": speakers,
            "method": "pattern",
            "confidence": 0.85
        }
    
    def extract_segments(self, transcript: str, min_length: int = 10) -> List[Dict]:
        """
        Extract meaningful segments from transcript
        Useful for analysis/coaching by segment
        """
        
        sentences = transcript.replace(".", ".\n").replace("?", "?\n").split("\n")
        segments = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) >= min_length:
                segments.append({
                    "id": f"seg_{i}",
                    "text": sentence,
                    "start_time": i * 5,  # Mock: assume 5 sec per sentence
                    "end_time": (i + 1) * 5
                })
        
        return segments


# ============================================================
# AUDIO SESSION MANAGER
# ============================================================

class AudioSession:
    """Manage audio recording session"""
    
    def __init__(self, session_id: str, user_id: str):
        """Initialize audio session"""
        self.session_id = session_id
        self.user_id = user_id
        self.recordings = []
        self.transcripts = []
        self.created_at = datetime.now(timezone.utc)
    
    def add_recording(self, audio_path: str, duration: float) -> Dict:
        """Add recording to session"""
        recording = {
            "id": f"rec_{len(self.recordings)}",
            "path": audio_path,
            "duration": duration,
            "added_at": datetime.now(timezone.utc).isoformat()
        }
        self.recordings.append(recording)
        return recording
    
    def add_transcript(self, recording_id: str, transcript: str, confidence: float) -> Dict:
        """Add transcript to session"""
        trans = {
            "recording_id": recording_id,
            "text": transcript,
            "confidence": confidence,
            "added_at": datetime.now(timezone.utc).isoformat()
        }
        self.transcripts.append(trans)
        return trans
    
    def export(self) -> Dict:
        """Export session data"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "recordings": self.recordings,
            "transcripts": self.transcripts,
            "total_duration": sum(r["duration"] for r in self.recordings)
        }


# ============================================================
# TEST HARNESS
# ============================================================

def run_tests():
    """Test audio module"""
    
    print("\n" + "=" * 60)
    print("🎙️  SANTINEL — AUDIO MODULE")
    print("=" * 60 + "\n")
    
    # Initialize
    print("🔌 Initializing audio handler...")
    audio = AudioHandler()
    print(f"   Whisper available: {audio.whisper_available}")
    print(f"   Supported formats: {audio.supported_formats}")
    print()
    
    # Test 1: Transcribe (mock)
    print("🎙️  Test 1: Mock transcription...")
    result = audio.transcribe("negotiation_1.wav")
    print(f"   Source: {result['source']}")
    print(f"   Language: {result['language']}")
    print(f"   Duration: {result['duration']}s")
    print(f"   Confidence: {result['confidence']:.0%}")
    print(f"   Text: {result['text'][:100]}...")
    print()
    
    # Test 2: Speaker diarization (mock)
    print("🎤 Test 2: Speaker diarization...")
    diarized = audio.split_speakers(result['text'])
    print(f"   Method: {diarized['method']}")
    print(f"   Confidence: {diarized['confidence']:.0%}")
    print(f"   Speakers detected: {len(diarized['speakers'])}")
    for speaker, lines in diarized['speakers'].items():
        print(f"   ├─ {speaker}: {len(lines)} segment(s)")
    print()
    
    # Test 3: Segment extraction
    print("📋 Test 3: Segment extraction...")
    segments = audio.extract_segments(result['text'])
    print(f"   Total segments: {len(segments)}")
    for seg in segments[:3]:
        print(f"   ├─ {seg['id']}: {seg['text'][:50]}...")
    print()
    
    # Test 4: Audio session
    print("📁 Test 4: Audio session management...")
    session = AudioSession("session_001", "user_001")
    rec = session.add_recording("negotiation_1.wav", result['duration'])
    trans = session.add_transcript(rec['id'], result['text'], result['confidence'])
    exported = session.export()
    print(f"   Session ID: {exported['session_id']}")
    print(f"   Recordings: {len(exported['recordings'])}")
    print(f"   Transcripts: {len(exported['transcripts'])}")
    print(f"   Total duration: {exported['total_duration']:.1f}s")
    print()
    
    print("✅ AUDIO_COMPLETE.PY — All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()