/**
 * Centralized API Service for News AI Frontend
 * Handles all API calls with mock data fallback
 * Compatible with existing backend endpoints
 */

import { buildSecureHeaders } from '../lib/security'

const API_BASE_URL = process.env.NEXT_PUBLIC_NOOPUR_API_BASE || 'http://localhost:8000';

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

// Mock data for development
const MOCK_NEWS_DATA = [
  {
    id: '1',
    title: 'AI Breakthrough in Natural Language Processing',
    source: 'TechCrunch',
    category: 'technology',
    url: 'https://techcrunch.com/ai-breakthrough',
    status: 'completed',
    timestamp: new Date().toISOString(),
    content: 'Researchers have made a significant breakthrough in natural language processing...',
    summary: 'Major AI advancement enables more accurate language understanding and generation.',
    audioUrl: '/audio/sample1.mp3',
    audioDuration: 180,
    insights: {
      sentiment: 'positive',
      tone: 'informative',
      category: 'technology',
      credibilityScore: 0.92,
      biasScore: 0.15,
      keywords: ['AI', 'NLP', 'breakthrough', 'research'],
      entities: ['OpenAI', 'GPT', 'Stanford University']
    },
    pipeline: {
      fetched: { status: 'completed', timestamp: new Date(Date.now() - 5000).toISOString() },
      filtered: { status: 'completed', timestamp: new Date(Date.now() - 4000).toISOString() },
      summarized: { status: 'completed', timestamp: new Date(Date.now() - 3000).toISOString() },
      verified: { status: 'completed', timestamp: new Date(Date.now() - 2000).toISOString() },
      scripted: { status: 'completed', timestamp: new Date(Date.now() - 1000).toISOString() },
      voiced: { status: 'completed', timestamp: new Date().toISOString() }
    },
    feedback: {
      likes: 24,
      skips: 2,
      flags: 0
    }
  },
  {
    id: '2',
    title: 'Global Climate Summit Reaches Historic Agreement',
    source: 'Reuters',
    category: 'environment',
    url: 'https://reuters.com/climate-summit',
    status: 'processing',
    timestamp: new Date().toISOString(),
    content: 'World leaders have agreed on ambitious new climate targets...',
    summary: 'Historic climate agreement sets new global emission reduction targets.',
    audioUrl: null,
    audioDuration: 0,
    insights: {
      sentiment: 'hopeful',
      tone: 'serious',
      category: 'environment',
      credibilityScore: 0.95,
      biasScore: 0.08,
      keywords: ['climate', 'summit', 'emissions', 'agreement'],
      entities: ['UN', 'Paris Agreement', 'COP28']
    },
    pipeline: {
      fetched: { status: 'completed', timestamp: new Date(Date.now() - 3000).toISOString() },
      filtered: { status: 'completed', timestamp: new Date(Date.now() - 2000).toISOString() },
      summarized: { status: 'completed', timestamp: new Date(Date.now() - 1000).toISOString() },
      verified: { status: 'processing', timestamp: new Date().toISOString() },
      scripted: { status: 'pending', timestamp: null },
      voiced: { status: 'pending', timestamp: null }
    },
    feedback: {
      likes: 15,
      skips: 1,
      flags: 0
    }
  },
  {
    id: '3',
    title: 'Stock Markets Rally on Positive Economic Data',
    source: 'CNBC',
    category: 'business',
    url: 'https://cnbc.com/markets-rally',
    status: 'completed',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    content: 'Major stock indices posted significant gains following better-than-expected employment data...',
    summary: 'Markets surge as strong economic indicators boost investor confidence.',
    audioUrl: '/audio/sample2.mp3',
    audioDuration: 150,
    insights: {
      sentiment: 'positive',
      tone: 'optimistic',
      category: 'business',
      credibilityScore: 0.88,
      biasScore: 0.12,
      keywords: ['stocks', 'markets', 'economy', 'rally'],
      entities: ['S&P 500', 'Dow Jones', 'NASDAQ', 'Federal Reserve']
    },
    pipeline: {
      fetched: { status: 'completed', timestamp: new Date(Date.now() - 8000).toISOString() },
      filtered: { status: 'completed', timestamp: new Date(Date.now() - 7000).toISOString() },
      summarized: { status: 'completed', timestamp: new Date(Date.now() - 6000).toISOString() },
      verified: { status: 'completed', timestamp: new Date(Date.now() - 5000).toISOString() },
      scripted: { status: 'completed', timestamp: new Date(Date.now() - 4000).toISOString() },
      voiced: { status: 'completed', timestamp: new Date(Date.now() - 3000).toISOString() }
    },
    feedback: {
      likes: 42,
      skips: 3,
      flags: 0
    }
  },
  {
    id: '4',
    title: 'Breakthrough in Renewable Energy Storage',
    source: 'Scientific American',
    category: 'science',
    url: 'https://scientificamerican.com/energy-storage',
    status: 'completed',
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    content: 'Scientists develop new battery technology with unprecedented energy density...',
    summary: 'Revolutionary battery technology promises to transform renewable energy storage.',
    audioUrl: '/audio/sample3.mp3',
    audioDuration: 200,
    insights: {
      sentiment: 'excited',
      tone: 'scientific',
      category: 'science',
      credibilityScore: 0.96,
      biasScore: 0.05,
      keywords: ['battery', 'renewable', 'energy', 'storage', 'technology'],
      entities: ['MIT', 'lithium-ion', 'solar energy']
    },
    pipeline: {
      fetched: { status: 'completed', timestamp: new Date(Date.now() - 12000).toISOString() },
      filtered: { status: 'completed', timestamp: new Date(Date.now() - 11000).toISOString() },
      summarized: { status: 'completed', timestamp: new Date(Date.now() - 10000).toISOString() },
      verified: { status: 'completed', timestamp: new Date(Date.now() - 9000).toISOString() },
      scripted: { status: 'completed', timestamp: new Date(Date.now() - 8000).toISOString() },
      voiced: { status: 'completed', timestamp: new Date(Date.now() - 7000).toISOString() }
    },
    feedback: {
      likes: 67,
      skips: 1,
      flags: 0
    }
  },
  {
    id: '5',
    title: 'Major Cybersecurity Vulnerability Discovered',
    source: 'Wired',
    category: 'technology',
    url: 'https://wired.com/security-vulnerability',
    status: 'flagged',
    timestamp: new Date(Date.now() - 1800000).toISOString(),
    content: 'Security researchers have identified a critical flaw affecting millions of devices...',
    summary: 'Critical security flaw discovered, immediate patches recommended for all users.',
    audioUrl: '/audio/sample4.mp3',
    audioDuration: 165,
    insights: {
      sentiment: 'concerned',
      tone: 'urgent',
      category: 'technology',
      credibilityScore: 0.90,
      biasScore: 0.10,
      keywords: ['cybersecurity', 'vulnerability', 'security', 'patch'],
      entities: ['Microsoft', 'CVE', 'CISA']
    },
    pipeline: {
      fetched: { status: 'completed', timestamp: new Date(Date.now() - 6000).toISOString() },
      filtered: { status: 'completed', timestamp: new Date(Date.now() - 5000).toISOString() },
      summarized: { status: 'completed', timestamp: new Date(Date.now() - 4000).toISOString() },
      verified: { status: 'completed', timestamp: new Date(Date.now() - 3000).toISOString() },
      scripted: { status: 'completed', timestamp: new Date(Date.now() - 2000).toISOString() },
      voiced: { status: 'completed', timestamp: new Date(Date.now() - 1000).toISOString() }
    },
    feedback: {
      likes: 31,
      skips: 5,
      flags: 2
    }
  }
];

const MOCK_CATEGORIES = [
  { id: 'all', name: 'All News', count: 125 },
  { id: 'technology', name: 'Technology', count: 45 },
  { id: 'business', name: 'Business', count: 32 },
  { id: 'science', name: 'Science', count: 18 },
  { id: 'environment', name: 'Environment', count: 15 },
  { id: 'health', name: 'Health', count: 15 }
];

/**
 * API Service Class
 */
class APIService {
  constructor() {
    this.useMockData = false; // Try real backend first, fallback to mock
    this.backendChecked = false;

    // Auto-check backend on initialization
    this.initialize();
  }

  async initialize() {
    if (!this.backendChecked) {
      const available = await checkBackendAvailability();
      this.useMockData = !available;
      this.backendChecked = true;
      console.log(`API Service initialized: ${available ? 'Using real backend' : 'Using mock data'}`);
    }
  }

  /**
   * Helper method to handle API calls
   * DISABLED silent mock fallback for Production Closure
   */
  async fetchWithFallback(endpoint, options = {}) {
    // strict "no mock" policy for production closure
    const FORCE_NO_MOCKS = true;

    if (FORCE_NO_MOCKS || !this.useMockData || !this.backendChecked) {
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
        // propagate error to UI instead of falling back
        throw error
      }
    }

    return this.getMockResponse(endpoint)
  }

  /**
   * Get mock response based on endpoint
   */
  getMockResponse(endpoint) {
    if (endpoint.includes('/news')) {
      return { success: true, data: MOCK_NEWS_DATA, total: MOCK_NEWS_DATA.length };
    }
    if (endpoint.includes('/categories')) {
      return { success: true, data: MOCK_CATEGORIES };
    }
    if (endpoint.includes('/processed/')) {
      const id = endpoint.split('/').pop();
      const item = MOCK_NEWS_DATA.find(n => n.id === id);
      return { success: true, data: item || null };
    }
    if (endpoint.includes('/audio/')) {
      return { success: true, url: '/audio/sample.mp3' };
    }
    if (endpoint.includes('/feedback')) {
      return { success: true, message: 'Feedback recorded' };
    }
    return { success: true, data: null };
  }

  /**
   * Get all news items
   */
  async getNews(filters = {}) {
    const { category, status, limit } = filters;

    // Try real backend
    if (!this.useMockData) {
      try {
        const queryParams = new URLSearchParams();
        if (category && category !== 'all') queryParams.append('category', category);
        if (status) queryParams.append('status', status);
        if (limit) queryParams.append('limit', limit.toString());

        const endpoint = `/api/news${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
        const result = await this.fetchWithFallback(endpoint);
        if (result && result.success) return result;
      } catch (error) {
        console.warn('Real news fetch failed, falling back to mock:', error);
      }
    }

    let data = [...MOCK_NEWS_DATA];

    // Apply filters
    if (category && category !== 'all') {
      data = data.filter(item => item.category === category);
    }
    if (status) {
      data = data.filter(item => item.status === status);
    }
    if (limit) {
      data = data.slice(0, limit);
    }

    return {
      success: true,
      data: data,
      total: data.length,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Get single processed news item by ID
   * Modified to fetch full data from /api/news/:id first, then merge with /api/processed/:id
   */
  async getProcessedNews(id) {
    if (!this.useMockData) {
      try {
        // Fetch 1: Full item details (title, summary, audioUrl, etc.)
        const fullItemResult = await this.fetchWithFallback(`/api/news/${id}`);
        
        // Fetch 2: Pipeline status (for visualizer)
        const pipelineResult = await this.fetchWithFallback(`/api/processed/${id}`);
        
        if (fullItemResult && fullItemResult.success) {
          const item = fullItemResult.data;
          const pipelineData = pipelineResult && pipelineResult.success ? pipelineResult.pipeline : null;
          
          // Map backend fields to frontend expected format if needed
          // Especially ensuring audioUrl is available at the root level
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
      } catch (error) {
        console.warn('Error fetching full news details, falling back to processed endpoint only:', error);
      }
      
      // Fallback: Just call processed endpoint (might be partial data)
      const result = await this.fetchWithFallback(`/api/processed/${id}`);
      return result;
    }
    
    // Mock data logic
    const result = await this.fetchWithFallback(`/api/processed/${id}`);
    return result;
  }

  /**
   * Get audio for news item
   */
  async getAudio(id) {
    const result = await this.fetchWithFallback(`/api/audio/${id}`);
    return result;
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
    const result = await this.fetchWithFallback('/api/feedback', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    return result;
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
    if (!this.useMockData) {
      const result = await this.fetchWithFallback('/api/categories');
      if (result && result.success) {
        // Map backend format to UI format
        const formatted = Object.entries(result.counts || {}).map(([id, count]) => ({
          id,
          name: id.charAt(0).toUpperCase() + id.slice(1),
          count
        }));
        return { success: true, data: [{ id: 'all', name: 'All News', count: result.total || 0 }, ...formatted] };
      }
    }
    return {
      success: true,
      data: MOCK_CATEGORIES
    };
  }

  /**
   * Get pipeline status for news item
   */
  async getPipelineStatus(id) {
    if (!this.useMockData) {
      return await this.getProcessedNews(id);
    }
    const news = MOCK_NEWS_DATA.find(item => item.id === id);
    if (news) {
      return {
        success: true,
        data: news.pipeline
      };
    }
    return {
      success: false,
      message: 'News item not found'
    };
  }

  /**
   * Toggle mock data mode
   */
  setMockDataMode(useMock) {
    this.useMockData = useMock;
    console.log(`API Service mode: ${useMock ? 'Mock Data' : 'Real Backend'}`);
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

