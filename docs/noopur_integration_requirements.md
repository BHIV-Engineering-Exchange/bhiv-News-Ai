## Backend Inputs Needed From Noopur

To finish the production-ready integration we need precise confirmation on the following backend details.

- Final base### 1. Endpoint Inventory & URLs
 URLs for staging and production.
- Full route list we must consume (`/news`, `/processed/:id`, `/audio/:id`, `/feedback`, health/endpoints needed for orchestration) and whether any query params/filters are required.
- Expected rate limits or throttling guidance per endpoint.

### 2. Authentication Scheme
- Source of JWTs (issuer, how we obtain/refresh them during development).
- Required claims/scopes in the token so our client can verify before sending.
- Token lifetime/refresh rules and any clock-skew tolerance we should honor.

### 3. Security Headers & Signing
- Confirmation that every API call must include:
  - `Authorization: Bearer <jwt>`
  - `X-Client-Nonce` (nonce format/length, any expiry expectations)
  - `X-Signature` (HMAC details)
- Shared secret or public key used for signature validation (staging vs production).
- Canonical string format we must sign (HTTP method, path, timestamp, body hash, etc.).
- Required hashing algorithm (e.g., HMAC-SHA256) and how the backend validates mismatch scenarios.

### 4. Response JSON Contracts
- Definitive schema for `/news` list items (fields such as `id`, `title`, `script`, `tone`, `priority_score`, `trend_score`, `audio_path`, pipeline status timestamps, etc.).
- Schema for `/processed/:id` detail payloads (including nested pipeline steps and insight fields Seeya expects).
- Structure for `/audio/:id` responses (URL, duration, format, any signed URL expiry).
- Error payload structure for 4xx/5xx responses so we can surface meaningful messages.

### 5. Feedback API Expectations
- Whether feedback is routed through the same backend or proxied elsewhere.
- Exact payload shape `{ id, item, signals }` plus accepted signal values.
- Required auth/signature headers on feedback POSTs and expected success/error responses.
- Any rate limiting or idempotency tokens we should include to avoid duplicates.

### 6. Deployment & CORS Settings
- Approved frontend origins (localhost, Vercel staging, production domains) to ensure CORS headers are configured.
- Any differences between staging and production headers or auth requirements.
- Logging/monitoring endpoints we should be aware of for troubleshooting.

### 7. Operational Notes
- Preferred retry policy for transient failures (timeouts, 429, 5xx) and recommended backoff.
- Contact/escalation path for backend incidents during testing or deployment windows.

Please review and supply the above so we can finalize API wrappers, security helpers, and staging deployment without guesswork. Once we have these details we’ll reflect them in `docs/frontend-integration.md` and the `.env` templates.

