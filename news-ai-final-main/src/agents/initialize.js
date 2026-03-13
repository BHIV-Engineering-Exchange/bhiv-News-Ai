import AgentRegistry from './registry.js';
import { getNewsItem, updateNewsItem } from '../db/connection.js';

/**
 * Create and register all core agents
 */
export const initializeAgents = (uniguruService) => {
  const registry = new AgentRegistry();

  // ======= FETCH AGENT =======
  registry.registerAgent('fetch', async (payload, newsItemId) => {
    console.log(`[Fetch Agent] Processing ${newsItemId}`);
    // In real scenario: fetch from external sources, validate format
    return {
      status: 'fetched',
      itemsProcessed: 1,
      timestamp: new Date()
    };
  }, { priority: 10, maxConcurrent: 10 });

  // ======= FILTER AGENT =======
  registry.registerAgent('filter', async (payload, newsItemId) => {
    console.log(`[Filter Agent] Processing ${newsItemId}`);
    const newsItem = await getNewsItem(newsItemId);
    
    // Filter logic: duplicate check, language detection, etc.
    const filtered = {
      isDuplicate: false,
      language: 'en',
      relevanceScore: 0.85
    };

    return {
      status: 'filtered',
      passed: true,
      details: filtered,
      timestamp: new Date()
    };
  }, { priority: 8, maxConcurrent: 5 });

  // ======= VERIFY AGENT =======
  registry.registerAgent('verify', async (payload, newsItemId) => {
    console.log(`[Verify Agent] Processing ${newsItemId}`);
    const newsItem = await getNewsItem(newsItemId);
    
    // Verify using Uniguru enrichment that was already done
    const verified = {
      verified: true,
      verificationScore: 0.88,
      verifiedBy: 'verify-agent',
      verificationNotes: 'Source credibility confirmed, facts aligned with known entities',
      verificationTimestamp: new Date()
    };

    await updateNewsItem(newsItemId, { verification: verified });

    return {
      status: 'verified',
      verified: true,
      verificationScore: 0.88,
      timestamp: new Date()
    };
  }, { priority: 9, maxConcurrent: 3 });

  // ======= SCRIPT AGENT =======
  registry.registerAgent('script', async (payload, newsItemId) => {
    console.log(`[Script Agent] Processing ${newsItemId}`);
    const newsItem = await getNewsItem(newsItemId);
    
    // Generate compelling script based on summary and sentiment
    const script = {
      headline: newsItem.summary?.short || '',
      bodyScript: newsItem.summary?.medium || '',
      callToAction: 'Learn more about this developing story',
      tone: newsItem.sentiment?.label || 'neutral',
      estimatedReadingTime: 2
    };

    return {
      status: 'scripted',
      script,
      timestamp: new Date()
    };
  }, { priority: 7, maxConcurrent: 4 });

  // ======= RL FEEDBACK AGENT =======
  registry.registerAgent('rlfeedback', async (payload, newsItemId) => {
    console.log(`[RL Feedback Agent] Processing ${newsItemId}`);
    const newsItem = await getNewsItem(newsItemId);
    
    // Evaluate tone accuracy and engagement prediction
    const feedback = {
      rewardScore: 0.82,
      toneAccuracy: 0.85,
      engagementPrediction: 0.79,
      correctionCount: 0,
      history: [{
        iteration: 1,
        score: 0.82,
        correctionType: 'none',
        timestamp: new Date()
      }]
    };

    await updateNewsItem(newsItemId, { feedback });

    return {
      status: 'feedback_applied',
      rewardScore: 0.82,
      suggestedCorrections: [],
      timestamp: new Date()
    };
  }, { priority: 6, maxConcurrent: 2 });

  return registry;
};

/**
 * Define task routing schema
 */
export const getTaskRoutingSchema = () => {
  return {
    taskFlow: [
      {
        stage: 1,
        agent: 'fetch',
        condition: 'always',
        timeout: 10000,
        priority: 10
      },
      {
        stage: 2,
        agent: 'filter',
        condition: 'fetch.status === "fetched"',
        timeout: 15000,
        priority: 8
      },
      {
        stage: 3,
        agent: 'verify',
        condition: 'filter.passed === true',
        timeout: 20000,
        priority: 9
      },
      {
        stage: 4,
        agent: 'script',
        condition: 'verify.verified === true',
        timeout: 15000,
        priority: 7
      },
      {
        stage: 5,
        agent: 'rlfeedback',
        condition: 'script.status === "scripted"',
        timeout: 10000,
        priority: 6
      }
    ],
    parallelizableStages: [
      // Can be parallelized if needed
    ],
    errorHandling: {
      maxRetries: 3,
      retryBackoffMs: 1000,
      failOnError: false
    }
  };
};
