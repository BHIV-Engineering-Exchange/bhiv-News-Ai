from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

class NewsItem(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    url: str
    title: str
    content: str
    summary: Optional[str] = None
    status: str = "raw"  # raw, verified, published
    authenticity_score: Optional[float] = None
    categories: List[str] = []
    tags: List[str] = []
    author: Optional[Dict[str, str]] = None
    publication_date: Optional[str] = None
    scraped_at: str
    verified_at: Optional[str] = None
    published_at: Optional[str] = None
    source_credibility: Optional[Dict[str, Any]] = None
    sentiment_analysis: Optional[Dict[str, Any]] = None
    video_search_results: Optional[List[Dict[str, Any]]] = None
    processing_metrics: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class AgentTask(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    agent_id: str
    task_type: str  # fetch, filter, verify, script, rl_feedback
    priority: int = 1
    status: str = "pending"  # pending, processing, completed, failed
    data: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None

class RLFeedback(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    news_item_id: str
    reward_score: float
    tone_score: float
    engagement_score: float
    correction_needed: bool = False
    correction_attempts: int = 0
    final_output: Dict[str, Any]
    metrics: Dict[str, Any]
    created_at: str