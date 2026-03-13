import express from 'express';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import 'dotenv/config';
import { connectDB } from './db/connection.js';
import { createNewsRouter } from './routes/news.js';
import UniguruService from './services/uniguru.js';
import { initializeAgents } from './agents/initialize.js';
import RLFeedbackLoop from './feedback/rl_loop.js';
import NewsProcessingPipeline from './pipeline/langgraph.js';
import { createBhivRouter } from './routes/bhiv.js';
import { createAgentsRouter } from './routes/agents.js';
import { createFeedbackRouter } from './routes/feedback.js';

const app = express();
const server = createServer(app);

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
// Lightweight CORS without external package
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS || 'http://localhost:3000,http://127.0.0.1:3000').split(',');
app.use((req, res, next) => {
  const origin = req.headers.origin;
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Client-Nonce, X-Signature, X-Timestamp');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  next();
});

// Initialize services
let uniguruService;
let agentRegistry;
let rlFeedbackLoop;
let newsPipeline;
let wsClients = new Set();

const PORT = process.env.PORT || 3000;
const WS_PORT = process.env.WS_PORT || 3001;

/**
 * Initialize application
 */
async function initializeApp() {
  try {
    console.log('🚀 Initializing Noopur News AI System...\n');

    // 1. Connect to MongoDB
    console.log('1️⃣  Connecting to MongoDB Atlas...');
    await connectDB(process.env.MONGODB_URI);

    // 2. Initialize Uniguru Service
    console.log('2️⃣  Initializing Uniguru Service...');
    uniguruService = new UniguruService(
      process.env.UNIGURU_API_KEY,
      process.env.UNIGURU_BASE_URL
    );

    // 3. Initialize Agent Registry
    console.log('3️⃣  Initializing Agent Registry...');
    agentRegistry = initializeAgents(uniguruService);

    // 4. Initialize RL Feedback Loop
    console.log('4️⃣  Initializing RL Feedback Loop...');
    rlFeedbackLoop = new RLFeedbackLoop(agentRegistry);

    // 5. Initialize LangGraph Pipeline
    console.log('5️⃣  Initializing LangGraph Pipeline...');
    newsPipeline = new NewsProcessingPipeline(agentRegistry, rlFeedbackLoop, uniguruService);

    // 6. Setup Routes
    console.log('6️⃣  Setting up API routes...');
    app.use('/api/news', createNewsRouter(uniguruService));
    app.use('/api/bhiv', createBhivRouter(newsPipeline, rlFeedbackLoop, broadcastUpdate));
    app.use('/api/agents', createAgentsRouter(agentRegistry));
    app.use('/api/feedback', createFeedbackRouter(rlFeedbackLoop, uniguruService));

    // 7. Health check endpoint
    app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date(),
        services: {
          database: 'connected',
          uniguru: 'initialized',
          agents: agentRegistry.getAllAgents().length,
          pipeline: 'ready'
        }
      });
    });

    // 8. System info endpoint
    app.get('/api/system/info', (req, res) => {
      res.json({
        system: 'Noopur News AI',
        version: '1.0.0',
        releaseTag: process.env.RELEASE_TAG || 'demo-stable-v1',
        agents: {
          total: agentRegistry.getAllAgents().length,
          byRole: {
            fetch: agentRegistry.getAgentsByRole('fetch').length,
            filter: agentRegistry.getAgentsByRole('filter').length,
            verify: agentRegistry.getAgentsByRole('verify').length,
            script: agentRegistry.getAgentsByRole('script').length,
            rlfeedback: agentRegistry.getAgentsByRole('rlfeedback').length
          }
        },
        pipeline: newsPipeline.getPipelineStats() || 'no data',
        feedbackThreshold: rlFeedbackLoop.feedbackThreshold
      });
    });

    // 9. Processed item polling endpoint (for PipelineViewer)
    app.get('/api/processed/:id', async (req, res) => {
      try {
        const { getNewsItem } = await import('./db/connection.js');
        const item = await getNewsItem(req.params.id);
        if (!item) {
          return res.status(404).json({ success: false, error: 'News item not found' });
        }
        const log = item.processingLog || [];
        const hasSummary = !!item.summary?.medium || !!item.summary?.short;
        const hasVerification = !!item.verification || item.status === 'verified' || item.status === 'published';
        const published = item.status === 'published';
        const voiced = !!item.publishedMetadata?.audioUrl || !!item.publishedMetadata?.distribution?.vaani;
        const fetchedStage = log.find(l => l.stage === 'created') ? 'completed' : 'pending';
        const filteredStage = hasVerification ? 'completed' : (log.find(l => l.stage === 'enrichment_start') ? 'processing' : 'pending');
        const summarizedStage = hasSummary ? 'completed' : 'pending';
        const scriptedStage = hasSummary ? 'completed' : 'pending';
        const verifiedStage = hasVerification ? 'completed' : 'pending';
        const voicedStage = voiced ? 'completed' : (published ? 'processing' : 'pending');
        res.json({
          success: true,
          status: item.status,
          pipeline: {
            fetched: { status: fetchedStage, timestamp: null },
            filtered: { status: filteredStage, timestamp: null },
            summarized: { status: summarizedStage, timestamp: null },
            verified: { status: verifiedStage, timestamp: null },
            scripted: { status: scriptedStage, timestamp: null },
            voiced: { status: voicedStage, timestamp: null }
          }
        });
      } catch (error) {
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 10. Audio preview endpoint (for TTSPlayer)
    app.get('/api/audio/:id', async (req, res) => {
      try {
        const { getNewsItem } = await import('./db/connection.js');
        const item = await getNewsItem(req.params.id);
        if (!item) {
          return res.status(404).json({ success: false, error: 'News item not found' });
        }
        const audioUrl = item.publishedMetadata?.audioUrl || null;
        res.json({
          success: true,
          available: !!audioUrl,
          url: audioUrl,
          note: audioUrl ? 'Audio available' : 'Audio not yet generated'
        });
      } catch (error) {
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // 11. Category listing endpoint (for filters)
    app.get('/api/categories', async (req, res) => {
      try {
        const { getNewsByStatus } = await import('./db/connection.js');
        const items = await getNewsByStatus('published');
        const counts = {};
        for (const it of items) {
          const cat = it.classification?.category || 'general';
          counts[cat] = (counts[cat] || 0) + 1;
        }
        res.json({ success: true, categories: Object.keys(counts), counts });
      } catch (error) {
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // Start Express Server
    server.listen(PORT, () => {
      console.log(`\n✓ Express server running on http://localhost:${PORT}`);
    });

    // Setup WebSocket Server (on different port)
    const wsServer = new WebSocketServer({ port: WS_PORT });
    setupWebSocket(wsServer);
    console.log(`✓ WebSocket server running on ws://localhost:${WS_PORT}`);

    console.log('\n✅ Noopur News AI System Ready!\n');
  } catch (error) {
    console.error('❌ Initialization error:', error.message);
    process.exit(1);
  }
}

/**
 * Setup WebSocket for real-time updates
 */
function setupWebSocket(wsServer) {
  wsServer.on('connection', (ws) => {
    console.log('[WebSocket] New client connected');
    wsClients.add(ws);

    // Send initial welcome message
    ws.send(JSON.stringify({
      type: 'welcome',
      message: 'Connected to Noopur News AI WebSocket',
      timestamp: new Date()
    }));

    ws.on('message', (message) => {
      try {
        const data = JSON.parse(message);
        console.log('[WebSocket] Message received:', data.type);
        handleWebSocketMessage(data, ws);
      } catch (error) {
        ws.send(JSON.stringify({
          type: 'error',
          error: 'Invalid message format'
        }));
      }
    });

    ws.on('close', () => {
      console.log('[WebSocket] Client disconnected');
      wsClients.delete(ws);
    });

    ws.on('error', (error) => {
      console.error('[WebSocket] Error:', error.message);
    });
  });
}

/**
 * Handle WebSocket messages
 */
function handleWebSocketMessage(data, ws) {
  switch (data.type) {
    case 'subscribe':
      // Subscribe to news updates
      ws.subscribe = data.newsItemId;
      ws.send(JSON.stringify({
        type: 'subscribed',
        newsItemId: data.newsItemId
      }));
      break;

    case 'request_stats':
      ws.send(JSON.stringify({
        type: 'stats',
        stats: newsPipeline.getPipelineStats(),
        timestamp: new Date()
      }));
      break;

    case 'request_agents':
      ws.send(JSON.stringify({
        type: 'agents',
        agents: agentRegistry.getAllQueueStatus(),
        timestamp: new Date()
      }));
      break;

    default:
      ws.send(JSON.stringify({
        type: 'error',
        error: `Unknown message type: ${data.type}`
      }));
  }
}

/**
 * Broadcast to all WebSocket clients
 */
export function broadcastUpdate(type, data) {
  const message = JSON.stringify({
    type,
    data,
    timestamp: new Date()
  });

  wsClients.forEach(client => {
    if (client.readyState === 1) {  // OPEN
      client.send(message);
    }
  });
}

/**
 * Global error handler
 */
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection:', reason);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

// Start application
initializeApp();

export { agentRegistry, newsPipeline, rlFeedbackLoop, uniguruService };
