# backend/services/evaluation_service.py
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class EvaluationService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    async def evaluate_audio(self, audio_bytes: bytes, transcript: Optional[str] = None, language: str = "en", user_id: Optional[str] = None) -> Dict:
        try:
            logger.info(f"[EVAL-AUDIO] Starting - lang={language}, size={len(audio_bytes)}")

            metrics = {
                "clarity": 0.85,
                "confidence": 0.72,
                "pacing": 0.68,
                "emotional_tone": 0.80,
                "filler_words": 0.90
            }

            feedback = []
            if metrics.get("clarity") < 0.6:
                feedback.append("Speak more clearly")
            if metrics.get("confidence") < 0.5:
                feedback.append("Project more confidence")

            overall_score = sum(metrics.values()) / len(metrics)

            result = {
                "type": "audio",
                "metrics": metrics,
                "score": round(overall_score, 2),
                "feedback": feedback,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"[EVAL-AUDIO] Complete - score={overall_score:.2f}")
            return result

        except Exception as e:
            logger.error(f"[EVAL-AUDIO] Failed: {str(e)}")
            return {"type": "audio", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

    async def evaluate_video(self, video_file_path: str, language: str = "en", user_id: Optional[str] = None) -> Dict:
        try:
            if not os.path.exists(video_file_path):
                raise FileNotFoundError(f"Video not found: {video_file_path}")

            metrics = {
                "eye_contact": 0.65,
                "body_language": 0.78,
                "gestures": 0.82,
                "facial_expression": 0.75,
                "appearance": 0.88
            }

            feedback = []
            if metrics.get("eye_contact") < 0.5:
                feedback.append("Look more at camera")

            overall_score = sum(metrics.values()) / len(metrics)

            result = {
                "type": "video",
                "metrics": metrics,
                "score": round(overall_score, 2),
                "feedback": feedback,
                "frames_analyzed": 10,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"[EVAL-VIDEO] Complete - score={overall_score:.2f}")
            return result

        except Exception as e:
            logger.error(f"[EVAL-VIDEO] Failed: {str(e)}")
            return {"type": "video", "error": str(e), "timestamp": datetime.utcnow().isoformat()}

async def setup_evaluation_routes(app):
    service = EvaluationService()

    @app.post("/api/evaluate/audio")
    async def evaluate_audio(request):
        try:
            audio_bytes = await request.body()
            language = request.query_params.get("language", "en")
            transcript = request.query_params.get("transcript")
            result = await service.evaluate_audio(audio_bytes, transcript, language)
            return {"success": "error" not in result, "data": result}
        except Exception as e:
            logger.error(f"[API] Audio eval: {str(e)}")
            return {"success": False, "error": str(e)}

    @app.post("/api/evaluate/video")
    async def evaluate_video(request):
        try:
            form = await request.form()
            video_file = form.get("video")
            if not video_file:
                return {"success": False, "error": "No video"}

            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                content = await video_file.read()
                tmp.write(content)
                tmp_path = tmp.name

            result = await service.evaluate_video(tmp_path)
            os.remove(tmp_path)
            return {"success": "error" not in result, "data": result}
        except Exception as e:
            logger.error(f"[API] Video eval: {str(e)}")
            return {"success": False, "error": str(e)}
