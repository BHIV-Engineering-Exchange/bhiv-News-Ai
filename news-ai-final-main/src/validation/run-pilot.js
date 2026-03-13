import 'dotenv/config';
import { v4 as uuidv4 } from 'uuid';
import RLFeedbackLoop from '../feedback/rl_loop.js';
import NewsProcessingPipeline from '../pipeline/langgraph.js';
import { initializeAgents } from '../agents/initialize.js';
import UniguruService from '../services/uniguru.js';
import { createNewsItem, updateNewsItem } from '../db/connection.js';

async function runPilot() {
  const channels = ['ttv', 'vaani', 'other'];
  const avatars = ['avatarA', 'avatarB', 'avatarC'];

  const UniguruMock = class {
    async classifyNews(title, content) {
      const cats = ['Technology', 'Finance', 'Health', 'Environment', 'Business', 'Sports'];
      const idx = Math.abs(title.length + content.length) % cats.length;
      return { category: cats[idx], subcategory: null, confidence: 0.8, timestamp: new Date() };
    }
    async analyzeSentiment(content) {
      const base = Math.min(1, Math.max(0, (content.length % 100) / 100));
      const label = base > 0.66 ? 'positive' : base > 0.33 ? 'neutral' : 'negative';
      const aspects = [
        { aspect: 'depth', sentiment: label, score: base },
        { aspect: 'clarity', sentiment: label, score: base - 0.1 }
      ];
      return { label, score: base * 2 - 1, confidence: 0.7, aspects, timestamp: new Date() };
    }
    async summarizeNews(title, content) {
      const short = `${title}`.slice(0, 120);
      const medium = `${content}`.slice(0, 280);
      const keyPoints = [title.split(' ')[0] || 'News', 'Key detail', content.split(' ').slice(0, 5).join(' ')];
      const entities = [{ type: 'ORG', value: 'Org' }, { type: 'PERSON', value: 'Person' }];
      return { short, medium, keyPoints, entities, timestamp: new Date() };
    }
    async processNewsComplete(title, content) {
      const [classification, sentiment, summary] = await Promise.all([
        this.classifyNews(title, content),
        this.analyzeSentiment(content),
        this.summarizeNews(title, content)
      ]);
      return { classification, sentiment, summary, processingTime: 1000, success: true };
    }
  };
  let uniguru = new UniguruService(process.env.UNIGURU_API_KEY, process.env.UNIGURU_BASE_URL);
  const healthy = await uniguru.healthCheck();
  if (!healthy) {
    uniguru = new UniguruMock();
  }
  const registry = initializeAgents(uniguru);
  const rl = new RLFeedbackLoop(registry);
  rl.setThreshold(0.6);
  const pipeline = new NewsProcessingPipeline(registry, rl, uniguru);

  const stories = [
    { title: 'Tech: Breakthrough in AI chips', content: 'New 3nm process improves efficiency and speed.' },
    { title: 'Finance: Markets react to rates', content: 'Interest rate changes drive portfolio shifts.' },
    { title: 'Health: Advisory for communities', content: 'Updated safety guidelines announced for local groups.' }
  ];

  const combos = [];
  for (const ch of channels) for (const av of avatars) combos.push({ channel: ch, avatar: av });

  const results = [];
  for (const combo of combos) {
    for (const story of stories) {
      const news = await createNewsItem({
        title: `${story.title} [${combo.channel}/${combo.avatar}]`,
        content: story.content,
        source: 'manual',
        status: 'raw'
      });
      const enriched = await uniguru.processNewsComplete(news.title, news.content);
      await updateNewsItem(news._id, {
        classification: enriched.classification,
        sentiment: enriched.sentiment,
        summary: enriched.summary,
        status: 'verified'
      });

      const start = Date.now();
      let pipelineResult;
      try {
        pipelineResult = await pipeline.processNewsItem(news._id, 3);
      } catch (err) {
        pipelineResult = {
          success: false,
          error: err.message,
          processingTime: Date.now() - start,
          finalRewardScore: 0
        };
      }

      results.push({
        combo,
        newsItemId: String(news._id),
        latencyMs: pipelineResult.processingTime,
        reward: pipelineResult.finalRewardScore,
        success: pipelineResult.success === true,
        iterations: pipelineResult.iterations || 0
      });
    }
  }

  const summary = {
    combos: results.length,
    avgLatencyMs: Math.round(results.reduce((a, r) => a + (r.latencyMs || 0), 0) / results.length),
    successRate: ((results.filter(r => r.success).length / results.length) * 100).toFixed(2) + '%',
    avgReward: (results.reduce((a, r) => a + (r.reward || 0), 0) / results.length).toFixed(3),
    retriesTriggered: results.filter(r => r.iterations > 1).length
  };

  console.log(JSON.stringify({ results, summary }, null, 2));
}

runPilot().catch(e => {
  console.error(e.message);
  process.exit(1);
});
