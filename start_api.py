# -*- coding: utf-8 -*-
"""
SANTINEL API Gateway — Whisper.cpp (via faster-whisper) + Google Speech Recognition fallback.

STT Strategy:
1. Primary: faster-whisper (local, offline, best quality)
2. Fallback: Google Speech Recognition (online, free limited)
"""

import os
import re
import sys
sys.path.insert(0, '.')

from typing import Callable, Dict, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

_SYMBOL_RE = re.compile(
    "[\U0001F000-\U0001FAFF☀-➿←-⇿️•▪●]"
)

import requests
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from auth_guard import get_current_user

# --------------------------------------------------------------------------- #
#  STT: Whisper.cpp (faster-whisper) + Google fallback                       #
# --------------------------------------------------------------------------- #

try:
    from faster_whisper import WhisperModel
    # Load base model (faster on CPU than small/medium)
    print("[WHISPER] Loading faster-whisper model 'base'...")
    whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    print("[WHISPER] Model loaded successfully")
    WHISPER_AVAILABLE = True
except Exception as e:
    print(f"[WHISPER] Failed to load: {e}")
    print("[WHISPER] Will use Google Speech Recognition fallback")
    whisper_model = None
    WHISPER_AVAILABLE = False

try:
    import speech_recognition as sr
    google_recognizer = sr.Recognizer()
    GOOGLE_AVAILABLE = True
    print("[GOOGLE] Speech Recognition library loaded")
except Exception as e:
    print(f"[GOOGLE] Failed to load: {e}")
    google_recognizer = None
    GOOGLE_AVAILABLE = False

STT_MODEL_NAME = "whisper-base"
MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25MB

# --------------------------------------------------------------------------- #
#  Framework module imports                                                   #
# --------------------------------------------------------------------------- #

_MODULE_SPECS = [
    ("cbt", "core.cbt_module", "CBTAssessment"),
    ("nlp", "core.nlp_module", "NLPModule"),
    ("ta", "core.ta_module", "TAModule"),
    ("ei", "core.ei_module", "EIModule"),
    ("attachment", "core.attachment_module", "AttachmentModule"),
    ("behavioral_econ", "core.behavioral_econ_module", "BehavioralEconomicsModule"),
    ("game_theory", "core.game_theory_module", "GameTheoryModule"),
    ("neuroscience", "core.neuroscience_module", "NeuroscienceModule"),
    ("narrative", "core.narrative_module", "NarrativeModule"),
    ("somatic", "core.somatic_module", "SomaticModule"),
]

FRAMEWORK_ORDER = [slug for slug, _, _ in _MODULE_SPECS]

_INSTANCES: Dict[str, object] = {}
for _slug, _mod_path, _cls_name in _MODULE_SPECS:
    try:
        _mod = __import__(_mod_path, fromlist=[_cls_name])
        _INSTANCES[_slug] = getattr(_mod, _cls_name)()
    except Exception as exc:
        print(f"[santinel] could not load {_mod_path}: {exc}")
        _INSTANCES[_slug] = None


# --------------------------------------------------------------------------- #
#  Bilingual helpers                                                          #
# --------------------------------------------------------------------------- #

def bi(en: str, ro: str, lang: str):
    """Return {en, ro} for lang='both', otherwise the single requested string."""
    if lang == "en":
        return en
    if lang == "ro":
        return ro
    return {"en": en, "ro": ro}


def humanize(token: Optional[str]) -> str:
    if not token:
        return "No clear signal"
    return token.replace("_", " ").strip().capitalize()


def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    text = _SYMBOL_RE.sub("", text).strip()
    return text


# --------------------------------------------------------------------------- #
#  Framework analysis                                                         #
# --------------------------------------------------------------------------- #

def run_all_frameworks(text: str, lang: str = "both") -> dict:
    """Run all 10 frameworks on text."""
    results = {}
    for slug in FRAMEWORK_ORDER:
        module = _INSTANCES.get(slug)
        if module and hasattr(module, "analyze"):
            try:
                finding = module.analyze(text)
                results[slug] = finding
            except Exception as e:
                print(f"[santinel] {slug} analysis failed: {e}")
                results[slug] = None
    return results


# --------------------------------------------------------------------------- #
#  STT Functions                                                              #
# --------------------------------------------------------------------------- #

def transcribe_with_whisper(audio_file_path: str, lang: str) -> Tuple[str, float]:
    """Transcribe using faster-whisper (local)."""
    try:
        print(f"[WHISPER] Transcribing {audio_file_path} (lang={lang})...")

        # Determine language code
        lang_code = "ro" if lang == "ro" else None  # None = auto-detect

        # Transcribe
        segments, info = whisper_model.transcribe(
            audio_file_path,
            language=lang_code,
            beam_size=5,  # Lower beam for speed on CPU
        )

        # Collect text (newer faster-whisper doesn't expose segment.confidence)
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text)

        text = " ".join(text_parts).strip()
        # Use language probability as confidence, or 0.9 if we got text
        confidence = info.language_probability if hasattr(info, 'language_probability') else (0.9 if text else 0.0)

        print(f"[WHISPER] SUCCESS: '{text}' (confidence={confidence:.2f})")
        return text, confidence

    except Exception as e:
        print(f"[WHISPER] ERROR: {e}")
        return None, None


def transcribe_with_google(audio_file_path: str, lang: str) -> Tuple[str, float]:
    """Transcribe using Google Speech Recognition (fallback)."""
    try:
        print(f"[GOOGLE] Transcribing {audio_file_path} (lang={lang})...")

        # Load audio
        with sr.AudioFile(audio_file_path) as source:
            audio_data = google_recognizer.record(source)

        # Language code
        lang_code = "ro-RO" if lang == "ro" else "en-US"

        # Transcribe
        text = google_recognizer.recognize_google(audio_data, language=lang_code)

        print(f"[GOOGLE] SUCCESS: '{text}'")
        return text, 0.85  # Google doesn't return confidence, assume high

    except sr.UnknownValueError:
        print("[GOOGLE] Could not understand audio")
        return "", 0.0
    except sr.RequestError as e:
        print(f"[GOOGLE] API error: {e}")
        return None, None
    except Exception as e:
        print(f"[GOOGLE] ERROR: {e}")
        return None, None


# --------------------------------------------------------------------------- #
#  FastAPI app                                                                #
# --------------------------------------------------------------------------- #

app = FastAPI(title="SANTINEL API", version="0.1.0")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
if CORS_ORIGINS and CORS_ORIGINS[0]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router)


# --------------------------------------------------------------------------- #
#  Routes                                                                     #
# --------------------------------------------------------------------------- #

@app.get("/health")
def health():
    """Health check."""
    loaded = [slug for slug in FRAMEWORK_ORDER if _INSTANCES.get(slug)]
    return {
        "status": "ok",
        "frameworks_loaded": len(loaded),
        "frameworks": loaded,
        "stt_model": STT_MODEL_NAME,
        "whisper_available": WHISPER_AVAILABLE,
        "google_available": GOOGLE_AVAILABLE,
    }


@app.post("/api/analyze")
def analyze(text: str, lang: str = "both"):
    """Analyze negotiation text."""
    if not text:
        return {"error": "No text provided"}
    result = run_all_frameworks(text.strip(), lang)
    return {"input": text, "lang": lang, **result}


@app.post("/api/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    lang: str = Form("auto"),
    user: dict = Depends(get_current_user),
):
    """Live speech-to-text: Whisper.cpp (primary) + Google (fallback)."""

    if not WHISPER_AVAILABLE and not GOOGLE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="transcription not configured (no STT model available)",
        )

    audio_data = await file.read()
    if not audio_data:
        return {"text": "", "model": STT_MODEL_NAME, "backend": "none"}
    if len(audio_data) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="audio segment too large")

    # Save to temp file
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        text = None
        confidence = None
        backend_used = None

        # Try Whisper first
        if WHISPER_AVAILABLE:
            print("[TRANSCRIBE] Trying Whisper...")
            text, confidence = transcribe_with_whisper(tmp_path, lang)
            if text is not None:
                backend_used = "whisper"

        # Fallback to Google if Whisper failed
        if text is None and GOOGLE_AVAILABLE:
            print("[TRANSCRIBE] Whisper failed, trying Google...")
            text, confidence = transcribe_with_google(tmp_path, lang)
            if text is not None:
                backend_used = "google"

        # Clean up
        import os
        try:
            os.unlink(tmp_path)
        except:
            pass

        if text is None:
            raise HTTPException(
                status_code=502,
                detail="transcription failed (all backends unavailable)"
            )

        return {
            "text": text,
            "model": STT_MODEL_NAME,
            "confidence": confidence,
            "backend": backend_used,
        }

    except HTTPException:
        raise
    except Exception as exc:
        print(f"[TRANSCRIBE] ERROR: {exc}")
        raise HTTPException(status_code=502, detail=f"transcription error: {exc}")


@app.get("/docs")
def docs():
    return {"docs": "Visit /docs for Swagger UI"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
