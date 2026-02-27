# News AI – Demo Notes

- Live Frontend URL: [https://YOUR_VERCEL_PROJECT_URL](https://YOUR_VERCEL_PROJECT_URL)
- Live Backend URL: [https://YOUR_RENDER_SERVICE_URL](https://YOUR_RENDER_SERVICE_URL)

## Demo Steps

1. Open the Live Frontend URL.
2. Navigate to “Advanced” or “Analyze”.
3. Enter a news article URL and start analysis.
4. Observe stages: scraping → vetting → summary → prompt → videos.
5. Confirm output shows summary, vetting results, and sidebar videos.

## Expected Behavior

- Pipeline completes end-to-end and displays results without errors.
- UI remains responsive; status indicator reflects backend online/offline.
- Secure headers (JWT/HMAC) are applied to backend requests.

## Latency Guidance

- If analysis stalls, wait up to 15 seconds; requests auto-timeout and show an error.
- Retry once; if backend is slow, verify backend health at /health and /docs.
- For peak load, reduce concurrency and re-run one URL at a time.

## URLs To Verify

- Backend Docs: https://YOUR_RENDER_SERVICE_URL/docs
- Health Check: https://YOUR_RENDER_SERVICE_URL/health

## Release Tag

- Git tag: demo-ready-v1

