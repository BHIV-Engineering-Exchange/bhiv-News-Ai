import mongoose from 'mongoose';
import { NewsItem, AgentTask, FeedbackMetrics } from '../models/schemas.js';

let db = null;
const memory = {
  newsItems: new Map(),
  agentTasks: new Map(),
  feedbackMetrics: new Map()
};

export const connectDB = async (mongoUri) => {
  try {
    if (db) {
      return db;
    }

    if (!mongoUri) {
      console.warn('⚠️  MongoDB URI not provided - running in offline mode');
      return null;
    }

    // Add timeout for connection attempt
    const connectionPromise = mongoose.connect(mongoUri, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      maxPoolSize: 10,
      socketTimeoutMS: 5000,
      connectTimeoutMS: 10000,
      serverSelectionTimeoutMS: 5000,
    });

    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Connection timeout')), 8000)
    );

    db = await Promise.race([connectionPromise, timeoutPromise]);

    console.log('✓ MongoDB Atlas connected successfully');
    return db;
  } catch (error) {
    console.warn('⚠️  MongoDB connection failed:', error.message);
    console.warn('   Running in offline mode - database operations will be unavailable');
    return null;
  }
};

export const disconnectDB = async () => {
  if (db) {
    await mongoose.disconnect();
    db = null;
    console.log('✓ MongoDB disconnected');
  }
};

export const getDB = () => {
  if (!db) {
    throw new Error('Database not connected. Call connectDB first.');
  }
  return db;
};

// News Item Operations
export const createNewsItem = async (newsData) => {
  try {
    if (!db) {
      const id = new mongoose.Types.ObjectId();
      const item = {
        _id: id,
        ...newsData,
        createdAt: new Date(),
        updatedAt: new Date(),
        processingLog: [{
          stage: 'created',
          status: 'initial',
          timestamp: new Date()
        }]
      };
      memory.newsItems.set(String(id), item);
      return item;
    } else {
      const newsItem = new NewsItem({
        ...newsData,
        processingLog: [{
          stage: 'created',
          status: 'initial',
          timestamp: new Date()
        }]
      });
      await newsItem.save();
      return newsItem;
    }
  } catch (error) {
    console.error('Error creating news item:', error);
    throw error;
  }
};

export const getNewsItem = async (id) => {
  if (!db) {
    return memory.newsItems.get(String(id)) || null;
  }
  return NewsItem.findById(id);
};

export const updateNewsItem = async (id, updates) => {
  if (!db) {
    const cur = memory.newsItems.get(String(id));
    if (!cur) return null;
    const next = { ...cur, ...updates, updatedAt: new Date() };
    memory.newsItems.set(String(id), next);
    return next;
  }
  return NewsItem.findByIdAndUpdate(id, updates, { new: true });
};

export const getNewsByStatus = async (status) => {
  if (!db) {
    const arr = Array.from(memory.newsItems.values()).filter(n => n.status === status);
    return arr.sort((a, b) => b.createdAt - a.createdAt);
  }
  return NewsItem.find({ status }).sort({ createdAt: -1 });
};

export const logNewsProcessing = async (newsItemId, stage, agent, status, details) => {
  if (!db) {
    const cur = memory.newsItems.get(String(newsItemId));
    if (!cur) return null;
    const log = cur.processingLog || [];
    log.push({ stage, agent, status, timestamp: new Date(), details });
    const next = { ...cur, processingLog: log, updatedAt: new Date() };
    memory.newsItems.set(String(newsItemId), next);
    return next;
  }
  return NewsItem.findByIdAndUpdate(
    newsItemId,
    {
      $push: {
        processingLog: {
          stage,
          agent,
          status,
          timestamp: new Date(),
          details
        }
      },
      $set: { updatedAt: new Date() }
    },
    { new: true }
  );
};

// Agent Task Operations
export const createAgentTask = async (taskData) => {
  if (!db) {
    const taskId = `${taskData.agentId}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const task = { ...taskData, taskId, status: 'pending', createdAt: new Date() };
    memory.agentTasks.set(taskId, task);
    return task;
  } else {
    const task = new AgentTask({
      ...taskData,
      taskId: `${taskData.agentId}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    });
    await task.save();
    return task;
  }
};

export const getAgentTask = async (taskId) => {
  if (!db) {
    return memory.agentTasks.get(taskId) || null;
  }
  return AgentTask.findOne({ taskId });
};

export const updateAgentTask = async (taskId, updates) => {
  if (!db) {
    const cur = memory.agentTasks.get(taskId);
    if (!cur) return null;
    const next = { ...cur, ...updates };
    memory.agentTasks.set(taskId, next);
    return next;
  }
  return AgentTask.findOneAndUpdate({ taskId }, updates, { new: true });
};

export const getAgentTasksByStatus = async (status) => {
  if (!db) {
    return Array.from(memory.agentTasks.values()).filter(t => t.status === status).sort((a, b) => a.createdAt - b.createdAt);
  }
  return AgentTask.find({ status }).sort({ createdAt: 1 });
};

export const getAgentTasksByAgent = async (agentId) => {
  if (!db) {
    return Array.from(memory.agentTasks.values()).filter(t => t.agentId === agentId).sort((a, b) => b.createdAt - a.createdAt);
  }
  return AgentTask.find({ agentId }).sort({ createdAt: -1 });
};

// Feedback Metrics Operations
export const createFeedbackMetrics = async (metricsData) => {
  if (!db) {
    memory.feedbackMetrics.set(String(metricsData.newsItemId), metricsData);
    return metricsData;
  }
  const metrics = new FeedbackMetrics(metricsData);
  await metrics.save();
  return metrics;
};

export const getFeedbackMetrics = async (newsItemId) => {
  if (!db) {
    return memory.feedbackMetrics.get(String(newsItemId)) || null;
  }
  return FeedbackMetrics.findOne({ newsItemId });
};

export const updateFeedbackMetrics = async (newsItemId, updates) => {
  if (!db) {
    const cur = memory.feedbackMetrics.get(String(newsItemId)) || {};
    const next = { ...cur, ...updates };
    memory.feedbackMetrics.set(String(newsItemId), next);
    return next;
  }
  return FeedbackMetrics.findOneAndUpdate({ newsItemId }, updates, { new: true });
};

export const getMetricsAggregation = async (filters = {}) => {
  if (!db) {
    const arr = Array.from(memory.feedbackMetrics.values());
    const avg = (f) => arr.length ? arr.reduce((a, m) => a + f(m), 0) / arr.length : 0;
    return [{
      _id: null,
      avgRewardScore: avg(m => m.rewardScore || 0),
      avgToneAccuracy: avg(m => m.toneAccuracy || 0),
      avgEngagementPrediction: avg(m => m.engagementPrediction || 0),
      avgCorrectionPercentage: avg(m => (m.correctionMetrics?.correctionPercentage) || 0),
      avgLatency: avg(m => (m.latency?.totalLatency) || 0),
      totalItems: arr.length
    }];
  }
  return FeedbackMetrics.aggregate([
    { $match: filters },
    {
      $group: {
        _id: null,
        avgRewardScore: { $avg: '$rewardScore' },
        avgToneAccuracy: { $avg: '$toneAccuracy' },
        avgEngagementPrediction: { $avg: '$engagementPrediction' },
        avgCorrectionPercentage: { $avg: '$correctionMetrics.correctionPercentage' },
        avgLatency: { $avg: '$latency.totalLatency' },
        totalItems: { $sum: 1 }
      }
    }
  ]);
};
