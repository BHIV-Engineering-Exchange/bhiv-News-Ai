from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import httpx

router = APIRouter()

NOOPUR_NODE_BASE_URL = os.getenv("NOOPUR_NODE_BASE_URL", "http://localhost:3000")
SANKALP_API_BASE = os.getenv("SANKALP_API_BASE", "http://localhost:8000")

class PreviewItem(BaseModel):
    title: Optional[str] = None
    lang: Optional[str] = None
    audience: Optional[str] = None
    tone: Optional[str] = None
    variants: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

class RunPipelineRequest(BaseModel):
    url: Optional[str] = Field(default=None, description="Input URL for scraping via unified tools (optional)")
    title: Optional[str] = Field(default=None, description="News title (optional if url provided)")
    content: Optional[str] = Field(default=None, description="News content (optional if url provided)")
    language: Optional[str] = Field(default="en", description="Content language code", pattern="^[a-z]{2}(-[A-Z]{2})?$")
    tone: Optional[str] = Field(default="neutral", description="Desired tone", pattern="^(neutral|informative|urgent|optimistic|serious|excited)$")
    avatar_ready: Optional[bool] = Field(default=False, description="Whether avatar/voice assets are ready")

class RunPipelineResponse(BaseModel):
    success: bool
    timestamp: str
    newsItemId: Optional[str]
    counts: Dict[str, int]
    preview: List[PreviewItem]
    pipeline: Dict[str, Any]
    seeya_compat: Optional[Dict[str, Any]]
    audio: Optional[Dict[str, Any]]

async def _check_uniguru_health() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{NOOPUR_NODE_BASE_URL}/health")
            if resp.status_code == 200:
                data = resp.json()
                return True if data else True
    except Exception:
        pass
    return False

async def _create_news(title: str, content: str) -> str:
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            f"{NOOPUR_NODE_BASE_URL}/api/news",
            json={"title": title, "content": content, "source": "unified"},
        )
        if resp.status_code != 201 and resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"create_news_failed: {resp.text}")
        data = resp.json()
        return str(data.get("newsId") or data.get("id"))

async def _process_bhiv(news_item_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{NOOPUR_NODE_BASE_URL}/api/bhiv/process",
            json={"newsItemId": news_item_id},
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"bhiv_process_failed: {resp.text}")
        data = resp.json()
        if isinstance(data, dict):
            data.setdefault('pipelineResult', {})
            data.setdefault('bhivResult', {})
            data.setdefault('newsItem', {})
            data.setdefault('seeya_compat', None)
        return data

async def _sankalp_audio(title: str, summary: str, tone: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            payload = {"task_type": "summary", "subject": title, "style": "professional", "tone": tone, "length": "short", "additional_context": summary}
            resp = await client.post(f"{SANKALP_API_BASE}/api/prompt", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return {"status": "ok", "prompt": data.get("prompt"), "metadata": data.get("metadata")}
    except Exception:
        return {"status": "fallback", "prompt": f"Voice-over for: {title}. Tone: {tone}. Summary: {summary[:200]}..."}
    return {"status": "none"}

def _build_preview(pipeline_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    script_stage = pipeline_result.get("pipelineResult", {}).get("script")
    preview: List[Dict[str, Any]] = []
    if isinstance(script_stage, dict):
        items = script_stage.get("items") or []
        for s in items[:10]:
            preview.append({
                "title": s.get("title"),
                "lang": s.get("lang"),
                "audience": s.get("audience"),
                "tone": s.get("tone"),
                "variants": s.get("variants"),
                "metadata": s.get("metadata"),
            })
    return preview

@router.post("/v1/run_pipeline", response_model=RunPipelineResponse)
async def run_pipeline(req: RunPipelineRequest):
    try:
        if not req.title and not req.url:
            raise HTTPException(status_code=400, detail="title or url is required")

        title = req.title or "Untitled"
        content = req.content or ""

        if req.url and not req.content:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    ur = await client.post(f"{SANKALP_API_BASE}/api/unified-news-workflow", json={"url": req.url})
                    if ur.status_code == 200:
                        ud = ur.json()
                        scraped = ud.get("data") or ud.get("scraped_data") or {}
                        title = scraped.get("title") or title
                        content = scraped.get("content") or content
            except Exception:
                pass

        uniguru_ok = await _check_uniguru_health()
        news_id = await _create_news(title, content)
        bhiv = await _process_bhiv(news_id)

        pipeline_result = bhiv.get("pipelineResult") or {}
        seeya_compat = bhiv.get("seeya_compat") if 'seeya_compat' in bhiv else None

        summary_text = ""
        try:
            si = seeya_compat or {}
            summary_text = (si.get("summary") or "") if isinstance(si, dict) else ""
        except Exception:
            pass

        audio_info = await _sankalp_audio(title, summary_text, req.tone or "neutral")
        preview = _build_preview(pipeline_result)
        counts = {
            "filtered": int(pipeline_result.get("verify", {}).get("count", 0)) if isinstance(pipeline_result, dict) else 0,
            "scripts": len(preview),
        }
        iterations = 0
        try:
            iterations = int(bhiv.get("pipelineResult", {}).get("iterations", 0))
        except Exception:
            iterations = 0
        rl_rerun_triggered = iterations > 1

        final_pipeline = {}
        if isinstance(pipeline_result, dict):
            final_pipeline.update(pipeline_result)
        final_pipeline.setdefault("uniguru_ok", bool(uniguru_ok))
        final_pipeline.setdefault("rl_rerun_triggered", bool(rl_rerun_triggered))

        return RunPipelineResponse(
            success=True,
            timestamp=datetime.utcnow().isoformat(),
            newsItemId=news_id,
            counts=counts,
            preview=[PreviewItem(**p) for p in preview],
            pipeline=final_pipeline,
            seeya_compat=seeya_compat,
            audio=audio_info or {"status": "none"},
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
