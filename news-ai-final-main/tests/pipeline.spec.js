import { jest } from '@jest/globals';
import { v4 as uuidv4 } from 'uuid';

const newsStore = new Map();
const metricsStore = new Map();
const tasksStore = new Map();

jest.unstable_mockModule('../src/db/connection.js', () => ({
  getNewsItem: async (id) => newsStore.get(id) || null,
  updateNewsItem: async (id, updates) => {
    const cur = newsStore.get(id) || {};
    const next = { ...cur, ...updates, updatedAt: new Date() };
    newsStore.set(id, next);
    return next;
  },
  logNewsProcessing: async () => null,
  createAgentTask: async (taskData) => {
    const taskId = `${taskData.agentId}-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    const t = { ...taskData, taskId, createdAt: new Date(), status: 'pending' };
    tasksStore.set(taskId, t);
    return t;
  },
  updateAgentTask: async (taskId, updates) => {
    const cur = tasksStore.get(taskId) || {};
    const next = { ...cur, ...updates };
    tasksStore.set(taskId, next);
    return next;
  },
  getAgentTasksByStatus: async () => [],
  getAgentTasksByAgent: async () => [],
  createFeedbackMetrics: async (m) => {
    metricsStore.set(m.newsItemId, m);
    return m;
  },
  getFeedbackMetrics: async (newsItemId) => metricsStore.get(newsItemId) || null,
  updateFeedbackMetrics: async (newsItemId, updates) => {
    const cur = metricsStore.get(newsItemId) || {};
    const next = { ...cur, ...updates };
    metricsStore.set(newsItemId, next);
    return next;
  },
  getMetricsAggregation: async () => {
    const arr = Array.from(metricsStore.values());
    const avg = (key, f = (x) => x) => arr.length ? arr.reduce((a, m) => a + f(m[key]), 0) / arr.length : 0;
    return [{
      avgRewardScore: avg('rewardScore'),
      avgToneAccuracy: avg('toneAccuracy'),
      avgEngagementPrediction: avg('engagementPrediction'),
      avgCorrectionPercentage: avg('correctionMetrics', (c) => c?.correctionPercentage || 0),
      avgLatency: avg('latency', (l) => l?.totalLatency || 0),
      totalItems: arr.length
    }];
  }
}));

const UniguruMock = class {
  async classifyNews(title, content) {
    const byCat = [
      'Technology', 'Entertainment', 'Sports', 'Business', 'Science',
      'Politics', 'Finance', 'Health', 'Environment', 'Culture'
    ];
    const idx = Math.abs(title.length + content.length) % byCat.length;
    return { category: byCat[idx], subcategory: null, confidence: 0.7 + (idx % 3) * 0.1, timestamp: new Date() };
  }
  async analyzeSentiment(content) {
    const base = Math.min(1, Math.max(0, (content.length % 100) / 100));
    const label = base > 0.66 ? 'positive' : base > 0.33 ? 'neutral' : 'negative';
    const aspects = [
      { aspect: 'depth', sentiment: label, score: base },
      { aspect: 'clarity', sentiment: label, score: base - 0.1 }
    ];
    return { label, score: base * 2 - 1, confidence: 0.6 + base * 0.4, aspects, timestamp: new Date() };
  }
  async summarizeNews(title, content) {
    const short = `${title}`.slice(0, 120);
    const medium = `${content}`.slice(0, 280);
    const keyPoints = [
      title.split(' ')[0] || 'News',
      'Key detail',
      content.split(' ').slice(0, 5).join(' ')
    ];
    const entities = [{ type: 'ORG', value: 'Org' }, { type: 'PERSON', value: 'Person' }];
    return { short, medium, keyPoints, entities, timestamp: new Date() };
  }
};

test('Self-correcting pipeline processes 10 mixed-category stories', async () => {
  const savedLog = console.log;
  const savedErr = console.error;
  console.log = () => {};
  console.error = () => {};
  const { default: NewsProcessingPipeline } = await import('../src/pipeline/langgraph.js');
  const { default: RLFeedbackLoop } = await import('../src/feedback/rl_loop.js');
  const { initializeAgents } = await import('../src/agents/initialize.js');
  const conn = await import('../src/db/connection.js');
  const uniguru = new UniguruMock();
  const registry = initializeAgents(uniguru);
  registry.processTaskAsync = async (task) => ({ status: 'completed', taskId: task.taskId });
  const rl = new RLFeedbackLoop(registry);
  rl.setThreshold(0.6);
  const pipeline = new NewsProcessingPipeline(registry, rl, uniguru);
  pipeline.waitForTask = async (taskId) => ({ status: 'completed', taskId });

  const samples = [
    { title: 'Tech breakthrough in chip design', content: 'New 3nm process improves efficiency.' },
    { title: 'Entertainment award show surprises', content: 'Unexpected winners spark debate.' },
    { title: 'Sports finals end in upset', content: 'Underdog wins championship match.' },
    { title: 'Business merger announced', content: 'Two giants combine to expand reach.' },
    { title: 'Science mission succeeds', content: 'Probe sends new planetary data.' },
    { title: 'Politics debate heats up', content: 'Candidates clash on policy.' },
    { title: 'Finance markets adjust', content: 'Interest rates influence movement.' },
    { title: 'Health advisory released', content: 'Guidelines updated for safety.' },
    { title: 'Environment project launches', content: 'Renewable initiative begins.' },
    { title: 'Culture festival begins', content: 'Artists showcase across venues.' }
  ];

  const ids = samples.map(s => {
    const id = uuidv4();
    newsStore.set(id, {
      _id: id,
      title: s.title,
      content: s.content,
      source: 'manual',
      status: 'raw',
      classification: { category: 'General', confidence: 0.5, timestamp: new Date() },
      sentiment: { label: 'neutral', score: 0, confidence: 0.5, aspects: [], timestamp: new Date() },
      summary: { short: s.title, medium: s.content, keyPoints: [s.title.split(' ')[0]], entities: [], timestamp: new Date() },
      createdAt: new Date()
    });
    return id;
  });

  const results = [];
  for (const id of ids) {
    const enrichedClass = await uniguru.classifyNews(newsStore.get(id).title, newsStore.get(id).content);
    const enrichedSent = await uniguru.analyzeSentiment(newsStore.get(id).content);
    const enrichedSum = await uniguru.summarizeNews(newsStore.get(id).title, newsStore.get(id).content);
    await conn.updateNewsItem(id, {
      classification: enrichedClass,
      sentiment: enrichedSent,
      summary: enrichedSum,
      status: 'verified'
    });
    const res = await pipeline.processNewsItem(id, 3);
    results.push(res);
  }

  expect(results.length).toBe(10);
  const improved = results.filter(r => r.finalRewardScore >= 0.6).length;
  expect(improved).toBeGreaterThanOrEqual(6);
  const adaptive = ids.filter(id => (metricsStore.get(id)?.iterationHistory || []).length >= 1).length;
  expect(adaptive).toBeGreaterThanOrEqual(10);
  console.log = savedLog;
  console.error = savedErr;
}, 20000);
