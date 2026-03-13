# 🔌 Backend Integration Guide

## Overview

This application supports **TWO API integration systems** that work seamlessly together:

1. **Original API** (`lib/api.ts`) - For existing features
2. **New API Service** (`services/api.js`) - For Live Dashboard and new features

Both systems are **fully compatible** and automatically fallback to mock data when the backend is unavailable.

---

## 🎯 How It Works

### Automatic Backend Detection

The application automatically:
1. ✅ Checks if backend is available on startup
2. ✅ Tries real API calls first
3. ✅ Falls back to mock data if backend is offline
4. ✅ Works perfectly in both scenarios

### No Configuration Needed!

- **Backend Online**: All features use real API
- **Backend Offline**: All features use mock data
- **Zero user impact**: Seamless transition

---

## 📡 API Systems

### 1. Original API (`lib/api.ts`)

**Used By:**
- ✅ Home page (`/`)
- ✅ Advanced Analysis page (`/advanced`)
- ✅ Testing page (`/testing`)
- ✅ Dashboard page (`/dashboard`)

**Endpoints:**
```typescript
// Health check
GET /health

// Unified news workflow
POST /api/unified-news-workflow
Body: { url: string }

// Individual tools
POST /api/scrape
POST /api/vet
POST /api/summarize
POST /api/prompt
POST /api/video-search
POST /api/validate-video
```

**Example Usage:**
```typescript
import { checkBackendHealth, runUnifiedWorkflow } from '@/lib/api'

// Check backend
const isHealthy = await checkBackendHealth()

// Run analysis
const result = await runUnifiedWorkflow('https://news-url.com')
```

### 2. New API Service (`services/api.js`)

**Used By:**
- ✅ Live Dashboard page (`/live`)
- ✅ News Feed page (`/feed`)
- ✅ New components (TTS Player, Pipeline Viewer, AI Insights, Feedback Panel)

**Endpoints:**
```javascript
// Get news items
GET /api/news?category=technology&limit=20

// Get processed news
GET /api/processed/:id

// Get audio
GET /api/audio/:id

// Submit feedback
POST /api/feedback
Body: { newsId, feedbackType, metadata }

// Get categories
GET /api/categories
```

**Example Usage:**
```javascript
import apiService from '@/services/api'

// Get news
const news = await apiService.getNews({ 
  category: 'technology', 
  limit: 10 
})

// Submit feedback
await apiService.submitFeedback('news-id', 'like')

// Check backend status
const isAvailable = apiService.isBackendAvailable()
```

---

## 🔄 Backend Compatibility

### Backend Requirements

Your Python backend (`unified_tools_backend/main.py`) should support:

#### Existing Endpoints (Already Implemented ✅)
```python
@app.get("/health")
@app.post("/api/unified-news-workflow")
@app.post("/api/scrape")
@app.post("/api/vet")
@app.post("/api/summarize")
@app.post("/api/prompt")
@app.post("/api/video-search")
@app.post("/api/validate-video")
```

#### New Endpoints (Optional - Mock data available)
```python
@app.get("/api/news")
@app.get("/api/processed/{id}")
@app.get("/api/audio/{id}")
@app.post("/api/feedback")
@app.get("/api/categories")
```

### If New Endpoints Are Missing

**No problem!** The new API service automatically uses mock data:
- ✅ 5 complete sample news items
- ✅ Full pipeline states
- ✅ AI insights and analytics
- ✅ Feedback system works locally

---

## 🚀 Running Both Systems

### Scenario 1: Backend Available

```bash
# Terminal 1: Start Backend
cd unified_tools_backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Start Frontend
cd blackhole-frontend
npm run dev
```

**Result:**
- ✅ Home page uses real backend
- ✅ Live Dashboard uses real backend (if endpoints exist)
- ✅ All features fully functional

### Scenario 2: Backend Offline

```bash
# Just start Frontend
cd blackhole-frontend
npm run dev
```

**Result:**
- ✅ Home page shows backend offline alert
- ✅ Live Dashboard uses mock data (works perfectly!)
- ✅ All features remain functional
- ✅ Perfect for demos and development

---

## 🔧 Configuration

### Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Force Mock Data (Development)

In any component:
```javascript
import apiService from '@/services/api'

// Use mock data
apiService.setMockDataMode(true)

// Use real backend
apiService.setMockDataMode(false)
```

---

## 📊 Feature Compatibility Matrix

| Feature | Original API | New API | Works Offline |
|---------|-------------|---------|---------------|
| **Home Analysis** | ✅ | - | ❌ Needs backend |
| **Live Dashboard** | - | ✅ | ✅ Mock data |
| **News Feed** | - | ✅ | ✅ Mock data |
| **TTS Player** | - | ✅ | ✅ Mock audio |
| **AI Insights** | - | ✅ | ✅ Mock data |
| **Feedback System** | - | ✅ | ✅ Local storage |
| **Dashboard Stats** | ✅ | - | ⚠️ Partial |
| **Testing Tools** | ✅ | - | ❌ Needs backend |
| **Advanced Analysis** | ✅ | - | ❌ Needs backend |

**Legend:**
- ✅ Full support
- ⚠️ Partial support
- ❌ Requires backend

---

## 🎯 Best Practices

### 1. **Always Check Backend Status**

```typescript
import { checkBackendHealth } from '@/lib/api'

const [backendStatus, setBackendStatus] = useState('checking')

useEffect(() => {
  const checkBackend = async () => {
    const isHealthy = await checkBackendHealth()
    setBackendStatus(isHealthy ? 'online' : 'offline')
  }
  checkBackend()
}, [])
```

### 2. **Show Backend Status to Users**

```tsx
<BackendStatus 
  status={backendStatus} 
  onRetry={checkBackend} 
/>
```

### 3. **Handle API Errors Gracefully**

```typescript
try {
  const result = await runUnifiedWorkflow(url)
  // Handle success
} catch (error) {
  // Show error message
  console.error('Analysis failed:', error)
}
```

### 4. **Use Appropriate API for Each Feature**

```typescript
// For unified news workflow
import { runUnifiedWorkflow } from '@/lib/api'

// For live dashboard features
import apiService from '@/services/api'
```

---

## 🔍 Testing Both APIs

### Test Original API

```bash
# Backend must be running
curl http://localhost:8000/health

# Should return:
# {"status": "healthy", "version": "4.0.0"}
```

### Test New API Endpoints

```bash
# These might not exist in current backend (uses mock data)
curl http://localhost:8000/api/news
curl http://localhost:8000/api/categories
```

---

## 🐛 Troubleshooting

### Issue: Backend shows offline but it's running

**Solution:**
```bash
# Check if backend is actually running
curl http://localhost:8000/health

# Check CORS settings in backend
# Ensure frontend URL is allowed

# Check environment variables
echo $NEXT_PUBLIC_API_BASE_URL
```

### Issue: Some features work, others don't

**Diagnosis:**
- ✅ Home page works → Original API is fine
- ❌ Live Dashboard doesn't work → Check new endpoints
- ✅ Live Dashboard shows mock data → Normal behavior!

**Solution:**
This is expected! New endpoints use mock data if not implemented in backend.

### Issue: Want to always use mock data

**Solution:**
```javascript
// In components using new API service
import apiService from '@/services/api'

useEffect(() => {
  apiService.setMockDataMode(true)
}, [])
```

---

## 🚀 Adding Backend Support for New Endpoints

If you want the Live Dashboard to use real backend data, add these to `unified_tools_backend/main.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# News endpoint
@app.get("/api/news")
async def get_news(category: str = "all", limit: int = 20):
    # Your implementation
    return {
        "success": True,
        "data": [...],  # List of news items
        "total": 5
    }

# Processed news endpoint
@app.get("/api/processed/{news_id}")
async def get_processed_news(news_id: str):
    # Your implementation
    return {
        "success": True,
        "data": {...}  # News item details
    }

# Audio endpoint
@app.get("/api/audio/{news_id}")
async def get_audio(news_id: str):
    # Your implementation
    return {
        "success": True,
        "url": "/audio/file.mp3"
    }

# Feedback endpoint
class FeedbackRequest(BaseModel):
    newsId: str
    feedbackType: str
    metadata: dict

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    # Your implementation
    # Store feedback for RL training
    return {
        "success": True,
        "message": "Feedback recorded"
    }

# Categories endpoint
@app.get("/api/categories")
async def get_categories():
    return {
        "success": True,
        "data": [
            {"id": "technology", "name": "Technology", "count": 45},
            # ... more categories
        ]
    }
```

---

## 📝 Summary

### ✅ What Works Now

**With Backend Running:**
- Home page analysis (real API)
- Advanced analysis (real API)
- Testing tools (real API)
- Dashboard (real API)
- Live Dashboard (mock data*)
- News Feed (mock data*)
- All new components

**Without Backend:**
- Live Dashboard (mock data)
- News Feed (mock data)
- TTS Player (mock audio)
- AI Insights (mock data)
- Feedback System (local storage)

*Will use real API when endpoints are implemented

### 🎯 Key Points

1. **Both API systems coexist perfectly**
2. **Automatic fallback to mock data**
3. **No configuration needed**
4. **Works with or without backend**
5. **Existing features unaffected**
6. **New features enhance the application**

---

## 📞 Need Help?

- **Backend Issues**: Check `unified_tools_backend/main.py`
- **Frontend Issues**: Check browser console
- **API Issues**: Check Network tab in DevTools
- **Questions**: See README.md or create an issue

---

**Both API systems work together seamlessly! 🎉**

*Backend Integration Guide - Last Updated: November 2024*

