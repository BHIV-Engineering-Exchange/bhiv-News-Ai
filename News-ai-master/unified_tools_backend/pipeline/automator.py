from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from enum import Enum
from agents.agent_registry import agent_registry
from rl.feedback_service import rl_feedback_service
from app.core.database import db_service
from app.services.uniguru import uniguru_service

class PipelineState(Enum):
    START = "start"
    FETCHING = "fetching"
    FILTERING = "filtering"
    VERIFYING = "verifying"
    SCRIPTING = "scripting"
    FEEDBACK = "feedback"
    CORRECTION = "correction"
    COMPLETED = "completed"
    FAILED = "failed"

class NewsProcessingState:
    def __init__(self, url: str):
        self.url = url
        self.state = PipelineState.START
        self.scraped_data: Optional[Dict[str, Any]] = None
        self.filtered_data: Optional[Dict[str, Any]] = None
        self.verified_data: Optional[Dict[str, Any]] = None
        self.script_data: Optional[Dict[str, Any]] = None
        self.feedback_data: Optional[Dict[str, Any]] = None
        self.final_output: Optional[Dict[str, Any]] = None
        self.errors: List[str] = []
        self.retry_count = 0
        self.max_retries = 3
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "state": self.state.value,
            "scraped_data": self.scraped_data,
            "filtered_data": self.filtered_data,
            "verified_data": self.verified_data,
            "script_data": self.script_data,
            "feedback_data": self.feedback_data,
            "final_output": self.final_output,
            "errors": self.errors,
            "retry_count": self.retry_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class LangGraphAutomator:
    def __init__(self):
        self.max_retry_attempts = 3
        self.reward_threshold = 0.6

    async def process_news_url(self, url: str) -> Dict[str, Any]:
        """Main entry point for processing a news URL through the complete pipeline"""
        try:
            # Initialize processing state
            processing_state = NewsProcessingState(url)

            # Execute the pipeline
            result = await self._execute_pipeline(processing_state)

            # Save final result to database if successful
            if result.get("success") and db_service.database:
                news_item = {
                    "url": url,
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "summary": result.get("summary", ""),
                    "status": "published" if result.get("success") else "failed",
                    "authenticity_score": result.get("authenticity_score", 0),
                    "categories": result.get("categories", []),
                    "sentiment_analysis": result.get("sentiment_analysis", {}),
                    "video_search_results": result.get("video_search_results", []),
                    "processing_metrics": result.get("processing_metrics", {}),
                    "scraped_at": result.get("scraped_at", datetime.now().isoformat()),
                    "verified_at": result.get("verified_at"),
                    "published_at": datetime.now().isoformat() if result.get("success") else None
                }
                await db_service.save_news_item(news_item)

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"Pipeline execution failed: {str(e)}",
                "url": url,
                "completed_at": datetime.now().isoformat()
            }

    async def _execute_pipeline(self, state: NewsProcessingState) -> Dict[str, Any]:
        """Execute the complete pipeline with state management"""
        try:
            # Step 1: Fetch Content
            state.state = PipelineState.FETCHING
            fetch_result = await self._fetch_content(state.url)
            if not fetch_result.get("success"):
                state.errors.append(f"Fetch failed: {fetch_result.get('error')}")
                return self._create_error_result(state, "Content fetching failed")

            state.scraped_data = fetch_result
            state.updated_at = datetime.now().isoformat()

            # Step 2: Filter Content
            state.state = PipelineState.FILTERING
            filter_result = await self._filter_content(state.scraped_data)
            if not filter_result.get("is_relevant"):
                state.errors.append("Content filtered out as irrelevant")
                return self._create_error_result(state, "Content not relevant enough")

            state.filtered_data = filter_result
            state.updated_at = datetime.now().isoformat()

            # Step 3: Verify Authenticity
            state.state = PipelineState.VERIFYING
            verify_result = await self._verify_content(state.scraped_data)
            state.verified_data = verify_result
            state.updated_at = datetime.now().isoformat()

            # Step 4: Generate Script
            state.state = PipelineState.SCRIPTING
            script_result = await self._generate_script(state.scraped_data, state.verified_data)
            state.script_data = script_result
            state.updated_at = datetime.now().isoformat()

            # Step 5: RL Feedback and Quality Check
            state.state = PipelineState.FEEDBACK
            feedback_result = await self._calculate_feedback(state.scraped_data, state.script_data)

            # Check if correction is needed
            if await rl_feedback_service.check_correction_needed(feedback_result):
                state.retry_count += 1
                if state.retry_count < self.max_retry_attempts:
                    # Trigger correction
                    state.state = PipelineState.CORRECTION
                    correction_result = await rl_feedback_service.trigger_correction(
                        state.scraped_data, feedback_result
                    )

                    if correction_result.get("correction_triggered"):
                        # Retry with improved content
                        improved_script = await self._generate_improved_script(
                            state.scraped_data, correction_result
                        )
                        state.script_data = improved_script

                        # Recalculate feedback
                        feedback_result = await self._calculate_feedback(state.scraped_data, state.script_data)

            state.feedback_data = feedback_result
            state.updated_at = datetime.now().isoformat()

            # Step 6: Final Output Generation
            state.state = PipelineState.COMPLETED
            final_result = await self._generate_final_output(state)

            return {
                "success": True,
                "pipeline_state": state.state.value,
                "url": state.url,
                "title": state.scraped_data.get("title", ""),
                "content": state.scraped_data.get("content", ""),
                "summary": state.script_data.get("video_script", "")[:200] + "..." if state.script_data else "",
                "authenticity_score": state.verified_data.get("authenticity_score", 0),
                "categories": [],  # Would be populated from Uniguru
                "sentiment_analysis": {},  # Would be populated from Uniguru
                "video_search_results": [],
                "processing_metrics": {
                    "total_steps": 6,
                    "retries_used": state.retry_count,
                    "reward_score": feedback_result.get("reward_score", 0),
                    "processing_time": self._calculate_processing_time(state),
                    "quality_gate_passed": feedback_result.get("reward_score", 0) >= self.reward_threshold
                },
                "scraped_at": state.scraped_data.get("scraped_at"),
                "verified_at": datetime.now().isoformat(),
                "published_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "pipeline_metadata": state.to_dict()
            }

        except Exception as e:
            state.state = PipelineState.FAILED
            state.errors.append(str(e))
            return self._create_error_result(state, str(e))

    async def _fetch_content(self, url: str) -> Dict[str, Any]:
        """Step 1: Fetch content using Fetch Agent"""
        try:
            task_id = await agent_registry.submit_task("fetch_agent", {"url": url})
            if task_id:
                # Wait for task completion (in real implementation, use async waiting)
                await asyncio.sleep(1)  # Simulate processing time
                result = await agent_registry.process_task(task_id)
                return result or {"error": "Fetch task failed"}
            else:
                return {"error": "Could not submit fetch task"}
        except Exception as e:
            return {"error": f"Fetch step failed: {str(e)}"}

    async def _filter_content(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Filter content using Filter Agent"""
        try:
            task_data = {
                "content": scraped_data.get("content", ""),
                "title": scraped_data.get("title", "")
            }
            task_id = await agent_registry.submit_task("filter_agent", task_data)
            if task_id:
                await asyncio.sleep(0.5)
                result = await agent_registry.process_task(task_id)
                return result or {"is_relevant": False}
            else:
                return {"is_relevant": False, "error": "Could not submit filter task"}
        except Exception as e:
            return {"is_relevant": False, "error": str(e)}

    async def _verify_content(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Verify content authenticity using Verify Agent"""
        try:
            task_data = {
                "content": scraped_data.get("content", ""),
                "title": scraped_data.get("title", ""),
                "url": scraped_data.get("url", "")
            }
            task_id = await agent_registry.submit_task("verify_agent", task_data)
            if task_id:
                await asyncio.sleep(0.5)
                result = await agent_registry.process_task(task_id)
                return result or {"authenticity_score": 50}
            else:
                return {"authenticity_score": 50, "error": "Could not submit verify task"}
        except Exception as e:
            return {"authenticity_score": 50, "error": str(e)}

    async def _generate_script(self, scraped_data: Dict[str, Any], verified_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Generate video script using Script Agent"""
        try:
            task_data = {
                "title": scraped_data.get("title", ""),
                "content": scraped_data.get("content", ""),
                "authenticity_score": verified_data.get("authenticity_score", 50)
            }
            task_id = await agent_registry.submit_task("script_agent", task_data)
            if task_id:
                await asyncio.sleep(0.5)
                result = await agent_registry.process_task(task_id)
                return result or {"video_script": "Script generation failed"}
            else:
                return {"video_script": "Could not submit script task", "error": "Task submission failed"}
        except Exception as e:
            return {"video_script": f"Script generation error: {str(e)}", "error": str(e)}

    async def _generate_improved_script(self, scraped_data: Dict[str, Any], correction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate improved script after correction"""
        try:
            improved_summary = correction_data.get("improved_summary", "")
            task_data = {
                "title": scraped_data.get("title", ""),
                "content": scraped_data.get("content", ""),
                "summary": improved_summary,
                "correction_attempt": True
            }
            task_id = await agent_registry.submit_task("script_agent", task_data)
            if task_id:
                await asyncio.sleep(0.5)
                result = await agent_registry.process_task(task_id)
                return result or {"video_script": "Improved script generation failed"}
            else:
                return {"video_script": "Could not submit improved script task"}
        except Exception as e:
            return {"video_script": f"Improved script error: {str(e)}"}

    async def _calculate_feedback(self, scraped_data: Dict[str, Any], script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Calculate RL feedback"""
        try:
            news_item = {
                "id": f"temp_{datetime.now().timestamp()}",
                "content": scraped_data.get("content", ""),
                "title": scraped_data.get("title", ""),
                "authenticity_score": 75,  # Would come from verification step
                "correction_attempts": 0
            }

            feedback = await rl_feedback_service.calculate_reward(news_item, script_data)
            return feedback
        except Exception as e:
            return {"reward_score": 0.5, "error": str(e)}

    async def _generate_final_output(self, state: NewsProcessingState) -> Dict[str, Any]:
        """Generate final output combining all pipeline results"""
        try:
            # Get Uniguru analysis for enhanced output
            content = state.scraped_data.get("content", "")
            title = state.scraped_data.get("title", "")

            # Classify content
            classification = await uniguru_service.classify_text(content)
            categories = classification.get("categories", []) if classification.get("success") else []

            # Analyze sentiment
            sentiment = await uniguru_service.analyze_sentiment(content)
            sentiment_data = {
                "sentiment": sentiment.get("sentiment", "neutral"),
                "polarity": sentiment.get("polarity", 0.0),
                "confidence": sentiment.get("confidence", 0.0)
            } if sentiment.get("success") else {}

            # Generate summary
            summary_result = await uniguru_service.summarize_text(content, max_length=150)
            summary = summary_result.get("summary", "") if summary_result.get("success") else ""

            return {
                "title": title,
                "content": content,
                "summary": summary,
                "categories": categories,
                "sentiment_analysis": sentiment_data,
                "video_script": state.script_data.get("video_script", ""),
                "authenticity_score": state.verified_data.get("authenticity_score", 0),
                "reward_score": state.feedback_data.get("reward_score", 0),
                "processing_complete": True
            }

        except Exception as e:
            return {
                "title": state.scraped_data.get("title", ""),
                "content": state.scraped_data.get("content", ""),
                "error": f"Final output generation failed: {str(e)}"
            }

    def _calculate_processing_time(self, state: NewsProcessingState) -> float:
        """Calculate total processing time"""
        try:
            start_time = datetime.fromisoformat(state.created_at)
            end_time = datetime.fromisoformat(state.updated_at)
            return (end_time - start_time).total_seconds()
        except:
            return 0.0

    def _create_error_result(self, state: NewsProcessingState, error_msg: str) -> Dict[str, Any]:
        """Create error result from failed pipeline execution"""
        return {
            "success": False,
            "error": error_msg,
            "url": state.url,
            "pipeline_state": state.state.value,
            "errors": state.errors,
            "retry_count": state.retry_count,
            "completed_at": datetime.now().isoformat()
        }

# Global instance
automator = LangGraphAutomator()