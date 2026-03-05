import 'dotenv/config';
import axios from 'axios';

const BASE = process.env.WORKER_API_BASE || `http://localhost:${process.env.PORT || 3000}`;

const queue = [];
const MAX_RETRIES = 3;

function enqueue(task) {
  queue.push({ ...task, attempts: 0, enqueuedAt: Date.now() });
}

async function processTask(task) {
  try {
    if (task.type === 'bhiv_process') {
      await axios.post(`${BASE}/api/bhiv/process`, { newsItemId: task.newsItemId }, { timeout: 60000 });
      console.log(`[queue] processed ${task.newsItemId}`);
      return true;
    }
    return true;
  } catch (err) {
    const status = err?.response?.status;
    const msg = err?.message || 'unknown';
    console.warn(`[queue] error for ${task.newsItemId}: ${status || ''} ${msg}`);
    // Retry on gateway timeout or network errors
    if (status === 504 || msg.includes('timeout') || msg.includes('ECONN')) {
      return false;
    }
    // Requeue BHIV failures
    if (task.type === 'bhiv_process') {
      return false;
    }
    return false;
  }
}

async function tick() {
  // Pull verified items not yet published
  try {
    const r = await axios.get(`${BASE}/api/news/status/verified`, { timeout: 15000 });
    const items = Array.isArray(r.data?.data) ? r.data.data : [];
    for (const it of items) {
      // Enqueue if not already in published state
      enqueue({ type: 'bhiv_process', newsItemId: String(it._id || it.id || it.newsId) });
    }
  } catch (err) {
    console.warn('[queue] fetch verified error', err?.message || err);
  }

  // Process queue
  const next = queue.shift();
  if (next) {
    const ok = await processTask(next);
    if (!ok) {
      next.attempts += 1;
      if (next.attempts < MAX_RETRIES) {
        const backoffMs = 2000 * next.attempts;
        console.log(`[queue] requeue ${next.newsItemId} in ${backoffMs}ms`);
        setTimeout(() => enqueue(next), backoffMs);
      } else {
        console.error(`[queue] drop task after ${MAX_RETRIES} attempts: ${next.newsItemId}`);
      }
    }
  }
}

// Run every minute
setInterval(tick, 60 * 1000);
// Prime run
tick();

console.log('[queue] worker started');
