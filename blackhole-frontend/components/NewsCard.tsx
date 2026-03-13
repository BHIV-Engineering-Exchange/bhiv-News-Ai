'use client'

import { Clock } from 'lucide-react'

interface NewsCardProps {
  title: string
  description: string
  source: string
  category: string
  publishedAt: string
  readTime?: string
  imageUrl?: string
  onClick: () => void
}

export default function NewsCard({
  title,
  description,
  source,
  category,
  publishedAt,
  readTime,
  imageUrl,
  onClick
}: NewsCardProps) {
  return (
    <div
      className="glass-effect rounded-xl overflow-hidden border border-white/20 hover:border-purple-400/50 transition-all duration-300 hover:scale-105 cursor-pointer group"
      onClick={onClick}
    >
      {/* Image */}
      {imageUrl && (
        <div className="relative h-48 overflow-hidden">
          <img
            src={imageUrl}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          />
          <div className="absolute top-3 left-3">
            <span className="px-3 py-1 bg-purple-500/90 text-white text-xs font-semibold rounded-full backdrop-blur-sm capitalize">
              {category}
            </span>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="p-5">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-purple-400 font-medium">{source}</span>
          <span className="text-xs text-gray-500">{publishedAt}</span>
        </div>

        <h3 className="text-lg font-bold text-white mb-2 line-clamp-2 group-hover:text-purple-300 transition-colors">
          {title}
        </h3>

        <p className="text-gray-400 text-sm mb-4 line-clamp-3">
          {description}
        </p>

        <div className="flex items-center justify-between">
          {readTime && (
            <span className="text-xs text-gray-500 flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              {readTime}
            </span>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation()
              onClick()
            }}
            className="text-sm text-purple-400 hover:text-purple-300 font-semibold flex items-center group/btn"
          >
            Analyze with AI
            <span className="ml-1 group-hover/btn:translate-x-1 transition-transform">→</span>
          </button>
        </div>
      </div>
    </div>
  )
}

