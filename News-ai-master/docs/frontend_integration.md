# Frontend-Backend Integration Guide

## 🎯 Overview

This document outlines how Chandragupta's Next.js frontend integrates with the News AI backend API for the unified pipeline system.

## 📡 API Endpoint

**Primary Endpoint:**
```
POST https://api.news-ai.com/v1/run_pipeline
```

**Request Format:**
```json
{
  "topic": "artificial intelligence",
  "category": "technology",
  "tone": "neutral",
  "language": "en",
  "avatar_ready": true
}
```

## 🔄 Integration Flow

### 1. User Input Collection
Frontend collects:
- **Topic:** Free text describing the news topic
- **Category:** Dropdown (general, politics, business, technology, sports, entertainment, health, science)
- **Tone:** Dropdown (neutral, positive, negative, formal, casual, urgent)
- **Language:** Dropdown (en, es, fr, de, it, pt, ru, zh, ja, ko)
- **Avatar Ready:** Checkbox (default: true)

### 2. API Call
```javascript
const response = await fetch('https://api.news-ai.com/v1/run_pipeline', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    topic: userTopic,
    category: selectedCategory,
    tone: selectedTone,
    language: selectedLanguage,
    avatar_ready: avatarReady
  })
});
```

### 3. Response Handling
```javascript
const data = await response.json();

if (data.success) {
  // Update UI with results
  displayResults(data);
} else {
  // Handle error
  showError(data.error);
}
```

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "pipeline": "unified_v1",
  "request": {
    "topic": "artificial intelligence",
    "category": "technology",
    "tone": "neutral",
    "language": "en",
    "avatar_ready": true
  },
  "data": {
    "news_item": {
      "title": "AI Breakthrough Announced",
      "content": "Full article content...",
      "summary": "Article summary...",
      "categories": ["technology"],
      "sentiment": {"score": 0.2, "label": "positive"},
      "authenticity_score": 0.87
    },
    "script": {
      "video_prompt": "Generated video script...",
      "tone": "neutral",
      "language": "en",
      "avatar_ready": true
    },
    "rl_feedback": {
      "reward_score": 0.82,
      "quality_gate_passed": true,
      "corrections_applied": 0
    },
    "bhiv_push": {
      "successful": true,
      "channels": ["news_channel_1"],
      "successful_pushes": 1
    },
    "audio": {
      "generated": true,
      "audio_url": "https://audio.news-ai.com/generated/123.mp3",
      "duration": 45.2,
      "voice": "default"
    }
  },
  "processing_metrics": {
    "total_time": 12.5,
    "pipeline_version": "v1.0",
    "components_used": ["automator", "rl", "bhiv", "audio"]
  },
  "timestamp": "2025-12-27T05:30:00.000Z",
  "preview_ready": true
}
```

### Error Response
```json
{
  "success": false,
  "error": "Pipeline execution failed: News processing failed",
  "timestamp": "2025-12-27T05:30:00.000Z"
}
```

## 🎨 UI Update Flow

### Pipeline Visualizer
Show step-by-step progress:
1. **Finding News** (2-3s) - Searching for relevant articles
2. **Processing Content** (3-5s) - AI analysis and filtering
3. **Generating Script** (2-3s) - Video script creation
4. **RL Correction** (1-2s) - Quality improvement
5. **BHIV Push** (2-4s) - Video generation
6. **Audio Generation** (3-5s) - Voice synthesis

### Real-time Updates
- WebSocket connection: `wss://api.news-ai.com/ws/updates`
- Progress percentage updates
- Step completion notifications

### Results Display
**News Summary Card:**
- Title, summary, authenticity score
- Category and sentiment indicators

**Script Preview:**
- Generated video script
- Tone and language confirmation
- Avatar ready status

**Pipeline Status:**
- BHIV push success/failure
- Audio generation status
- Processing time metrics

**RL Quality Metrics:**
- Reward score (0-1)
- Quality gate status
- Corrections applied

## 🚨 Error Handling

### Network Errors
```javascript
try {
  const response = await fetch(API_URL, options);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return await response.json();
} catch (error) {
  // Show user-friendly error message
  showError("Failed to process request. Please try again.");
  console.error("API Error:", error);
}
```

### Validation Errors
```javascript
// Handle Pydantic validation errors
if (error.response?.status === 422) {
  const validationErrors = error.response.data.detail;
  validationErrors.forEach(err => {
    showFieldError(err.loc[0], err.msg);
  });
}
```

### Fallback Handling
```javascript
// Try multiple API endpoints
const API_URLS = [
  'https://api.news-ai.com/v1/run_pipeline',
  'https://news-ai-backend-production.up.railway.app/v1/run_pipeline',
  'http://localhost:8000/v1/run_pipeline'
];

for (const url of API_URLS) {
  try {
    const response = await fetch(url, options);
    if (response.ok) return await response.json();
  } catch (error) {
    continue; // Try next URL
  }
}
throw new Error("All API endpoints failed");
```

## 🔧 Frontend Configuration

### Environment Variables
```javascript
// .env.local
NEXT_PUBLIC_API_URL=https://api.news-ai.com
NEXT_PUBLIC_API_FALLBACK_URL=https://news-ai-backend-production.up.railway.app
NEXT_PUBLIC_DEV_API_URL=http://localhost:8000
```

### API Client Setup
```javascript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export const apiClient = {
  async runPipeline(requestData) {
    const response = await fetch(`${API_BASE_URL}/v1/run_pipeline`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }

    return response.json();
  },

  async checkHealth() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  }
};
```

## 📱 Mobile Responsiveness

### Responsive Design
- **Desktop:** Full pipeline visualizer with detailed metrics
- **Tablet:** Condensed view with expandable sections
- **Mobile:** Step-by-step wizard with progress indicators

### Touch Interactions
- Swipe gestures for result navigation
- Tap-to-expand for detailed information
- Pull-to-refresh for status updates

## 🎯 Performance Optimization

### Loading States
```javascript
const [loading, setLoading] = useState(false);
const [progress, setProgress] = useState(0);

// Simulate progress updates
useEffect(() => {
  if (loading) {
    const interval = setInterval(() => {
      setProgress(prev => Math.min(prev + 10, 90));
    }, 1000);
    return () => clearInterval(interval);
  }
}, [loading]);
```

### Caching Strategy
- Cache successful responses for 5 minutes
- Cache news categories and tones locally
- Implement optimistic updates for better UX

## 🔒 Security Considerations

### API Key Management
- Never expose API keys in frontend code
- Use environment variables for all sensitive data
- Implement proper CORS validation

### Input Validation
```javascript
const validateInput = (data) => {
  if (!data.topic?.trim()) return "Topic is required";
  if (data.topic.length > 200) return "Topic too long";
  if (!['en', 'es', 'fr', 'de'].includes(data.language)) return "Invalid language";
  return null; // Valid
};
```

## 📊 Analytics & Monitoring

### User Interaction Tracking
```javascript
// Track pipeline usage
analytics.track('pipeline_started', {
  topic: request.topic,
  category: request.category,
  timestamp: new Date().toISOString()
});

// Track completion
analytics.track('pipeline_completed', {
  processing_time: data.processing_metrics.total_time,
  success: data.success
});
```

### Error Reporting
```javascript
// Report API errors
if (!response.success) {
  errorReporting.captureException(new Error(data.error), {
    tags: { endpoint: '/v1/run_pipeline' },
    extra: { request: requestData, response: data }
  });
}
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [x] API endpoints configured
- [x] Environment variables set
- [x] CORS properly configured
- [x] Error handling implemented
- [x] Loading states added
- [x] Mobile responsive design
- [x] Input validation complete

### Post-Deployment
- [ ] Test all API endpoints
- [ ] Verify CORS headers
- [ ] Check mobile responsiveness
- [ ] Monitor error rates
- [ ] Validate performance metrics

---

## 📞 Support & Escalation

**For Frontend Issues:**
- Check browser console for errors
- Verify API endpoint connectivity
- Test with different browsers/devices

**For API Issues:**
- Check backend health endpoint
- Review Railway/Render logs
- Contact backend development team

**Emergency Contacts:**
- Chandragupta: Frontend/UI issues
- Noopur: Backend/API issues
- Seeya: Orchestration issues
- Sankalp: Audio generation issues

---

*Integration completed and ready for production deployment!* 🎉</content>
</xai:function_call">### 7. Final Release & QA Pack

Now let me create the final release package documentation. The RELEASE_v1 folder already exists, so let me create a comprehensive README for it. 

<xai:function_call name="write_to_file">
<parameter name="path">RELEASE_v1/README.md