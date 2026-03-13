# News AI Admin Panel - Quick Start Guide

## 🎛️ Admin Panel Overview

The News AI Admin Panel provides system administrators and content creators with tools to monitor, manage, and optimize the News AI production pipeline.

## 🚀 Quick Start

### 1. Access the Admin Panel
```
URL: https://api.news-ai.com/admin
Authentication: API Key required (contact system administrator)
```

### 2. Dashboard Overview
The admin panel provides real-time insights into:
- **System Health** - Backend, database, and external service status
- **Pipeline Performance** - Success rates, latency, and throughput
- **RL Analytics** - Reward scores, correction rates, and model performance
- **Queue Management** - Background job status and worker utilization
- **Content Analytics** - News processing statistics and trends

## 📊 Key Admin Features

### System Monitoring
```bash
# Check overall system health
GET /health

# View detailed service status
GET /api/health

# Monitor background queue
GET /api/queue/stats

# Check scheduler status
GET /api/scheduler/stats
```

### RL System Management
```bash
# View RL performance metrics
GET /api/rl/metrics

# Access detailed RL logs
GET /logs/rl/rl_metrics.jsonl

# Review test results
GET /logs/rl/rl_test_results.json
```

### Content Management
```bash
# Browse processed news items
GET /api/news?status=published&limit=50

# Search specific articles
GET /api/news/search?q=keyword

# View processing statistics
GET /api/analytics/processing
```

### Queue & Scheduler Control
```bash
# Manually trigger news processing
POST /api/scheduler/trigger
{
  "category": "live",
  "source_url": "https://example.com/news"
}

# View active jobs
GET /api/queue/jobs

# Cancel specific job
DELETE /api/queue/job/{job_id}
```

## 🔧 Common Admin Tasks

### Daily Monitoring Checklist
1. **System Health Check**
   - Verify all services are operational
   - Check error rates and latency
   - Review recent failures

2. **Performance Review**
   - Monitor average processing time
   - Check RL correction rates
   - Review queue backlog

3. **Content Quality Assessment**
   - Sample recent outputs
   - Review authenticity scores
   - Check engagement metrics

### Weekly Maintenance Tasks
1. **Log Rotation**
   ```bash
   # RL logs are automatically rotated
   # Check log sizes and compression
   ls -la logs/rl/
   ```

2. **Performance Optimization**
   - Review and adjust RL weights
   - Update news source lists
   - Optimize database queries

3. **Security Updates**
   - Rotate API keys
   - Update dependencies
   - Review access logs

### Monthly Reporting
1. **Generate Performance Reports**
   ```bash
   # Export RL metrics for analysis
   GET /api/rl/metrics?period=monthly

   # Download processing statistics
   GET /api/analytics/monthly
   ```

2. **Content Analytics**
   - Top-performing categories
   - User engagement trends
   - Quality improvement metrics

## 🚨 Alert Management

### Critical Alerts
- **System Down**: Backend unresponsive for >5 minutes
- **High Error Rate**: >10% of requests failing
- **Queue Backlog**: >1000 pending jobs
- **RL Performance**: Reward score drops below 0.5

### Warning Alerts
- **High Latency**: Average response >10 seconds
- **Low Success Rate**: <90% pipeline success
- **Storage Issues**: Database nearing capacity
- **External Service**: Uniguru/BHIV API degradation

### Response Procedures

#### System Down Alert
1. Check Railway dashboard for infrastructure issues
2. Verify database connectivity
3. Restart failed services
4. Notify development team if manual intervention required

#### High Error Rate Alert
1. Review recent error logs
2. Check external service status (Uniguru, BHIV)
3. Verify API rate limits
4. Implement fallback processing if needed

#### Queue Backlog Alert
1. Increase worker count if possible
2. Check for stuck jobs
3. Review processing bottlenecks
4. Consider temporary rate limiting

## 📈 Performance Optimization

### RL System Tuning
```python
# Adjust reward weights based on performance
# Higher engagement weight for better user interaction
# Higher quality weight for more accurate content

current_weights = {
    "tone_weight": 0.25,
    "engagement_weight": 0.50,  # Increased for better engagement
    "quality_weight": 0.25
}
```

### Queue Optimization
- **Worker Scaling**: Adjust based on load (2-10 workers)
- **Priority Management**: Ensure critical jobs are processed first
- **Retry Configuration**: Optimize backoff strategies

### Database Optimization
- **Indexing**: Ensure proper indexes on frequently queried fields
- **Connection Pooling**: Maintain optimal connection pool size
- **Query Optimization**: Monitor and optimize slow queries

## 🔐 Security Best Practices

### Access Control
- Use strong API keys with appropriate permissions
- Implement IP whitelisting for admin access
- Regular key rotation (monthly)

### Data Protection
- Encrypt sensitive configuration data
- Regular database backups
- Secure log storage and rotation

### Monitoring & Auditing
- Log all admin actions
- Monitor for suspicious activity
- Regular security audits

## 📞 Support & Troubleshooting

### Getting Help
1. **Documentation**: Check this guide first
2. **Logs**: Review system and application logs
3. **Metrics**: Use admin panel dashboards
4. **Team**: Contact development team for complex issues

### Common Issues & Solutions

#### High Latency Issues
```
Symptoms: Slow response times, timeout errors
Solutions:
- Check database performance
- Review external API response times
- Scale worker processes
- Optimize database queries
```

#### Memory Issues
```
Symptoms: Out of memory errors, service restarts
Solutions:
- Monitor memory usage patterns
- Adjust worker process limits
- Implement memory-efficient processing
- Consider horizontal scaling
```

#### External Service Failures
```
Symptoms: Uniguru/BHIV API errors
Solutions:
- Check service status pages
- Implement fallback processing
- Adjust retry logic
- Contact service providers if needed
```

## 🎯 Advanced Configuration

### Custom Scheduling
```python
# Add new news categories
scheduler.add_news_category(
    name="breaking",
    interval="*/5",  # Every 5 minutes
    sources=["https://breaking-news-source.com"]
)
```

### RL Model Updates
```python
# Update RL reward function
rl_service.update_reward_function({
    "tone_weight": 0.3,
    "engagement_weight": 0.4,
    "quality_weight": 0.3,
    "freshness_bonus": 0.1
})
```

### Performance Tuning
```python
# Adjust system parameters
config.update({
    "max_workers": 8,
    "queue_size_limit": 2000,
    "rate_limit_per_minute": 200,
    "db_connection_pool": 20
})
```

---

*This quick start guide provides essential information for administering the News AI production system. For detailed technical documentation, refer to the API documentation and integration guides.*