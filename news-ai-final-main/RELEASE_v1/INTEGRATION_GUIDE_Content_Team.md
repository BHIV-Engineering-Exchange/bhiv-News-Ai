# Integration Guide (Content Team)

- Goal
  - Create, verify, and publish content through unified workflow
- Steps
  - Submit item: POST /api/news
  - Monitor: open frontend /live, polling GET /api/processed/:id
  - Review summary and sentiment; request corrections if needed
  - Publish: backend auto-publishes when reward >= threshold
  - Distribute: POST /api/bhiv/stream with target ttv|vaani
- Feedback
  - POST /api/feedback { newsId, feedbackType, metadata }
  - Types: like, skip, editor_approve, manual_override
- Audio
  - GET /api/audio/:id → { available, url }
- Categories
  - GET /api/categories for filters
