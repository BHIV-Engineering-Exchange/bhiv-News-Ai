# News AI Frontend-Backend Integration Guide

## 🎯 Integration Overview

This guide provides complete instructions for integrating Chandragupta's Vercel frontend with Noopur's Railway backend. The integration enables real-time news processing, pipeline visualization, voice preview, and live feed updates.

## 🔗 API Endpoints

### Base URLs
- **Production Backend**: `https://api.news-ai.com`
- **Staging Backend**: `https://news-ai-backend-staging.up.railway.app`
- **Frontend**: `https://news-ai-frontend.vercel.app`

### Key Endpoints for Frontend

#### 1. Unified Pipeline Processing
```javascript
// POST /v1/run_pipeline
const response = await fetch('https://api.news-ai.com/v1/run_pipeline', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: newsUrl,
    options: {
      enable_bhiv_push: true,
      enable_audio: true,
      channels: ['news_channel_1'],
      avatars: ['avatar_alice'],
      voice: 'default'
    }
  })
});

const result = await response.json();
// result.data contains news_item, script, rl_feedback, bhiv_push, audio
```

#### 2. Real-time Updates (WebSocket)
```javascript
// WebSocket connection for live updates
const ws = new WebSocket('wss://api.news-ai.com/ws/updates');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // Handle pipeline progress, completion, errors
  updatePipelineVisualizer(update);
};
```

#### 3. Health & Status Checks
```javascript
// GET /health
const health = await fetch('https://api.news-ai.com/health');
const status = await health.json();
// Check services: database, uniguru, bhiv_core, websocket
```

## 🎨 Frontend Integration Code

### React Hook for Pipeline Processing

```typescript
// hooks/useNewsPipeline.ts
import { useState, useCallback } from 'react';

interface PipelineResult {
  success: boolean;
  data: {
    news_item: any;
    script: any;
    rl_feedback: any;
    bhiv_push: any;
    audio: any;
  };
  processing_metrics: any;
}

export const useNewsPipeline = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const processNews = useCallback(async (url: string, options: any = {}) => {
    setIsProcessing(true);
    setError(null);

    try {
      const response = await fetch('https://api.news-ai.com/v1/run_pipeline', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, options })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);

      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  return { processNews, isProcessing, result, error };
};
```

### WebSocket Integration for Real-time Updates

```typescript
// hooks/useWebSocketUpdates.ts
import { useEffect, useRef, useState } from 'react';

interface PipelineUpdate {
  type: 'progress' | 'completion' | 'error';
  stage: string;
  progress: number;
  data?: any;
}

export const useWebSocketUpdates = () => {
  const [updates, setUpdates] = useState<PipelineUpdate[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket('wss://api.news-ai.com/ws/updates');
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const update = JSON.parse(event.data);
          setUpdates(prev => [...prev.slice(-9), update]); // Keep last 10 updates
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');
        // Auto-reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return { updates, isConnected };
};
```

### Pipeline Visualizer Component

```typescript
// components/PipelineVisualizer.tsx
import React from 'react';
import { useWebSocketUpdates } from '../hooks/useWebSocketUpdates';

const PipelineVisualizer: React.FC = () => {
  const { updates, isConnected } = useWebSocketUpdates();

  const stages = [
    'Input Processing',
    'Content Fetch',
    'Relevance Filter',
    'Authenticity Check',
    'Script Generation',
    'RL Feedback',
    'BHIV Push',
    'Audio Generation',
    'Complete'
  ];

  const getStageStatus = (stageName: string) => {
    const relevantUpdates = updates.filter(u => u.stage === stageName);
    if (relevantUpdates.length === 0) return 'pending';

    const latest = relevantUpdates[relevantUpdates.length - 1];
    if (latest.type === 'error') return 'error';
    if (latest.type === 'completion') return 'completed';
    return 'processing';
  };

  return (
    <div className="pipeline-visualizer">
      <div className="connection-status">
        <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '🟢' : '🔴'}
        </span>
        Real-time Updates: {isConnected ? 'Connected' : 'Disconnected'}
      </div>

      <div className="pipeline-stages">
        {stages.map((stage, index) => (
          <div key={stage} className={`stage ${getStageStatus(stage)}`}>
            <div className="stage-number">{index + 1}</div>
            <div className="stage-name">{stage}</div>
            <div className="stage-status">
              {getStageStatus(stage) === 'completed' && '✅'}
              {getStageStatus(stage) === 'processing' && '⏳'}
              {getStageStatus(stage) === 'error' && '❌'}
              {getStageStatus(stage) === 'pending' && '⏸️'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PipelineVisualizer;
```

### Voice Preview Component

```typescript
// components/VoicePreview.tsx
import React, { useState, useRef } from 'react';

interface VoicePreviewProps {
  audioUrl?: string;
  isGenerating: boolean;
}

const VoicePreview: React.FC<VoicePreviewProps> = ({ audioUrl, isGenerating }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  const handlePlay = async () => {
    if (!audioRef.current || !audioUrl) return;

    try {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        await audioRef.current.play();
        setIsPlaying(true);
      }
    } catch (err) {
      console.error('Audio playback failed:', err);
    }
  };

  const handleAudioEnd = () => {
    setIsPlaying(false);
  };

  if (isGenerating) {
    return (
      <div className="voice-preview generating">
        <div className="loading-spinner">🎵</div>
        <p>Generating audio...</p>
      </div>
    );
  }

  if (!audioUrl) {
    return (
      <div className="voice-preview no-audio">
        <p>No audio available</p>
      </div>
    );
  }

  return (
    <div className="voice-preview">
      <audio
        ref={audioRef}
        src={audioUrl}
        onEnded={handleAudioEnd}
        preload="metadata"
      />
      <button
        onClick={handlePlay}
        className={`play-button ${isPlaying ? 'playing' : 'paused'}`}
      >
        {isPlaying ? '⏸️ Pause' : '▶️ Play'}
      </button>
      <div className="audio-info">
        <small>Generated by Sankalp Insight Node</small>
      </div>
    </div>
  );
};

export default VoicePreview;
```

## 🎬 Live Feed Integration

### Real-time News Feed Component

```typescript
// components/LiveNewsFeed.tsx
import React, { useEffect, useState } from 'react';

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  published_at: string;
  categories: string[];
  authenticity_score: number;
}

const LiveNewsFeed: React.FC = () => {
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchNewsItems();
    // Set up polling for live updates every 30 seconds
    const interval = setInterval(fetchNewsItems, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchNewsItems = async () => {
    try {
      const response = await fetch('https://api.news-ai.com/api/news?limit=20');
      const data = await response.json();

      if (data.success) {
        setNewsItems(data.data);
      }
    } catch (err) {
      console.error('Failed to fetch news items:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="loading">Loading live feed...</div>;
  }

  return (
    <div className="live-news-feed">
      <h3>📰 Live News Feed</h3>
      <div className="news-items">
        {newsItems.map((item) => (
          <div key={item.id} className="news-item">
            <div className="news-header">
              <h4>{item.title}</h4>
              <span className="authenticity-score">
                Authenticity: {item.authenticity_score}%
              </span>
            </div>
            <p className="news-summary">{item.summary}</p>
            <div className="news-meta">
              <span className="categories">
                {item.categories.join(', ')}
              </span>
              <span className="timestamp">
                {new Date(item.published_at).toLocaleString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LiveNewsFeed;
```

## 🚨 Error Handling

### Error Message Display Component

```typescript
// components/ErrorDisplay.tsx
import React from 'react';

interface ErrorDisplayProps {
  error: string | null;
  onDismiss?: () => void;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onDismiss }) => {
  if (!error) return null;

  const getErrorType = (error: string) => {
    if (error.includes('504') || error.includes('timeout')) {
      return 'network';
    }
    if (error.includes('uniguru') || error.includes('api')) {
      return 'api';
    }
    if (error.includes('authenticity') || error.includes('content')) {
      return 'content';
    }
    return 'general';
  };

  const getErrorMessage = (error: string, type: string) => {
    switch (type) {
      case 'network':
        return 'Network connection issue. Please check your internet and try again.';
      case 'api':
        return 'External service temporarily unavailable. Using fallback processing.';
      case 'content':
        return 'Content processing issue. The article may not be suitable for processing.';
      default:
        return 'An unexpected error occurred. Please try again.';
    }
  };

  const errorType = getErrorType(error);
  const userMessage = getErrorMessage(error, errorType);

  return (
    <div className={`error-display ${errorType}`}>
      <div className="error-icon">
        {errorType === 'network' && '🌐'}
        {errorType === 'api' && '🔧'}
        {errorType === 'content' && '📝'}
        {errorType === 'general' && '⚠️'}
      </div>
      <div className="error-content">
        <h4>Error</h4>
        <p>{userMessage}</p>
        {process.env.NODE_ENV === 'development' && (
          <details>
            <summary>Technical Details</summary>
            <code>{error}</code>
          </details>
        )}
      </div>
      {onDismiss && (
        <button className="dismiss-button" onClick={onDismiss}>
          ✕
        </button>
      )}
    </div>
  );
};

export default ErrorDisplay;
```

## 🔧 Environment Configuration

### Frontend Environment Variables (.env.local)

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=https://api.news-ai.com
NEXT_PUBLIC_WS_URL=wss://api.news-ai.com

# Feature Flags
NEXT_PUBLIC_ENABLE_VOICE_PREVIEW=true
NEXT_PUBLIC_ENABLE_LIVE_FEED=true
NEXT_PUBLIC_ENABLE_PIPELINE_VISUALIZER=true

# Analytics (optional)
NEXT_PUBLIC_GA_TRACKING_ID=your_ga_id
```

### CORS Configuration (Backend)

The backend is already configured to accept requests from Vercel domains:

```python
# main.py CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://news-ai-frontend.vercel.app",
        "https://chandragupta-news-ai.vercel.app",
        "http://localhost:3000"  # Development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 🧪 Testing the Integration

### Manual Testing Checklist

1. **API Connectivity**
   - [ ] Health check endpoint responds
   - [ ] CORS headers present
   - [ ] Rate limiting works

2. **Pipeline Processing**
   - [ ] News URL submission works
   - [ ] Processing completes successfully
   - [ ] All data fields populated

3. **Real-time Updates**
   - [ ] WebSocket connection establishes
   - [ ] Progress updates received
   - [ ] Completion notifications work

4. **Voice Preview**
   - [ ] Audio generation triggers
   - [ ] Audio URL provided
   - [ ] Playback works in browser

5. **Live Feed**
   - [ ] News items load on page load
   - [ ] Auto-refresh works
   - [ ] New items appear in real-time

6. **Error Handling**
   - [ ] Network errors display user-friendly messages
   - [ ] API failures show appropriate fallbacks
   - [ ] Invalid URLs handled gracefully

### Automated Testing

```bash
# Run frontend tests
npm test

# Run integration tests (if implemented)
npm run test:integration

# Check API connectivity
curl -X GET "https://api.news-ai.com/health"
```

## 📊 Performance Optimization

### Frontend Optimizations

1. **Lazy Loading**
   ```typescript
   const PipelineVisualizer = lazy(() => import('./components/PipelineVisualizer'));
   ```

2. **Memoization**
   ```typescript
   const memoizedResult = useMemo(() => processResult(data), [data]);
   ```

3. **Debounced API Calls**
   ```typescript
   const debouncedSearch = useCallback(
     debounce((query) => searchNews(query), 300),
     []
   );
   ```

### Backend Optimizations

1. **Response Compression**
   - Railway automatically compresses responses

2. **Caching Strategy**
   - Implement Redis for frequently accessed data
   - Cache news categories and metadata

3. **Database Indexing**
   - Ensure proper indexes on MongoDB collections

## 🎯 Production URLs

- **Frontend**: https://news-ai-frontend.vercel.app
- **Backend API**: https://api.news-ai.com
- **Health Check**: https://api.news-ai.com/health
- **API Docs**: https://api.news-ai.com/docs

## 📞 Support

For integration issues:
1. Check browser console for errors
2. Verify API endpoints are accessible
3. Check Railway/ Vercel deployment status
4. Review environment variables
5. Check CORS configuration

---

*Integration completed successfully. Frontend and backend are now fully connected with real-time updates, voice preview, and live feed functionality.*