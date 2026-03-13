import { getNewsItem, updateNewsItem, createFeedbackMetrics, getFeedbackMetrics, updateFeedbackMetrics } from '../db/connection.js';
import fs from 'fs';
import path from 'path';

class RLFeedbackLoop {
  constructor(agentRegistry) {
    this.registry = agentRegistry;
    this.feedbackThreshold = 0.6;  // Reward threshold for auto-reroute
  }

  /**
   * Evaluate news item output and generate reward score
   */
  async evaluateOutput(newsItemId, uniguruService) {
    try {
      const newsItem = await getNewsItem(newsItemId);
      
      if (!newsItem) {
        throw new Error(`News item not found: ${newsItemId}`);
      }

      console.log(`[RL Loop] Evaluating output for ${newsItemId}`);

      // 1. Evaluate tone accuracy
      const toneAccuracy = this.evaluateToneAccuracy(newsItem);

      // 2. Evaluate engagement prediction
      const engagementPrediction = this.evaluateEngagementPrediction(newsItem);

      const baseReward = (toneAccuracy * 0.4) + (engagementPrediction * 0.6);
      const existingMetrics = await getFeedbackMetrics(newsItemId);
      const priorRewards = (existingMetrics?.iterationHistory || []).map(i => i.reward);
      const meanPrior = priorRewards.length ? priorRewards.reduce((a, b) => a + b, 0) / priorRewards.length : baseReward;
      const latencyMs = Date.now() - new Date(newsItem.createdAt).getTime();
      const deterministic = String(process.env.RL_DETERMINISTIC || '').toLowerCase() === 'true';
      const latencyFactor = deterministic ? 1.0 : (latencyMs > 30000 ? 0.9 : 1.0);
      const correctionPressure = deterministic ? 0 : (existingMetrics?.correctionMetrics?.totalCorrections || 0);
      const correctionFactor = deterministic ? 1.0 : (correctionPressure > 3 ? 0.9 : 1.0);
      const scalingBase = deterministic ? baseReward : (meanPrior * 0.5 + baseReward * 0.5);
      const scaling = Math.max(0.7, Math.min(1.3, scalingBase)) * latencyFactor * correctionFactor;
      const rewardScore = Math.max(0, Math.min(1, baseReward * scaling));

      // 4. Determine if corrections needed
      const correctionsNeeded = rewardScore < this.feedbackThreshold;
      const correctionTypes = [];

      if (correctionsNeeded) {
        correctionTypes.push(...this.determineCorrectionTypes(newsItem, rewardScore));
      }

      const metricsData = {
        newsItemId,
        rewardScore,
        toneAccuracy,
        engagementPrediction,
        correctionMetrics: {
          totalCorrections: (existingMetrics?.correctionMetrics?.totalCorrections || 0) + (correctionsNeeded ? 1 : 0),
          correctionTypes: {
            tone: correctionTypes.includes('tone') ? 1 : 0,
            sentiment: correctionTypes.includes('sentiment') ? 1 : 0,
            summary: correctionTypes.includes('summary') ? 1 : 0,
            classification: correctionTypes.includes('classification') ? 1 : 0
          },
          correctionPercentage: correctionsNeeded ? 100 : 0
        },
        latency: {
          totalLatency: Date.now() - new Date(newsItem.createdAt).getTime(),
          classificationLatency: newsItem.classification?.timestamp ? Date.now() - new Date(newsItem.classification.timestamp).getTime() : 0,
          sentimentLatency: newsItem.sentiment?.timestamp ? Date.now() - new Date(newsItem.sentiment.timestamp).getTime() : 0,
          summarizationLatency: newsItem.summary?.timestamp ? Date.now() - new Date(newsItem.summary.timestamp).getTime() : 0
        },
        iterationHistory: existingMetrics?.iterationHistory || []
      };

      // Add current iteration
      metricsData.iterationHistory.push({
        iteration: metricsData.iterationHistory.length + 1,
        reward: rewardScore,
        corrections: correctionTypes,
        timestamp: new Date()
      });

      // Save metrics
      if (existingMetrics) {
        await updateFeedbackMetrics(newsItemId, metricsData);
      } else {
        await createFeedbackMetrics(metricsData);
      }

      const histRewards = metricsData.iterationHistory.map(i => i.reward);
      const meanReward = histRewards.reduce((a, b) => a + b, 0) / histRewards.length;
      this.feedbackThreshold = Math.max(0.5, Math.min(0.9, 0.6 + (meanReward - 0.5) * 0.2));

      try {
        const dir = path.join(process.cwd(), 'logs', 'rl');
        fs.mkdirSync(dir, { recursive: true });
        const line = JSON.stringify({
          newsItemId,
          rewardScore,
          toneAccuracy,
          engagementPrediction,
          correctionsNeeded,
          correctionTypes,
          meanReward,
          totalLatency: metricsData.latency.totalLatency,
          timestamp: new Date().toISOString()
        }) + '\n';
        fs.appendFileSync(path.join(dir, 'rl_metrics.jsonl'), line);
      } catch (e) {
      }

      console.log(`[RL Loop] Reward score: ${rewardScore.toFixed(2)} - Corrections needed: ${correctionsNeeded}`);

      // 6. Handle low scores with auto-reroute
      if (correctionsNeeded && correctionTypes.length > 0) {
        await this.autoReroute(newsItemId, newsItem, correctionTypes, uniguruService);
      }

      return {
        rewardScore,
        toneAccuracy,
        engagementPrediction,
        correctionsNeeded,
        correctionTypes,
        metrics: metricsData
      };
    } catch (error) {
      console.error('[RL Loop] Evaluation error:', error.message);
      throw error;
    }
  }

  /**
   * Evaluate tone accuracy
   */
  evaluateToneAccuracy(newsItem) {
    // Base score from sentiment confidence
    let score = newsItem.sentiment?.confidence || 0.5;

    // Adjust based on aspect sentiments consistency
    if (newsItem.sentiment?.aspects && newsItem.sentiment.aspects.length > 0) {
      const aspectScores = newsItem.sentiment.aspects.map(a => Math.abs(a.score));
      const avgAspectScore = aspectScores.reduce((a, b) => a + b, 0) / aspectScores.length;
      score = (score + avgAspectScore) / 2;
    }

    // Boost if classification is confident
    if (newsItem.classification?.confidence > 0.8) {
      score = Math.min(1, score * 1.1);
    }

    return Math.min(1, Math.max(0, score));
  }

  /**
   * Evaluate engagement prediction
   */
  evaluateEngagementPrediction(newsItem) {
    let score = 0.5;

    // Positive sentiment increases engagement
    if (newsItem.sentiment?.label === 'positive') {
      score += 0.2;
    } else if (newsItem.sentiment?.label === 'neutral') {
      score += 0.1;
    }

    // Key points indicate compelling content
    if (newsItem.summary?.keyPoints && newsItem.summary.keyPoints.length > 2) {
      score += 0.15;
    }

    // Named entities increase engagement (story about people/places/orgs)
    if (newsItem.summary?.entities && newsItem.summary.entities.length > 1) {
      score += 0.1;
    }

    // Certain categories have higher engagement
    const highEngagementCategories = ['Technology', 'Entertainment', 'Sports', 'Business'];
    if (highEngagementCategories.includes(newsItem.classification?.category)) {
      score += 0.1;
    }

    return Math.min(1, Math.max(0, score));
  }

  /**
   * Determine what types of corrections are needed
   */
  determineCorrectionTypes(newsItem, rewardScore) {
    const corrections = [];

    // Check tone accuracy
    if (!newsItem.sentiment || newsItem.sentiment.confidence < 0.6) {
      corrections.push('sentiment');
      corrections.push('tone');
    }

    // Check summary quality
    if (!newsItem.summary?.keyPoints || newsItem.summary.keyPoints.length < 2) {
      corrections.push('summary');
    }

    // Check classification
    if (!newsItem.classification || newsItem.classification.confidence < 0.7) {
      corrections.push('classification');
    }

    return corrections;
  }

  /**
   * Auto-reroute low-scoring outputs for re-processing
   */
  async autoReroute(newsItemId, newsItem, correctionTypes, uniguruService) {
    try {
      console.log(`[RL Loop] Auto-rerouting ${newsItemId} for corrections:`, correctionTypes);

      // Re-process with Uniguru
      if (correctionTypes.includes('sentiment') || correctionTypes.includes('tone')) {
        console.log(`[RL Loop] Re-analyzing sentiment for ${newsItemId}`);
        
        try {
          const newSentiment = await uniguruService.analyzeSentiment(newsItem.content);
          await updateNewsItem(newsItemId, { sentiment: newSentiment });
        } catch (error) {
          console.error(`[RL Loop] Sentiment re-analysis failed:`, error.message);
        }
      }

      if (correctionTypes.includes('summary')) {
        console.log(`[RL Loop] Re-summarizing for ${newsItemId}`);
        
        try {
          const newSummary = await uniguruService.summarizeNews(newsItem.title, newsItem.content);
          await updateNewsItem(newsItemId, { summary: newSummary });
        } catch (error) {
          console.error(`[RL Loop] Summarization re-analysis failed:`, error.message);
        }
      }

      if (correctionTypes.includes('classification')) {
        console.log(`[RL Loop] Re-classifying for ${newsItemId}`);
        
        try {
          const newClassification = await uniguruService.classifyNews(newsItem.title, newsItem.content);
          await updateNewsItem(newsItemId, { classification: newClassification });
        } catch (error) {
          console.error(`[RL Loop] Classification re-analysis failed:`, error.message);
        }
      }

      // Re-evaluate after corrections
      console.log(`[RL Loop] Re-evaluating after corrections for ${newsItemId}`);
      const updatedItem = await getNewsItem(newsItemId);
      const reEvaluation = await this.evaluateOutput(newsItemId, uniguruService);

      console.log(`[RL Loop] New reward score: ${reEvaluation.rewardScore.toFixed(2)}`);

    } catch (error) {
      console.error('[RL Loop] Auto-reroute error:', error.message);
    }
  }

  /**
   * Set feedback threshold
   */
  setThreshold(threshold) {
    if (threshold < 0 || threshold > 1) {
      throw new Error('Threshold must be between 0 and 1');
    }
    this.feedbackThreshold = threshold;
    console.log(`[RL Loop] Threshold set to ${threshold}`);
  }

  /**
   * Log metrics
   */
  async logMetrics(newsItemId) {
    try {
      const metrics = await getFeedbackMetrics(newsItemId);
      
      if (!metrics) {
        console.log(`[RL Loop] No metrics found for ${newsItemId}`);
        return null;
      }

      return {
        newsItemId,
        rewardScore: metrics.rewardScore,
        correctionPercentage: metrics.correctionMetrics.correctionPercentage,
        totalLatency: metrics.latency.totalLatency,
        iterations: metrics.iterationHistory.length
      };
    } catch (error) {
      console.error('[RL Loop] Metrics logging error:', error.message);
      throw error;
    }
  }
}

export default RLFeedbackLoop;
