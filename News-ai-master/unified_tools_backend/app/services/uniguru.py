import httpx
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class UniguruService:
    def __init__(self):
        self.base_url = os.getenv("UNIGURU_BASE_URL", "https://api.uniguru.com")
        self.api_key = os.getenv("UNIGURU_API_KEY")
        self.timeout = 30.0
        self.max_retries = 3
        self.fallback_enabled = True

    async def classify_text(self, text: str, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Classify text content using Uniguru API with fallback"""
        try:
            if not self.api_key:
                if self.fallback_enabled:
                    return await self._fallback_classify_text(text, categories)
                return {"error": "Uniguru API key not configured"}

            url = f"{self.base_url}/classify"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "text": text[:5000],  # Limit text length
                "categories": categories or ["news", "sports", "politics", "technology", "entertainment"]
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "categories": result.get("categories", []),
                        "confidence_scores": result.get("confidence_scores", {}),
                        "primary_category": result.get("primary_category", ""),
                        "processed_at": datetime.now().isoformat()
                    }
                else:
                    # Try fallback on API failure
                    if self.fallback_enabled and response.status_code >= 500:
                        return await self._fallback_classify_text(text, categories)
                    return {"error": f"Classification failed: {response.status_code}"}

        except Exception as e:
            # Try fallback on exception
            if self.fallback_enabled:
                return await self._fallback_classify_text(text, categories)
            return {"error": f"Uniguru classification error: {str(e)}"}

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using Uniguru API with fallback"""
        try:
            if not self.api_key:
                if self.fallback_enabled:
                    return await self._fallback_analyze_sentiment(text)
                return {"error": "Uniguru API key not configured"}

            url = f"{self.base_url}/sentiment"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {"text": text[:5000]}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "sentiment": result.get("sentiment", "neutral"),
                        "polarity": result.get("polarity", 0.0),
                        "confidence": result.get("confidence", 0.0),
                        "processed_at": datetime.now().isoformat()
                    }
                else:
                    # Try fallback on API failure
                    if self.fallback_enabled and response.status_code >= 500:
                        return await self._fallback_analyze_sentiment(text)
                    return {"error": f"Sentiment analysis failed: {response.status_code}"}

        except Exception as e:
            # Try fallback on exception
            if self.fallback_enabled:
                return await self._fallback_analyze_sentiment(text)
            return {"error": f"Uniguru sentiment error: {str(e)}"}

    async def summarize_text(self, text: str, max_length: int = 150, style: str = "concise") -> Dict[str, Any]:
        """Summarize text using Uniguru API with fallback"""
        try:
            if not self.api_key:
                if self.fallback_enabled:
                    return await self._fallback_summarize_text(text, max_length)
                return {"error": "Uniguru API key not configured"}

            url = f"{self.base_url}/summarize"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "text": text[:10000],  # Limit text length
                "max_length": max_length,
                "style": style
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "summary": result.get("summary", ""),
                        "original_length": len(text),
                        "summary_length": len(result.get("summary", "")),
                        "compression_ratio": len(result.get("summary", "")) / len(text) if text else 0,
                        "processed_at": datetime.now().isoformat()
                    }
                else:
                    # Try fallback on API failure
                    if self.fallback_enabled and response.status_code >= 500:
                        return await self._fallback_summarize_text(text, max_length)
                    return {"error": f"Summarization failed: {response.status_code}"}

        except Exception as e:
            # Try fallback on exception
            if self.fallback_enabled:
                return await self._fallback_summarize_text(text, max_length)
            return {"error": f"Uniguru summarization error: {str(e)}"}

    # Fallback Methods
    async def _fallback_classify_text(self, text: str, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fallback classification using simple keyword matching"""
        try:
            categories_list = categories or ["news", "sports", "politics", "technology", "entertainment"]
            text_lower = text.lower()

            # Simple keyword-based classification
            scores = {}
            for category in categories_list:
                keywords = self._get_category_keywords(category)
                score = sum(1 for keyword in keywords if keyword in text_lower)
                scores[category] = min(score / len(keywords), 1.0) if keywords else 0.0

            # Find primary category
            primary_category = max(scores.keys(), key=lambda x: scores[x]) if scores else "news"

            return {
                "success": True,
                "categories": list(scores.keys()),
                "confidence_scores": scores,
                "primary_category": primary_category,
                "fallback_used": True,
                "processed_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Fallback classification failed: {str(e)}"}

    async def _fallback_analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using simple rules"""
        try:
            text_lower = text.lower()
            positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like", "best"]
            negative_words = ["bad", "terrible", "awful", "hate", "worst", "disappointing", "poor", "fail"]

            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if positive_count > negative_count:
                sentiment = "positive"
                polarity = 0.5
            elif negative_count > positive_count:
                sentiment = "negative"
                polarity = -0.5
            else:
                sentiment = "neutral"
                polarity = 0.0

            return {
                "success": True,
                "sentiment": sentiment,
                "polarity": polarity,
                "confidence": 0.6,  # Lower confidence for fallback
                "fallback_used": True,
                "processed_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Fallback sentiment analysis failed: {str(e)}"}

    async def _fallback_summarize_text(self, text: str, max_length: int = 150) -> Dict[str, Any]:
        """Fallback summarization using extractive method"""
        try:
            sentences = text.split('.')
            # Simple extractive summarization: take first and last sentences
            if len(sentences) >= 2:
                summary = sentences[0].strip() + '. ' + sentences[-1].strip() + '.'
            else:
                summary = text[:max_length]

            # Ensure summary doesn't exceed max_length
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."

            return {
                "success": True,
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary),
                "compression_ratio": len(summary) / len(text) if text else 0,
                "fallback_used": True,
                "processed_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Fallback summarization failed: {str(e)}"}

    def _get_category_keywords(self, category: str) -> List[str]:
        """Get keywords for category-based fallback classification"""
        keyword_map = {
            "news": ["news", "report", "update", "breaking", "announcement"],
            "sports": ["game", "team", "player", "score", "match", "tournament"],
            "politics": ["government", "election", "policy", "minister", "president"],
            "technology": ["software", "hardware", "app", "digital", "tech", "innovation"],
            "entertainment": ["movie", "music", "celebrity", "show", "film", "actor"]
        }
        return keyword_map.get(category, [])

# Global instance
uniguru_service = UniguruService()