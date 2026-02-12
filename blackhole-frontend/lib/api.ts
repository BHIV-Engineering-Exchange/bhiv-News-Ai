const API_BASE = process.env.NEXT_PUBLIC_NOOPUR_API_BASE || 'http://localhost:8000'
const SANKALP_API_BASE = process.env.NEXT_PUBLIC_SANKALP_API_BASE || 'http://localhost:8000'

export interface WorkflowResult {
  success: boolean
  data?: {
    url: string
    timestamp: string
    workflow_steps: string[]
    processing_time: {
      scraping: number
      vetting: number
      summarization: number
      prompt_generation: number
      video_search: number
    }
    scraped_data: {
      title: string
      content_length: number
      author: string
      date: string
    }
    vetting_results: {
      authenticity_score: number
      credibility_rating: string
      is_reliable: boolean
    }
    summary: {
      text: string
      original_length: number
      summary_length: number
      compression_ratio: number
    }
    video_prompt: {
      prompt: string
      for_video_creation: boolean
      based_on_summary: boolean
    }
    sidebar_videos: {
      videos: Array<{
        title: string
        url: string
        thumbnail?: string
        duration?: string
        source: string
      }>
      total_found: number
      ready_for_playback: boolean
    }
    total_processing_time: number
    workflow_complete: boolean
    steps_completed: number
  }
  message?: string
  timestamp?: string
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
      },
    })

    if (!response.ok) {
      return false
    }

    const data = await response.json()
    return data.status === 'healthy'
  } catch (error) {
    console.error('Backend health check failed:', error)
    return false
  }
}

export async function runUnifiedWorkflow(url: string): Promise<WorkflowResult> {
  try {
    console.log(`📡 Connecting to backend at: ${API_BASE}`)
    return await runLegacyWorkflow(url);
  } catch (error) {
    console.error('Unified workflow failed:', error)
    throw new Error(error instanceof Error ? error.message : 'Unknown error occurred')
  }
}

/**
 * Step 1 of the new workflow: Create a news item
 */
export async function initiateNewsAnalysis(url: string): Promise<string> {
  const response = await fetch(`${API_BASE}/api/news`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true',
    },
    body: JSON.stringify({
      title: "Analyzing News...",
      content: "Extracted from URL",
      sourceUrl: url,
      source: 'web'
    }),
  })

  if (!response.ok) {
    throw new Error(`Failed to create news item: ${response.status}`)
  }

  const data = await response.json()
  return data.newsId || data.id
}

/**
 * Step 2 of the new workflow: Trigger processing
 */
export async function triggerPipeline(newsId: string): Promise<any> {
  const response = await fetch(`${API_BASE}/api/bhiv/process`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ newsItemId: newsId }),
  })

  if (!response.ok) {
    throw new Error(`Pipeline execution failed: ${response.status}`)
  }

  return await response.json()
}

/**
 * Legacy workflow fallback for compatibility with Python-only backend
 */
async function runLegacyWorkflow(url: string): Promise<WorkflowResult> {
  const response = await fetch(`${API_BASE}/api/unified-news-workflow`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true',
    },
    body: JSON.stringify({ url }),
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return await response.json()
}

/**
 * Maps the new backend response (BHIV + Pipeline) to the Frontend WorkflowResult interface
 */
function mapToWorkflowResult(data: any): WorkflowResult {
  const seeya = data.seeya_compat || {}
  const pipeline = data.pipelineResult || {}

  return {
    success: data.success,
    data: {
      url: seeya.source_url || '',
      timestamp: new Date().toISOString(),
      workflow_steps: ['fetch', 'filter', 'verify', 'script', 'feedback'],
      processing_time: {
        scraping: 1.5,
        vetting: pipeline.processingTime ? pipeline.processingTime / 1000 : 2.0,
        summarization: 1.0,
        prompt_generation: 0.5,
        video_search: 1.0
      },
      scraped_data: {
        title: seeya.title || 'Untitled',
        content_length: 500,
        author: 'AI Agent',
        date: new Date().toLocaleDateString()
      },
      vetting_results: {
        authenticity_score: Math.round((pipeline.finalRewardScore || 0.85) * 100),
        credibility_rating: (pipeline.finalRewardScore || 0.85) > 0.8 ? 'High' : 'Medium',
        is_reliable: (pipeline.finalRewardScore || 0.85) > 0.7
      },
      summary: {
        text: data.newsItem?.summary?.medium || 'Summary not available',
        original_length: 1000,
        summary_length: 200,
        compression_ratio: 0.2
      },
      video_prompt: {
        prompt: data.newsItem?.script?.headline || 'Create a news report about the event',
        for_video_creation: true,
        based_on_summary: true
      },
      sidebar_videos: {
        videos: [],
        total_found: 0,
        ready_for_playback: false
      },
      total_processing_time: pipeline.processingTime || 0,
      workflow_complete: true,
      steps_completed: 5
    }
  }
}


export async function testIndividualTool(tool: string, payload: any): Promise<any> {
  try {
    const endpoints: { [key: string]: string } = {
      scraping: '/api/scrape',
      vetting: '/api/vet',
      summarization: '/api/summarize',
      prompt: '/api/prompt',
      video: '/api/video-search',
      'validate-video': '/api/validate-video',
      'bhiv-process': '/api/bhiv/process'
    }

    const endpoint = endpoints[tool]
    if (!endpoint) {
      throw new Error(`Unknown tool: ${tool}`)
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`${tool} tool test failed:`, error)
    throw error
  }
}

/**
 * Fetches the real-time pipeline status for a specific news item
 */
export async function getDetailedPipelineStatus(newsId: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE}/api/processed/${newsId}`)
    if (!response.ok) throw new Error('Status poll failed')
    return await response.json()
  } catch (error) {
    console.error('Pipeline status poll failed:', error)
    return null
  }
}

/**
 * Fetches a single news item by ID
 */
export async function getNewsItemById(newsId: string): Promise<any> {
  const response = await fetch(`${API_BASE}/api/news/${newsId}`)
  if (!response.ok) throw new Error('Failed to fetch news item')
  const result = await response.json()
  return result.data
}

/**
 * Fetches available news categories from the backend
 */
export async function getAvailableCategories(): Promise<{ categories: string[], counts: Record<string, number> }> {
  try {
    const response = await fetch(`${API_BASE}/api/categories`)
    if (!response.ok) throw new Error('Failed to fetch categories')
    const data = await response.json()
    return {
      categories: data.categories || [],
      counts: data.counts || {}
    }
  } catch (error) {
    console.error('Category fetch failed:', error)
    return { categories: [], counts: {} }
  }
}

/**
 * Checks for audio preview availability
 */
export async function getAudioAvailability(newsId: string): Promise<{ available: boolean, url: string | null }> {
  try {
    const response = await fetch(`${API_BASE}/api/audio/${newsId}`)
    if (!response.ok) throw new Error('Audio check failed')
    const data = await response.json()
    return {
      available: data.available,
      url: data.url
    }
  } catch (error) {
    console.error('Audio check failed:', error)
    return { available: false, url: null }
  }
}

export async function getBackendStatus(): Promise<{
  status: string
  services: { [key: string]: any }
  endpoints: number
  version: string
}> {
  try {
    const response = await fetch(`${API_BASE}/health`)
    if (!response.ok) {
      throw new Error('Backend not responding')
    }
    return await response.json()
  } catch (error) {
    throw new Error('Failed to get backend status')
  }
}


// ============================================================================
// Sankalp (Insight Node) API Integration
// ============================================================================

import { buildSecureHeaders } from './security'

export interface SankalpItem {
  id: string
  script: string
  tone: string
  language: string
  audio_path: string
  priority_score: number
  trend_score: number
  title?: string
  summary_short?: string
  summary_medium?: string
  category?: string
  polarity?: string
  timestamp?: string
  audio_duration?: number
  voice_used?: string
  synthesis_status?: string
  avatar?: string
}

export interface SankalpFeedResponse {
  generated_at?: string
  items: SankalpItem[]
}

export interface FeedbackSignals {
  editor_approve?: boolean
  user_like?: boolean
  user_skip?: boolean
  manual_override?: boolean
}

export interface FeedbackResponse {
  id: string
  reward: number
  action: string
  requeued: boolean
}

/**
 * Fetch news feed from Sankalp's weekly report
 * Note: This assumes Sankalp exposes the weekly_report.json via HTTP
 * If not, we'll need to integrate via Noopur or file system
 */
export async function getSankalpFeed(): Promise<SankalpFeedResponse> {
  try {
    // Check if backend is available first
    const isBackendAvailable = await checkBackendHealth()
    if (!isBackendAvailable) {
      // Backend not available, return empty feed silently
      return { items: [] }
    }

    const url = `${SANKALP_API_BASE}/exports/weekly_report.json`
    const secureHeaders = await buildSecureHeaders(url, 'GET')

    // Create abort controller for timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout

    // Try to fetch from weekly_report.json endpoint
    // If Sankalp doesn't expose this, we'll need to adjust
    let response: Response
    try {
      response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...secureHeaders,
        },
        signal: controller.signal,
      })
      clearTimeout(timeoutId)
    } catch (fetchError) {
      clearTimeout(timeoutId)
      if (fetchError instanceof Error && fetchError.name === 'AbortError') {
        // Timeout - return empty feed
        return { items: [] }
      }
      throw fetchError
    }

    if (!response.ok) {
      // Fallback: try sample_integration.json
      const fallbackUrl = `${SANKALP_API_BASE}/exports/sample_integration.json`
      const fallbackHeaders = await buildSecureHeaders(fallbackUrl, 'GET')
      const fallbackController = new AbortController()
      const fallbackTimeoutId = setTimeout(() => fallbackController.abort(), 5000)

      let fallbackResponse: Response
      try {
        fallbackResponse = await fetch(fallbackUrl, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            ...fallbackHeaders,
          },
          signal: fallbackController.signal,
        })
        clearTimeout(fallbackTimeoutId)
      } catch (fetchError) {
        clearTimeout(fallbackTimeoutId)
        if (fetchError instanceof Error && fetchError.name === 'AbortError') {
          // Timeout - return empty feed
          return { items: [] }
        }
        throw fetchError
      }

      if (!fallbackResponse.ok) {
        // Silently return empty feed instead of throwing
        return { items: [] }
      }

      const data = await fallbackResponse.json()
      return { items: data.items || [] }
    }

    const data = await response.json()
    return { items: data.items || [], generated_at: data.generated_at }
  } catch (error) {
    // Only log error once to prevent console spam
    if (!(error as any).__logged) {
      console.warn('⚠️ Sankalp feed unavailable (backend may be offline):', error instanceof Error ? error.message : 'Unknown error')
        ; (error as any).__logged = true
    }
    // Return empty feed on error
    return { items: [] }
  }
}

/**
 * Submit feedback to the local orchestrator's feedback system
 */
export async function submitFeedback(
  itemId: string,
  item: Partial<SankalpItem>,
  signals: FeedbackSignals
): Promise<FeedbackResponse> {
  try {
    // Determine primary endpoint based on where the item came from
    // For news items processed by Noopur Node, we use its feedback router
    const feedbackUrl = `${API_BASE}/api/feedback`
    const feedbackType = signals.editor_approve ? 'approve' : (signals.user_like ? 'like' : (signals.user_skip ? 'skip' : 'view'))

    const response = await fetch(feedbackUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        newsId: itemId,
        feedbackType: feedbackType,
        metadata: {
          signals,
          title: item.title,
          timestamp: new Date()
        }
      }),
    })

    if (!response.ok) {
      // Fallback to Sankalp feedback if main orchestrator fails
      return await submitSankalpFeedback(itemId, item, signals)
    }

    const data = await response.json()
    return {
      id: itemId,
      reward: data.reward || 0,
      action: feedbackType,
      requeued: false
    }
  } catch (error) {
    console.error('Failed to submit feedback:', error)
    return await submitSankalpFeedback(itemId, item, signals)
  }
}

/**
 * Legacy/Microservice feedback fallback
 */
async function submitSankalpFeedback(
  itemId: string,
  item: Partial<SankalpItem>,
  signals: FeedbackSignals
): Promise<FeedbackResponse> {
  const url = `${SANKALP_API_BASE}/feedback`
  const body = {
    id: itemId,
    item: item,
    signals: signals,
  }
  const secureHeaders = await buildSecureHeaders(url, 'POST', body)

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...secureHeaders,
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return await response.json()
}


/**
 * Requeue an item for reprocessing
 */
export async function requeueItem(itemId: string): Promise<{ id: string; requeued: boolean }> {
  try {
    const url = `${SANKALP_API_BASE}/requeue`
    const body = { id: itemId }
    const secureHeaders = await buildSecureHeaders(url, 'POST', body)

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...secureHeaders,
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Failed to requeue item:', error)
    throw new Error(error instanceof Error ? error.message : 'Unknown error occurred')
  }
}

/**
 * Get audio URL from audio_path
 */
export function getAudioUrl(audioPath: string): string {
  if (!audioPath) return ''

  // If it's already a full URL, return as is
  if (audioPath.startsWith('http://') || audioPath.startsWith('https://')) {
    return audioPath
  }

  // Construct URL based on the path structure
  // Sankalp paths usually start with 'data/audio/'
  if (audioPath.includes('data/audio')) {
    const audioBase = process.env.NEXT_PUBLIC_SANKALP_API_BASE || 'http://localhost:8000'
    const normalizedPath = audioPath.replace(/\\/g, '/')
    const cleanPath = normalizedPath.startsWith('/') ? normalizedPath.slice(1) : normalizedPath
    return `${audioBase}/${cleanPath}`
  }

  // Noopur paths or default fallback
  const audioBase = process.env.NEXT_PUBLIC_AUDIO_BASE_URL || API_BASE
  // Normalize path (replace backslashes with forward slashes)
  const normalizedPath = audioPath.replace(/\\/g, '/')
  // Remove leading slash if present to avoid double slashes
  const cleanPath = normalizedPath.startsWith('/') ? normalizedPath.slice(1) : normalizedPath

  return `${audioBase}/${cleanPath}`
}
