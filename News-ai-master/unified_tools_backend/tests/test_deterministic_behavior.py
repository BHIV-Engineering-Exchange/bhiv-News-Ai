#!/usr/bin/env python3
"""
Deterministic Behavior Tests for News AI Backend

Tests that RL feedback and fallback logic produce consistent, deterministic outputs
across multiple runs with identical inputs.
"""

import unittest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any

# Import the services we want to test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rl.feedback_service import rl_feedback_service
from app.services.uniguru import uniguru_service
from pipeline.automator import automator
from unified_pipeline import unified_pipeline


class TestDeterministicRLFeedback(unittest.TestCase):
    """Test deterministic behavior of RL feedback calculations"""

    def setUp(self):
        """Set up test fixtures with fixed inputs"""
        self.test_news_item = {
            "title": "Test News Article",
            "content": "This is a test news article content for deterministic testing.",
            "summary": "Test summary",
            "categories": ["technology", "business"],
            "sentiment": {
                "polarity": 0.2,
                "subjectivity": 0.3,
                "confidence": 0.85
            },
            "authenticity_score": 0.92
        }

        self.test_script_output = {
            "video_prompt": "Create a video about test news",
            "tone": "neutral",
            "language": "en",
            "avatar_ready": True,
            "corrections_applied": 0
        }

    def test_rl_feedback_deterministic(self):
        """Test that RL feedback produces identical results across runs"""
        results = []

        # Run feedback calculation 5 times
        for i in range(5):
            with patch('rl.feedback_service.datetime') as mock_datetime:
                # Fix timestamp for determinism
                mock_datetime.now.return_value.isoformat.return_value = "2024-01-14T12:00:00.000Z"

                result = rl_feedback_service.calculate_reward(
                    self.test_news_item,
                    self.test_script_output
                )
                results.append(result)

        # All results should be identical
        for i in range(1, len(results)):
            self.assertEqual(results[0], results[i],
                           f"RL feedback result {i} differs from first result")

    def test_rl_feedback_structure_consistent(self):
        """Test that RL feedback always returns the same structure"""
        required_fields = [
            "reward_score", "quality_gate_passed", "corrections_applied",
            "feedback_details", "timestamp"
        ]

        result = rl_feedback_service.calculate_reward(
            self.test_news_item,
            self.test_script_output
        )

        for field in required_fields:
            self.assertIn(field, result, f"Required field '{field}' missing from RL feedback")

    def test_rl_quality_gate_deterministic(self):
        """Test that quality gate decisions are deterministic"""
        gate_results = []

        for i in range(10):
            result = rl_feedback_service.calculate_reward(
                self.test_news_item,
                self.test_script_output
            )
            gate_results.append(result["quality_gate_passed"])

        # Quality gate should be consistent
        first_result = gate_results[0]
        for result in gate_results[1:]:
            self.assertEqual(first_result, result,
                           "Quality gate decision is not deterministic")


class TestDeterministicUniguruFallback(unittest.TestCase):
    """Test deterministic behavior of Uniguru service with fallbacks"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_text = "This is a test text for summarization and analysis."
        self.max_length = 50

    @patch('app.services.uniguru.requests.post')
    def test_summarize_deterministic(self, mock_post):
        """Test that summarization produces consistent results"""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "summary": "Test summary result",
            "success": True
        }
        mock_post.return_value = mock_response

        results = []

        # Run summarization 5 times
        for i in range(5):
            result = uniguru_service.summarize_text(self.test_text, self.max_length)
            results.append(result)

        # All results should be identical
        for i in range(1, len(results)):
            self.assertEqual(results[0], results[i],
                           f"Summarization result {i} differs from first result")

    @patch('app.services.uniguru.requests.post')
    def test_sentiment_analysis_deterministic(self, mock_post):
        """Test that sentiment analysis produces consistent results"""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "sentiment": "positive",
            "confidence": 0.85,
            "success": True
        }
        mock_post.return_value = mock_response

        results = []

        # Run sentiment analysis 5 times
        for i in range(5):
            result = uniguru_service.analyze_sentiment(self.test_text)
            results.append(result)

        # All results should be identical
        for i in range(1, len(results)):
            self.assertEqual(results[0], results[i],
                           f"Sentiment result {i} differs from first result")


class TestDeterministicPipelineFallback(unittest.TestCase):
    """Test deterministic behavior of pipeline with fallback logic"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_url = "https://example.com/test-article"
        self.test_options = {
            "enable_bhiv_push": True,
            "channels": ["test_channel"],
            "avatars": ["test_avatar"]
        }

    @patch('pipeline.automator.unified_pipeline')
    @patch('pipeline.automator.rl_feedback_service')
    def test_pipeline_fallback_deterministic(self, mock_rl, mock_pipeline):
        """Test that pipeline fallback logic is deterministic"""
        # Mock pipeline success
        mock_pipeline.process_news.return_value = {
            "success": True,
            "news_item": {"title": "Test", "content": "Content"},
            "script": {"video_prompt": "Prompt"},
            "rl_feedback": {"reward_score": 0.8},
            "bhiv_push": {"successful": True}
        }

        # Mock RL service
        mock_rl.calculate_reward.return_value = {
            "reward_score": 0.8,
            "quality_gate_passed": True,
            "corrections_applied": 0
        }

        results = []

        # Run pipeline 5 times
        for i in range(5):
            result = automator.process_news_url(self.test_url)
            results.append(result)

        # All results should be identical
        for i in range(1, len(results)):
            self.assertEqual(results[0], results[i],
                           f"Pipeline result {i} differs from first result")

    @patch('pipeline.automator.unified_pipeline')
    def test_pipeline_error_handling_deterministic(self, mock_pipeline):
        """Test that error handling and fallbacks are deterministic"""
        # Mock pipeline failure
        mock_pipeline.process_news.side_effect = Exception("Processing failed")

        results = []

        # Run pipeline 5 times with failure
        for i in range(5):
            try:
                result = automator.process_news_url(self.test_url)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})

        # All error results should be identical
        for i in range(1, len(results)):
            self.assertEqual(results[0], results[i],
                           f"Error handling result {i} differs from first result")


class TestDeterministicUnifiedPipeline(unittest.TestCase):
    """Test deterministic behavior of the unified pipeline"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_request = {
            "url": "https://example.com/test-news",
            "options": {
                "enable_bhiv_push": True,
                "channels": ["test_channel"],
                "avatars": ["test_avatar"],
                "voice": "neutral"
            }
        }

    @patch('unified_pipeline.unified_pipeline')
    @patch('unified_pipeline.rl_feedback_service')
    @patch('unified_pipeline.bhiv_service')
    def test_unified_pipeline_deterministic(self, mock_bhiv, mock_rl, mock_pipeline):
        """Test that unified pipeline produces deterministic results"""
        # Mock all dependencies
        mock_pipeline.extract_news.return_value = {
            "title": "Test News",
            "content": "Test content",
            "summary": "Test summary",
            "categories": ["test"],
            "sentiment": {"polarity": 0.1},
            "authenticity_score": 0.9
        }

        mock_pipeline.generate_script.return_value = {
            "video_prompt": "Test prompt",
            "tone": "neutral",
            "language": "en",
            "avatar_ready": True
        }

        mock_rl.calculate_reward.return_value = {
            "reward_score": 0.8,
            "quality_gate_passed": True,
            "corrections_applied": 0
        }

        mock_bhiv.push_to_bhiv_core.return_value = {
            "successful": True,
            "channels": ["test_channel"],
            "successful_pushes": 1
        }

        results = []

        # Run unified pipeline 5 times
        for i in range(5):
            result = unified_pipeline.process_news(self.test_request)
            results.append(result)

        # All results should be identical
        for i in range(1, len(results)):
            self.assertEqual(results[0], results[i],
                           f"Unified pipeline result {i} differs from first result")


class TestDeterministicCorrections(unittest.TestCase):
    """Test deterministic behavior of RL correction thresholds"""

    def setUp(self):
        """Set up test fixtures"""
        self.low_quality_news = {
            "title": "Poor Quality News",
            "content": "This is very short content.",
            "summary": "Short",
            "categories": ["unknown"],
            "sentiment": {"polarity": -0.8, "confidence": 0.3},
            "authenticity_score": 0.4
        }

        self.high_quality_script = {
            "video_prompt": "High quality video prompt with good structure",
            "tone": "professional",
            "language": "en",
            "avatar_ready": True
        }

    def test_correction_thresholds_deterministic(self):
        """Test that correction thresholds produce consistent decisions"""
        correction_results = []

        for i in range(10):
            result = rl_feedback_service.calculate_reward(
                self.low_quality_news,
                self.high_quality_script
            )
            correction_results.append(result["corrections_applied"])

        # Correction count should be consistent
        first_result = correction_results[0]
        for result in correction_results[1:]:
            self.assertEqual(first_result, result,
                           "Correction threshold decision is not deterministic")


if __name__ == '__main__':
    unittest.main(verbosity=2)