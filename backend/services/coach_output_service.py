# backend/services/coach_output_service.py
import logging, asyncio
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CoachOutputManager:
    def __init__(self, framework_service, tts_service):
        self.framework_service = framework_service
        self.tts_service = tts_service

    async def generate_coach_response(self, user_transcript: str, framework_key: str, language: str = "en", include_audio: bool = True) -> Dict:
        logger.info(f"[COACH] Generating response - framework={framework_key}, lang={language}")

        try:
            # STEP 1: Generate text
            logger.info("[COACH] Generating text advice...")
            coach_text = await self.framework_service.generate_advice(
                user_transcript=user_transcript,
                framework_key=framework_key,
                language=language
            )
            logger.info(f"[COACH] Text generated: {len(coach_text)} chars")

            # STEP 2: Generate audio (optional, don't fail if TTS fails)
            audio_url = None
            if include_audio:
                try:
                    logger.info("[COACH] Generating audio...")
                    audio_url = await self.tts_service.text_to_speech(
                        text=coach_text,
                        language=language
                    )
                    logger.info(f"[COACH] Audio generated: {audio_url}")
                except Exception as e:
                    logger.warning(f"[COACH] TTS failed but continuing: {str(e)}")

            # STEP 3: Return guaranteed response
            result = {
                "success": True,
                "text": coach_text,
                "audio_url": audio_url,
                "framework": framework_key,
                "language": language,
                "timestamp": datetime.utcnow().isoformat(),
                "error": None
            }

            logger.info("[COACH] Complete response ready")
            return result

        except Exception as e:
            logger.error(f"[COACH] Generation failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "text": None,
                "audio_url": None,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

async def setup_coach_routes(app, framework_service, tts_service):
    manager = CoachOutputManager(framework_service, tts_service)

    @app.post("/api/coach/advice")
    async def get_coach_advice(request):
        try:
            data = await request.json()
            transcript = data.get("transcript", "")
            framework = data.get("framework", "cbt")
            language = data.get("language", "en")
            include_audio = data.get("include_audio", True)

            result = await manager.generate_coach_response(
                user_transcript=transcript,
                framework_key=framework,
                language=language,
                include_audio=include_audio
            )

            return {"success": result.get("success", False), "data": result}
        except Exception as e:
            logger.error(f"[API] Coach advice: {str(e)}")
            return {"success": False, "error": str(e)}
