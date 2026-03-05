# Noopur News AI - Test Scenarios & Workflows

## Test Scenarios

### Scenario 1: Single News Item Complete Processing

**Goal:** Process one news item from raw → published

**Steps:**

```bash
# 1. Create raw news
RESPONSE=$(curl -s -X POST http://localhost:3000/api/news \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tech Company Announces New AI Product",
    "content": "In a groundbreaking announcement today, tech company revealed their latest artificial intelligence product that promises to revolutionize data analysis. The product combines cutting-edge machine learning with an intuitive user interface. Early beta testers report significant improvements in processing speed and accuracy.",
    "source": "api",
    "sourceUrl": "https://example.com/news/ai-product"
  }')

NEWS_ID=$(echo $RESPONSE | grep -o '"newsId":"[^"]*' | cut -d'"' -f4)
echo "Created news ID: $NEWS_ID"

# 2. Wait for Uniguru enrichment (5-10 seconds)
sleep 5
curl http://localhost:3000/api/news/$NEWS_ID | jq '.data | {
  title,
  status,
  classification,
  sentiment,
  summary: .summary | {short, keyPoints}
}'

# 3. Process through pipeline
curl -X POST http://localhost:3000/api/bhiv/process \
  -H "Content-Type: application/json" \
  -d "{
    \"newsItemId\": \"$NEWS_ID\",
    \"distribution\": {\"ttv\": true, \"vaani\": true}
  }" | jq '.'

# 4. Verify published status
curl http://localhost:3000/api/bhiv/status/$NEWS_ID | jq '.'
```

**Expected Outcome:**
- News moves from `raw` → `verified` (after enrichment) → `published` (after pipeline)
- Reward score ≥ 0.6 (no auto-reroute needed)
- BHIV distribution successful to both TTV and Vaani
- WebSocket clients receive published event

---

### Scenario 2: Auto-Reroute on Low Reward Score

**Goal:** Demonstrate RL feedback loop with low score triggering re-processing

**Setup:** Create a news item with ambiguous or inconsistent content

```bash
# Create ambiguous news (may trigger low reward)
RESPONSE=$(curl -s -X POST http://localhost:3000/api/news \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Xyz Report Shows Data",
    "content": "The xyz metric indicates changes. Data shows variance. Unclear implications. Mixed signals suggest uncertainty about future direction.",
    "source": "manual"
  }')

NEWS_ID=$(echo $RESPONSE | grep -o '"newsId":"[^"]*' | cut -d'"' -f4)

# Wait for enrichment
sleep 5

# Process through pipeline (will attempt up to 3 iterations)
curl -X POST http://localhost:3000/api/bhiv/process \
  -H "Content-Type: application/json" \
  -d "{
    \"newsItemId\": \"$NEWS_ID\"
  }" | jq '.pipelineResult | {
    finalRewardScore,
    iterations,
    processingTime
  }'
```

**Expected Outcome:**
- First iteration: Reward < 0.6
- Auto-reroute triggered: Re-analyze with Uniguru
- Subsequent iterations: Improved reward score
- Metrics tracked for each iteration
- Final status depends on max iterations & threshold

---

### Scenario 3: Batch News Processing

**Goal:** Process multiple news items in parallel

```bash
# Create 5 news items
declare -a NEWS_IDS

SAMPLE_TITLES=(
  "Market Reaches Record High"
  "New Medical Breakthrough"
  "Climate Summit Agreement"
  "Sports Championship Final"
  "Tech IPO Announcement"
)

SAMPLE_CONTENT=(
  "Stock markets surged today on positive economic data with unemployment at 5-year lows and consumer spending robust..."
  "Researchers announced successful clinical trials of breakthrough treatment showing 85% efficacy rate..."
  "World leaders reached historic agreement on climate action with commitments to 50% emission reductions..."
  "Champion athlete wins record-breaking championship in thrilling final match..."
  "Technology startup completes IPO with strong investor demand and stock up 25% on first day..."
)

# Create all news items
for i in {0..4}; do
  RESPONSE=$(curl -s -X POST http://localhost:3000/api/news \
    -H "Content-Type: application/json" \
    -d "{
      \"title\": \"${SAMPLE_TITLES[$i]}\",
      \"content\": \"${SAMPLE_CONTENT[$i]}\",
      \"source\": \"api\"
    }")
  
  NEWS_ID=$(echo $RESPONSE | grep -o '"newsId":"[^"]*' | cut -d'"' -f4)
  NEWS_IDS+=($NEWS_ID)
  echo "Created: $NEWS_ID"
done

# Wait for enrichment
sleep 10

# Process all through pipeline
for NEWS_ID in "${NEWS_IDS[@]}"; do
  echo "Processing $NEWS_ID..."
  curl -X POST http://localhost:3000/api/bhiv/process \
    -H "Content-Type: application/json" \
    -d "{\"newsItemId\": \"$NEWS_ID\"}" \
    > /dev/null
done

# Stream all to BHIV
curl -X POST http://localhost:3000/api/bhiv/stream \
  -H "Content-Type: application/json" \
  -d '{
    "target": "ttv",
    "filter": {"status": "published"}
  }' | jq '.streamResult'
```

**Expected Outcome:**
- All 5 items processed in parallel
- Each gets classified (5 different categories)
- Each achieves reward > 0.6
- All published within 30-40 seconds total
- Batch stream to BHIV succeeds with 5 items

---

### Scenario 4: Agent Queue Status Monitoring

**Goal:** Monitor agent queues during processing

```bash
# Start in terminal 1: View system info every 2 seconds
watch -n 2 'curl -s http://localhost:3000/api/system/info | jq .'

# In terminal 2: Create lots of news items rapidly
for i in {1..20}; do
  curl -s -X POST http://localhost:3000/api/news \
    -H "Content-Type: application/json" \
    -d "{
      \"title\": \"News Item $i\",
      \"content\": \"Content for news item $i with various information...\",
      \"source\": \"api\"
    }" > /dev/null &
done
wait

# In terminal 3: Monitor via WebSocket
websocat ws://localhost:3001
> {"type": "request_agents"}
```

**Expected Outcome:**
- Agent queues grow as items are created
- Queue lengths decrease as agents process
- Priority ordering respected (fetch first, then verify)
- Final queue lengths return to 0
- WebSocket shows real-time queue status

---

### Scenario 5: Webhook Feedback from BHIV

**Goal:** Simulate BHIV sending back engagement metrics

```bash
# Simulate BHIV webhook (in your BHIV mock server or curl)
curl -X POST http://localhost:3000/api/bhiv/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "newsItemId": "507f1f77bcf86cd799439011",
    "status": "delivered",
    "metrics": {
      "engagement": 0.92,
      "reach": 150000,
      "clicks": 3500,
      "shares": 1200
    },
    "feedback": {
      "userSentiment": "positive",
      "avgTimeSpent": 45,
      "completionRate": 0.88
    }
  }'

# Listen on WebSocket for status update
websocat ws://localhost:3001
# Should receive: 
# {
#   "type": "bhiv_status_update",
#   "data": {...}
# }
```

---

### Scenario 6: Error Handling & Recovery

**Goal:** Test retry logic and error handling

```bash
# Test with missing required field
curl -X POST http://localhost:3000/api/news \
  -H "Content-Type: application/json" \
  -d '{"source": "api"}'
# Expected: 400 Bad Request error

# Test with invalid news ID
curl http://localhost:3000/api/news/invalid123
# Expected: 404 Not Found

# Test system during MongoDB downtime
# (Requires simulating connection loss)
# Expected: 500 error with connection message

# Test task timeout (automatically retried)
# Agent tasks with timeout < 5s will trigger backoff retry
```

---

### Scenario 7: RL Feedback Metrics Analysis

**Goal:** Analyze RL feedback loop performance

```bash
# Get single news metrics
curl 'http://localhost:3000/api/news/507f1f77bcf86cd799439011' | jq '.data.feedback'

# Check if metrics stored in database
# Via MongoDB:
# db.feedback_metrics.find({newsItemId: ObjectId(...)})

# Analyze iteration history
curl 'http://localhost:3000/api/news/507f1f77bcf86cd799439011' | jq '.data.feedback.history'

# Expected output:
{
  "rewardScore": 0.82,
  "toneAccuracy": 0.85,
  "engagementPrediction": 0.79,
  "history": [
    {
      "iteration": 1,
      "score": 0.68,
      "correctionType": "sentiment",
      "timestamp": "2024-11-10T15:30:00Z"
    },
    {
      "iteration": 2,
      "score": 0.82,
      "correctionType": "none",
      "timestamp": "2024-11-10T15:30:05Z"
    }
  ]
}
```

---

### Scenario 8: WebSocket Real-time Monitoring

**Goal:** Monitor all system events in real-time

```bash
# Terminal 1: Start WebSocket listener
websocat ws://localhost:3001

# Terminal 2: Create and process news
# All events appear in Terminal 1

# Expected events:
# 1. {"type": "news_published", "data": {...}}
# 2. {"type": "stream_initiated", "data": {...}}
# 3. {"type": "bhiv_status_update", "data": {...}}

# You can also request stats:
> {"type": "request_stats"}
< {"type": "stats", "stats": {...}, "timestamp": "..."}

# Request agent queues:
> {"type": "request_agents"}
< {"type": "agents", "agents": [...], "timestamp": "..."}
```

---

## Performance Testing

### Load Test: Process 100 News Items

```bash
#!/bin/bash
# save as load_test.sh

echo "Starting load test: 100 news items"
START=$(date +%s)

for i in {1..100}; do
  curl -s -X POST http://localhost:3000/api/news \
    -H "Content-Type: application/json" \
    -d "{
      \"title\": \"News Item $i\",
      \"content\": \"Content $i about various topics in news reporting...\",
      \"source\": \"api\"
    }" > /dev/null
  
  if [ $((i % 10)) -eq 0 ]; then
    echo "Created: $i items"
  fi
done

echo "Waiting 30 seconds for processing..."
sleep 30

# Check results
PUBLISHED=$(curl -s http://localhost:3000/api/news/status/published | grep -o '"_id"' | wc -l)
echo "Published items: $PUBLISHED/100"

END=$(date +%s)
DURATION=$((END - START))
echo "Total time: ${DURATION}s"
echo "Throughput: $((100 * 60 / DURATION)) items/min"
```

Run with:
```bash
chmod +x load_test.sh
./load_test.sh
```

**Expected Metrics:**
- Creation: 100 items in ~20-30 seconds
- Processing: ~50-70% published within 30s
- System handles sustained load without crashes
- Memory usage stays stable

---

## Validation Checklist

- [ ] Database connection established
- [ ] All 5 agents registered
- [ ] Uniguru enrichment working (or mocked)
- [ ] WebSocket connections accepted
- [ ] Single news → published successfully
- [ ] Low-score item triggers auto-reroute
- [ ] Batch processing completed
- [ ] BHIV endpoints respond correctly
- [ ] Metrics logged accurately
- [ ] WebSocket broadcasts working
- [ ] System info reflects correct state
- [ ] Errors logged appropriately
- [ ] Recovery from failures successful

---

## Stress Testing

Monitor during heavy load:
```bash
# Terminal 1: Watch system
watch -n 1 'curl -s http://localhost:3000/health | jq .'

# Terminal 2: Monitor MongoDB connection pool
# Check with MongoDB Atlas dashboard

# Terminal 3: Monitor Node process
node --expose-gc src/index.js  # Enable garbage collection logging

# Terminal 4: Generate load
./load_test.sh
```

Observe for:
- No hung processes
- Connection pool doesn't exceed limits
- Memory usage doesn't grow unbounded
- All items eventually processed
- Error rate stays below 5%

