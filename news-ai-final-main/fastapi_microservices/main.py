from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import httpx
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import hmac
import hashlib

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
UNIGURU_API_KEY = os.getenv('UNIGURU_API_KEY')
UNIGURU_BASE_URL = os.getenv('UNIGURU_BASE_URL', 'https://api.uniguru.com/v1')
AUTO_PUBLISH = os.getenv('AUTO_PUBLISH', 'false').lower() == 'true'

if not MONGODB_URI:
    raise RuntimeError('MONGODB_URI is required in environment')

client = AsyncIOMotorClient(MONGODB_URI)
db = client.get_default_database() if client else None
news_collection = db.get_collection('news_items')

app = FastAPI(title='Noopur - Uniguru FastAPI Microservice')
try:
    from unified_pipeline import router as unified_router
    app.include_router(unified_router)
except Exception:
    pass

ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RATE_LIMIT_PER_MIN = int(os.getenv('RATE_LIMIT_PER_MIN', '60'))
_rate_state: Dict[str, Dict[str, Any]] = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    try:
        ip = request.client.host or "unknown"
        key = f"{ip}:{request.url.path}"
        now = int(datetime.utcnow().timestamp() // 60)
        entry = _rate_state.get(key)
        if not entry or entry.get('bucket') != now:
            _rate_state[key] = {'bucket': now, 'count': 0}
        _rate_state[key]['count'] += 1
        if _rate_state[key]['count'] > RATE_LIMIT_PER_MIN:
            return FastAPI.responses.JSONResponse(
                status_code=429,
                content={"detail": "rate_limited"}
            )
    except Exception:
        pass
    return await call_next(request)

def _validate_signature(path: str, headers: Dict[str, str]) -> bool:
    secret = os.getenv('JWT_HMAC_SECRET')
    if not secret:
        return True
    nonce = headers.get('x-client-nonce') or headers.get('X-Client-Nonce')
    ts = headers.get('x-timestamp') or headers.get('X-Timestamp')
    sig = headers.get('x-signature') or headers.get('X-Signature')
    if not nonce or not ts or not sig:
        return False
    msg = f"{nonce}:{ts}:{path}".encode('utf-8')
    expect = hmac.new(secret.encode('utf-8'), msg, hashlib.sha256).hexdigest()
    try:
        return hmac.compare_digest(expect, sig)
    except Exception:
        return False

@app.get('/auth/validate')
async def auth_validate(request: Request):
    headers = dict(request.headers)
    ok = _validate_signature(str(request.url.path), headers)
    jwt_header = headers.get('authorization') or headers.get('Authorization') or ''
    has_jwt = jwt_header.lower().startswith('bearer ')
    return {
        'success': True,
        'signatureValid': ok,
        'jwtReceived': has_jwt,
        'headers': {
            'nonce': headers.get('x-client-nonce') or headers.get('X-Client-Nonce'),
            'timestamp': headers.get('x-timestamp') or headers.get('X-Timestamp'),
            'signature': headers.get('x-signature') or headers.get('X-Signature')
        }
    }


class NewsIn(BaseModel):
    title: str
    content: str
    source: Optional[str] = 'manual'
    sourceUrl: Optional[str] = ''


class UniguruService:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}

    async def _post(self, path: str, json_data: Dict[str, Any], timeout: int = 30):
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=self.headers, json=json_data)
            resp.raise_for_status()
            return resp.json()

    async def classify_news(self, title: str, content: str) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('UNIGURU_API_KEY not set')
        return await self._post('/classify', {'title': title, 'content': content})

    async def analyze_sentiment(self, content: str) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('UNIGURU_API_KEY not set')
        return await self._post('/sentiment', {'text': content})

    async def summarize_news(self, title: str, content: str) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('UNIGURU_API_KEY not set')
        return await self._post('/summarize', {'title': title, 'content': content})

    async def process_news_complete(self, title: str, content: str) -> Dict[str, Any]:
        # Call all three in parallel
        tasks = []
        async with httpx.AsyncClient() as client:
            # sequentially call using methods to keep error traces clear
            classification = await self.classify_news(title, content)
            sentiment = await self.analyze_sentiment(content)
            summary = await self.summarize_news(title, content)

        return {
            'classification': classification,
            'sentiment': sentiment,
            'summary': summary,
            'processingTime': 0
        }


uniguru = UniguruService(UNIGURU_API_KEY, UNIGURU_BASE_URL)


@app.post('/api/news')
async def create_news(item: NewsIn, background_tasks: BackgroundTasks):
    # Insert raw
    doc = {
        'title': item.title,
        'content': item.content,
        'source': item.source,
        'sourceUrl': item.sourceUrl,
        'status': 'raw',
        'createdAt': datetime.utcnow(),
        'updatedAt': datetime.utcnow(),
    }
    res = await news_collection.insert_one(doc)
    news_id = str(res.inserted_id)

    # Process in background
    background_tasks.add_task(process_and_update, news_id, item.title, item.content)

    return {'success': True, 'newsId': news_id, 'status': 'raw'}


@app.get('/api/news/{news_id}')
async def get_news(news_id: str):
    from bson import ObjectId
    doc = await news_collection.find_one({'_id': ObjectId(news_id)})
    if not doc:
        raise HTTPException(status_code=404, detail='News item not found')
    # convert ObjectId
    doc['id'] = str(doc['_id'])
    del doc['_id']
    return {'success': True, 'data': doc}


async def process_and_update(news_id: str, title: str, content: str):
    from bson import ObjectId
    try:
        result = await uniguru.process_news_complete(title, content)

        update = {
            'classification': result.get('classification'),
            'sentiment': result.get('sentiment'),
            'summary': result.get('summary'),
            'status': 'verified',
            'updatedAt': datetime.utcnow()
        }

        if AUTO_PUBLISH:
            update['status'] = 'published'
            update['publishedMetadata'] = {'publishedAt': datetime.utcnow(), 'publishedBy': 'uniguru-microservice'}

        await news_collection.update_one({'_id': ObjectId(news_id)}, {'$set': update})
    except Exception as e:
        await news_collection.update_one({'_id': ObjectId(news_id)}, {'$set': {'status': 'failed', 'error': str(e), 'updatedAt': datetime.utcnow()}})


@app.post('/api/classify')
async def classify_endpoint(payload: Dict[str, Any]):
    title = payload.get('title', '')
    content = payload.get('content', '')
    try:
        return await uniguru.classify_news(title, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/health')
async def health():
    return {
        'status': 'healthy',
        'time': datetime.utcnow().isoformat(),
        'services': {
            'uniguru': bool(UNIGURU_API_KEY),
            'mongodb': bool(db)
        }
    }


@app.post('/api/sentiment')
async def sentiment_endpoint(payload: Dict[str, Any]):
    content = payload.get('content', '')
    try:
        return await uniguru.analyze_sentiment(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/summarize')
async def summarize_endpoint(payload: Dict[str, Any]):
    title = payload.get('title', '')
    content = payload.get('content', '')
    try:
        return await uniguru.summarize_news(title, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

NOOPUR_NODE_BASE_URL = os.getenv("NOOPUR_NODE_BASE_URL", "http://localhost:3001")
SANKALP_API_BASE = os.getenv("SANKALP_API_BASE", "http://localhost:8001")

@app.post('/api/bhiv/process')
async def proxy_bhiv_process(request: Request):
    try:
        body = await request.json()
    except:
        body = {}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Filter headers to avoid issues with host or content-length mismatch
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ('host', 'content-length')}
        resp = await client.post(
            f"{NOOPUR_NODE_BASE_URL}/api/bhiv/process",
            json=body,
            headers=headers
        )
        return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))

@app.post('/api/feedback')
async def proxy_feedback(request: Request):
    try:
        body = await request.json()
    except:
        body = {}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ('host', 'content-length')}
        resp = await client.post(
            f"{NOOPUR_NODE_BASE_URL}/api/feedback",
            json=body,
            headers=headers
        )
        return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))

@app.get('/api/categories')
async def proxy_categories(request: Request):
    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ('host', 'content-length')}
        resp = await client.get(
            f"{NOOPUR_NODE_BASE_URL}/api/categories",
            headers=headers
        )
        return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))

@app.post('/api/unified-news-workflow')
async def proxy_unified_workflow(request: Request):
    try:
        body = await request.json()
    except:
        body = {}
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ('host', 'content-length')}
        resp = await client.post(
            f"{SANKALP_API_BASE}/api/unified-news-workflow",
            json=body,
            headers=headers
        )
        return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))

@app.get('/api/processed/{id}')
async def proxy_processed_status(id: str, request: Request):
    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ('host', 'content-length')}
        resp = await client.get(
            f"{NOOPUR_NODE_BASE_URL}/api/processed/{id}",
            headers=headers
        )
        return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))

@app.get('/api/audio/{id}')
async def proxy_audio_status(id: str, request: Request):
    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ('host', 'content-length')}
        resp = await client.get(
            f"{NOOPUR_NODE_BASE_URL}/api/audio/{id}",
            headers=headers
        )
        return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))

