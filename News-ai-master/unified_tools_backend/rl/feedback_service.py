from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import json
import os
import random
import math
from pathlib import Path
from app.core.database import db_service
from app.services.uniguru import uniguru_service
from agents.agent_registry import agent_registry

class CorrectionBandit:
    def __init__(self):
        self.arms = {
            "uniguru_resummarization": {"pulls": 0, "rewards": 0.0},
            "tone_adjustment": {"pulls": 0, "rewards": 0.0},
            "engagement_boost": {"pulls": 0, "rewards": 0.0},
            "quality_enhancement": {"pulls": 0, "rewards": 0.0},
            "content_expansion": {"pulls": 0, "rewards": 0.0}
        }
    
    def select_arm(self) -> str:
        """Select correction strategy using UCB1 algorithm"""
        total_pulls = sum(arm["pulls"] for arm in self.arms.values())
        if total_pulls == 0:
            return random.choice(list(self.arms.keys()))
        
        best_arm = None
        best_ucb = -float('inf')
        
        for arm_name, arm_data in self.arms.items():
            if arm_data["pulls"] == 0:
                return arm_name
            
            avg_reward = arm_data["rewards"] / arm_data["pulls"]
            ucb = avg_reward + math.sqrt(2 * math.log(total_pulls) / arm_data["pulls"])
            
            if ucb > best_ucb:
                best_ucb = ucb
                best_arm = arm_name
        
        return best_arm
    
    def update_arm(self, arm_name: str, reward: float):
        """Update arm statistics with reward"""
        if arm_name in self.arms:
            self.arms[arm_name]["pulls"] += 1
            self.arms[arm_name]["rewards"] += reward
    
    def get_arm_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all arms"""
        stats = {}
        for arm_name, arm_data in self.arms.items():
            pulls = arm_data["pulls"]
            if pulls > 0:
                avg_reward = arm_data["rewards"] / pulls
            else:
                avg_reward = 0.0
            stats[arm_name] = {
                "pulls": pulls,
                "avg_reward": round(avg_reward, 3),
                "total_rewards": round(arm_data["rewards"], 3)
            }
        return stats

class RLFeedbackService:
    def __init__(self):
        self.reward_threshold = 0.6  # Minimum acceptable reward score
        self.max_correction_attempts = 3

        # Adaptive reward scaling
        self.adaptive_scaling = True
        self.performance_history = []
        self.scaling_factors = {
            "tone_weight": 0.3,
            "engagement_weight": 0.4,
            "quality_weight": 0.3
        }

        # Logging configuration
        self.logs_dir = Path("logs/rl")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.logs_dir / "rl_metrics.jsonl"

        # Performance tracking
        self.session_stats = {
            "total_evaluations": 0,
            "mean_reward": 0.0,
            "correction_rate": 0.0,
            "avg_latency": 0.0,
            "session_start": datetime.now().isoformat()
        }

    async def calculate_reward(self, news_item: Dict[str, Any], script_output: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive reward score for news processing output with adaptive scaling"""
        start_time = datetime.now()

        try:
            content = news_item.get("content", "")
            title = news_item.get("title", "")
            authenticity_score = news_item.get("authenticity_score", 50)
            script = script_output.get("video_script", "")

            # Calculate component scores
            tone_score = await self._calculate_tone_score(content, script)
            engagement_score = await self._calculate_engagement_score(content, script, title)
            quality_score = await self._calculate_quality_score(content, authenticity_score, script_output)

            # Apply adaptive reward scaling
            if self.adaptive_scaling:
                weights = self._get_adaptive_weights()
            else:
                weights = self.scaling_factors

            # Overall reward (weighted average with adaptive scaling)
            reward_score = (tone_score * weights["tone_weight"]) + \
                          (engagement_score * weights["engagement_weight"]) + \
                          (quality_score * weights["quality_weight"])

            # Determine if correction is needed
            correction_needed = reward_score < self.reward_threshold

            # Calculate latency
            latency = (datetime.now() - start_time).total_seconds()

            feedback_data = {
                "news_item_id": news_item.get("id", ""),
                "reward_score": round(reward_score, 3),
                "tone_score": round(tone_score, 3),
                "engagement_score": round(engagement_score, 3),
                "quality_score": round(quality_score, 3),
                "correction_needed": correction_needed,
                "correction_attempts": news_item.get("correction_attempts", 0),
                "final_output": {
                    "title": title,
                    "content": content,
                    "script": script,
                    "authenticity_score": authenticity_score
                },
                "metrics": {
                    "content_length": len(content.split()),
                    "script_length": len(script.split()) if script else 0,
                    "processing_timestamp": datetime.now().isoformat(),
                    "latency_seconds": round(latency, 3),
                    "reward_components": weights
                },
                "adaptive_scaling": {
                    "enabled": self.adaptive_scaling,
                    "performance_history_size": len(self.performance_history)
                }
            }

            # Update performance history for adaptive scaling
            self.performance_history.append({
                "reward_score": reward_score,
                "timestamp": datetime.now().isoformat(),
                "correction_needed": correction_needed
            })

            # Keep only last 100 evaluations for adaptive scaling
            if len(self.performance_history) > 100:
                self.performance_history = self.performance_history[-100:]

            # Update session statistics
            self._update_session_stats(reward_score, correction_needed, latency)

            # Auto-log RL event
            await self._log_rl_event(feedback_data)

            # Save feedback to database
            if db_service.database:
                await db_service.save_rl_feedback(feedback_data)

            return feedback_data

        except Exception as e:
            return {
                "error": f"Reward calculation failed: {str(e)}",
                "reward_score": 0.0,
                "correction_needed": True
            }

    async def _calculate_tone_score(self, content: str, script: str) -> float:
        """Calculate tone appropriateness score (0-1)"""
        try:
            # Define keyword lists for consistency checking
            emotional_words = ["shocking", "outrageous", "unbelievable", "devastating", "incredible"]
            neutral_words = ["according to", "reported", "stated", "confirmed", "announced"]

            # Analyze content tone using Uniguru sentiment analysis
            sentiment_result = await uniguru_service.analyze_sentiment(content)

            if sentiment_result.get("success"):
                polarity = sentiment_result.get("polarity", 0.0)
                # For news, we want neutral to slightly positive tone
                # Optimal polarity is between -0.1 and 0.3
                if -0.1 <= polarity <= 0.3:
                    tone_score = 0.9
                elif -0.3 <= polarity <= 0.5:
                    tone_score = 0.7
                else:
                    tone_score = 0.4
            else:
                # Fallback: keyword-based analysis
                emotional_count = sum(1 for word in emotional_words if word in content.lower())
                neutral_count = sum(1 for word in neutral_words if word in content.lower())

                if neutral_count >= emotional_count + 2:
                    tone_score = 0.85
                elif neutral_count >= emotional_count:
                    tone_score = 0.7
                else:
                    tone_score = 0.4

            # Check script tone consistency
            if script:
                script_emotional = sum(1 for word in emotional_words if word in script.lower())
                script_neutral = sum(1 for word in neutral_words if word in script.lower())

                if script_neutral >= script_emotional:
                    tone_score += 0.1  # Bonus for consistent neutral script
                else:
                    tone_score -= 0.1  # Penalty for inconsistent tone

            return max(0.0, min(1.0, tone_score))

        except Exception as e:
            print(f"Tone score calculation error: {e}")
            return 0.5  # Neutral fallback

    async def _calculate_engagement_score(self, content: str, script: str, title: str) -> float:
        """Calculate engagement potential score (0-1)"""
        try:
            score = 0.5  # Base score

            # Content length factor
            word_count = len(content.split())
            if word_count > 300:
                score += 0.2
            elif word_count > 150:
                score += 0.1
            elif word_count < 50:
                score -= 0.2

            # Title engagement
            if title:
                title_lower = title.lower()
                engaging_words = ["breaking", "urgent", "exclusive", "major", "crisis", "update"]
                engaging_count = sum(1 for word in engaging_words if word in title_lower)
                score += min(0.15, engaging_count * 0.05)

            # Script quality
            if script:
                script_words = len(script.split())
                if script_words > 50:
                    score += 0.15
                elif script_words > 20:
                    score += 0.1

                # Check for call-to-action phrases
                cta_phrases = ["stay tuned", "more updates", "follow for more", "breaking news"]
                cta_count = sum(1 for phrase in cta_phrases if phrase in script.lower())
                score += min(0.1, cta_count * 0.05)

            # Content freshness indicators
            time_indicators = ["today", "yesterday", "this morning", "just now", "breaking"]
            time_count = sum(1 for indicator in time_indicators if indicator in content.lower())
            score += min(0.1, time_count * 0.03)

            return max(0.0, min(1.0, score))

        except Exception as e:
            print(f"Engagement score calculation error: {e}")
            return 0.5  # Neutral fallback

    async def _calculate_quality_score(self, content: str, authenticity_score: float, script_output: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-1)"""
        try:
            score = 0.5  # Base score

            # Authenticity contribution (normalized)
            score += (authenticity_score / 100) * 0.4

            # Content structure quality
            sentences = len([s for s in content.split('.') if s.strip()])
            if sentences > 8:
                score += 0.15
            elif sentences > 4:
                score += 0.1

            # Source attribution
            attribution_indicators = ["according to", "source said", "reported by", "official statement"]
            attribution_count = sum(1 for indicator in attribution_indicators if indicator in content.lower())
            score += min(0.15, attribution_count * 0.05)

            # Script quality contribution
            script_length = script_output.get("script_length", 0)
            if script_length > 30:
                score += 0.1
            elif script_length > 15:
                score += 0.05

            # Fact vs opinion balance
            opinion_words = ["i think", "in my opinion", "probably", "maybe", "could be"]
            fact_words = ["confirmed", "verified", "data shows", "research indicates", "according to"]

            opinion_count = sum(1 for word in opinion_words if word in content.lower())
            fact_count = sum(1 for word in fact_words if word in content.lower())

            if fact_count > opinion_count:
                score += 0.1
            elif opinion_count > fact_count + 2:
                score -= 0.1

            return max(0.0, min(1.0, score))

        except Exception as e:
            print(f"Quality score calculation error: {e}")
            return 0.5  # Neutral fallback

    async def check_correction_needed(self, feedback_result: Dict[str, Any]) -> bool:
        """Check if content needs correction based on reward score"""
        reward_score = feedback_result.get("reward_score", 0)
        correction_attempts = feedback_result.get("correction_attempts", 0)

        return reward_score < self.reward_threshold and correction_attempts < self.max_correction_attempts

    async def trigger_correction(self, news_item: Dict[str, Any], feedback_result: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger correction process for low-quality content"""
        try:
            news_item_id = news_item.get("id", "")
            current_attempts = news_item.get("correction_attempts", 0)

            if current_attempts >= self.max_correction_attempts:
                return {
                    "correction_triggered": False,
                    "reason": "Maximum correction attempts reached",
                    "attempts": current_attempts
                }

            # Increment correction attempts
            new_attempts = current_attempts + 1

            # Update news item
            update_data = {
                "correction_attempts": new_attempts,
                "status": "correction_pending",
                "last_correction_attempt": datetime.now().isoformat()
            }

            if db_service.database:
                await db_service.update_news_item(news_item_id, update_data)

            # Trigger re-summarization via Uniguru
            content = news_item.get("content", "")
            if content:
                # Request improved summarization
                summary_result = await uniguru_service.summarize_text(
                    content,
                    max_length=200,
                    style="concise"
                )

                if summary_result.get("success"):
                    improved_summary = summary_result.get("summary")

                    # Generate new script with improved content
                    script_task_data = {
                        "title": news_item.get("title", ""),
                        "content": content,
                        "summary": improved_summary
                    }

                    script_result = await agent_registry.submit_task("script_agent", script_task_data)

                    return {
                        "correction_triggered": True,
                        "attempts": new_attempts,
                        "improved_summary": improved_summary,
                        "new_script_task_id": script_result,
                        "correction_method": "uniguru_resummarization"
                    }

            return {
                "correction_triggered": False,
                "reason": "Unable to generate improved content",
                "attempts": new_attempts
            }

        except Exception as e:
            return {
                "correction_triggered": False,
                "error": f"Correction trigger failed: {str(e)}"
            }

    async def get_feedback_metrics(self, news_item_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Get feedback metrics and statistics"""
        try:
            if not db_service.database:
                return {"error": "Database not connected"}

            if news_item_id:
                # Get feedback for specific news item
                feedback_list = await db_service.get_feedback_by_news_item(news_item_id)
            else:
                # Get recent feedback from all items
                collection = await db_service.get_collection("rl_feedback")
                cursor = collection.find().sort("created_at", -1).limit(limit)
                feedback_list = await cursor.to_list(length=limit)

            if not feedback_list:
                return {"total_feedback": 0, "metrics": {}}

            # Calculate aggregate metrics
            total_feedback = len(feedback_list)
            avg_reward = sum(f.get("reward_score", 0) for f in feedback_list) / total_feedback
            avg_tone = sum(f.get("tone_score", 0) for f in feedback_list) / total_feedback
            avg_engagement = sum(f.get("engagement_score", 0) for f in feedback_list) / total_feedback
            avg_quality = sum(f.get("quality_score", 0) for f in feedback_list) / total_feedback

            corrections_needed = sum(1 for f in feedback_list if f.get("correction_needed", False))
            correction_rate = corrections_needed / total_feedback if total_feedback > 0 else 0

            # Score distribution
            score_ranges = {
                "excellent": sum(1 for f in feedback_list if f.get("reward_score", 0) >= 0.8),
                "good": sum(1 for f in feedback_list if 0.6 <= f.get("reward_score", 0) < 0.8),
                "needs_improvement": sum(1 for f in feedback_list if 0.4 <= f.get("reward_score", 0) < 0.6),
                "poor": sum(1 for f in feedback_list if f.get("reward_score", 0) < 0.4)
            }

            return {
                "total_feedback": total_feedback,
                "metrics": {
                    "average_reward_score": round(avg_reward, 3),
                    "average_tone_score": round(avg_tone, 3),
                    "average_engagement_score": round(avg_engagement, 3),
                    "average_quality_score": round(avg_quality, 3),
                    "correction_rate": round(correction_rate, 3),
                    "score_distribution": score_ranges
                },
                "recent_feedback": feedback_list[:10],  # Last 10 feedback entries
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Metrics retrieval failed: {str(e)}"}

    def _get_adaptive_weights(self) -> Dict[str, float]:
        """Calculate adaptive weights based on performance history"""
        if len(self.performance_history) < 10:
            print(f"DEBUG: Not enough performance history ({len(self.performance_history)}), using defaults")
            return self.scaling_factors  # Not enough data, use defaults

        # Analyze recent performance to adjust weights
        recent_scores = [p["reward_score"] for p in self.performance_history[-20:]]
        avg_recent_reward = sum(recent_scores) / len(recent_scores)
        correction_rate_recent = sum(1 for p in self.performance_history[-20:] if p["correction_needed"]) / len(self.performance_history[-20:])

        print(f"DEBUG: Adaptive weights - avg_recent_reward: {avg_recent_reward:.3f}, correction_rate: {correction_rate_recent:.3f}")

        # If recent performance is good, emphasize quality
        # If recent performance needs improvement, emphasize engagement
        if avg_recent_reward > 0.7:
            # High performance: focus on maintaining quality
            weights = {
                "tone_weight": 0.25,
                "engagement_weight": 0.35,
                "quality_weight": 0.4
            }
            print(f"DEBUG: High performance detected, using quality-focused weights: {weights}")
            return weights
        elif avg_recent_reward < 0.5:
            # Low performance: boost engagement to improve scores
            weights = {
                "tone_weight": 0.2,
                "engagement_weight": 0.5,
                "quality_weight": 0.3
            }
            print(f"DEBUG: Low performance detected, using engagement-focused weights: {weights}")
            return weights
        else:
            # Medium performance: balanced approach
            print(f"DEBUG: Medium performance, using balanced weights: {self.scaling_factors}")
            return self.scaling_factors

    def _update_session_stats(self, reward_score: float, correction_needed: bool, latency: float):
        """Update session statistics"""
        self.session_stats["total_evaluations"] += 1

        # Rolling average for mean reward
        current_count = self.session_stats["total_evaluations"]
        current_mean = self.session_stats["mean_reward"]
        self.session_stats["mean_reward"] = (current_mean * (current_count - 1) + reward_score) / current_count

        # Update correction rate
        corrections = sum(1 for p in self.performance_history if p["correction_needed"])
        self.session_stats["correction_rate"] = corrections / len(self.performance_history) if self.performance_history else 0

        # Update average latency
        current_latency_avg = self.session_stats["avg_latency"]
        self.session_stats["avg_latency"] = (current_latency_avg * (current_count - 1) + latency) / current_count

    async def _log_rl_event(self, feedback_data: Dict[str, Any]):
        """Log RL event to JSONL file"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "rl_evaluation",
                "data": feedback_data,
                "session_stats": self.session_stats.copy()
            }

            with open(self.metrics_file, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False)
                f.write('\n')

        except Exception as e:
            print(f"Failed to log RL event: {e}")

    async def generate_test_dataset(self, num_cases: int = 10) -> List[Dict[str, Any]]:
        """Generate a test dataset for RL improvements testing"""
        test_cases = []

        # Sample news content templates
        news_templates = [
            {
                "title": "Breaking: Major Tech Breakthrough Announced",
                "content": "A revolutionary new technology has been announced today that promises to change the way we live. Scientists have developed an innovative solution that addresses long-standing challenges in the field. The breakthrough comes after years of research and development.",
                "authenticity_score": 85,
                "expected_quality": "high"
            },
            {
                "title": "Local Event Draws Small Crowd",
                "content": "A community event took place yesterday with limited attendance. The organizers had hoped for more participation but weather conditions may have affected turnout. The event featured local vendors and entertainment.",
                "authenticity_score": 60,
                "expected_quality": "medium"
            },
            {
                "title": "URGENT: Crisis Situation Developing",
                "content": "EMERGENCY ALERT: A serious situation is unfolding that requires immediate attention. Authorities are responding to reports of unusual activity. Stay tuned for updates as more information becomes available.",
                "authenticity_score": 75,
                "expected_quality": "high_engagement"
            },
            {
                "title": "New Study Shows Interesting Results",
                "content": "Researchers have published findings from a recent study. The results indicate some trends that may be worth noting. Further research is needed to confirm these observations.",
                "authenticity_score": 70,
                "expected_quality": "medium"
            },
            {
                "title": "Celebrity Makes Surprise Announcement",
                "content": "In a shocking turn of events, a famous celebrity has made a major life decision. Fans around the world are reacting to the news with mixed emotions. Social media is buzzing with reactions and speculation.",
                "authenticity_score": 55,
                "expected_quality": "high_engagement"
            }
        ]

        for i in range(num_cases):
            # Select template based on case number
            template = news_templates[i % len(news_templates)]

            # Generate script output (simulated)
            script_output = {
                "video_script": f"Today we're covering: {template['title']}. {template['content'][:100]}... Stay tuned for more updates.",
                "tone": "neutral",
                "language": "en"
            }

            test_case = {
                "case_id": f"test_case_{i+1}",
                "news_item": {
                    "id": f"test_news_{i+1}",
                    "title": template["title"],
                    "content": template["content"],
                    "authenticity_score": template["authenticity_score"]
                },
                "script_output": script_output,
                "expected_category": template["expected_quality"],
                "generated_at": datetime.now().isoformat()
            }

            test_cases.append(test_case)

        return test_cases

    async def run_rl_test_suite(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run RL evaluation on test dataset and return comprehensive results"""
        results = []
        start_time = datetime.now()

        for test_case in test_cases:
            try:
                feedback = await self.calculate_reward(
                    test_case["news_item"],
                    test_case["script_output"]
                )

                result = {
                    "case_id": test_case["case_id"],
                    "expected_category": test_case["expected_category"],
                    "actual_reward": feedback["reward_score"],
                    "tone_score": feedback["tone_score"],
                    "engagement_score": feedback["engagement_score"],
                    "quality_score": feedback["quality_score"],
                    "correction_needed": feedback["correction_needed"],
                    "latency": feedback["metrics"]["latency_seconds"]
                }

                results.append(result)

            except Exception as e:
                results.append({
                    "case_id": test_case["case_id"],
                    "error": str(e),
                    "expected_category": test_case["expected_category"]
                })

        # Calculate aggregate metrics
        successful_results = [r for r in results if "actual_reward" in r]

        if successful_results:
            avg_reward = sum(r["actual_reward"] for r in successful_results) / len(successful_results)
            avg_latency = sum(r["latency"] for r in successful_results) / len(successful_results)
            correction_rate = sum(1 for r in successful_results if r["correction_needed"]) / len(successful_results)

            # Category performance
            category_performance = {}
            for result in successful_results:
                cat = result["expected_category"]
                if cat not in category_performance:
                    category_performance[cat] = []
                category_performance[cat].append(result["actual_reward"])

            for cat in category_performance:
                category_performance[cat] = {
                    "avg_reward": sum(category_performance[cat]) / len(category_performance[cat]),
                    "count": len(category_performance[cat])
                }
        else:
            avg_reward = avg_latency = correction_rate = 0
            category_performance = {}

        return {
            "test_summary": {
                "total_cases": len(test_cases),
                "successful_evaluations": len(successful_results),
                "avg_reward": round(avg_reward, 3),
                "avg_latency": round(avg_latency, 3),
                "correction_rate": round(correction_rate, 3)
            },
            "category_performance": category_performance,
            "detailed_results": results,
            "test_duration": (datetime.now() - start_time).total_seconds(),
            "generated_at": datetime.now().isoformat()
        }

# Global instance
rl_feedback_service = RLFeedbackService()