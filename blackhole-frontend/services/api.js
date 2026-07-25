/**
 * Centralized API Service for News AI Frontend
 * Handles all API calls, directly communicating with the backend.
 * Compatible with existing backend endpoints
 */

import { buildSecureHeaders } from '../lib/security'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_NOOPUR_API_BASE || 'https://news-ai-1l4d.onrender.com';

// Check if real backend is available
let backendAvailable = false;

async function checkBackendAvailability() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
      },
    });
    backendAvailable = response.ok;
    return backendAvailable;
  } catch (error) {
    backendAvailable = false;
    return false;
  }
}

/**
 * API Service Class
 */
class APIService {
  constructor() {
    this.backendChecked = false;
    // Auto-check backend on initialization
    this.initialize();
  }

  async initialize() {
    if (!this.backendChecked) {
      const available = await checkBackendAvailability();
      this.backendChecked = true;
      console.log(`API Service initialized: Backend available = ${available}`);
    }
  }

  /**
   * Helper method to handle API calls
   */
  async fetchFromAPI(endpoint, options = {}) {
    try {
      const url = `${API_BASE_URL}${endpoint}`
      const method = options.method || 'GET'

      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true',
          ...options.headers,
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      backendAvailable = true
      return data
    } catch (error) {
      console.error(`API call to ${endpoint} failed: ${error.message}`)
      backendAvailable = false
      // propagate error to UI
      throw error
    }
  }

  /**
   * Get all news items
   */
  async getNews(filters = {}) {
    const { category, status, limit } = filters;
    const queryParams = new URLSearchParams();
    if (category && category !== 'all') queryParams.append('category', category);
    if (status) queryParams.append('status', status);
    if (limit) queryParams.append('limit', limit.toString());

    const endpoint = `/api/news${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return await this.fetchFromAPI(endpoint);
  }

  /**
   * Get single processed news item by ID
   */
  async getProcessedNews(id) {
    try {
      // Fetch 1: Full item details (title, summary, audioUrl, etc.)
      const fullItemResult = await this.fetchFromAPI(`/api/news/${id}`);
      
      // Fetch 2: Pipeline status (for visualizer)
      const pipelineResult = await this.fetchFromAPI(`/api/processed/${id}`);
      
      if (fullItemResult && fullItemResult.success) {
        const item = fullItemResult.data;
        const pipelineData = pipelineResult && pipelineResult.success ? pipelineResult.pipeline : null;
        
        // Map backend fields to frontend expected format if needed
        const audioUrl = item.publishedMetadata?.audioUrl || null;
        
        return {
          success: true,
          data: {
            ...item,
            audioUrl: audioUrl,
            audioDuration: item.publishedMetadata?.audioDuration || 0,
            pipeline: pipelineData || item.processingLog // Fallback to processingLog if pipeline endpoint fails
          }
        };
      }
      return fullItemResult;
    } catch (error) {
      console.warn('Error fetching full news details, falling back to processed endpoint only:', error);
      return await this.fetchFromAPI(`/api/processed/${id}`);
    }
  }

  /**
   * Get audio for news item
   */
  async getAudio(id) {
    return await this.fetchFromAPI(`/api/audio/${id}`);
  }

  /**
   * Submit feedback for news item
   */
  async submitFeedback(newsId, feedbackType, metadata = {}) {
    const payload = {
      newsId,
      feedbackType, // 'like', 'skip', 'approve', 'flag'
      metadata,
      timestamp: new Date().toISOString()
    };

    // Store in localStorage
    this.storeFeedbackLocally(payload);

    // Send to API
    return await this.fetchFromAPI('/api/feedback', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  /**
   * Store feedback in localStorage for analytics
   */
  storeFeedbackLocally(feedback) {
    try {
      const existing = JSON.parse(localStorage.getItem('feedbackHistory') || '[]');
      existing.push(feedback);
      // Keep only last 100 feedback items
      const limited = existing.slice(-100);
      localStorage.setItem('feedbackHistory', JSON.stringify(limited));
    } catch (error) {
      console.error('Error storing feedback locally:', error);
    }
  }

  /**
   * Get feedback history from localStorage
   */
  getFeedbackHistory() {
    try {
      return JSON.parse(localStorage.getItem('feedbackHistory') || '[]');
    } catch (error) {
      console.error('Error reading feedback history:', error);
      return [];
    }
  }

  /**
   * Get categories
   */
  async getCategories() {
    const result = await this.fetchFromAPI('/api/categories');
    if (result && result.success) {
      // Map backend format to UI format
      const formatted = Object.entries(result.counts || {}).map(([id, count]) => ({
        id,
        name: id.charAt(0).toUpperCase() + id.slice(1),
        count
      }));
      return { success: true, data: [{ id: 'all', name: 'All News', count: result.total || 0 }, ...formatted] };
    }
    return result;
  }

  /**
   * Get pipeline status for news item
   */
  async getPipelineStatus(id) {
    return await this.getProcessedNews(id);
  }

  /**
   * Toggle mock data mode (No-op now, kept for backward compatibility)
   */
  setMockDataMode(useMock) {
    console.log(`Mock data mode is disabled. Real backend is always used.`);
  }

  /**
   * Get backend availability status
   */
  isBackendAvailable() {
    return backendAvailable;
  }

  /**
   * Force backend check
   */
  async recheckBackend() {
    this.backendChecked = false;
    await this.initialize();
    return backendAvailable;
  }

  /**
   * Get API base URL
   */
  getBaseURL() {
    return API_BASE_URL;
  }
}

// Export singleton instance
const apiService = new APIService();
export default apiService;
