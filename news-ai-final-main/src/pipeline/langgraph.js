import { getNewsItem, updateNewsItem, logNewsProcessing } from '../db/connection.js';

class NewsProcessingPipeline {
  constructor(agentRegistry, rlFeedbackLoop, uniguruService) {
    this.registry = agentRegistry;
    this.feedbackLoop = rlFeedbackLoop;
    this.uniguruService = uniguruService;
    this.pipelineHistory = [];
  }

  /**
   * Main pipeline: Fetch → Verify → Script → Feedback
   * Automatically retries low-scoring items
   */
  async processNewsItem(newsItemId, maxIterations = 3) {
    try {
      console.log(`\n[Pipeline] Starting processing for ${newsItemId}`);
      
      const startTime = Date.now();
      let currentIteration = 1;
      let rewardScore = 0;
      let pipelineResult = null;

      while (currentIteration <= maxIterations) {
        console.log(`[Pipeline] Iteration ${currentIteration}/${maxIterations}`);

        try {
          // Execute pipeline stages
          pipelineResult = await this.executePipelineStages(newsItemId);
          
          // Evaluate output with RL feedback
          const evaluation = await this.feedbackLoop.evaluateOutput(newsItemId, this.uniguruService);
          rewardScore = evaluation.rewardScore;

          console.log(`[Pipeline] Iteration ${currentIteration} - Reward: ${rewardScore.toFixed(2)}`);

          // Check if we meet quality threshold
          if (rewardScore >= this.feedbackLoop.feedbackThreshold) {
            console.log(`[Pipeline] ✓ Quality threshold met. Publishing...`);
            
            // Promote to published
            await updateNewsItem(newsItemId, {
              status: 'published',
              'publishedMetadata.publishedAt': new Date(),
              'publishedMetadata.publishedBy': 'langgraph-pipeline'
            });

            await logNewsProcessing(newsItemId, 'published', 'langgraph-pipeline', 'completed', {
              reward: rewardScore,
              iterations: currentIteration,
              processingTime: Date.now() - startTime
            });

            break;
          } else if (currentIteration < maxIterations) {
            console.log(`[Pipeline] ↻ Low score, retrying... (${currentIteration}/${maxIterations})`);
            currentIteration++;
          } else {
            console.log(`[Pipeline] ✗ Max iterations reached. Publishing with current quality.`);
            
            // Publish anyway after max iterations
            await updateNewsItem(newsItemId, {
              status: 'published',
              'publishedMetadata.publishedAt': new Date(),
              'publishedMetadata.publishedBy': 'langgraph-pipeline-final'
            });

            await logNewsProcessing(newsItemId, 'published_final', 'langgraph-pipeline', 'completed', {
              reward: rewardScore,
              iterations: currentIteration,
              processingTime: Date.now() - startTime,
              note: 'Published after max iterations'
            });
            break;
          }
        } catch (stageError) {
          console.error(`[Pipeline] Stage error on iteration ${currentIteration}:`, stageError.message);
          
          if (currentIteration < maxIterations) {
            currentIteration++;
          } else {
            throw stageError;
          }
        }
      }

      const result = {
        newsItemId,
        success: true,
        finalRewardScore: rewardScore,
        iterations: currentIteration,
        processingTime: Date.now() - startTime,
        pipelineResult
      };

      this.pipelineHistory.push(result);
      console.log(`[Pipeline] ✓ Completed: ${JSON.stringify(result)}`);

      return result;
    } catch (error) {
      console.error('[Pipeline] Fatal error:', error.message);
      
      await logNewsProcessing(newsItemId, 'pipeline_failed', 'langgraph-pipeline', 'failed', {
        error: error.message
      });

      throw error;
    }
  }

  /**
   * Execute pipeline stages in sequence
   */
  async executePipelineStages(newsItemId) {
    const results = {
      fetch: null,
      verify: null,
      script: null
    };

    try {
      // Stage 1: Fetch (already done at creation, but ensure data is valid)
      console.log(`[Pipeline:Fetch] Processing`);
      const fetchTask = await this.registry.submitTask(
        newsItemId,
        'fetch',
        { action: 'validate_and_fetch' },
        10
      );
      results.fetch = await this.waitForTask(fetchTask.taskId);

      // Stage 2: Verify (check facts and credibility)
      console.log(`[Pipeline:Verify] Processing`);
      const verifyTask = await this.registry.submitTask(
        newsItemId,
        'verify',
        { action: 'verify_facts' },
        9
      );
      results.verify = await this.waitForTask(verifyTask.taskId);

      // Stage 3: Script (generate compelling narrative)
      console.log(`[Pipeline:Script] Processing`);
      const scriptTask = await this.registry.submitTask(
        newsItemId,
        'script',
        { action: 'generate_script' },
        7
      );
      results.script = await this.waitForTask(scriptTask.taskId);

      console.log(`[Pipeline] All stages completed for ${newsItemId}`);

      return results;
    } catch (error) {
      console.error('[Pipeline:Stages] Error:', error.message);
      throw error;
    }
  }

  /**
   * Wait for async task to complete
   */
  async waitForTask(taskId, maxWaitMs = 30000) {
    const startTime = Date.now();
    const pollIntervalMs = 500;

    return new Promise((resolve, reject) => {
      const pollTask = async () => {
        if (Date.now() - startTime > maxWaitMs) {
          reject(new Error(`Task timeout: ${taskId}`));
          return;
        }

        try {
          // In real implementation, query database for task status
          // For now, simulate task completion
          await new Promise(r => setTimeout(r, pollIntervalMs));
          
          // After poll interval, assume task completed
          if (Date.now() - startTime > 1000) {
            resolve({ status: 'completed', taskId });
            return;
          }

          pollTask();
        } catch (error) {
          reject(error);
        }
      };

      pollTask();
    });
  }

  /**
   * Process batch of news items
   */
  async processBatch(newsItemIds, maxIterations = 3) {
    console.log(`\n[Pipeline] Processing batch of ${newsItemIds.length} items`);
    
    const results = await Promise.allSettled(
      newsItemIds.map(id => this.processNewsItem(id, maxIterations))
    );

    const summary = {
      total: newsItemIds.length,
      successful: results.filter(r => r.status === 'fulfilled').length,
      failed: results.filter(r => r.status === 'rejected').length,
      results: results.map((r, i) => ({
        newsItemId: newsItemIds[i],
        status: r.status,
        data: r.status === 'fulfilled' ? r.value : { error: r.reason.message }
      }))
    };

    console.log(`[Pipeline] Batch complete: ${summary.successful}/${summary.total} successful`);
    return summary;
  }

  /**
   * Get pipeline statistics
   */
  getPipelineStats() {
    if (this.pipelineHistory.length === 0) {
      return null;
    }

    const successful = this.pipelineHistory.filter(r => r.success);
    const avgReward = successful.reduce((a, r) => a + r.finalRewardScore, 0) / successful.length;
    const avgIterations = successful.reduce((a, r) => a + r.iterations, 0) / successful.length;
    const avgTime = successful.reduce((a, r) => a + r.processingTime, 0) / successful.length;

    return {
      totalProcessed: this.pipelineHistory.length,
      successful: successful.length,
      failed: this.pipelineHistory.length - successful.length,
      averageRewardScore: avgReward,
      averageIterations: avgIterations,
      averageProcessingTime: avgTime,
      successRate: (successful.length / this.pipelineHistory.length * 100).toFixed(2) + '%'
    };
  }

  /**
   * Reset history
   */
  resetHistory() {
    this.pipelineHistory = [];
    console.log('[Pipeline] History reset');
  }
}

export default NewsProcessingPipeline;
