import mongoose from 'mongoose';

const newsItemSchema = new mongoose.Schema(
  {
    _id: mongoose.Schema.Types.ObjectId,
    
    // Source information
    title: {
      type: String,
      required: true,
      index: true
    },
    content: {
      type: String,
      required: true
    },
    source: {
      type: String,
      required: true,
      enum: ['rss', 'api', 'manual', 'social']
    },
    sourceUrl: String,
    
    // Pipeline status
    status: {
      type: String,
      enum: ['raw', 'verified', 'published'],
      default: 'raw',
      index: true
    },
    
    // Uniguru Enrichment - Classification
    classification: {
      category: String,
      subcategory: String,
      confidence: Number,
      timestamp: Date
    },
    
    // Uniguru Enrichment - Sentiment
    sentiment: {
      label: { type: String, enum: ['positive', 'negative', 'neutral'] },
      score: Number,  // -1 to 1
      aspects: [{
        aspect: String,
        sentiment: String,
        score: Number
      }],
      timestamp: Date
    },
    
    // Uniguru Enrichment - Summarization
    summary: {
      short: String,      // 1-2 sentence summary
      medium: String,     // paragraph summary
      keyPoints: [String],
      entities: [{
        type: String,      // PERSON, ORG, LOCATION, etc.
        value: String
      }],
      timestamp: Date
    },
    
    // Verification Stage
    verification: {
      verified: Boolean,
      verificationScore: Number,  // 0-1
      verifiedBy: String,  // agent_id
      verificationNotes: String,
      verificationTimestamp: Date
    },
    
    // RL Feedback
    feedback: {
      rewardScore: Number,  // 0-1
      toneAccuracy: Number,
      engagementPrediction: Number,
      correctionCount: Number,
      history: [{
        iteration: Number,
        score: Number,
        correctionType: String,
        timestamp: Date
      }]
    },
    
    // Publishing
    publishedMetadata: {
      publishedAt: Date,
      publishedBy: String,  // agent_id
      distribution: {
        ttv: Boolean,
        vaani: Boolean,
        other: [String]
      }
    },
    
    // Metadata
    tags: [String],
    language: { type: String, default: 'en' },
    createdAt: { type: Date, default: Date.now, index: true },
    updatedAt: { type: Date, default: Date.now },
    processingLog: [{
      stage: String,
      agent: String,
      status: String,
      timestamp: Date,
      details: mongoose.Schema.Types.Mixed
    }]
  },
  { 
    collection: 'news_items',
    timestamps: true 
  }
);

// Indexes for performance
newsItemSchema.index({ status: 1, createdAt: -1 });
newsItemSchema.index({ 'classification.category': 1 });
newsItemSchema.index({ 'sentiment.label': 1 });
newsItemSchema.index({ 'verification.verified': 1 });
newsItemSchema.index({ 'publishedMetadata.publishedAt': -1 });
newsItemSchema.index({ tags: 1 });
newsItemSchema.index({ 'processingLog.stage': 1 });

export const NewsItem = mongoose.model('NewsItem', newsItemSchema);

// Agent Task Schema
const agentTaskSchema = new mongoose.Schema(
  {
    _id: mongoose.Schema.Types.ObjectId,
    
    taskId: {
      type: String,
      unique: true,
      required: true,
      index: true
    },
    
    agentId: {
      type: String,
      required: true,
      index: true
    },
    
    agentRole: {
      type: String,
      enum: ['fetch', 'filter', 'verify', 'script', 'rlfeedback'],
      required: true
    },
    
    newsItemId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'NewsItem',
      required: true
    },
    
    priority: {
      type: Number,
      min: 0,
      max: 10,
      default: 5
    },
    
    status: {
      type: String,
      enum: ['pending', 'processing', 'completed', 'failed', 'retry'],
      default: 'pending',
      index: true
    },
    
    payload: mongoose.Schema.Types.Mixed,
    result: mongoose.Schema.Types.Mixed,
    
    error: {
      message: String,
      stack: String,
      retryCount: Number,
      lastRetry: Date
    },
    
    executionMetrics: {
      startTime: Date,
      endTime: Date,
      duration: Number,  // milliseconds
      tokens: Number
    },
    
    createdAt: { type: Date, default: Date.now, index: true },
    updatedAt: { type: Date, default: Date.now },
    completedAt: Date
  },
  { 
    collection: 'agent_tasks',
    timestamps: true
  }
);

agentTaskSchema.index({ agentId: 1, status: 1 });
agentTaskSchema.index({ status: 1, createdAt: -1 });
agentTaskSchema.index({ newsItemId: 1 });
agentTaskSchema.index({ agentRole: 1 });

export const AgentTask = mongoose.model('AgentTask', agentTaskSchema);

// Feedback Metrics Schema
const feedbackMetricsSchema = new mongoose.Schema(
  {
    _id: mongoose.Schema.Types.ObjectId,
    
    newsItemId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'NewsItem',
      unique: true,
      required: true
    },
    
    rewardScore: Number,      // Final reward (0-1)
    toneAccuracy: Number,     // How well tone was identified
    engagementPrediction: Number,  // Predicted engagement score
    
    correctionMetrics: {
      totalCorrections: Number,
      correctionTypes: {
        tone: Number,
        sentiment: Number,
        summary: Number,
        classification: Number
      },
      correctionPercentage: Number  // % of output that needed correction
    },
    
    latency: {
      totalLatency: Number,           // milliseconds
      classificationLatency: Number,
      sentimentLatency: Number,
      summarizationLatency: Number
    },
    
    iterationHistory: [{
      iteration: Number,
      reward: Number,
      corrections: [String],
      timestamp: Date
    }],
    
    createdAt: { type: Date, default: Date.now },
    updatedAt: { type: Date, default: Date.now }
  },
  { 
    collection: 'feedback_metrics',
    timestamps: true
  }
);

export const FeedbackMetrics = mongoose.model('FeedbackMetrics', feedbackMetricsSchema);
feedbackMetricsSchema.index({ rewardScore: -1 });
feedbackMetricsSchema.index({ toneAccuracy: -1 });
feedbackMetricsSchema.index({ 'latency.totalLatency': 1 });
