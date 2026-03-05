import express from 'express';
import axios from 'axios';
import { getTaskRoutingSchema } from '../agents/initialize.js';
import { getNewsItem } from '../db/connection.js';

export const createAgentsRouter = (agentRegistry) => {
  const router = express.Router();

  router.get('/status', async (req, res) => {
    try {
      const agents = agentRegistry.getAllAgents();
      const queues = agentRegistry.getAllQueueStatus();
      res.json({ success: true, agents, queues });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  router.post('/orchestrate', async (req, res) => {
    try {
      const { newsItemId, distribution } = req.body || {};
      if (!newsItemId) {
        return res.status(400).json({ success: false, error: 'newsItemId is required' });
      }
      const schema = getTaskRoutingSchema();
      const results = {};
      for (const step of schema.taskFlow) {
        const task = await agentRegistry.submitTask(newsItemId, step.agent, {}, step.priority);
        const result = await agentRegistry.processTaskAsync(task, task.agentId || agentRegistry.getAgentsByRole(step.agent)[0]?.id);
        results[step.agent] = result || {};
      }
      const item = await getNewsItem(newsItemId);
      const baseUrl = `http://localhost:${process.env.PORT || 3000}`;
      const bhivResp = await axios.post(`${baseUrl}/api/bhiv/process`, { newsItemId, distribution: distribution || {} });
      res.json({
        success: true,
        message: 'Orchestration completed',
        stages: results,
        bhiv: bhivResp.data,
        newsItem: {
          id: item?._id,
          title: item?.title,
          status: item?.status
        }
      });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  return router;
};
