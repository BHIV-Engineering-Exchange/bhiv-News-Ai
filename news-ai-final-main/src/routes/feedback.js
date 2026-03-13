import express from 'express';
import { getFeedbackMetrics, getMetricsAggregation } from '../db/connection.js';

export const createFeedbackRouter = (rlFeedbackLoop, uniguruService) => {
  const router = express.Router();

  // Simple feedback endpoint for frontend
  router.post('/', async (req, res) => {
    try {
      const { newsId, feedbackType, metadata } = req.body || {};
      if (!newsId || !feedbackType) {
        return res.status(400).json({ success: false, error: 'newsId and feedbackType are required' });
      }
      const { getFeedbackMetrics, updateFeedbackMetrics, getNewsItem, updateNewsItem } = await import('../db/connection.js');
      const item = await getNewsItem(newsId);
      if (!item) {
        return res.status(404).json({ success: false, error: 'News item not found' });
      }
      const metrics = (await getFeedbackMetrics(newsId)) || {};
      const now = new Date();
      const history = Array.isArray(metrics.userFeedbackHistory) ? metrics.userFeedbackHistory : [];
      history.push({ type: feedbackType, at: now, meta: metadata || {} });
      await updateFeedbackMetrics(newsId, { userFeedbackHistory: history });
      const feedback = Object.assign({}, item.feedback || {});
      feedback[feedbackType] = (feedback[feedbackType] || 0) + 1;
      await updateNewsItem(newsId, { feedback });
      res.json({ success: true, message: 'Feedback recorded', counts: feedback });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  router.post('/evaluate', async (req, res) => {
    try {
      const { newsItemId } = req.body || {};
      if (!newsItemId) {
        return res.status(400).json({ success: false, error: 'newsItemId is required' });
      }
      const evaluation = await rlFeedbackLoop.evaluateOutput(newsItemId, uniguruService);
      res.json({ success: true, evaluation });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  router.get('/metrics', async (req, res) => {
    try {
      const { newsItemId } = req.query || {};
      if (!newsItemId) {
        return res.status(400).json({ success: false, error: 'newsItemId is required' });
      }
      const metrics = await rlFeedbackLoop.logMetrics(newsItemId);
      res.json({ success: true, metrics });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  router.get('/aggregate', async (req, res) => {
    try {
      const agg = await getMetricsAggregation({});
      res.json({ success: true, aggregate: agg?.[0] || null });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  router.post('/threshold', async (req, res) => {
    try {
      const { threshold } = req.body || {};
      if (threshold === undefined) {
        return res.status(400).json({ success: false, error: 'threshold is required' });
      }
      rlFeedbackLoop.setThreshold(Number(threshold));
      res.json({ success: true, threshold: rlFeedbackLoop.feedbackThreshold });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  return router;
};
