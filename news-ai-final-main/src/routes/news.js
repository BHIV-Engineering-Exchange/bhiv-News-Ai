import express from 'express';
import { v4 as uuidv4 } from 'uuid';
import {
  createNewsItem,
  getNewsItem,
  getNewsByStatus,
  updateNewsItem,
  logNewsProcessing
} from '../db/connection.js';

export const createNewsRouter = (uniguruService) => {
  const router = express.Router();

  /**
   * GET /api/news - List news items with optional filters
   * Query: status=raw|verified|published, category=<string>, limit=<int>
   */
  router.get('/', async (req, res) => {
    try {
      const status = (req.query.status || 'published').toString().toLowerCase();
      const category = req.query.category ? req.query.category.toString().toLowerCase() : null;
      const limit = req.query.limit ? Math.max(1, Math.min(100, parseInt(req.query.limit, 10))) : 20;
      const validStatuses = ['raw', 'verified', 'published'];
      if (!validStatuses.includes(status)) {
        return res.status(400).json({ success: false, error: `Invalid status. Must be one of: ${validStatuses.join(', ')}` });
      }
      const items = await getNewsByStatus(status);
      const filtered = category ? items.filter(i => (i.classification?.category || '').toLowerCase() === category) : items;
      const sliced = filtered.slice(0, limit);
      res.json({
        success: true,
        status,
        count: sliced.length,
        data: sliced.map(i => ({
          id: i._id,
          title: i.title,
          source: i.source,
          category: i.classification?.category || 'general',
          status: i.status,
          timestamp: i.updatedAt || i.createdAt,
          summary: i.summary?.short || null,
          insights: { sentiment: i.sentiment?.label || null },
          pipeline: { processingLog: (i.processingLog || []).length }
        }))
      });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  /**
   * POST /api/news - Submit raw news item
   */
  router.post('/', async (req, res) => {
    try {
      const { title, content, source, sourceUrl } = req.body;

      if (!title || !content) {
        return res.status(400).json({
          success: false,
          error: 'Title and content are required'
        });
      }

      // Create raw news item
      const newsItem = await createNewsItem({
        title,
        content,
        source: source || 'manual',
        sourceUrl: sourceUrl || '',
        status: 'raw'
      });

      // Start enrichment (async, non-blocking)
      enrichNewsItemAsync(newsItem._id, title, content, uniguruService);

      res.status(201).json({
        success: true,
        message: 'News item created and enrichment started',
        newsId: newsItem._id,
        status: 'raw'
      });
    } catch (error) {
      console.error('Error creating news item:', error);
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  /**
   * GET /api/news/:id - Get news item by ID
   */
  router.get('/:id', async (req, res) => {
    try {
      const newsItem = await getNewsItem(req.params.id);

      if (!newsItem) {
        return res.status(404).json({
          success: false,
          error: 'News item not found'
        });
      }

      res.json({
        success: true,
        data: newsItem
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  /**
   * GET /api/news/status/:status - Get news by status
   */
  router.get('/status/:status', async (req, res) => {
    try {
      const validStatuses = ['raw', 'verified', 'published'];
      const status = req.params.status.toLowerCase();

      if (!validStatuses.includes(status)) {
        return res.status(400).json({
          success: false,
          error: `Invalid status. Must be one of: ${validStatuses.join(', ')}`
        });
      }

      const newsItems = await getNewsByStatus(status);

      res.json({
        success: true,
        status,
        count: newsItems.length,
        data: newsItems
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  /**
   * PUT /api/news/:id - Update news item
   */
  router.put('/:id', async (req, res) => {
    try {
      const { status, verification, feedback } = req.body;
      
      const updates = {};
      if (status) updates.status = status;
      if (verification) updates.verification = verification;
      if (feedback) updates.feedback = feedback;

      const updatedItem = await updateNewsItem(req.params.id, updates);

      res.json({
        success: true,
        message: 'News item updated',
        data: updatedItem
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    }
  });

  return router;
};

/**
 * Async enrichment of news item with Uniguru
 */
async function enrichNewsItemAsync(newsItemId, title, content, uniguruService) {
  try {
    console.log(`[Enrichment] Starting async enrichment for ${newsItemId}`);

    // Log start
    await logNewsProcessing(newsItemId, 'enrichment_start', 'uniguru', 'processing', {});

    // Call Uniguru API
    const enrichedData = await uniguruService.processNewsComplete(title, content);

    // Update news item with enriched data
    await updateNewsItem(newsItemId, {
      classification: enrichedData.classification,
      sentiment: enrichedData.sentiment,
      summary: enrichedData.summary,
      status: 'verified'  // Auto-promote to verified after enrichment
    });

    // Log completion
    await logNewsProcessing(newsItemId, 'enrichment_complete', 'uniguru', 'completed', {
      processingTime: enrichedData.processingTime,
      classification: enrichedData.classification.category,
      sentimentLabel: enrichedData.sentiment.label
    });

    console.log(`[Enrichment] Completed for ${newsItemId}`);
  } catch (error) {
    console.error(`[Enrichment] Error for ${newsItemId}:`, error.message);
    
    await logNewsProcessing(newsItemId, 'enrichment_failed', 'uniguru', 'failed', {
      error: error.message
    });
  }
}
