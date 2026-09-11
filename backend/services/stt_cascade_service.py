# backend/services/stt_cascade_service.py
import asyncio, logging, os, httpx
from typing import Dict

logger = logging.getLogger(__name__)

class DeepgramProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.timeout = 3.0

    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> Dict:
        try:
            headers = {"Authorization": f"Token {self.api_key}", "Content-Type": "audio/wav"}
            params = {"model": os.getenv("DEEPGRAM_STT_MODEL", "nova-2"), "language": language}
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post("https://api.deepgram.com/v1/listen", headers=headers, params=params, content=audio_bytes)
                if response.status_code == 200:
                    data = response.json()
                    transcript = data["results"]["channels"][0]["alternatives"][0]["transcript"]
                    confidence = data["results"]["channels"][0]["alternatives"][0].get("confidence", 0.0)
                    return {"success": True, "transcript": transcript, "confidence": confidence, "provider": "deepgram"}
                return {"success": False, "error": f"Deepgram {response.status_code}"}
        except asyncio.TimeoutError:
            return {"success": False, "error": "Deepgram timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class WhisperProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.timeout = 5.0

    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> Dict:
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                files = {"file": ("audio.wav", audio_bytes)}
                data = {"model": "whisper-1", "language": language}
                response = await client.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data)
                if response.status_code == 200:
                    result = response.json()
                    return {"success": True, "transcript": result["text"], "confidence": 0.95, "provider": "whisper"}
                return {"success": False, "error": f"Whisper {response.status_code}"}
        except asyncio.TimeoutError:
            return {"success": False, "error": "Whisper timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class GoogleProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.timeout = 10.0

    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> Dict:
        try:
            import base64
            audio_content = base64.b64encode(audio_bytes).decode("utf-8")
            payload = {"config": {"encoding": "LINEAR16", "sampleRateHertz": 16000, "languageCode": "en-US" if language == "en" else "ro-RO"}, "audio": {"content": audio_content}}
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"https://speech.googleapis.com/v1/speech:recognize", params={"key": self.api_key}, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    if "results" in result and result["results"]:
                        transcript = result["results"][0]["alternatives"][0]["transcript"]
                        confidence = result["results"][0]["alternatives"][0].get("confidence", 0.9)
                        return {"success": True, "transcript": transcript, "confidence": confidence, "provider": "google"}
                    return {"success": False, "error": "No speech"}
                return {"success": False, "error": f"Google {response.status_code}"}
        except asyncio.TimeoutError:
            return {"success": False, "error": "Google timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class CascadeSTTService:
    def __init__(self):
        self.deepgram_key = os.getenv("DEEPGRAM_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.google_key = os.getenv("GOOGLE_SPEECH_API_KEY")
        self.providers = []
        if self.deepgram_key:
            self.providers.append(("deepgram", DeepgramProvider(self.deepgram_key)))
        if self.openai_key:
            self.providers.append(("whisper", WhisperProvider(self.openai_key)))
        if self.google_key:
            self.providers.append(("google", GoogleProvider(self.google_key)))

    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> Dict:
        logger.info(f"[STT] Cascade start - {len(self.providers)} providers")
        cascade_errors = []
        for provider_name, provider in self.providers:
            logger.info(f"[STT] Trying {provider_name}...")
            result = await provider.transcribe(audio_bytes, language)
            if result.get("success"):
                logger.info(f"[STT] Success: {provider_name}")
                return result
            cascade_errors.append(f"{provider_name}: {result.get('error', 'unknown')}")
        logger.error("[STT] All failed")
        return {"success": False, "error": "All providers failed", "cascade_errors": cascade_errors}

async def setup_stt_routes(app):
    stt_service = CascadeSTTService()

    @app.post("/api/transcribe")
    async def transcribe(request):
        try:
            audio_bytes = await request.body()
            language = request.query_params.get("language", "en")
            result = await stt_service.transcribe(audio_bytes, language)
            return {"success": result.get("success", False), "data": result}
        except Exception as e:
            logger.error(f"[API] Transcribe: {str(e)}")
            return {"success": False, "error": str(e)}
