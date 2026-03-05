import express from 'express';
import axios from 'axios';
import { getNewsItem, getNewsByStatus } from '../db/connection.js';

export const createBhivRouter = (newsPipeline, rlFeedbackLoop, broadcastUpdate = () => {}) => {
  const router = express.Router();

  function mapNoopurToSeeyaArticle(item, reward = 0) {
    return {
      id: String(item._id),
      title: item.title,
      source_name: item.source || 'noopur',
      source_url: item.sourceUrl || '',
      thumbnail_url: item.thumbnail_url || '',
      category: item.classification?.category || 'general',
      published_at: item.publishedMetadata?.publishedAt || new Date(),
      relevance_score: reward || item.feedback?.rewardScore || 0,
      processing_status: item.status,
      processing_progress: item.processingLog?.length || 0,
      group_key: item.classification?.subcategory || null
    };
  }

  /**
   * POST /api/bhiv/process - Process news through pipeline and send to BHIV
   */
  router.post('/process', async (req, res) => {
    try {
      const { newsItemId, distribution } = req.body;

      if (!newsItemId) {
        return res.status(400).json({
          success: false,
          error: 'newsItemId is required'
        });
      }

      // Process through pipeline
      const pipelineResult = await newsPipeline.processNewsItem(newsItemId, 3);

      // Get processed news item
      const newsItem = await getNewsItem(newsItemId);

      // Send to BHIV endpoints
      const bhivResult = await sendToBhiv(newsItem, distribution || {});

      // Broadcast update
      broadcastUpdate('news_published', {
        newsItemId,
        status: 'published',
        reward: pipelineResult.finalRewardScore,
        bhivStatus: bhivResult.status,
        article: mapNoopurToSeeyaArticle(newsItem, pipelineResult.finalRewardScore)
      });

      res.json({
        success: true,
        message: 'News processed and sent to BHIV',
        pipelineResult,
        bhivResult,
        newsItem: {
          id: newsItem._id,
          title: newsItem.title,
          status: newsItem.status,
          reward: pipelineResult.finalRewardScore
        },
        seeya_compat: mapNoopurToSeeyaArticle(newsItem, pipelineResult.finalRewardScore)
      });
    } catch (error) {
      console.error('Error in BHIV processing:', error.message);
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  /**
   * POST /api/bhiv/stream - Stream published news to BHIV endpoints
   */
  router.post('/stream', async (req, res) => {
    try {
      const { target, newsItemIds, filter } = req.body;

      if (!target) {
        return res.status(400).json({
          success: false,
          error: 'Target (ttv or vaani) is required'
        });
      }

      // Get news items
      let newsItems;
      if (newsItemIds && newsItemIds.length > 0) {
        newsItems = await Promise.all(
          newsItemIds.map(id => getNewsItem(id))
        );
      } else if (filter?.status) {
        newsItems = await getNewsByStatus(filter.status);
      } else {
        newsItems = await getNewsByStatus('published');
      }

      // Stream to BHIV
      const streamResult = await streamToBhiv(target, newsItems);

       const seeyaPayload = newsItems.map(n => mapNoopurToSeeyaArticle(n));
      broadcastUpdate('stream_initiated', {
        target,
        itemsStreamed: newsItems.length,
        status: streamResult.status,
        articles: seeyaPayload
      });

      res.json({
        success: true,
        message: `Streamed ${newsItems.length} items to ${target}`,
        streamResult,
        seeya_compat: {
          articles: seeyaPayload,
          meta: {
            total_count: seeyaPayload.length,
            current_page: 1,
            has_next: false
          }
        }
      });
    } catch (error) {
      console.error('Error in BHIV streaming:', error.message);
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  /**
   * POST /api/bhiv/webhook - Receive webhook from BHIV with status updates
   */
  router.post('/webhook', express.json(), async (req, res) => {
    try {
      const { newsItemId, status, metrics, feedback } = req.body;

      console.log(`[BHIV Webhook] Received status for ${newsItemId}: ${status}`);

      // Store feedback from BHIV
      if (feedback) {
        // Can be used to improve RL feedback loop
        console.log('[BHIV Webhook] Metrics:', metrics);
      }

      // Broadcast to WebSocket clients
      broadcastUpdate('bhiv_status_update', {
        newsItemId,
        status,
        metrics,
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'Webhook processed'
      });
    } catch (error) {
      console.error('Error in BHIV webhook:', error.message);
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  /**
   * GET /api/bhiv/status/:newsItemId - Get BHIV distribution status
   */
  router.get('/status/:newsItemId', async (req, res) => {
    try {
      const newsItem = await getNewsItem(req.params.newsItemId);

      if (!newsItem) {
        return res.status(404).json({
          success: false,
          error: 'News item not found'
        });
      }

      res.json({
        success: true,
        newsItemId: newsItem._id,
        distribution: newsItem.publishedMetadata?.distribution || {
          ttv: false,
          vaani: false,
          other: []
        },
        publishedAt: newsItem.publishedMetadata?.publishedAt,
        status: newsItem.status,
        seeya_compat: mapNoopurToSeeyaArticle(newsItem)
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  /**
   * GET /api/bhiv/core/sync - Produce live feed payload for Core consumers
   */
  router.get('/core/sync', async (req, res) => {
    try {
      const items = await getNewsByStatus('published');
      const articles = items.map(n => mapNoopurToSeeyaArticle(n));
      broadcastUpdate('core_sync', {
        articles,
        meta: {
          total_count: articles.length,
          current_page: 1,
          has_next: false
        }
      });
      res.json({
        success: true,
        articles,
        meta: {
          total_count: articles.length,
          current_page: 1,
          has_next: false
        }
      });
    } catch (error) {
      console.error('Error in Core sync:', error.message);
      res.status(500).json({ success: false, error: error.message });
    }
  });

  return router;
};

/**
 * Send news item to BHIV endpoints
 */
async function sendToBhiv(newsItem, distribution) {
  const results = {
    status: 'completed',
    ttv: null,
    vaani: null
  };

  try {
    // TTV Endpoint
    if (distribution.ttv !== false) {
      try {
        console.log(`[BHIV] Sending to TTV: ${newsItem.title}`);
        const ttvResponse = await axios.post(
          `${process.env.BHIV_API_URL}/ttv/publish`,
          {
            newsId: newsItem._id,
            title: newsItem.title,
            content: newsItem.content,
            summary: newsItem.summary?.short,
            category: newsItem.classification?.category,
            sentiment: newsItem.sentiment?.label,
            publishedAt: new Date()
          },
          {
            headers: {
              'Authorization': `Bearer ${process.env.BHIV_API_KEY}`,
              'Content-Type': 'application/json'
            },
            timeout: 10000
          }
        );

        results.ttv = {
          success: true,
          status: ttvResponse.data.status,
          messageId: ttvResponse.data.messageId
        };
      } catch (error) {
        console.error('[BHIV] TTV error:', error.message);
        results.ttv = { success: false, error: error.message };
      }
    }

    // Vaani Endpoint
    if (distribution.vaani !== false) {
      try {
        console.log(`[BHIV] Sending to Vaani: ${newsItem.title}`);
        const vaaniResponse = await axios.post(
          `${process.env.BHIV_API_URL}/vaani/publish`,
          {
            newsId: newsItem._id,
            title: newsItem.title,
            summary: newsItem.summary?.medium,
            keyPoints: newsItem.summary?.keyPoints,
            entities: newsItem.summary?.entities,
            tone: newsItem.sentiment?.label,
            publishedAt: new Date()
          },
          {
            headers: {
              'Authorization': `Bearer ${process.env.BHIV_API_KEY}`,
              'Content-Type': 'application/json'
            },
            timeout: 10000
          }
        );

        results.vaani = {
          success: true,
          status: vaaniResponse.data.status,
          messageId: vaaniResponse.data.messageId
        };
      } catch (error) {
        console.error('[BHIV] Vaani error:', error.message);
        results.vaani = { success: false, error: error.message };
      }
    }

    return results;
  } catch (error) {
    console.error('[BHIV] SendToBhiv error:', error.message);
    throw error;
  }
}

/**
 * Stream multiple news items to BHIV endpoint
 */
async function streamToBhiv(target, newsItems) {
  try {
    const endpoint = target.toLowerCase() === 'ttv' ? '/ttv/batch' : '/vaani/batch';
    
    const payload = newsItems.map(item => ({
      newsId: item._id,
      title: item.title,
      content: item.content,
      summary: target === 'ttv' ? item.summary?.short : item.summary?.medium,
      category: item.classification?.category,
      sentiment: item.sentiment?.label,
      keyPoints: item.summary?.keyPoints,
      entities: item.summary?.entities
    }));

    console.log(`[BHIV] Streaming ${newsItems.length} items to ${target}`);

    const response = await axios.post(
      `${process.env.BHIV_API_URL}${endpoint}`,
      {
        items: payload,
        totalCount: newsItems.length,
        batchId: `batch-${Date.now()}`
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.BHIV_API_KEY}`,
          'Content-Type': 'application/json'
        },
        timeout: 30000
      }
    );

    return {
      success: true,
      status: response.data.status,
      processed: response.data.processed || newsItems.length,
      batchId: response.data.batchId
    };
  } catch (error) {
    console.error('[BHIV] StreamToBhiv error:', error.message);
    throw error;
  }
}
