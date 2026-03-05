#!/usr/bin/env python3
"""
Hardening Tests for RL Correction Thresholds and Uniguru Fallback Logic
Tests deterministic behavior and repeatable fallback mechanisms
"""

import asyncio
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rl.feedback_service import RLFeedbackService, rl_feedback_service
from app.services.uniguru import UniguruService, uniguru_service


class TestRLCorrectionThresholds(unittest.TestCase):
    """Test RL correction thresholds and deterministic behavior"""

    def setUp(self):
        self.rl_service = RLFeedbackService()
        self.sample_news_item = {
            "id": "test_news_001",
            "title": "Breaking: Major Technology Breakthrough",
            "content": "Scientists have announced a revolutionary new technology that promises to transform the industry. The breakthrough comes after years of intensive research and development.",
            "authenticity_score": 85
        }
        self.sample_script_output = {
            "video_script": "Breaking news: Scientists announce revolutionary technology breakthrough with potential to transform multiple industries."
        }

    def test_reward_threshold_06_triggers_correction(self):
        """Test that reward scores below 0.6 trigger correction"""
        # Mock very low-quality content that should definitely score below 0.6
        low_quality_news = {
            "id": "test_low_quality",
            "title": "News",
            "content": "Bad.",  # Extremely short, low quality
            "authenticity_score": 10  # Very low authenticity
        }
        low_quality_script = {
            "video_script": "Bad."  # Very short script
        }

        # Calculate reward
        result = asyncio.run(self.rl_service.calculate_reward(low_quality_news, low_quality_script))

        # Assert correction is needed
        self.assertTrue(result["correction_needed"], f"Low quality content should trigger correction, score: {result['reward_score']}")
        self.assertLess(result["reward_score"], 0.6, f"Reward score should be below 0.6, got: {result['reward_score']}")

    def test_reward_threshold_06_no_correction_when_above(self):
        """Test that reward scores above 0.6 do not trigger correction"""
        # Use high-quality sample content with better attributes
        high_quality_news = {
            "id": "test_high_quality",
            "title": "Breaking: Major Scientific Breakthrough Announced Today",
            "content": "According to leading researchers at the institute, a revolutionary new technology has been developed that promises to transform multiple industries. The breakthrough, confirmed by independent experts, comes after years of rigorous scientific research and development. Industry analysts state that this innovation could have far-reaching implications for healthcare, transportation, and communication sectors. The announcement was made at a prestigious international conference where scientists gathered to discuss future technological advancements.",
            "authenticity_score": 95  # High authenticity
        }
        high_quality_script = {
            "video_script": "Breaking news: Scientists have announced a revolutionary breakthrough in technology. According to researchers, this development could transform healthcare, transportation, and communication. Stay tuned for more updates on this major scientific advancement."
        }

        result = asyncio.run(self.rl_service.calculate_reward(high_quality_news, high_quality_script))

        # Assert score is above threshold
        self.assertGreaterEqual(result["reward_score"], 0.6, f"High quality content should score >= 0.6, got {result['reward_score']}")

    def test_max_correction_attempts_3(self):
        """Test that maximum correction attempts is 3"""
        self.assertEqual(self.rl_service.max_correction_attempts, 3, "Max correction attempts should be 3")

        # Test with attempts at limit
        news_with_max_attempts = self.sample_news_item.copy()
        news_with_max_attempts["correction_attempts"] = 3

        correction_result = asyncio.run(self.rl_service.trigger_correction(news_with_max_attempts, {"reward_score": 0.3}))
        self.assertFalse(correction_result["correction_triggered"], "Should not trigger correction at max attempts")
        self.assertEqual(correction_result["attempts"], 3, "Attempts should remain at max")

    def test_correction_attempts_increment(self):
        """Test that correction attempts increment properly"""
        news_item = self.sample_news_item.copy()
        news_item["correction_attempts"] = 1

        # Mock the database and agent calls
        with patch.object(self.rl_service, '_get_adaptive_weights', return_value={"tone_weight": 0.3, "engagement_weight": 0.4, "quality_weight": 0.3}):
            correction_result = asyncio.run(self.rl_service.trigger_correction(news_item, {"reward_score": 0.3}))

        # Should increment attempts
        self.assertEqual(correction_result["attempts"], 2, "Correction attempts should increment")

    def test_adaptive_weights_based_on_performance(self):
        """Test that adaptive weights adjust based on recent performance"""
        # Simulate low performance history
        self.rl_service.performance_history = [
            {"reward_score": 0.4, "correction_needed": True},
            {"reward_score": 0.3, "correction_needed": True},
            {"reward_score": 0.5, "correction_needed": True}
        ]

        weights = self.rl_service._get_adaptive_weights()
        # Should boost engagement for low performance
        self.assertGreater(weights["engagement_weight"], weights["quality_weight"], "Should boost engagement for low performance")

    def test_deterministic_reward_calculation(self):
        """Test that reward calculation is deterministic for same inputs"""
        # Run calculation multiple times
        results = []
        for _ in range(3):
            result = asyncio.run(self.rl_service.calculate_reward(self.sample_news_item, self.sample_script_output))
            results.append(result["reward_score"])

        # All results should be identical (deterministic)
        self.assertEqual(len(set(results)), 1, "Reward calculation should be deterministic")


class TestUniguruFallbackLogic(unittest.TestCase):
    """Test Uniguru fallback mechanisms"""

    def setUp(self):
        self.uniguru_service = UniguruService()
        self.sample_text = "This is a sample news article about technology and innovation."

    def test_fallback_when_no_api_key(self):
        """Test fallback activation when API key is not configured"""
        # Temporarily remove API key
        original_key = self.uniguru_service.api_key
        self.uniguru_service.api_key = None

        try:
            result = asyncio.run(self.uniguru_service.classify_text(self.sample_text))
            self.assertTrue(result["success"], "Fallback should work when no API key")
            self.assertIn("fallback_used", result, "Should indicate fallback was used")
        finally:
            self.uniguru_service.api_key = original_key

    def test_fallback_on_api_failure(self):
        """Test fallback activation on API failure"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock API failure
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            result = asyncio.run(self.uniguru_service.classify_text(self.sample_text))
            self.assertTrue(result["success"], "Fallback should work on API failure")
            self.assertIn("fallback_used", result, "Should indicate fallback was used")

    def test_fallback_sentiment_analysis(self):
        """Test fallback sentiment analysis logic"""
        positive_text = "This is amazing and wonderful news!"
        negative_text = "This is terrible and disappointing."
        neutral_text = "This is a news article."

        # Test positive
        result_pos = asyncio.run(self.uniguru_service._fallback_analyze_sentiment(positive_text))
        self.assertEqual(result_pos["sentiment"], "positive")
        self.assertGreater(result_pos["polarity"], 0)

        # Test negative
        result_neg = asyncio.run(self.uniguru_service._fallback_analyze_sentiment(negative_text))
        self.assertEqual(result_neg["sentiment"], "negative")
        self.assertLess(result_neg["polarity"], 0)

        # Test neutral
        result_neutral = asyncio.run(self.uniguru_service._fallback_analyze_sentiment(neutral_text))
        self.assertEqual(result_neutral["sentiment"], "neutral")
        self.assertEqual(result_neutral["polarity"], 0.0)

    def test_fallback_classification(self):
        """Test fallback classification logic"""
        tech_text = "New software technology breakthrough announced today."
        sports_text = "Team wins championship game with amazing performance."
        politics_text = "Government announces new policy changes."

        # Test technology classification
        result_tech = asyncio.run(self.uniguru_service._fallback_classify_text(tech_text))
        self.assertIn("technology", result_tech["categories"])
        self.assertEqual(result_tech["primary_category"], "technology")

        # Test sports classification
        result_sports = asyncio.run(self.uniguru_service._fallback_classify_text(sports_text))
        self.assertIn("sports", result_sports["categories"])

        # Test politics classification
        result_politics = asyncio.run(self.uniguru_service._fallback_classify_text(politics_text))
        self.assertIn("politics", result_politics["categories"])

    def test_fallback_summarization(self):
        """Test fallback summarization logic"""
        long_text = "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence. This is the fifth sentence."

        result = asyncio.run(self.uniguru_service._fallback_summarize_text(long_text, max_length=100))
        self.assertTrue(result["success"])
        self.assertLessEqual(len(result["summary"]), 100)
        # The fallback takes first and last sentences
        self.assertIn("first sentence", result["summary"])  # Should include first sentence
        # Check that it includes some content from the text
        self.assertGreater(len(result["summary"]), 20)

    def test_fallback_deterministic(self):
        """Test that fallback methods are deterministic"""
        text = "Sample text for testing determinism."

        # Run classification multiple times
        results = []
        for _ in range(3):
            result = asyncio.run(self.uniguru_service._fallback_classify_text(text))
            results.append(result["primary_category"])

        # Should be consistent
        self.assertEqual(len(set(results)), 1, "Fallback classification should be deterministic")


class TestRLUniguruIntegration(unittest.TestCase):
    """Test integration between RL and Uniguru services"""

    def setUp(self):
        self.rl_service = RLFeedbackService()
        self.uniguru_service = UniguruService()

    def test_rl_uses_uniguru_fallback_in_tone_calculation(self):
        """Test that RL tone calculation uses Uniguru fallback when API fails"""
        # Mock Uniguru sentiment failure
        with patch.object(self.uniguru_service, 'analyze_sentiment', side_effect=Exception("API Error")):
            # This should trigger fallback in tone calculation
            news_item = {
                "content": "This is positive news about technology.",
                "title": "Good News",
                "authenticity_score": 80
            }
            script = {"video_script": "Good news about technology."}

            result = asyncio.run(self.rl_service.calculate_reward(news_item, script))

            # Should still calculate tone score using fallback
            self.assertIn("tone_score", result)
            self.assertIsInstance(result["tone_score"], float)

    def test_rl_fallback_performance_consistency(self):
        """Test that RL performance is consistent even with fallbacks"""
        news_item = {
            "content": "Technology breakthrough announced.",
            "title": "Tech News",
            "authenticity_score": 75
        }
        script = {"video_script": "Technology breakthrough announced."}

        # Run multiple times to ensure consistency
        results = []
        for _ in range(5):
            with patch.object(self.uniguru_service, 'analyze_sentiment', side_effect=Exception("API Error")):
                result = asyncio.run(self.rl_service.calculate_reward(news_item, script))
                results.append(result["reward_score"])

        # Should be reasonably consistent (within 0.1 range due to fallback)
        max_diff = max(results) - min(results)
        self.assertLess(max_diff, 0.1, "RL scores should be consistent even with fallbacks")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)