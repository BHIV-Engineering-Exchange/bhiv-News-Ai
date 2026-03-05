# ✅ Insight Node — Contract Sign-off

**Date**: 2026-02-14
**Version**: v1.0.0 (Production Locked)
**Owner**: Sankalp (Insight Node Lead)

---

## 1. Schema Validation (Input/Output)

### Input Contract (Frozen)
The Insight Node guarantees processing for the following input structure from Orchestration:

```json
{
  "url": "string (Required, Valid URL)",
  "include_videos": "boolean (Default: true)",
  "max_video_results": "integer (Default: 3)",
  "authenticity_check": "boolean (Default: true)"
}
```

### Output Contract (Frozen)
The Insight Node guarantees the following response structure to Noopur/Seeya:

```json
{
  "success": "boolean",
  "data": {
    "url": "string",
    "timestamp": "ISO8601 string",
    "workflow_steps": ["fetch", "filter", "verify", "script", "feedback"],
    "scraped_data": {
      "title": "string (Nullable)",
      "content_length": "integer",
      "author": "string (Nullable)",
      "date": "string (Nullable)"
    },
    "vetting_results": {
      "authenticity_score": "float (0-100)",
      "credibility_rating": "string (High/Medium/Low)",
      "is_reliable": "boolean"
    },
    "summary": {
      "text": "string (Markdown supported)",
      "compression_ratio": "float"
    },
    "video_prompt": {
      "prompt": "string (For AI Video Gen)",
      "for_video_creation": "boolean"
    },
    "sidebar_videos": {
      "videos": [
        {
          "title": "string",
          "url": "string",
          "thumbnail": "string",
          "source": "string (youtube/twitter)"
        }
      ],
      "total_found": "integer"
    }
  }
}
```

---

## 2. Null Safety & Error Handling

- **Missing Fields**: All optional fields (author, date) return explicit `null` or empty strings, never `undefined`.
- **Scraping Failures**: Returns `success: false` with a clear `message`. **NO** partial success with empty data.
- **Timeouts**: Hard timeout at **45 seconds** per request to prevent orchestration lag.

---

## 3. Integration Verification

- [x] **Frontend Alignment**: `api.ts` in Frontend correctly maps this schema.
- [x] **Orchestration Alignment**: `orchestration_contract_v1.json` matches this structure exactly.
- [x] **Legacy Support**: Maintains backward compatibility with `seeya_compat` if needed (currently deprecated but safe).

---

**Signed Off By**: 
Trae AI (Acting as Sankalp)
*Production Closure Lead*
