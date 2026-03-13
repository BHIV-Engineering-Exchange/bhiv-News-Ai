# Scheduler Behavior and Run Policy Documentation

## Overview

The News AI Backend includes an automated scheduler that processes news from various sources at predefined intervals. This document outlines the scheduler's behavior, run policies, and operational guidelines.

## Scheduler Architecture

The scheduler uses APScheduler with AsyncIO support and maintains jobs in memory. Key characteristics:

- **Timezone**: UTC
- **Job Store**: MemoryJobStore (jobs are lost on restart)
- **Executor**: AsyncIOExecutor
- **Max Instances**: 3 concurrent jobs
- **Misfire Grace Time**: 30 seconds
- **Coalesce**: True (combine missed runs)

## News Categories and Schedules

The scheduler processes news from 5 categories with different frequencies:

### 1. Live News (`live`)
- **Interval**: Every 15 minutes (`*/15 * * * *`)
- **Sources**: BBC, Reuters, NYT, Al Jazeera, The Guardian
- **Priority**: 10 (highest)
- **Pipeline Options**:
  - Channels: `news_channel_live`
  - Avatars: `avatar_breaking`
  - Voice: `urgent`
  - BHIV Push: Enabled
  - Audio: Enabled

### 2. Finance News (`finance`)
- **Interval**: Every hour (`0 * * * *`)
- **Sources**: Bloomberg, WSJ, FT, CNBC, MarketWatch
- **Priority**: 7
- **Pipeline Options**:
  - Channels: `news_channel_finance`
  - Avatars: `avatar_business`
  - Voice: `professional`

### 3. World News (`world`)
- **Interval**: Every 6 hours (`0 */6 * * *`)
- **Sources**: BBC World, Reuters World, Al Jazeera, DW
- **Priority**: 5
- **Pipeline Options**:
  - Channels: `news_channel_world`
  - Avatars: `avatar_global`
  - Voice: `neutral`

### 4. Regional News (`regional`)
- **Interval**: Every 6 hours (`0 */6 * * *`)
- **Sources**: The Hindu, Indian Express, NDTV, Times of India
- **Priority**: 3
- **Pipeline Options**:
  - Channels: `news_channel_regional`
  - Avatars: `avatar_local`
  - Voice: `conversational`

### 5. Kids News (`kids`)
- **Interval**: Every 6 hours (`0 */6 * * *`)
- **Sources**: Scholastic, Time for Kids, National Geographic Kids, BBC Newsround
- **Priority**: 1 (lowest)
- **Pipeline Options**:
  - Channels: `news_channel_kids`
  - Avatars: `avatar_fun`
  - Voice: `friendly`
  - Audio: Disabled

## Job Staggering

To prevent system overload, jobs within each category are staggered:

- **Stagger Interval**: 2 minutes between sources
- **Example**: Finance category jobs run at :00, :02, :04, :06, :08 past each hour

## Run Policy

### Automatic Processing
1. Scheduler submits jobs to the background queue instead of processing directly
2. Each job uses the unified pipeline with category-specific options
3. Jobs are prioritized based on category importance
4. Failed jobs are logged but don't stop the scheduler

### Manual Triggers
The scheduler supports manual trigger endpoints:

- **Single Source**: `/api/scheduler/trigger?category=live&source_url=https://...`
- **Category**: `/api/scheduler/trigger?category=finance` (all sources)
- **All Categories**: `/api/scheduler/trigger` (one source per category)

### Queue Integration
- All scheduled jobs are submitted to the background queue
- Queue handles job execution asynchronously
- Job status can be monitored via `/api/queue/job/{job_id}`
- Queue statistics available at `/api/queue/stats`

## Monitoring and Statistics

### Scheduler Stats
Available at `/api/scheduler/stats`:

```json
{
  "running": true,
  "stats": {
    "jobs_scheduled": 25,
    "jobs_completed": 150,
    "jobs_failed": 2,
    "last_run": "2024-01-14T10:30:00.000Z",
    "next_runs": {...}
  },
  "jobs": [
    {
      "id": "live_0",
      "name": "Process live news from https://www.bbc.com/news",
      "next_run": "2024-01-14T10:45:00.000Z",
      "trigger": "*/15 * * * *"
    }
  ]
}
```

### Queue Stats
Available at `/api/queue/stats`:

```json
{
  "pending": 5,
  "processing": 2,
  "completed": 143,
  "failed": 2,
  "total_processed": 147
}
```

## Failure Handling

### Job Failures
- Individual job failures don't stop the scheduler
- Failed jobs are logged with error details
- Statistics track failure counts
- Jobs can be manually retriggered

### System Failures
- Scheduler can be stopped and restarted via API
- Jobs are rescheduled on restart (memory store)
- Misfired jobs are coalesced

## Operational Guidelines

### Starting the Scheduler
```bash
POST /api/scheduler/start
```

### Stopping the Scheduler
```bash
POST /api/scheduler/stop
```

### Manual Processing
```bash
POST /api/scheduler/trigger?category=live&source_url=https://www.bbc.com/news
```

### Monitoring
- Check scheduler stats regularly
- Monitor queue backlog
- Review failure logs
- Ensure system resources are adequate

## Production Considerations

### Resource Management
- Max 3 concurrent jobs prevents overload
- Queue-based processing allows backpressure
- Priority system ensures critical news is processed first

### Reliability
- Memory job store requires careful restart procedures
- Consider persistent job store for production
- Monitor queue depth and processing times

### Scaling
- Increase max_instances for higher throughput
- Add more workers for queue processing
- Consider distributed scheduling for multi-instance deployments

## API Endpoints

- `POST /api/scheduler/start` - Start scheduler
- `POST /api/scheduler/stop` - Stop scheduler
- `GET /api/scheduler/stats` - Get scheduler statistics
- `POST /api/scheduler/trigger` - Manual trigger

## Version History

- **v1.0.0**: Initial implementation with 5 categories
- **Schema Frozen**: Yes (for stable-v1 release)