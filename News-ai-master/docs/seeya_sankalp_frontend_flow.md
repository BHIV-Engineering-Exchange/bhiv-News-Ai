# 🔄 Seeya ↔ Sankalp ↔ Frontend Flow Documentation

## Overview

This document details the explicit integration flow between Seeya's Orchestrator, Sankalp's Insight Node, and Chandragupta's Frontend, showing how these three systems collaborate to deliver the complete News AI user experience.

## 🏗️ System Roles

### Seeya's Orchestrator
- **Role**: Workflow coordination and task routing
- **Responsibilities**:
  - Receive requests from frontend
  - Route jobs to appropriate backend services
  - Manage queue priorities and scheduling
  - Handle background processing coordination
  - Monitor pipeline execution status

### Sankalp's Insight Node
- **Role**: Audio generation and voice synthesis
- **Responsibilities**:
  - Convert text scripts to audio files
  - Provide multiple voice options
  - Handle audio format optimization
  - Deliver audio URLs for integration

### Chandragupta's Frontend
- **Role**: User interface and experience management
- **Responsibilities**:
  - Accept user inputs (news URLs)
  - Display real-time processing progress
  - Show results and audio previews
  - Handle user interactions and feedback

## 🔄 Complete Integration Flow

### Phase 1: Request Initiation

```
User Action → Frontend → Seeya Orchestrator → Backend Processing
```

**Detailed Flow:**
1. **User Input** (Frontend)
   - User enters news URL in input field
   - Frontend validates URL format
   - User clicks "Analyze News Article"

2. **Frontend Processing**
   ```javascript
   // Frontend API call
   const response = await fetch('/api/process-news', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       url: newsUrl,
       enable_full_pipeline: true,
       enable_bhiv_push: true
     })
   });
   ```

3. **Seeya Orchestrator Routing**
   - Receives frontend request
   - Validates request parameters
   - Routes to unified pipeline endpoint
   - Initiates background job tracking

### Phase 2: Pipeline Execution

```
Backend Processing → Agent Workflow → Sankalp Audio → Quality Validation
```

**Detailed Flow:**
1. **Backend Pipeline Start**
   - Unified pipeline receives request
   - LangGraph workflow initializes
   - Fetch agent scrapes news content

2. **Content Processing**
   - Filter agent assesses relevance
   - Verify agent checks authenticity
   - Script agent generates video prompts

3. **Sankalp Audio Integration**
   ```python
   # Backend calls Sankalp
   audio_result = await sankalp_service.generate_audio(
       text=script_content,
       voice="alice",
       language="en"
   )
   ```

4. **Audio Processing Response**
   ```json
   {
     "success": true,
     "audio_url": "https://sankalp-audio.com/generated/file.mp3",
     "duration": 45,
     "voice": "alice",
     "format": "mp3"
   }
   ```

### Phase 3: Real-time Updates

```
Processing Updates → Seeya Orchestrator → WebSocket → Frontend Display
```

**Detailed Flow:**
1. **Progress Broadcasting**
   - Backend sends WebSocket updates
   - Seeya orchestrator relays status
   - Frontend receives real-time progress

2. **WebSocket Message Format**
   ```json
   {
     "type": "pipeline_progress",
     "stage": "audio_generation",
     "progress": 75,
     "message": "Generating voice synthesis...",
     "timestamp": "2025-12-27T09:31:51.304Z"
   }
   ```

3. **Frontend Progress Display**
   - Updates pipeline visualizer
   - Shows current processing stage
   - Displays estimated completion time

### Phase 4: Results Delivery

```
Final Results → Seeya Aggregation → Frontend Presentation → User Feedback
```

**Detailed Flow:**
1. **Result Compilation**
   - Backend completes all processing
   - Seeya orchestrator aggregates results
   - Includes audio URLs from Sankalp

2. **Complete Response Structure**
   ```json
   {
     "success": true,
     "data": {
       "news_analysis": {
         "title": "Breaking News Title",
         "summary": "AI-generated summary...",
         "category": "politics",
         "sentiment": "neutral"
       },
       "video_script": {
         "content": "Generated video script...",
         "tone_score": 0.85,
         "engagement_score": 0.92
       },
       "audio": {
         "url": "https://sankalp-audio.com/file.mp3",
         "duration": 45,
         "voice": "alice"
       },
       "processing_stats": {
         "total_time": 3.2,
         "stages_completed": 5,
         "rl_score": 0.89
       }
     }
   }
   ```

3. **Frontend Results Display**
   - Shows news analysis summary
   - Provides audio preview player
   - Displays video script
   - Offers download/share options

## 📊 Data Exchange Contracts

### Frontend → Seeya Request Contract

```typescript
interface NewsProcessingRequest {
  url: string;
  enable_full_pipeline: boolean;
  enable_bhiv_push: boolean;
  channel?: string;
  avatar?: string;
  options?: {
    voice?: string;
    language?: string;
    tone?: string;
  };
}
```

### Seeya → Backend Routing Contract

```python
class OrchestratorRequest:
    def __init__(self, request_data: dict):
        self.url = request_data['url']
        self.pipeline_options = request_data.get('options', {})
        self.priority = self.calculate_priority()
        self.tracking_id = self.generate_tracking_id()
```

### Backend → Sankalp Audio Contract

```python
class AudioGenerationRequest:
    def __init__(self, text: str, voice: str = "default"):
        self.text = text
        self.voice = voice
        self.language = "en"
        self.format = "mp3"
        self.quality = "high"
```

### Sankalp → Backend Response Contract

```python
class AudioGenerationResponse:
    def __init__(self, success: bool, audio_url: str = None):
        self.success = success
        self.audio_url = audio_url
        self.duration = self.get_duration()
        self.file_size = self.get_file_size()
        self.metadata = {
            "voice": self.voice,
            "language": self.language,
            "generated_at": datetime.now().isoformat()
        }
```

## 🔄 Error Handling & Fallbacks

### Sankalp Audio Failure
```
Detection: Audio generation timeout/failure
Seeya Action: Log error, continue pipeline
Frontend Action: Show audio unavailable message
Fallback: Text-only content delivery
Recovery: Queue audio generation retry
```

### Seeya Orchestrator Failure
```
Detection: Routing service unavailable
Frontend Action: Direct API call to backend
Fallback: Simplified processing mode
Recovery: Automatic service restart
```

### Frontend Update Failure
```
Detection: WebSocket disconnection
Seeya Action: Buffer updates for reconnection
Fallback: HTTP polling for status
Recovery: Automatic reconnection logic
```

## 📈 Performance Metrics

### Response Time Targets
- **Frontend → Seeya**: <100ms
- **Seeya → Backend**: <200ms
- **Backend → Sankalp**: <2 seconds
- **Sankalp Audio Generation**: <30 seconds
- **Complete Pipeline**: <5 seconds

### Success Rate Requirements
- **Seeya Routing**: >99.9%
- **Sankalp Audio**: >97%
- **Frontend Updates**: >99.5%
- **End-to-End Pipeline**: >95%

## 🧪 Integration Testing Scenarios

### Happy Path Test
1. Frontend submits news URL
2. Seeya routes to unified pipeline
3. Backend processes with agents
4. Sankalp generates audio
5. Frontend displays complete results

### Audio Failure Test
1. Simulate Sankalp service down
2. Verify pipeline continues
3. Check frontend handles missing audio
4. Confirm error logging

### Real-time Update Test
1. Monitor WebSocket connections
2. Verify progress updates
3. Test reconnection logic
4. Validate message ordering

## 🚀 Scaling Considerations

### Seeya Orchestrator Scaling
- Horizontal scaling with load balancer
- Redis-backed session storage
- Queue partitioning for high throughput

### Sankalp Audio Scaling
- Asynchronous processing queues
- CDN distribution for audio files
- Voice synthesis resource pooling

### Frontend Scaling
- Vercel edge network distribution
- WebSocket connection optimization
- Progressive loading strategies

---

*This flow documentation ensures seamless integration between Seeya's orchestration, Sankalp's audio generation, and Chandragupta's frontend, delivering a cohesive user experience for the News AI platform.*