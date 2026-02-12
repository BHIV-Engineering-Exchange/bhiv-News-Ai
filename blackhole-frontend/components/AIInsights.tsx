'use client'

import { TrendingUp, Shield, Hash, Users, AlertTriangle } from 'lucide-react'

interface InsightsData {
  sentiment: string
  tone: string
  category: string
  credibilityScore: number
  biasScore: number
  keywords: string[]
  entities: string[]
}

interface AIInsightsProps {
  insights: InsightsData
}

export default function AIInsights({ insights }: AIInsightsProps) {
  const getSentimentColor = (sentiment: string) => {
    const colors: Record<string, string> = {
      positive: 'text-green-400 bg-green-400/20',
      negative: 'text-red-400 bg-red-400/20',
      neutral: 'text-gray-400 bg-gray-400/20',
      excited: 'text-purple-400 bg-purple-400/20',
      concerned: 'text-orange-400 bg-orange-400/20',
      hopeful: 'text-blue-400 bg-blue-400/20'
    }
    return colors[sentiment.toLowerCase()] || colors.neutral
  }

  const getToneIcon = (tone: string) => {
    const icons: Record<string, string> = {
      informative: '📚',
      urgent: '⚡',
      serious: '🎯',
      optimistic: '✨',
      scientific: '🔬',
      casual: '💬'
    }
    return icons[tone.toLowerCase()] || '📝'
  }

  const getCredibilityLevel = (score: number) => {
    if (score >= 0.9) return { label: 'Very High', color: 'text-green-400', bgColor: 'bg-green-400' }
    if (score >= 0.75) return { label: 'High', color: 'text-blue-400', bgColor: 'bg-blue-400' }
    if (score >= 0.6) return { label: 'Medium', color: 'text-yellow-400', bgColor: 'bg-yellow-400' }
    return { label: 'Low', color: 'text-red-400', bgColor: 'bg-red-400' }
  }

  const getBiasLevel = (score: number) => {
    if (score <= 0.1) return { label: 'Minimal', color: 'text-green-400' }
    if (score <= 0.25) return { label: 'Low', color: 'text-blue-400' }
    if (score <= 0.5) return { label: 'Moderate', color: 'text-yellow-400' }
    return { label: 'High', color: 'text-red-400' }
  }

  const credibility = getCredibilityLevel(insights.credibilityScore)
  const bias = getBiasLevel(insights.biasScore)

  return (
    <div className="glass-effect rounded-xl p-6 border border-white/20">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white flex items-center mb-1">
          <TrendingUp className="w-5 h-5 mr-2 text-purple-400" />
          AI Insights & Analysis
        </h3>
        <p className="text-sm text-gray-400">Automated content analysis results</p>
      </div>

      {/* Main Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Sentiment */}
        <div className="bg-black/30 rounded-lg p-4">
          <div className="text-xs text-gray-500 mb-2">Sentiment</div>
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${getSentimentColor(insights.sentiment)}`}>
            {insights.sentiment.charAt(0).toUpperCase() + insights.sentiment.slice(1)}
          </div>
        </div>

        {/* Tone */}
        <div className="bg-black/30 rounded-lg p-4">
          <div className="text-xs text-gray-500 mb-2">Tone</div>
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{getToneIcon(insights.tone)}</span>
            <span className="text-sm font-semibold text-white capitalize">{insights.tone}</span>
          </div>
        </div>
      </div>

      {/* Credibility Score */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-400">Credibility Score</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`text-sm font-semibold ${credibility.color}`}>{credibility.label}</span>
            <span className="text-sm text-white font-bold">{Math.round(insights.credibilityScore * 100)}%</span>
          </div>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
          <div
            className={`h-full ${credibility.bgColor} rounded-full transition-all duration-500`}
            style={{ width: `${insights.credibilityScore * 100}%` }}
          />
        </div>
      </div>

      {/* Bias Score */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-400">Bias Detection</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`text-sm font-semibold ${bias.color}`}>{bias.label}</span>
            <span className="text-sm text-white font-bold">{Math.round(insights.biasScore * 100)}%</span>
          </div>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${
              insights.biasScore <= 0.1 ? 'bg-green-400' :
              insights.biasScore <= 0.25 ? 'bg-blue-400' :
              insights.biasScore <= 0.5 ? 'bg-yellow-400' :
              'bg-red-400'
            } rounded-full`}
            style={{ width: `${insights.biasScore * 100}%` }}
          />
        </div>
      </div>

      {/* Category */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-2">
          <Hash className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400">Category</span>
        </div>
        <div className="inline-flex items-center px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-sm font-semibold">
          {insights.category.charAt(0).toUpperCase() + insights.category.slice(1)}
        </div>
      </div>

      {/* Keywords */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-3">
          <Hash className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400">Key Topics</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {insights.keywords.map((keyword, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-medium"
            >
              {keyword}
            </span>
          ))}
        </div>
      </div>

      {/* Entities */}
      <div>
        <div className="flex items-center space-x-2 mb-3">
          <Users className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400">Mentioned Entities</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {insights.entities.map((entity, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-pink-500/20 text-pink-400 rounded-full text-xs font-medium"
            >
              {entity}
            </span>
          ))}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 pt-6 border-t border-white/10">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-lg font-bold text-purple-400">{insights.keywords.length}</div>
            <div className="text-xs text-gray-500">Keywords</div>
          </div>
          <div>
            <div className="text-lg font-bold text-pink-400">{insights.entities.length}</div>
            <div className="text-xs text-gray-500">Entities</div>
          </div>
          <div>
            <div className={`text-lg font-bold ${credibility.color}`}>
              {Math.round(insights.credibilityScore * 100)}
            </div>
            <div className="text-xs text-gray-500">Trust Score</div>
          </div>
        </div>
      </div>
    </div>
  )
}

