from fastapi import HTTPException
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import logging
from pipeline.automator import automator
from bhiv_connector.bhiv_service import bhiv_service
from rl.feedback_service import rl_feedback_service
from app.services.uniguru import uniguru_service

logger = logging.getLogger(__name__)

class UnifiedPipeline:
    def __init__(self):
        self.max_retries = 3
        self.uniguru_fallback_model = "local-summarizer"  # Placeholder for fallback

    async def run_full_pipeline(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unified pipeline endpoint that orchestrates the complete News AI workflow:
        1. Fetch news content
        2. Filter and verify
        3. Generate script with RL correction
        4. Push to BHIV for video generation
        5. Generate audio via Sankalp's Insight Node
        6. Return complete JSON for frontend preview
        """
        start_time = datetime.now()

        try:
            # Validate request
            validation_result = self._validate_request(request)
            if not validation_result["valid"]:
                raise HTTPException(status_code=400, detail=validation_result["errors"])

            url = request["url"]
            options = request.get("options", {})

            logger.info(f"Starting unified pipeline for URL: {url}")

            # Step 1: Process news through backend pipeline
            news_result = await self._process_news_content(url, options)
            if not news_result["success"]:
                return self._create_error_response("News processing failed", news_result)

            # Step 2: RL correction loop
            corrected_result = await self._apply_rl_corrections(news_result["data"], options)
            if not corrected_result["success"]:
                return self._create_error_response("RL correction failed", corrected_result)

            # Step 3: BHIV push for video generation
            bhiv_result = await self._push_to_bhiv(corrected_result["data"], options)
            if not bhiv_result["success"]:
                logger.warning(f"BHIV push failed: {bhiv_result.get('error')}")
                # Continue without BHIV for now

            # Step 4: Audio generation via Sankalp's Insight Node
            audio_result = await self._generate_audio(corrected_result["data"], options)
            if not audio_result["success"]:
                logger.warning(f"Audio generation failed: {audio_result.get('error')}")
                # Continue without audio

            # Step 5: Compile final response for frontend
            final_response = self._compile_final_response(
                corrected_result["data"],
                bhiv_result,
                audio_result,
                start_time
            )

            logger.info(f"Unified pipeline completed successfully for URL: {url}")
            return final_response

        except Exception as e:
            logger.error(f"Unified pipeline failed: {str(e)}")
            return self._create_error_response(f"Pipeline execution failed: {str(e)}", {})

    def _validate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate incoming request schema"""
        errors = []

        if not request.get("url"):
            errors.append("URL is required")

        if not isinstance(request.get("url", ""), str):
            errors.append("URL must be a string")

        # Validate options if provided
        options = request.get("options", {})
        if options:
            if not isinstance(options, dict):
                errors.append("Options must be a dictionary")

            # Validate specific flags
            valid_flags = ["enable_bhiv_push", "enable_audio", "force_correction", "skip_verification"]
            for flag in valid_flags:
                if flag in options and not isinstance(options[flag], bool):
                    errors.append(f"{flag} must be a boolean")

            # Validate tone
            if "tone" in options:
                valid_tones = ["neutral", "positive", "negative", "formal", "casual"]
                if options["tone"] not in valid_tones:
                    errors.append(f"Tone must be one of: {', '.join(valid_tones)}")

            # Validate language
            if "language" in options:
                if not isinstance(options["language"], str) or len(options["language"]) != 2:
                    errors.append("Language must be a 2-letter ISO code (e.g., 'en', 'es')")

            # Validate avatar_ready
            if "avatar_ready" in options and not isinstance(options["avatar_ready"], bool):
                errors.append("avatar_ready must be a boolean")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    async def _process_news_content(self, url: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Process news content through the backend pipeline"""
        try:
            # Use existing automator
            result = await automator.process_news_url(url)

            # Add validation flags
            if result.get("success"):
                script_data = result.get("script_data", {})
                # Use provided options or defaults from script_data
                result["validation_flags"] = {
                    "tone_ready": options.get("tone", script_data.get("tone", "neutral")),
                    "language_ready": options.get("language", script_data.get("language", "en")),
                    "avatar_ready": options.get("avatar_ready", script_data.get("avatar_ready", False))
                }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"News processing failed: {str(e)}"
            }

    async def _apply_rl_corrections(self, news_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Apply RL corrections if needed"""
        try:
            script_output = news_data.get("script_data", {})
            news_item = {
                "content": news_data.get("content", ""),
                "title": news_data.get("title", ""),
                "authenticity_score": news_data.get("authenticity_score", 0)
            }

            feedback = await rl_feedback_service.calculate_reward(news_item, script_output)

            # Check if correction is needed
            if feedback.get("reward_score", 0) < 0.6 or options.get("force_correction", False):
                logger.info("Applying RL corrections")
                correction_result = await rl_feedback_service.trigger_correction(news_item, feedback)

                if correction_result.get("correction_triggered"):
                    # Update script with corrections
                    news_data["script_data"] = correction_result.get("improved_script", script_output)
                    news_data["corrections_applied"] = news_data.get("corrections_applied", 0) + 1
                    news_data["rl_feedback"] = feedback

            return {
                "success": True,
                "data": news_data
            }

        except Exception as e:
            logger.error(f"RL correction failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": news_data  # Return original data
            }

    async def _push_to_bhiv(self, news_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Push content to BHIV Core for video generation"""
        try:
            if not options.get("enable_bhiv_push", True):
                return {"success": True, "skipped": True}

            # Prepare content for BHIV
            bhiv_content = {
                "title": news_data.get("title", ""),
                "script": news_data.get("script_data", {}).get("video_script", ""),
                "metadata": {
                    "tone": news_data.get("script_data", {}).get("tone", "neutral"),
                    "language": news_data.get("script_data", {}).get("language", "en"),
                    "authenticity_score": news_data.get("authenticity_score", 0)
                }
            }

            # Determine channels and avatars based on content
            channels = options.get("channels", ["news_channel_1"])
            avatars = options.get("avatars", ["avatar_alice"])

            result = await bhiv_service.push_channel_avatar_matrix(bhiv_content, channels, avatars)

            return {
                "success": result.get("successful_pushes", 0) > 0,
                "data": result,
                "channels": channels,
                "avatars": avatars
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"BHIV push failed: {str(e)}"
            }

    async def _generate_audio(self, news_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audio via Sankalp's Insight Node"""
        try:
            if not options.get("enable_audio", True):
                return {"success": True, "skipped": True}

            # Prepare audio generation request
            audio_request = {
                "text": news_data.get("script_data", {}).get("video_script", ""),
                "voice": options.get("voice", "default"),
                "language": news_data.get("script_data", {}).get("language", "en"),
                "tone": news_data.get("script_data", {}).get("tone", "neutral")
            }

            # Simulate Sankalp's Insight Node API call
            # In real implementation, this would be an HTTP call to Sankalp's service
            audio_result = await self._call_sankalp_audio_api(audio_request)

            return {
                "success": audio_result.get("success", False),
                "audio_url": audio_result.get("audio_url"),
                "duration": audio_result.get("duration"),
                "voice_used": audio_request["voice"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Audio generation failed: {str(e)}"
            }

    async def _call_sankalp_audio_api(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation of Sankalp's Insight Node API call"""
        # In production, this would make an actual HTTP request
        # For now, simulate success/failure
        await asyncio.sleep(1)  # Simulate API call delay

        # Mock successful response
        return {
            "success": True,
            "audio_url": f"https://audio.news-ai.com/generated/{datetime.now().timestamp()}.mp3",
            "duration": len(request["text"]) * 0.1,  # Rough estimate
            "format": "mp3",
            "size_bytes": len(request["text"]) * 50
        }

    def _compile_final_response(self, news_data: Dict[str, Any], bhiv_result: Dict[str, Any],
                               audio_result: Dict[str, Any], start_time: datetime) -> Dict[str, Any]:
        """Compile final response for frontend consumption"""
        processing_time = (datetime.now() - start_time).total_seconds()

        return {
            "success": True,
            "pipeline": "unified_v1",
            "data": {
                "news_item": {
                    "title": news_data.get("title", ""),
                    "content": news_data.get("content", ""),
                    "summary": news_data.get("summary", ""),
                    "categories": news_data.get("categories", []),
                    "sentiment": news_data.get("sentiment_analysis", {}),
                    "authenticity_score": news_data.get("authenticity_score", 0)
                },
                "script": {
                    "video_prompt": news_data.get("script_data", {}).get("video_script", ""),
                    "tone": news_data.get("validation_flags", {}).get("tone_ready", "neutral"),
                    "language": news_data.get("validation_flags", {}).get("language_ready", "en"),
                    "avatar_ready": news_data.get("validation_flags", {}).get("avatar_ready", False)
                },
                "rl_feedback": {
                    "reward_score": news_data.get("rl_feedback", {}).get("reward_score", 0),
                    "quality_gate_passed": news_data.get("rl_feedback", {}).get("reward_score", 0) >= 0.6,
                    "corrections_applied": news_data.get("corrections_applied", 0)
                },
                "bhiv_push": {
                    "successful": bhiv_result.get("success", False),
                    "channels": bhiv_result.get("channels", []),
                    "successful_pushes": bhiv_result.get("data", {}).get("successful_pushes", 0)
                },
                "audio": {
                    "generated": audio_result.get("success", False),
                    "audio_url": audio_result.get("audio_url"),
                    "duration": audio_result.get("duration"),
                    "voice": audio_result.get("voice_used")
                }
            },
            "processing_metrics": {
                "total_time": processing_time,
                "pipeline_version": "v1.0",
                "components_used": ["automator", "rl", "bhiv", "audio"]
            },
            "timestamp": datetime.now().isoformat(),
            "preview_ready": True
        }

    def _create_error_response(self, error_msg: str, partial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create error response with partial data if available"""
        return {
            "success": False,
            "error": error_msg,
            "partial_data": partial_data,
            "timestamp": datetime.now().isoformat()
        }

# Global instance
unified_pipeline = UnifiedPipeline()