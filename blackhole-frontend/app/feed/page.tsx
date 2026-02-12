'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import BackendStatus from '@/components/BackendStatus'
import { checkBackendHealth, getSankalpFeed, type SankalpItem } from '@/lib/api'
import { getSavedNews, removeSavedNews, SavedNewsItem } from '@/lib/newsStorage'
import { Search, Filter, TrendingUp, Clock, Globe, Newspaper, Trash2, PlayCircle, X } from 'lucide-react'

interface NewsItem {
  id: string
  title: string
  description: string
  url: string
  source: string
  category: string
  imageUrl?: string
  publishedAt: string
  readTime?: string
  isScraped?: boolean
  // Sankalp integration fields
  script?: string
  tone?: string
  audio_path?: string
  priority_score?: number
  trend_score?: number
  audio_duration?: number
  relatedVideos?: Array<{
    title?: string
    url?: string
    thumbnail?: string
    duration?: string
    source?: string
  }>
}

export default function NewsFeed() {
  const router = useRouter()
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [newsItems, setNewsItems] = useState<NewsItem[]>([])
  const [activeVideo, setActiveVideo] = useState<{
    article: NewsItem
    video: NonNullable<NewsItem['relatedVideos']>[number]
  } | null>(null)

  useEffect(() => {
    checkBackend()
    loadNewsFeed()
    const interval = setInterval(checkBackend, 30000)

    // Listen for storage changes to refresh feed when new articles are added
    const handleStorageChange = () => {
      loadNewsFeed()
    }
    window.addEventListener('storage', handleStorageChange)

    // Listen for custom event when articles are saved in same tab
    const handleNewsSaved = (event?: CustomEvent) => {
      console.log('📰 News article saved event received:', event?.detail)
      loadNewsFeed()
    }
    window.addEventListener('newsArticleSaved', handleNewsSaved as EventListener)

    // Also listen for localStorage changes
    const handleStorageUpdate = () => {
      if (localStorage.getItem('newsFeedUpdated')) {
        console.log('📰 Storage update detected, refreshing feed')
        loadNewsFeed()
        localStorage.removeItem('newsFeedUpdated')
      }
    }
    window.addEventListener('storage', handleStorageUpdate)

    // Removed auto-refresh to prevent deleted articles from reappearing

    return () => {
      clearInterval(interval)
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('storage', handleStorageUpdate)
      window.removeEventListener('newsArticleSaved', handleNewsSaved as EventListener)
    }
  }, [])

  const checkBackend = async () => {
    try {
      const isHealthy = await checkBackendHealth()
      setBackendStatus(isHealthy ? 'online' : 'offline')
    } catch (error) {
      setBackendStatus('offline')
    }
  }

  const loadNewsFeed = async () => {
    console.log('🔄 loadNewsFeed called')
    // Load only from server file
    let articles: NewsItem[] = []
    try {
      console.log('📰 Fetching from /api/scraped-news...')
      const response = await fetch('/api/scraped-news')
      console.log('📰 Response status:', response.status)
      if (response.ok) {
        const data = await response.json()
        console.log('📰 Response data:', data)
        if (Array.isArray(data?.data)) {
          articles = mapSavedItemsToNews(data.data as SavedNewsItem[])
          console.log('📰 Mapped articles:', articles.length)
        }
      }
    } catch (error) {
      console.warn('❌ Failed to load articles:', error)
    }

    console.log('📰 Total news loaded:', articles.length)

    // Sample news items - in production, this would come from an API
    const sampleNews: NewsItem[] = [
      {
        id: '1',
        title: 'Breaking: Major AI Breakthrough in Natural Language Processing',
        description: 'Researchers announce significant advancement in AI language models, enabling more accurate and context-aware responses.',
        url: 'https://www.bbc.com/news/technology',
        source: 'BBC News',
        category: 'technology',
        imageUrl: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800',
        publishedAt: '2 hours ago',
        readTime: '5 min read'
      },
      {
        id: '2',
        title: 'Global Climate Summit Reaches Historic Agreement',
        description: 'World leaders commit to ambitious new targets for carbon emission reductions by 2030.',
        url: 'https://www.reuters.com/sustainability/climate-energy/',
        source: 'Reuters',
        category: 'environment',
        imageUrl: 'https://images.unsplash.com/photo-1569163139394-de4798aa62b3?w=800',
        publishedAt: '4 hours ago',
        readTime: '7 min read'
      },
      {
        id: '3',
        title: 'Tech Giants Announce Major Partnership in Quantum Computing',
        description: 'Leading technology companies join forces to accelerate quantum computing research and development.',
        url: 'https://www.theverge.com/tech',
        source: 'The Verge',
        category: 'technology',
        imageUrl: 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800',
        publishedAt: '6 hours ago',
        readTime: '4 min read'
      },
      {
        id: '4',
        title: 'Stock Markets Rally on Positive Economic Data',
        description: 'Major indices see significant gains following better-than-expected employment and inflation figures.',
        url: 'https://www.cnbc.com/world-markets/',
        source: 'CNBC',
        category: 'business',
        imageUrl: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800',
        publishedAt: '8 hours ago',
        readTime: '6 min read'
      },
      {
        id: '5',
        title: 'New Study Reveals Health Benefits of Mediterranean Diet',
        description: 'Long-term research shows significant improvements in cardiovascular health and longevity.',
        url: 'https://www.theguardian.com/science',
        source: 'The Guardian',
        category: 'health',
        imageUrl: 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800',
        publishedAt: '10 hours ago',
        readTime: '5 min read'
      },
      {
        id: '6',
        title: 'Space Agency Announces Plans for Mars Mission',
        description: 'Ambitious new timeline set for crewed mission to Mars, with launch targeted for 2030.',
        url: 'https://www.space.com/news',
        source: 'Space.com',
        category: 'science',
        imageUrl: 'https://images.unsplash.com/photo-1614732414444-096e5f1122d5?w=800',
        publishedAt: '12 hours ago',
        readTime: '8 min read'
      },
      {
        id: '7',
        title: 'Cybersecurity Alert: New Vulnerability Discovered',
        description: 'Security researchers identify critical flaw affecting millions of devices worldwide.',
        url: 'https://www.wired.com/category/security/',
        source: 'Wired',
        category: 'technology',
        imageUrl: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800',
        publishedAt: '14 hours ago',
        readTime: '6 min read'
      },
      {
        id: '8',
        title: 'Entertainment Industry Embraces Virtual Reality',
        description: 'Major studios announce slate of VR experiences, signaling shift in entertainment consumption.',
        url: 'https://variety.com/v/digital/',
        source: 'Variety',
        category: 'entertainment',
        imageUrl: 'https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?w=800',
        publishedAt: '16 hours ago',
        readTime: '5 min read'
      },
      {
        id: '9',
        title: 'Electric Vehicle Sales Surge in Major Markets',
        description: 'Latest figures show record adoption rates as prices decline and charging infrastructure expands.',
        url: 'https://www.cnn.com/business/tech',
        source: 'CNN Business',
        category: 'business',
        imageUrl: 'https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=800',
        publishedAt: '18 hours ago',
        readTime: '4 min read'
      },
      {
        id: '10',
        title: 'Breakthrough in Renewable Energy Storage Technology',
        description: 'Scientists develop new battery technology promising longer lifespan and faster charging.',
        url: 'https://www.scientificamerican.com/energy-sustainability/',
        source: 'Scientific American',
        category: 'science',
        imageUrl: 'https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800',
        publishedAt: '20 hours ago',
        readTime: '7 min read'
      },
      {
        id: '11',
        title: 'Global Education Initiative Reaches 1 Million Students',
        description: 'International program providing free online education celebrates major milestone.',
        url: 'https://www.edweek.org/technology',
        source: 'Education Week',
        category: 'education',
        imageUrl: 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800',
        publishedAt: '22 hours ago',
        readTime: '5 min read'
      },
      {
        id: '12',
        title: 'Artificial Intelligence in Healthcare Shows Promise',
        description: 'AI diagnostic tools demonstrate accuracy comparable to experienced physicians in recent trials.',
        url: 'https://www.healthcareitnews.com/',
        source: 'Healthcare IT News',
        category: 'health',
        imageUrl: 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800',
        publishedAt: '1 day ago',
        readTime: '6 min read'
      }
    ]


    const finalNews = articles.length > 0 ? articles : sampleNews

    // CRITICAL: Sanitize all items to ensure they have valid title and description
    const sanitizedNews = finalNews.map(item => ({
      ...item,
      id: item.id || `item-${Date.now()}-${Math.random()}`,
      title: String(item.title || 'Untitled'),
      description: String(item.description || ''),
      url: String(item.url || item.id || ''),
      category: String(item.category || 'general'),
      source: String(item.source || 'Unknown'),
      publishedAt: String(item.publishedAt || 'Recently'),
    }))

    setNewsItems(sanitizedNews)
  }

  const categories = [
    { id: 'all', name: 'All', icon: Globe },
    { id: 'technology', name: 'Technology', icon: TrendingUp },
    { id: 'business', name: 'Business', icon: Newspaper },
    { id: 'science', name: 'Science', icon: Clock },
    { id: 'health', name: 'Health', icon: Filter },
    { id: 'environment', name: 'Environment', icon: Globe },
    { id: 'entertainment', name: 'Entertainment', icon: Newspaper },
    { id: 'education', name: 'Education', icon: Clock }
  ]

  const filteredNews = newsItems.filter(item => {
    // Safety check: ensure item has required properties
    if (!item || typeof item !== 'object') return false

    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory
    const title = String(item.title || '')
    const description = String(item.description || '')
    const matchesSearch = title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  const handleAnalyzeArticle = (url: string) => {
    // Navigate to home page with the URL pre-filled
    router.push(`/?url=${encodeURIComponent(url)}`)
  }

  const handleNewsCardClick = (news: NewsItem) => {
    if (news.isScraped && news.relatedVideos && news.relatedVideos.length > 0) {
      setActiveVideo({ article: news, video: news.relatedVideos[0] })
      return
    }
    handleAnalyzeArticle(news.url)
  }

  const handleRemoveArticle = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    console.log('🗑️ Delete button clicked for:', id)
    if (confirm('Remove this article permanently?')) {
      try {
        console.log('🗑️ Sending DELETE request to /api/scraped-news?id=' + id)
        const response = await fetch(`/api/scraped-news?id=${id}`, { method: 'DELETE' })
        console.log('🗑️ DELETE response status:', response.status)
        const result = await response.json()
        console.log('🗑️ DELETE response body:', result)
        
        console.log('🗑️ Updating UI state, removing article:', id)
        setNewsItems(prev => {
          const filtered = prev.filter(item => item.id !== id)
          console.log('🗑️ Articles before:', prev.length, 'after:', filtered.length)
          return filtered
        })
        console.log('✅ Article deletion complete')
      } catch (error) {
        console.error('❌ Failed to delete:', error)
      }
    }
  }

  return (
    <div className="min-h-screen">
      <Header backendStatus={backendStatus} />

      <main className="container mx-auto px-6 py-8">
        <BackendStatus status={backendStatus} onRetry={checkBackend} />

        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <Newspaper className="w-10 h-10 text-purple-400" />
            <h1 className="text-4xl font-bold text-white">News Feed</h1>
            {newsItems.filter(item => item.isScraped).length > 0 && (
              <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-semibold">
                {newsItems.filter(item => item.isScraped).length} Scraped
              </span>
            )}
          </div>
          <p className="text-gray-400 text-lg">
            Browse the latest news from trusted sources worldwide. Scraped articles appear first. Click any article to analyze it with AI.
          </p>
          <div className="mt-4">
            <button
              onClick={() => {
                if (confirm('Are you sure you want to clear all saved news data? This cannot be undone.')) {
                  localStorage.removeItem('scraped_news_articles')
                  window.location.reload()
                }
              }}
              className="text-xs text-red-400 hover:text-red-300 underline"
            >
              Clear Saved Data (Fix Errors)
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search news articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-black/40 border border-white/20 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            />
          </div>
        </div>

        {/* Category Filter */}
        <div className="mb-8 overflow-x-auto">
          <div className="flex space-x-3 pb-2">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${selectedCategory === category.id
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  : 'bg-black/40 text-gray-300 hover:bg-black/60 border border-white/10'
                  }`}
              >
                <category.icon className="w-4 h-4" />
                <span>{category.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* News Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredNews.map((news) => (
            <div
              key={news.id}
              className="glass-effect rounded-xl overflow-hidden border border-white/20 hover:border-purple-400/50 transition-all duration-300 hover:scale-105 cursor-pointer group"
              onClick={() => handleNewsCardClick(news)}
            >
              {/* Image */}
              <div className="relative h-48 overflow-hidden bg-gradient-to-br from-purple-900/20 to-pink-900/20">
                {news.imageUrl ? (
                  <>
                    <img
                      src={news.imageUrl}
                      alt={news.title}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                      onError={(e) => {
                        // Fallback to gradient background if image fails to load
                        const target = e.target as HTMLImageElement
                        target.style.display = 'none'
                      }}
                    />
                    <div className="absolute top-3 left-3">
                      <span className="px-3 py-1 bg-purple-500/90 text-white text-xs font-semibold rounded-full backdrop-blur-sm capitalize">
                        {news.category || 'general'}
                      </span>
                    </div>
                  </>
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="text-center p-4">
                      <Newspaper className="w-12 h-12 text-purple-400/50 mx-auto mb-2" />
                      <div className="absolute top-3 left-3">
                        <span className="px-3 py-1 bg-purple-500/90 text-white text-xs font-semibold rounded-full backdrop-blur-sm capitalize">
                          {news.category || 'general'}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-purple-400 font-medium">{news.source}</span>
                    <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs font-semibold rounded-full capitalize">
                      {news.category || 'general'}
                    </span>
                    {/* Sankalp scores */}
                    {news.priority_score !== undefined && (
                      <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs font-semibold rounded-full" title="Priority Score">
                        ⭐ {Math.round(news.priority_score * 100)}%
                      </span>
                    )}
                    {news.trend_score !== undefined && news.trend_score > 0.5 && (
                      <span className="px-2 py-0.5 bg-orange-500/20 text-orange-400 text-xs font-semibold rounded-full flex items-center" title="Trending">
                        <TrendingUp className="w-3 h-3 mr-1" />
                        {Math.round(news.trend_score * 100)}%
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500">{news.publishedAt}</span>
                    {news.isScraped && (
                      <button
                        onClick={(e) => handleRemoveArticle(news.id, e)}
                        className="p-1 hover:bg-red-500/20 rounded transition-colors"
                        title="Remove from feed"
                      >
                        <Trash2 className="w-3 h-3 text-red-400" />
                      </button>
                    )}
                  </div>
                </div>

                <h3 className="text-lg font-bold text-white mb-2 line-clamp-2 group-hover:text-purple-300 transition-colors">
                  {news.title}
                </h3>

                <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                  {news.description}
                </p>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-xs text-gray-500 flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {news.readTime || (news.audio_duration ? `${Math.ceil(news.audio_duration)}s` : '')}
                    </span>
                    {news.tone && (
                      <span className="text-xs text-gray-500 capitalize" title="Tone">
                        🎭 {news.tone}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-3">
                    {news.audio_path && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          // Open audio player modal or play audio
                          console.log('Play audio:', news.audio_path)
                        }}
                        className="text-sm text-green-400 hover:text-green-300 font-semibold flex items-center group/btn"
                        title="Play Audio"
                      >
                        <PlayCircle className="w-4 h-4 mr-1" />
                        Audio
                      </button>
                    )}
                    {news.isScraped && news.relatedVideos?.length ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleNewsCardClick(news)
                        }}
                        className="text-sm text-pink-400 hover:text-pink-300 font-semibold flex items-center group/btn"
                      >
                        <PlayCircle className="w-4 h-4 mr-1" />
                        Watch Video
                        <span className="ml-1 group-hover/btn:translate-x-1 transition-transform">▶</span>
                      </button>
                    ) : !news.audio_path && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleAnalyzeArticle(news.url)
                        }}
                        className="text-sm text-purple-400 hover:text-purple-300 font-semibold flex items-center group/btn"
                      >
                        Analyze with AI
                        <span className="ml-1 group-hover/btn:translate-x-1 transition-transform">→</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredNews.length === 0 && (
          <div className="text-center py-16">
            <Search className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">No articles found</h3>
            <p className="text-gray-500">Try adjusting your search or filter criteria</p>
          </div>
        )}

        {/* Stats Footer */}
        <div className="mt-12 glass-effect rounded-xl p-6 border border-white/20">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-3xl font-bold text-purple-400 mb-2">{newsItems.length}</div>
              <div className="text-gray-400">Total Articles</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-400 mb-2">
                {newsItems.filter(item => item.isScraped).length}
              </div>
              <div className="text-gray-400">Scraped Articles</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-pink-400 mb-2">{categories.length - 1}</div>
              <div className="text-gray-400">Categories</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-400 mb-2">24/7</div>
              <div className="text-gray-400">Live Updates</div>
            </div>
          </div>
        </div>
      </main>

      {/* Video Modal */}
      {activeVideo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-gray-900 rounded-2xl shadow-2xl w-full max-w-4xl border border-white/10">
            <div className="flex items-center justify-between border-b border-white/10 px-6 py-4">
              <div>
                <p className="text-sm text-purple-300 uppercase tracking-wide">Related Video</p>
                <h3 className="text-xl font-bold text-white">{activeVideo.article.title}</h3>
                <p className="text-gray-400 text-sm">
                  Source: {activeVideo.video.source || 'YouTube'}
                </p>
              </div>
              <button
                className="p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
                onClick={() => setActiveVideo(null)}
              >
                <X className="w-5 h-5 text-white" />
              </button>
            </div>

            <div className="p-6">
              <div className="relative w-full pb-[56.25%] rounded-xl overflow-hidden border border-white/10">
                {getVideoEmbedUrl(activeVideo.video.url) ? (
                  <iframe
                    src={getVideoEmbedUrl(activeVideo.video.url)!}
                    className="absolute inset-0 w-full h-full"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    title={activeVideo.video.title || 'Related video'}
                  />
                ) : (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/50 text-white space-y-4">
                    <p className="text-center px-6">
                      Unable to embed this video. Open it directly to view.
                    </p>
                    <a
                      href={activeVideo.video.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-purple-500 rounded-full font-semibold hover:bg-purple-600 transition-colors"
                    >
                      Open Video
                    </a>
                  </div>
                )}
              </div>

              <div className="mt-6 flex flex-wrap gap-3 justify-between">
                <div className="text-sm text-gray-400 flex flex-col">
                  {activeVideo.video.title && (
                    <span className="text-white font-semibold">{activeVideo.video.title}</span>
                  )}
                  {activeVideo.video.duration && <span>Duration: {activeVideo.video.duration}</span>}
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => handleAnalyzeArticle(activeVideo.article.url)}
                    className="px-4 py-2 bg-purple-500/20 text-purple-300 rounded-full border border-purple-400/50 hover:bg-purple-500/30 transition-colors"
                  >
                    Analyze Article
                  </button>
                  <a
                    href={activeVideo.video.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 bg-white/10 text-white rounded-full border border-white/20 hover:bg-white/20 transition-colors"
                  >
                    Open on {activeVideo.video.source || 'YouTube'}
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function getVideoEmbedUrl(url?: string) {
  if (!url) return null
  const youtubeMatch = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([A-Za-z0-9_-]+)/)
  if (youtubeMatch) {
    return `https://www.youtube.com/embed/${youtubeMatch[1]}?autoplay=1`
  }
  return null
}

function extractSourceFromUrl(url: string): string {
  try {
    const urlObj = new URL(url)
    const hostname = urlObj.hostname
    const source = hostname
      .replace(/^www\./, '')
      .split('.')
      .slice(0, -1)
      .join(' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
    return source || 'Unknown Source'
  } catch {
    return 'Unknown Source'
  }
}

function formatTimeAgo(timestamp: string): string {
  try {
    const date = new Date(timestamp)
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (seconds < 60) return 'Just now'
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`
    if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`

    return date.toLocaleDateString()
  } catch {
    return 'Recently'
  }
}

function mapSavedItemsToNews(items: any[]): NewsItem[] {
  return items.map(item => ({
    id: item.id || `item-${Date.now()}-${Math.random()}`,
    title: typeof item.title === 'string' ? item.title : (item.script?.substring(0, 100) || 'Untitled'),
    description: typeof item.script === 'string' ? item.script :
      (typeof item.description === 'string' ? item.description :
        (typeof item.description === 'object' && (item.description as any)?.text) ? (item.description as any).text :
          'No description available'),
    url: String(item.url || item.id || ''), // Use id as URL fallback, ensure it's a string
    source: typeof item.source === 'string' ? item.source : extractSourceFromUrl(String(item.id || '')),
    category: typeof item.category === 'string' ? item.category : 'general',
    imageUrl: item.imageUrl,
    publishedAt: typeof item.publishedAt === 'string' ? item.publishedAt : 'Recently',
    readTime: item.audio_duration ? `${Math.ceil(item.audio_duration)}s audio` : (typeof item.readTime === 'string' ? item.readTime : undefined),
    isScraped: true,
    // Sankalp fields
    script: typeof item.script === 'string' ? item.script : '',
    tone: typeof item.tone === 'string' ? item.tone : '',
    audio_path: typeof item.audio_path === 'string' ? item.audio_path : '',
    priority_score: typeof item.priority_score === 'number' ? item.priority_score : 0,
    trend_score: typeof item.trend_score === 'number' ? item.trend_score : 0,
    audio_duration: typeof item.audio_duration === 'number' ? item.audio_duration : 0,
    relatedVideos: item.relatedVideos
  }))
}

function mergeByUrl(items: NewsItem[]): NewsItem[] {
  const seen = new Set<string>()
  const merged: NewsItem[] = []
  for (const item of items) {
    const key = item.url || item.id
    if (!seen.has(key)) {
      seen.add(key)
      merged.push(item)
    }
  }
  return merged
}


