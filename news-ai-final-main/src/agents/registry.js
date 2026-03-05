import { v4 as uuidv4 } from 'uuid';
import { createAgentTask, updateAgentTask, getAgentTasksByStatus, getAgentTasksByAgent } from '../db/connection.js';

class AgentRegistry {
  constructor() {
    this.agents = new Map();
    this.taskQueues = new Map();
    this.taskHandlers = new Map();
  }

  /**
   * Register a new agent with specific role
   */
  registerAgent(agentRole, handler, options = {}) {
    const agentId = `agent-${agentRole}-${uuidv4().substring(0, 8)}`;
    
    const agentConfig = {
      id: agentId,
      role: agentRole,  // fetch, filter, verify, script, rlfeedback
      handler,
      priority: options.priority || 5,
      maxConcurrent: options.maxConcurrent || 5,
      timeout: options.timeout || 30000,
      retryPolicy: {
        maxRetries: options.maxRetries || 3,
        backoffMultiplier: options.backoffMultiplier || 2,
        initialDelayMs: options.initialDelayMs || 1000
      },
      status: 'active',
      createdAt: new Date()
    };

    this.agents.set(agentId, agentConfig);
    this.taskQueues.set(agentId, []);
    this.taskHandlers.set(agentId, handler);

    console.log(`✓ Agent registered: ${agentId} (${agentRole})`);
    return agentId;
  }

  /**
   * Submit a task to an agent
   */
  async submitTask(newsItemId, agentRole, payload, priority = 5) {
    // Find agent with matching role
    let targetAgent = null;
    for (const [agentId, config] of this.agents.entries()) {
      if (config.role === agentRole && config.status === 'active') {
        targetAgent = { id: agentId, config };
        break;
      }
    }

    if (!targetAgent) {
      throw new Error(`No active agent found for role: ${agentRole}`);
    }

    // Create task in database
    const task = await createAgentTask({
      agentId: targetAgent.id,
      agentRole,
      newsItemId,
      priority,
      status: 'pending',
      payload
    });

    // Add to queue
    this.taskQueues.get(targetAgent.id).push(task);
    console.log(`✓ Task submitted: ${task.taskId} to ${targetAgent.id}`);

    // Process task async
    this.processTaskAsync(task, targetAgent.id);

    return task;
  }

  /**
   * Process task asynchronously
   */
  async processTaskAsync(task, agentId) {
    try {
      const agentConfig = this.agents.get(agentId);
      const handler = this.taskHandlers.get(agentId);

      if (!handler) {
        throw new Error(`No handler found for agent: ${agentId}`);
      }

      // Update status to processing
      await updateAgentTask(task.taskId, {
        status: 'processing',
        'executionMetrics.startTime': new Date()
      });

      // Execute handler with timeout
      const result = await this.executeWithTimeout(
        handler(task.payload, task.newsItemId),
        agentConfig.timeout
      );

      // Update task with result
      await updateAgentTask(task.taskId, {
        status: 'completed',
        result,
        'executionMetrics.endTime': new Date(),
        completedAt: new Date()
      });

      console.log(`✓ Task completed: ${task.taskId}`);
      return result;
    } catch (error) {
      console.error(`✗ Task failed: ${task.taskId}`, error.message);
      await this.handleTaskError(task, agentId, error);
    }
  }

  /**
   * Handle task errors with retry logic
   */
  async handleTaskError(task, agentId, error) {
    const agentConfig = this.agents.get(agentId);
    const retryPolicy = agentConfig.retryPolicy;

    // Get current error info
    const errorInfo = {
      message: error.message,
      stack: error.stack,
      retryCount: (task.error?.retryCount || 0) + 1,
      lastRetry: new Date()
    };

    if (errorInfo.retryCount <= retryPolicy.maxRetries) {
      // Calculate backoff delay
      const delayMs = retryPolicy.initialDelayMs * Math.pow(retryPolicy.backoffMultiplier, errorInfo.retryCount - 1);
      
      console.log(`↻ Retrying task ${task.taskId} (attempt ${errorInfo.retryCount}/${retryPolicy.maxRetries}) in ${delayMs}ms`);

      // Update to retry status
      await updateAgentTask(task.taskId, {
        status: 'retry',
        error: errorInfo
      });

      // Schedule retry
      setTimeout(() => {
        this.processTaskAsync(task, agentId);
      }, delayMs);
    } else {
      // Max retries exceeded
      console.error(`✗ Task failed permanently: ${task.taskId}`);
      
      await updateAgentTask(task.taskId, {
        status: 'failed',
        error: errorInfo
      });
    }
  }

  /**
   * Execute function with timeout
   */
  executeWithTimeout(promise, timeoutMs) {
    return Promise.race([
      promise,
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error(`Task timeout after ${timeoutMs}ms`)), timeoutMs)
      )
    ]);
  }

  /**
   * Get agent by ID
   */
  getAgent(agentId) {
    return this.agents.get(agentId);
  }

  /**
   * Get all agents
   */
  getAllAgents() {
    return Array.from(this.agents.values());
  }

  /**
   * Get agents by role
   */
  getAgentsByRole(agentRole) {
    return Array.from(this.agents.values()).filter(a => a.role === agentRole);
  }

  /**
   * Get queue status for agent
   */
  getQueueStatus(agentId) {
    const queue = this.taskQueues.get(agentId);
    return {
      agentId,
      queueLength: queue ? queue.length : 0,
      agent: this.agents.get(agentId)
    };
  }

  /**
   * Get all queue statuses
   */
  getAllQueueStatus() {
    const statuses = [];
    for (const [agentId, queue] of this.taskQueues.entries()) {
      statuses.push({
        agentId,
        queueLength: queue.length,
        agent: this.agents.get(agentId)
      });
    }
    return statuses;
  }

  /**
   * Disable agent
   */
  disableAgent(agentId) {
    const agent = this.agents.get(agentId);
    if (agent) {
      agent.status = 'inactive';
      console.log(`✓ Agent disabled: ${agentId}`);
    }
  }

  /**
   * Enable agent
   */
  enableAgent(agentId) {
    const agent = this.agents.get(agentId);
    if (agent) {
      agent.status = 'active';
      console.log(`✓ Agent enabled: ${agentId}`);
    }
  }
}

export default AgentRegistry;
