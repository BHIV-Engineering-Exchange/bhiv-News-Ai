# 🛡️ Fallback Strategy Documentation

## Overview

This document outlines the comprehensive fallback strategies implemented across the News AI system to ensure high availability, graceful degradation, and automatic recovery from various failure scenarios.

## 🏗️ Fallback Architecture

### Primary Principles
1. **Graceful Degradation**: System continues operating with reduced functionality
2. **Automatic Recovery**: Self-healing mechanisms for transient failures
3. **User Transparency**: Failures handled without user awareness when possible
4. **Data Preservation**: No data loss during failure scenarios

### Fallback Hierarchy
```
Level 1: Component-level fallbacks (immediate, automatic)
Level 2: Service-level fallbacks (short-term degradation)
Level 3: System-level fallbacks (long-term alternatives)
Level 4: Manual intervention (human oversight required)
```

## 🔧 Component-Level Fallbacks

### 1. Uniguru AI Service Failure

**Detection Mechanism:**
```python
async def check_uniguru_health() -> bool:
    """Check Uniguru API availability"""
    try:
        response = await uniguru_client.health_check()
        return response.status_code == 200
    except Exception:
        return False
```

**Fallback Strategy:**
```python
async def classify_with_fallback(text: str) -> dict:
    """Classify text with fallback mechanisms"""

    # Primary: Uniguru API
    try:
        result = await uniguru_service.classify_text(text)
        if result['success']:
            return result
    except Exception as e:
        logger.warning(f"Uniguru classification failed: {e}")

    # Fallback 1: Cached classifications
    cached_result = await get_cached_classification(text)
    if cached_result:
        return cached_result

    # Fallback 2: Rule-based classification
    return await rule_based_classification(text)

    # Fallback 3: Default category
    return {
        'success': True,
        'category': 'general',
        'method': 'fallback_default',
        'confidence': 0.5
    }
```

**Recovery Process:**
- Retry with exponential backoff (1s, 2s, 4s, 8s)
- Maximum 3 retry attempts
- Circuit breaker pattern for sustained failures
- Automatic health checks every 30 seconds

### 2. Sankalp Audio Generation Failure

**Detection:**
```python
async def validate_audio_generation(text: str, voice: str) -> bool:
    """Validate audio generation capability"""
    try:
        # Quick validation request
        test_result = await sankalp_service.generate_audio(
            text="test", voice=voice, validate_only=True
        )
        return test_result['available']
    except Exception:
        return False
```

**Fallback Strategy:**
```python
async def generate_audio_with_fallback(script_data: dict) -> dict:
    """Generate audio with comprehensive fallbacks"""

    text = script_data['content']
    preferred_voice = script_data.get('voice', 'alice')

    # Primary: Preferred voice
    try:
        result = await sankalp_service.generate_audio(text, preferred_voice)
        if result['success']:
            return result
    except Exception as e:
        logger.warning(f"Primary audio generation failed: {e}")

    # Fallback 1: Alternative voice
    alternative_voices = ['alice', 'bob', 'charlie']
    alternative_voices.remove(preferred_voice)

    for voice in alternative_voices:
        try:
            result = await sankalp_service.generate_audio(text, voice)
            if result['success']:
                result['fallback_voice'] = True
                return result
        except Exception:
            continue

    # Fallback 2: Text-to-speech service
    try:
        result = await fallback_tts_service.generate_audio(text, 'neutral')
        result['method'] = 'fallback_tts'
        return result
    except Exception as e:
        logger.error(f"All audio generation failed: {e}")

    # Fallback 3: Skip audio, continue pipeline
    return {
        'success': False,
        'skipped': True,
        'reason': 'audio_generation_unavailable',
        'text_available': True
    }
```

**Recovery:**
- Voice availability checks every 60 seconds
- Automatic failover between voice options
- Queue audio generation for later retry

### 3. BHIV Core Push Failure

**Detection:**
```python
async def check_bhiv_connectivity() -> dict:
    """Check BHIV Core connection status"""
    try:
        status = await bhiv_service.check_bhiv_status()
        return {
            'available': status.get('status') == 'healthy',
            'channels': status.get('available_channels', []),
            'response_time': status.get('response_time', 0)
        }
    except Exception:
        return {'available': False, 'channels': []}
```

**Fallback Strategy:**
```python
async def push_with_fallback(content: dict, channel: str, avatar: str) -> dict:
    """Push content to BHIV with fallback handling"""

    # Primary: Direct push
    try:
        result = await bhiv_service.push_to_bhiv_core(channel, avatar, content)
        if result['success']:
            return result
    except Exception as e:
        logger.warning(f"BHIV push failed: {e}")

    # Fallback 1: Retry with backoff
    for attempt in range(3):
        try:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            result = await bhiv_service.push_to_bhiv_core(channel, avatar, content)
            if result['success']:
                return result
        except Exception:
            continue

    # Fallback 2: Queue for later delivery
    await background_queue.add_job(
        'bhiv_push_retry',
        {
            'content': content,
            'channel': channel,
            'avatar': avatar,
            'retry_count': 0,
            'max_retries': 5
        }
    )

    # Fallback 3: Store for manual review
    await db_service.store_failed_push({
        'content': content,
        'channel': channel,
        'avatar': avatar,
        'failure_reason': str(e),
        'timestamp': datetime.now().isoformat()
    })

    return {
        'success': False,
        'queued_for_retry': True,
        'stored_for_review': True,
        'estimated_retry': '6 hours'
    }
```

**Recovery:**
- Connection health checks every 30 seconds
- Automatic retry queue processing
- Manual review workflow for failed pushes

## 🌐 Network & Infrastructure Fallbacks

### 4. Database Connection Failure

**Detection:**
```python
async def validate_database_connection() -> bool:
    """Validate MongoDB Atlas connectivity"""
    try:
        db = await db_service.get_database()
        await db.command('ping')
        return True
    except Exception:
        return False
```

**Fallback Strategy:**
```python
async def store_with_fallback(data: dict, collection: str) -> dict:
    """Store data with database fallback"""

    # Primary: MongoDB Atlas
    try:
        result = await db_service.insert_document(collection, data)
        return {'success': True, 'method': 'primary', 'id': result.inserted_id}
    except Exception as e:
        logger.warning(f"Primary database failed: {e}")

    # Fallback 1: Local file storage
    try:
        filename = f"fallback_{collection}_{int(time.time())}.json"
        with open(f"fallback_storage/{filename}", 'w') as f:
            json.dump(data, f)
        return {'success': True, 'method': 'local_file', 'filename': filename}
    except Exception as e:
        logger.error(f"Local storage failed: {e}")

    # Fallback 2: Memory cache (temporary)
    cache_key = f"{collection}_{hash(str(data))}"
    memory_cache[cache_key] = {
        'data': data,
        'timestamp': datetime.now().isoformat(),
        'expires': (datetime.now() + timedelta(hours=24)).isoformat()
    }
    return {'success': True, 'method': 'memory_cache', 'cache_key': cache_key}
```

**Recovery:**
- Connection pool monitoring
- Automatic reconnection logic
- Data synchronization when primary DB recovers

### 5. WebSocket Connection Failure

**Detection:**
```python
def check_websocket_health() -> dict:
    """Check WebSocket server health"""
    return {
        'connections': len(active_connections),
        'uptime': websocket_server.uptime,
        'message_rate': websocket_server.message_rate,
        'error_rate': websocket_server.error_rate
    }
```

**Fallback Strategy:**
```python
async def send_realtime_update(user_id: str, update_data: dict):
    """Send real-time update with fallback"""

    # Primary: WebSocket
    try:
        if user_id in active_connections:
            await active_connections[user_id].send_json(update_data)
            return {'success': True, 'method': 'websocket'}
    except Exception as e:
        logger.warning(f"WebSocket send failed: {e}")

    # Fallback 1: Server-sent events (SSE)
    try:
        await sse_service.send_event(user_id, update_data)
        return {'success': True, 'method': 'sse'}
    except Exception:
        pass

    # Fallback 2: HTTP polling notification
    try:
        await polling_service.queue_notification(user_id, update_data)
        return {'success': True, 'method': 'polling'}
    except Exception as e:
        logger.error(f"All real-time methods failed: {e}")

    # Fallback 3: Email notification (critical updates only)
    if update_data.get('priority') == 'high':
        await email_service.send_notification(
            user_id, "Pipeline Update", json.dumps(update_data, indent=2)
        )
        return {'success': True, 'method': 'email'}
```

## 🤖 AI/ML Fallbacks

### 6. RL Model Failure

**Detection:**
```python
async def validate_rl_model() -> bool:
    """Validate RL feedback model availability"""
    try:
        test_input = {'news_item': {}, 'script_output': {}}
        result = await rl_service.calculate_reward(test_input['news_item'], test_input['script_output'])
        return 'reward' in result
    except Exception:
        return False
```

**Fallback Strategy:**
```python
async def calculate_reward_with_fallback(news_item: dict, script_output: dict) -> dict:
    """Calculate RL reward with fallbacks"""

    # Primary: Full RL model
    try:
        reward = await rl_service.calculate_reward(news_item, script_output)
        if reward['success']:
            return reward
    except Exception as e:
        logger.warning(f"RL model failed: {e}")

    # Fallback 1: Simplified scoring
    try:
        simplified_score = await simplified_reward_calculator(news_item, script_output)
        return {
            'success': True,
            'reward': simplified_score,
            'method': 'simplified',
            'confidence': 0.7
        }
    except Exception:
        pass

    # Fallback 2: Rule-based scoring
    rule_score = calculate_rule_based_reward(news_item, script_output)
    return {
        'success': True,
        'reward': rule_score,
        'method': 'rule_based',
        'confidence': 0.5
    }
```

### 7. Agent Processing Failure

**Fallback Strategy:**
```python
async def process_with_agent_fallback(agent_type: str, task_data: dict) -> dict:
    """Process task with agent fallback"""

    # Primary: Specialized agent
    try:
        result = await agent_registry.submit_task(agent_type, task_data)
        if result and result['success']:
            return result
    except Exception as e:
        logger.warning(f"Agent {agent_type} failed: {e}")

    # Fallback 1: Alternative agent
    fallback_agents = {
        'content_fetch': ['web_scraper'],
        'content_filter': ['basic_filter'],
        'content_verify': ['authenticity_checker'],
        'script_generator': ['basic_script_writer']
    }

    for fallback_agent in fallback_agents.get(agent_type, []):
        try:
            result = await agent_registry.submit_task(fallback_agent, task_data)
            if result and result['success']:
                result['fallback_agent'] = True
                return result
        except Exception:
            continue

    # Fallback 2: Direct processing
    return await direct_processing_fallback(agent_type, task_data)
```

## 📊 Monitoring & Alerting

### Fallback Health Dashboard

```python
async def get_fallback_status() -> dict:
    """Get comprehensive fallback system status"""
    return {
        'uniguru_fallback': await check_uniguru_fallback_status(),
        'sankalp_fallback': await check_sankalp_fallback_status(),
        'bhiv_fallback': await check_bhiv_fallback_status(),
        'database_fallback': await check_database_fallback_status(),
        'websocket_fallback': await check_websocket_fallback_status(),
        'rl_fallback': await check_rl_fallback_status(),
        'overall_health': calculate_overall_fallback_health()
    }
```

### Alert Thresholds
- **Warning**: >5% fallback usage in 1 hour
- **Critical**: >20% fallback usage in 1 hour
- **Emergency**: >50% fallback usage sustained

### Automated Recovery Actions
- Service restart on repeated failures
- Circuit breaker activation/deactivation
- Load balancer adjustments
- Resource scaling triggers

## 🧪 Fallback Testing

### Test Scenarios
```python
async def run_fallback_tests():
    """Comprehensive fallback testing suite"""

    test_scenarios = [
        'uniguru_service_down',
        'sankalp_audio_unavailable',
        'bhiv_core_timeout',
        'database_connection_lost',
        'websocket_server_crash',
        'rl_model_corruption',
        'network_partition',
        'high_load_conditions'
    ]

    results = []
    for scenario in test_scenarios:
        result = await test_fallback_scenario(scenario)
        results.append(result)

    return generate_fallback_test_report(results)
```

### Performance Benchmarks
- **Detection Time**: <5 seconds for all failures
- **Fallback Activation**: <10 seconds
- **Recovery Time**: <30 seconds for transient failures
- **Data Loss**: 0% during fallback operations

---

*This fallback strategy ensures the News AI system maintains high availability and graceful degradation across all failure scenarios, with comprehensive monitoring and automatic recovery mechanisms.*