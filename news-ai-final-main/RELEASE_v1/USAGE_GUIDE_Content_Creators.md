# Usage Guide (Content Creators)

- Create
  - Use frontend Home to paste URL and Analyze
  - Backend creates item via POST /api/news
- Track
  - Use /live to see status; polling GET /api/processed/:id
- Preview
  - Summaries and insights shown in ResultsDisplay
  - Voice preview via GET /api/audio/:id
- Feedback
  - Click Like/Skip/Approve to send POST /api/feedback
- Export
  - Admin can stream published items to TTV/Vaani
