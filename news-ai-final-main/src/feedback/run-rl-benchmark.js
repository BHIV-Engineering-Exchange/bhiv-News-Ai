import 'dotenv/config';
import { v4 as uuidv4 } from 'uuid';
import RLFeedbackLoop from './rl_loop.js';
import NewsProcessingPipeline from '../pipeline/langgraph.js';
import { initializeAgents } from '../agents/initialize.js';
import UniguruService from '../services/uniguru.js';
import fs from 'fs';
import path from 'path';
import { createNewsItem, updateNewsItem } from '../db/connection.js';

async function main() {
  const cases = [
    { title: 'Tech breakthrough', content: 'New AI chip improves efficiency.' },
    { title: 'Finance update', content: 'Markets react to interest rates.' },
    { title: 'Health advisory', content: 'Updated safety guidelines for communities.' },
    { title: 'Sports highlight', content: 'Team secures last-minute victory.' },
    { title: 'Entertainment news', content: 'Film sets new box office record.' },
    { title: 'Business merger', content: 'Companies announce strategic merger.' },
    { title: 'Science discovery', content: 'Researchers find promising material.' },
    { title: 'Environment action', content: 'New policies aim to cut emissions.' },
    { title: 'Technology launch', content: 'Startup releases innovative product.' },
    { title: 'Regional update', content: 'Local council approves new plan.' }
  ];

  class UniguruMock {
    async classifyNews(title, content) {
      return { category: 'Technology', confidence: 0.8, timestamp: new Date() };
    }
    async analyzeSentiment(content) {
      return { label: 'positive', confidence: 0.7, aspects: [], timestamp: new Date() };
    }
    async summarizeNews(title, content) {
      return { short: 'Short summary.', medium: 'Medium summary paragraph.', keyPoints: ['Point A','Point B'], entities: [{ type: 'PERSON', value: 'Alex' }], timestamp: new Date() };
    }
    async processNewsComplete(title, content) {
      const c = await this.classifyNews(title, content);
      const s = await this.analyzeSentiment(content);
      const m = await this.summarizeNews(title, content);
      return { classification: c, sentiment: s, summary: m, processingTime: 1000, success: true };
    }
  }

  let uniguru = new UniguruService(process.env.UNIGURU_API_KEY, process.env.UNIGURU_BASE_URL);
  try {
    const ok = await uniguru.healthCheck();
    if (!ok) uniguru = new UniguruMock();
  } catch {
    uniguru = new UniguruMock();
  }

  const registry = initializeAgents(uniguru);
  const rl = new RLFeedbackLoop(registry);
  rl.setThreshold(0.6);
  const pipeline = new NewsProcessingPipeline(registry, rl, uniguru);

  const dir = path.join(process.cwd(), 'logs', 'rl');
  fs.mkdirSync(dir, { recursive: true });
  const lines = [];

  for (const c of cases) {
    const item = await createNewsItem({ title: c.title, content: c.content, source: 'benchmark', status: 'raw' });
    const enriched = await uniguru.processNewsComplete(c.title, c.content);
    await updateNewsItem(item._id, { classification: enriched.classification, sentiment: enriched.sentiment, summary: enriched.summary, status: 'verified' });
    let result;
    try {
      result = await pipeline.processNewsItem(String(item._id), 3);
    } catch (e) {
      result = { success: false, finalRewardScore: 0, processingTime: 0 };
    }
    lines.push({ id: String(item._id), reward: result.finalRewardScore || 0, latencyMs: result.processingTime || 0, success: !!result.success });
  }

  const meanReward = lines.reduce((a, r) => a + r.reward, 0) / lines.length;
  const correctionRate = 1 - (lines.filter(l => l.success).length / lines.length);
  const avgLatency = Math.round(lines.reduce((a, r) => a + r.latencyMs, 0) / lines.length);
  const summary = { meanReward, correctionRate, avgLatency, cases: lines.length, timestamp: new Date().toISOString() };
  fs.writeFileSync(path.join(dir, 'rl_summary.json'), JSON.stringify(summary, null, 2));
  console.log(JSON.stringify(summary));
}

main().catch(e => {
  console.error(e.message);
  process.exit(1);
});
