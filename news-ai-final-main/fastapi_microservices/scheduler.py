import asyncio
import os
import httpx
from datetime import datetime

UNIFIED_ENDPOINT = os.getenv("UNIFIED_ENDPOINT", "http://localhost:8000/v1/run_pipeline")

async def _run_category(url: str | None, title: str | None, content: str | None):
    payload = {}
    if url:
        payload["url"] = url
    if title:
        payload["title"] = title
    if content:
        payload["content"] = content
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(UNIFIED_ENDPOINT, json=payload)
        return resp.status_code, resp.text

async def schedule_loop():
    while True:
        now = datetime.utcnow()
        if now.minute % 15 == 0:
            try:
                await _run_category(url=None, title="Live Update", content="Pull latest items for Live")
            except Exception:
                pass
        if now.minute == 0:
            try:
                await _run_category(url=None, title="Finance Hourly", content="Finance scheduled batch")
            except Exception:
                pass
        if now.hour % 6 == 0 and now.minute == 0:
            try:
                await _run_category(url=None, title="World/Kids/Regional", content="Six-hour scheduled batch")
            except Exception:
                pass
        await asyncio.sleep(60)

def start_scheduler():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_loop())

if __name__ == "__main__":
    start_scheduler()
