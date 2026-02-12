'use client'

import { useState, useEffect } from 'react'
import { Radio, TrendingUp, Clock, Eye, Play } from 'lucide-react'
import PipelineViewer from './PipelineViewer'

interface NewsItem {
  id: string
  title: string
  source: string
  category: string
  status: string
  timestamp: string
  summary?: string
  insights?: any
  pipeline: any
}

interface LiveFeedViewerProps {
  items: NewsItem[]
  onItemSelect?: (item: NewsItem) => void
  selectedId?: string
}

export default function LiveFeedViewer({ items, onItemSelect, selectedId }: LiveFeedViewerProps) {
  const [liveItems, setLiveItems] = useState<NewsItem[]>(items)
  const [filter, setFilter] = useState<'all' | 'completed' | 'processing'>('all')

  useEffect(() => {
    setLiveItems(items)
  }, [items])

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { color: string; label: string; icon: string }> = {
      completed: { color: 'bg-green-500/20 text-green-400 border-green-500/50', label: 'Completed', icon: '✓' },
      processing: { color: 'bg-purple-500/20 text-purple-400 border-purple-500/50', label: 'Processing', icon: '⚡' },
      pending: { color: 'bg-gray-500/20 text-gray-400 border-gray-500/50', label: 'Pending', icon: '○' },
      flagged: { color: 'bg-red-500/20 text-red-400 border-red-500/50', label: 'Flagged', icon: '🚩' }
    }
    return badges[status] || badges.pending
  }

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      technology: 'bg-blue-500/20 text-blue-400',
      business: 'bg-green-500/20 text-green-400',
      science: 'bg-purple-500/20 text-purple-400',
      health: 'bg-pink-500/20 text-pink-400',
      environment: 'bg-teal-500/20 text-teal-400',
      entertainment: 'bg-yellow-500/20 text-yellow-400'
    }
    return colors[category] || 'bg-gray-500/20 text-gray-400'
  }

  const getTimeAgo = (timestamp: string) => {
    const now = new Date()
    const then = new Date(timestamp)
    const seconds = Math.floor((now.getTime() - then.getTime()) / 1000)
    
    if (seconds < 60) return `${seconds}s ago`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
    return `${Math.floor(seconds / 86400)}d ago`
  }

  const filteredItems = liveItems.filter(item => {
    if (filter === 'all') return true
    return item.status === filter
  })

  return (
    <div className="glass-effect rounded-xl p-6 border border-white/20">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center mb-1">
            <Radio className="w-5 h-5 mr-2 text-purple-400" />
            Live News Feed
            <span className="ml-2 w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
          </h3>
          <p className="text-sm text-gray-400">Real-time processing updates</p>
        </div>

        {/* Stats */}
        <div className="flex items-center space-x-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">{liveItems.length}</div>
            <div className="text-xs text-gray-500">Total</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">
              {liveItems.filter(i => i.status === 'completed').length}
            </div>
            <div className="text-xs text-gray-500">Ready</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex space-x-2 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            filter === 'all'
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
              : 'bg-black/30 text-gray-400 hover:bg-black/50'
          }`}
        >
          All ({liveItems.length})
        </button>
        <button
          onClick={() => setFilter('completed')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            filter === 'completed'
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
              : 'bg-black/30 text-gray-400 hover:bg-black/50'
          }`}
        >
          Completed ({liveItems.filter(i => i.status === 'completed').length})
        </button>
        <button
          onClick={() => setFilter('processing')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            filter === 'processing'
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
              : 'bg-black/30 text-gray-400 hover:bg-black/50'
          }`}
        >
          Processing ({liveItems.filter(i => i.status === 'processing').length})
        </button>
      </div>

      {/* Feed Items */}
      <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
        {filteredItems.map((item) => {
          const statusBadge = getStatusBadge(item.status)
          const isSelected = selectedId === item.id

          return (
            <div
              key={item.id}
              onClick={() => onItemSelect && onItemSelect(item)}
              className={`border-2 rounded-lg p-4 transition-all cursor-pointer ${
                isSelected
                  ? 'border-purple-400 bg-purple-400/10'
                  : 'border-white/10 bg-black/20 hover:border-white/30 hover:bg-black/30'
              }`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${getCategoryColor(item.category)}`}>
                      {item.category}
                    </span>
                    <span className={`px-2 py-0.5 rounded-full border text-xs font-semibold flex items-center space-x-1 ${statusBadge.color}`}>
                      <span>{statusBadge.icon}</span>
                      <span>{statusBadge.label}</span>
                    </span>
                  </div>
                  <h4 className="text-sm font-semibold text-white line-clamp-2 mb-1">
                    {item.title}
                  </h4>
                  <div className="flex items-center space-x-3 text-xs text-gray-500">
                    <span className="flex items-center">
                      <TrendingUp className="w-3 h-3 mr-1" />
                      {item.source}
                    </span>
                    <span className="flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {getTimeAgo(item.timestamp)}
                    </span>
                  </div>
                </div>

                {item.status === 'completed' && (
                  <button className="ml-3 p-2 bg-purple-500/20 hover:bg-purple-500/30 rounded-lg transition-colors">
                    <Play className="w-4 h-4 text-purple-400" />
                  </button>
                )}
              </div>

              {/* Pipeline Preview */}
              {item.pipeline && (
                <div className="mt-3 pt-3 border-t border-white/10">
                  <PipelineViewer pipeline={item.pipeline} compact={true} />
                </div>
              )}

              {/* Summary Preview */}
              {item.summary && isSelected && (
                <div className="mt-3 p-3 bg-black/30 rounded-lg">
                  <p className="text-xs text-gray-400 line-clamp-2">{item.summary}</p>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Empty State */}
      {filteredItems.length === 0 && (
        <div className="text-center py-12">
          <Eye className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400">No items in this category</p>
          <p className="text-sm text-gray-500 mt-1">Check back soon for updates</p>
        </div>
      )}
    </div>
  )
}

