# Admin Panel Quick-Start

- Health
  - Check GET /health and GET /api/system/info
- Pipeline
  - Trigger orchestration: POST /api/agents/orchestrate
  - Process & distribute: POST /api/bhiv/process
- Thresholds
  - Set RL threshold: POST /api/feedback/threshold { threshold }
- Metrics
  - Get feedback metrics: GET /api/feedback/metrics?newsItemId=<id>
  - Aggregation: GET /api/feedback/aggregate
- Categories
  - GET /api/categories to manage filters
