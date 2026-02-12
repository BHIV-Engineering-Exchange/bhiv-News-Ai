'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/Header'
import BackendStatus from '@/components/BackendStatus'
import LiveFeedViewer from '@/components/LiveFeedViewer'
import TTSPlayer from '@/components/TTSPlayer'
import PipelineViewer from '@/components/PipelineViewer'
import AIInsights from '@/components/AIInsights'
import FeedbackPanel from '@/components/FeedbackPanel'
import { checkBackendHealth, getDetailedPipelineStatus } from '@/lib/api'
import apiService from '@/services/api'
import { Filter, LayoutGrid } from 'lucide-react'
import { useWebSocket } from '@/hooks/useWebSocket'

export default function LiveDashboard() {
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking')
  const [newsItems, setNewsItems] = useState<any[]>([])
  const [selectedItem, setSelectedItem] = useState<any | null>(null)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [categories, setCategories] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // WebSocket Integration
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:3002'
  const { lastMessage } = useWebSocket(wsUrl)

  useEffect(() => {
    if (lastMessage) {
      const { type, data } = lastMessage
      console.log('📡 Live Dashboard WS Message:', type, data)

      if (type === 'bhiv_status_update' || type === 'news_published') {
        const newsId = data.newsItemId || data.id

        // Update the list
        setNewsItems(prevItems => prevItems.map(item => {
          if (item.id === newsId || item._id === newsId) {
            return {
              ...item,
              status: data.status || item.status,
              // If we have more detailed info, update it
              ...data.article
            }
          }
          return item
        }))

        // Update selected item if it's the one that changed
        if (selectedItem && (selectedItem.id === newsId || selectedItem._id === newsId)) {
          // If it's a major update, we might want to refetch or just patch
          setSelectedItem((prev: any) => ({
            ...prev,
            status: data.status || prev.status,
            ...data.article
          }))

          // Also fetch detailed pipeline status to update PipelineViewer
          fetchDetailedStatus(newsId)
        }
      }
    }
  }, [lastMessage])

  const fetchDetailedStatus = async (id: string) => {
    const status = await getDetailedPipelineStatus(id)
    if (status && status.success) {
      setSelectedItem((prev: any) => {
        if (prev && (prev.id === id || prev._id === id)) {
          return { ...prev, pipeline: status.pipeline }
        }
        return prev
      })
    }
  }

  useEffect(() => {
    checkBackend()
    loadCategories()
    loadNews()

    const interval = setInterval(checkBackend, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    loadNews()
  }, [selectedCategory])

  const checkBackend = async () => {
    try {
      const isHealthy = await checkBackendHealth()
      setBackendStatus(isHealthy ? 'online' : 'offline')
    } catch (error) {
      setBackendStatus('offline')
    }
  }

  const loadCategories = async () => {
    try {
      const result = await apiService.getCategories()
      if (result.success) {
        setCategories(result.data)
      }
    } catch (error) {
      console.error('Failed to load categories:', error)
    }
  }

  const loadNews = async () => {
    setIsLoading(true)
    try {
      const result = await apiService.getNews({
        category: selectedCategory,
        limit: 20
      })

      if (result.success) {
        setNewsItems(result.data)
        // Auto-select first item if none selected
        if (!selectedItem && result.data.length > 0) {
          setSelectedItem(result.data[0])
        }
      }
    } catch (error) {
      console.error('Failed to load news:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFeedbackSubmit = async (type: string, response?: any) => {
    console.log('📝 Feedback submitted:', type, response)

    // Update the selected item immediately with the Reward or new stats if provided
    if (selectedItem && response) {
      setSelectedItem((prev: any) => ({
        ...prev,
        feedback: {
          ...prev.feedback,
          likes: type === 'like' ? (prev.feedback?.likes || 0) + 1 : (prev.feedback?.likes || 0),
          skips: type === 'skip' ? (prev.feedback?.skips || 0) + 1 : (prev.feedback?.skips || 0),
          flags: type === 'flag' ? (prev.feedback?.flags || 0) + 1 : (prev.feedback?.flags || 0),
        },
        // Update reward/score if returned by RL loop
        priority_score: response.reward !== undefined ? response.reward : prev.priority_score
      }))
    }
  }

  const handleItemSelect = async (item: any) => {
    setSelectedItem(item)
    // Fetch full details if item is from a list (which might be partial)
    try {
      const fullItem = await apiService.getProcessedNews(item.id)
      if (fullItem && fullItem.success) {
        setSelectedItem(fullItem.data)
      }
    } catch (error) {
      console.error('Failed to fetch full news details:', error)
    }
  }

  return (
    <div className="min-h-screen">
      <Header backendStatus={backendStatus} />

      <main className="container mx-auto px-6 py-8">
        <BackendStatus status={backendStatus} onRetry={checkBackend} />

        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <LayoutGrid className="w-10 h-10 text-purple-400" />
                <h1 className="text-4xl font-bold text-white">Live Dashboard</h1>
                <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-semibold flex items-center">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></span>
                  Live
                </span>
              </div>
              <p className="text-gray-400 text-lg">
                Real-time AI-powered news processing pipeline
              </p>
            </div>
          </div>
        </div>

        {/* Category Filter */}
        <div className="mb-6">
          <div className="flex items-center space-x-2 mb-3">
            <Filter className="w-5 h-5 text-gray-400" />
            <span className="text-sm text-gray-400 font-medium">Filter by Category</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${selectedCategory === category.id
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  : 'bg-black/40 text-gray-300 hover:bg-black/60 border border-white/10'
                  }`}
              >
                {category.name}
                <span className="ml-2 text-xs opacity-70">({category.count})</span>
              </button>
            ))}
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Left Column - Live Feed */}
          <div className="xl:col-span-1">
            <LiveFeedViewer
              items={newsItems}
              onItemSelect={handleItemSelect}
              selectedId={selectedItem?.id}
            />
          </div>

          {/* Right Column - Details */}
          <div className="xl:col-span-2 space-y-6">
            {selectedItem ? (
              <>
                {/* Article Header */}
                <div className="glass-effect rounded-xl p-6 border border-white/20">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-3">
                        <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-xs font-semibold">
                          {selectedItem.category}
                        </span>
                        <span className="text-sm text-gray-500">{selectedItem.source}</span>
                      </div>
                      <h2 className="text-2xl font-bold text-white mb-3">
                        {selectedItem.title}
                      </h2>
                      {selectedItem.summary && (
                        <p className="text-gray-300 leading-relaxed">
                          {selectedItem.summary}
                        </p>
                      )}
                    </div>
                  </div>

                  {selectedItem.url && (
                    <a
                      href={selectedItem.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
                    >
                      View Original Article →
                    </a>
                  )}
                </div>

                {/* Pipeline Viewer */}
                {selectedItem.pipeline && (
                  <PipelineViewer pipeline={selectedItem.pipeline} />
                )}

                {/* TTS Player */}
                {selectedItem.audioUrl && (
                  <TTSPlayer
                    audioUrl={selectedItem.audioUrl}
                    title={selectedItem.title}
                    duration={selectedItem.audioDuration}
                    newsId={selectedItem.id}
                  />
                )}

                {/* AI Insights */}
                {selectedItem.insights && (
                  <AIInsights insights={selectedItem.insights} />
                )}

                {/* Feedback Panel */}
                <FeedbackPanel
                  newsId={selectedItem.id}
                  currentFeedback={selectedItem.feedback}
                  onFeedbackSubmit={handleFeedbackSubmit}
                />
              </>
            ) : (
              <div className="glass-effect rounded-xl p-12 border border-white/20 text-center">
                <LayoutGrid className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-400 mb-2">
                  Select a news item
                </h3>
                <p className="text-gray-500">
                  Choose an article from the feed to view details, insights, and controls
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="glass-effect rounded-xl p-8 text-center">
              <div className="w-12 h-12 border-4 border-purple-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-white font-semibold">Loading news items...</p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

