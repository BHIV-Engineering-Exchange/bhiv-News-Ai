# Seeya UI JSON Response Contracts

## Overview

This document defines the exact JSON response contracts for Seeya UI integration with the News AI backend. All contracts are designed to be compatible with the frontend implementation and include comprehensive error handling, real-time status updates, and voice preview functionality.

## 1. Error States Mapping Contract

### Error Response Structure

All API endpoints return standardized error responses with the following contract:

```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": "string",
    "category": "string",
    "retryable": boolean,
    "timestamp": "ISO8601_datetime",
    "request_id": "string"
  },
  "partial_data": {},
  "recovery_suggestions": ["string"]
}
```

### Error Code Categories

#### Validation Errors (4xx)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": "URL is required and must be a valid HTTP/HTTPS URL",
    "category": "validation",
    "retryable": false,
    "timestamp": "2025-12-29T08:02:59.274Z",
    "request_id": "req_12345"
  },
  "recovery_suggestions": [
    "Provide a valid news article URL",
    "Ensure URL starts with http:// or https://"
  ]
}
```

#### Processing Errors (5xx)
```json
{
  "success": false,
  "error": {
    "code": "PROCESSING_FAILED",
    "message": "News content processing failed",
    "details": "Unable to extract article content from provided URL",
    "category": "processing",
    "retryable": true,
    "timestamp": "2025-12-29T08:02:59.274Z",
    "request_id": "req_12345"
  },
  "partial_data": {
    "url": "https://example.com/article",
    "title_extracted": true
  },
  "recovery_suggestions": [
    "Try a different news source",
    "Check if the article is behind a paywall",
    "Verify the URL is accessible"
  ]
}
```

#### Service Unavailable Errors
```json
{
  "success": false,
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "External service temporarily unavailable",
    "details": "Uniguru AI service is experiencing high load",
    "category": "external_service",
    "retryable": true,
    "timestamp": "2025-12-29T08:02:59.274Z",
    "request_id": "req_12345"
  },
  "recovery_suggestions": [
    "Wait 30 seconds and retry",
    "Use fallback processing mode",
    "Contact support if issue persists"
  ]
}
```

### Complete Error Code Reference

| Error Code | HTTP Status | Category | Retryable | Description |
|------------|-------------|----------|-----------|-------------|
| `VALIDATION_ERROR` | 400 | validation | false | Invalid request parameters |
| `MISSING_REQUIRED_FIELD` | 400 | validation | false | Required field missing |
| `INVALID_URL_FORMAT` | 400 | validation | false | URL format invalid |
| `UNSUPPORTED_CONTENT_TYPE` | 400 | validation | false | Content type not supported |
| `PROCESSING_FAILED` | 500 | processing | true | Content processing failed |
| `SCRAPING_BLOCKED` | 403 | processing | false | Website blocks scraping |
| `CONTENT_EXTRACTION_FAILED` | 500 | processing | true | Failed to extract article content |
| `SERVICE_UNAVAILABLE` | 503 | external_service | true | External service down |
| `UNIGURU_API_ERROR` | 502 | external_service | true | Uniguru service error |
| `BHIV_PUSH_FAILED` | 502 | external_service | true | BHIV push failed |
| `AUDIO_GENERATION_FAILED` | 502 | external_service | true | Audio generation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | rate_limit | true | Too many requests |
| `INTERNAL_ERROR` | 500 | system | true | Unexpected system error |
| `DATABASE_ERROR` | 500 | system | true | Database operation failed |

## 2. Pipeline Visualizer Status Payload

### Real-time Status Update Structure

The pipeline visualizer receives WebSocket updates with the following contract:

```json
{
  "type": "pipeline_status",
  "request_id": "string",
  "stage": "string",
  "status": "string",
  "progress": number,
  "message": "string",
  "timestamp": "ISO8601_datetime",
  "stage_data": {},
  "estimated_completion": "ISO8601_datetime",
  "retry_count": number
}
```

### Pipeline Stages and Status Values

#### Stage Definitions
- `initializing`: Pipeline setup and validation
- `fetching`: News content retrieval
- `filtering`: Content relevance assessment
- `verifying`: Authenticity verification
- `scripting`: Video script generation
- `rl_correction`: Quality improvement via RL
- `bhiv_push`: Video generation push
- `audio_generation`: Voice synthesis
- `finalizing`: Response compilation

#### Status Values
- `pending`: Stage not yet started
- `running`: Stage currently executing
- `completed`: Stage finished successfully
- `failed`: Stage failed (see error details)
- `skipped`: Stage bypassed (e.g., audio disabled)

### Example Status Updates

#### Stage Start
```json
{
  "type": "pipeline_status",
  "request_id": "req_12345",
  "stage": "fetching",
  "status": "running",
  "progress": 15,
  "message": "Fetching article content from URL...",
  "timestamp": "2025-12-29T08:03:00.000Z",
  "stage_data": {
    "url": "https://example.com/news-article",
    "attempt": 1
  },
  "estimated_completion": "2025-12-29T08:03:05.000Z",
  "retry_count": 0
}
```

#### Stage Completion
```json
{
  "type": "pipeline_status",
  "request_id": "req_12345",
  "stage": "scripting",
  "status": "completed",
  "progress": 60,
  "message": "Video script generated successfully",
  "timestamp": "2025-12-29T08:03:15.000Z",
  "stage_data": {
    "script_length": 280,
    "tone": "neutral",
    "language": "en"
  },
  "estimated_completion": "2025-12-29T08:03:25.000Z",
  "retry_count": 0
}
```

#### Stage Failure with Retry
```json
{
  "type": "pipeline_status",
  "request_id": "req_12345",
  "stage": "bhiv_push",
  "status": "failed",
  "progress": 75,
  "message": "BHIV push failed, retrying...",
  "timestamp": "2025-12-29T08:03:20.000Z",
  "stage_data": {
    "error": "Connection timeout",
    "channels_attempted": ["news_channel_1"],
    "will_retry": true
  },
  "estimated_completion": "2025-12-29T08:03:35.000Z",
  "retry_count": 1
}
```

#### Pipeline Completion
```json
{
  "type": "pipeline_complete",
  "request_id": "req_12345",
  "success": true,
  "total_time": 8.5,
  "stages_completed": 8,
  "final_result": {
    "preview_ready": true,
    "audio_available": true,
    "video_generated": true
  },
  "timestamp": "2025-12-29T08:03:25.000Z"
}
```

## 3. Voice Preview Payload Structure

### Audio Generation Response Contract

```json
{
  "success": true,
  "audio": {
    "id": "string",
    "url": "string",
    "duration": number,
    "size_bytes": number,
    "format": "string",
    "bitrate": number,
    "sample_rate": number,
    "channels": number,
    "voice": "string",
    "language": "string",
    "tone": "string",
    "generated_at": "ISO8601_datetime",
    "expires_at": "ISO8601_datetime",
    "metadata": {
      "text_length": number,
      "processing_time": number,
      "quality_score": number
    }
  },
  "preview": {
    "available": boolean,
    "url": "string",
    "duration_preview": number
  },
  "alternatives": [
    {
      "voice": "string",
      "url": "string",
      "duration": number
    }
  ]
}
```

### Voice Options and Specifications

#### Supported Voices
- `alice`: Female, neutral, professional
- `bob`: Male, neutral, professional
- `charlie`: Male, energetic, casual
- `diana`: Female, warm, storytelling
- `default`: System default voice

#### Audio Formats
- `mp3`: Standard quality (128kbps)
- `wav`: High quality, uncompressed
- `aac`: Mobile optimized (96kbps)

### Example Voice Preview Response

```json
{
  "success": true,
  "audio": {
    "id": "audio_12345",
    "url": "https://audio.news-ai.com/generated/audio_12345.mp3",
    "duration": 45.2,
    "size_bytes": 5760000,
    "format": "mp3",
    "bitrate": 128,
    "sample_rate": 44100,
    "channels": 2,
    "voice": "alice",
    "language": "en",
    "tone": "neutral",
    "generated_at": "2025-12-29T08:03:20.000Z",
    "expires_at": "2025-12-30T08:03:20.000Z",
    "metadata": {
      "text_length": 1250,
      "processing_time": 3.2,
      "quality_score": 0.92
    }
  },
  "preview": {
    "available": true,
    "url": "https://audio.news-ai.com/preview/audio_12345_preview.mp3",
    "duration_preview": 10.0
  },
  "alternatives": [
    {
      "voice": "bob",
      "url": "https://audio.news-ai.com/generated/audio_12345_bob.mp3",
      "duration": 44.8
    },
    {
      "voice": "diana",
      "url": "https://audio.news-ai.com/generated/audio_12345_diana.mp3",
      "duration": 46.1
    }
  ]
}
```

### Audio Generation Error Response

```json
{
  "success": false,
  "error": {
    "code": "AUDIO_GENERATION_FAILED",
    "message": "Voice synthesis failed",
    "details": "Sankalp service returned invalid audio format",
    "category": "external_service",
    "retryable": true,
    "timestamp": "2025-12-29T08:03:20.000Z",
    "request_id": "req_12345"
  },
  "fallback": {
    "text_only_available": true,
    "estimated_retry_time": "2025-12-29T08:04:20.000Z"
  }
}
```

## 4. Complete Unified Pipeline Response

### Success Response Contract

```json
{
  "success": true,
  "pipeline": "unified_v1",
  "request": {
    "url": "string",
    "options": {
      "enable_bhiv_push": boolean,
      "enable_audio": boolean,
      "channels": ["string"],
      "avatars": ["string"],
      "voice": "string",
      "tone": "string",
      "language": "string",
      "avatar_ready": boolean
    }
  },
  "data": {
    "news_item": {
      "id": "string",
      "title": "string",
      "content": "string",
      "summary": "string",
      "categories": ["string"],
      "sentiment": {
        "score": number,
        "label": "string",
        "confidence": number
      },
      "authenticity_score": number,
      "published_at": "ISO8601_datetime",
      "scraped_at": "ISO8601_datetime"
    },
    "script": {
      "video_prompt": "string",
      "tone": "string",
      "language": "string",
      "avatar_ready": boolean,
      "word_count": number,
      "estimated_duration": number
    },
    "rl_feedback": {
      "reward_score": number,
      "quality_gate_passed": boolean,
      "corrections_applied": number,
      "tone_score": number,
      "engagement_score": number,
      "final_quality_score": number
    },
    "bhiv_push": {
      "successful": boolean,
      "channels": ["string"],
      "successful_pushes": number,
      "failed_pushes": number,
      "push_ids": ["string"],
      "estimated_completion": "ISO8601_datetime"
    },
    "audio": {
      "generated": boolean,
      "audio_url": "string",
      "duration": number,
      "voice": "string",
      "format": "string",
      "size_bytes": number,
      "preview_available": boolean,
      "alternatives_available": boolean
    }
  },
  "processing_metrics": {
    "total_time": number,
    "pipeline_version": "string",
    "components_used": ["string"],
    "stages_completed": number,
    "retries_used": number,
    "cache_hits": number
  },
  "preview_ready": boolean,
  "download_urls": {
    "audio": "string",
    "script": "string",
    "full_report": "string"
  },
  "timestamp": "ISO8601_datetime",
  "request_id": "string"
}
```

## 5. Validation Schemas

### Request Validation Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["url"],
  "properties": {
    "url": {
      "type": "string",
      "format": "uri",
      "pattern": "^https?://"
    },
    "options": {
      "type": "object",
      "properties": {
        "enable_bhiv_push": {"type": "boolean"},
        "enable_audio": {"type": "boolean"},
        "channels": {
          "type": "array",
          "items": {"type": "string"},
          "maxItems": 10
        },
        "avatars": {
          "type": "array",
          "items": {"type": "string"},
          "maxItems": 10
        },
        "voice": {
          "type": "string",
          "enum": ["alice", "bob", "charlie", "diana", "default"]
        },
        "tone": {
          "type": "string",
          "enum": ["neutral", "positive", "negative", "formal", "casual", "urgent"]
        },
        "language": {
          "type": "string",
          "pattern": "^[a-z]{2}$"
        },
        "avatar_ready": {"type": "boolean"}
      }
    }
  }
}
```

## 6. Frontend Integration Examples

### Error Handling in Frontend
```javascript
// Handle API response
const handleApiResponse = (response) => {
  if (!response.success) {
    const error = response.error;

    // Show user-friendly message
    showErrorToast(error.message);

    // Handle specific error types
    switch (error.category) {
      case 'validation':
        highlightInvalidFields(error.details);
        break;
      case 'processing':
        if (error.retryable) {
          showRetryButton();
        }
        break;
      case 'external_service':
        showServiceUnavailableMessage();
        break;
    }

    // Log for debugging
    console.error('API Error:', error);
    return;
  }

  // Process successful response
  updatePipelineVisualizer(response.data);
};
```

### WebSocket Status Updates
```javascript
// Handle real-time status updates
const handlePipelineStatus = (statusUpdate) => {
  const { stage, status, progress, message, stage_data } = statusUpdate;

  // Update progress bar
  updateProgressBar(progress);

  // Update stage indicator
  updateStageStatus(stage, status);

  // Show status message
  showStatusMessage(message);

  // Handle stage-specific data
  if (stage_data) {
    updateStageDetails(stage, stage_data);
  }
};
```

### Voice Preview Integration
```javascript
// Handle voice preview
const handleVoicePreview = (audioData) => {
  if (audioData.audio) {
    // Set up audio player
    const audioPlayer = new Audio(audioData.audio.url);
    audioPlayer.controls = true;

    // Show voice alternatives
    if (audioData.alternatives) {
      showVoiceAlternatives(audioData.alternatives);
    }

    // Display audio metadata
    showAudioInfo(audioData.audio);
  }
};
```

---

*These contracts ensure consistent, reliable integration between the News AI backend and Seeya UI frontend, with comprehensive error handling and real-time status updates.*