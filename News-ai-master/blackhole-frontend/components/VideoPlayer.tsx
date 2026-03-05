'use client'

import { useState, useEffect } from 'react'
import { Play, Pause, SkipForward, SkipBack, Volume2, Maximize, ExternalLink, AlertCircle } from 'lucide-react'

interface Video {
  title: string
  url: string
  thumbnail?: string
  duration?: string
  source: string
  video_id?: string
  mock_data?: boolean
  demo_video?: boolean
  embed_url?: string
  working_video?: boolean
  relevance_score?: number
}

interface VideoPlayerProps {
  videos: Video[]
  title?: string
}

export default function VideoPlayer({ videos, title = "Related Videos" }: VideoPlayerProps) {
  const [currentVideo, setCurrentVideo] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [videoError, setVideoError] = useState<string | null>(null)
  const [isValidating, setIsValidating] = useState(false)

  // Use default videos if none provided
  const defaultVideos: Video[] = [
    {
      title: "AI News Analysis Demo - Blackhole Infiverse LLP",
      url: "https://www.youtube.com/embed/dQw4w9WgXcQ",
      thumbnail: "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      duration: "3:24",
      source: "Demo"
    },
    {
      title: "Advanced Web Scraping Techniques",
      url: "https://www.youtube.com/embed/dQw4w9WgXcQ",
      thumbnail: "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      duration: "5:17",
      source: "Demo"
    },
    {
      title: "News Authenticity Verification",
      url: "https://www.youtube.com/embed/dQw4w9WgXcQ",
      thumbnail: "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      duration: "4:52",
      source: "Demo"
    }
  ]

  const videoList = videos.length > 0 ? videos : defaultVideos
  const currentVideoData = videoList[currentVideo]

  useEffect(() => {
    // Simulate video progress
    let interval: NodeJS.Timeout
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentTime(prev => prev + 1)
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isPlaying])

  const togglePlay = () => {
    setIsPlaying(!isPlaying)
  }

  const nextVideo = () => {
    setCurrentVideo((prev) => (prev + 1) % videoList.length)
    setCurrentTime(0)
    setIsPlaying(true)
  }

  const prevVideo = () => {
    setCurrentVideo((prev) => (prev - 1 + videoList.length) % videoList.length)
    setCurrentTime(0)
    setIsPlaying(true)
  }

  const selectVideo = (index: number) => {
    setCurrentVideo(index)
    setCurrentTime(0)
    setIsPlaying(false)
    setVideoError(null)
    // DISABLED: Video validation to prevent API spam
    // validateCurrentVideo(videoList[index])
  }

  const validateCurrentVideo = async (video: Video) => {
    // DISABLED: Video validation is causing excessive API calls
    // Just return without validation to prevent the loop
    return
  }

  const openInNewTab = () => {
    if (currentVideoData.url.includes('youtube.com') || currentVideoData.url.includes('youtu.be')) {
      const videoId = currentVideoData.url.split('/').pop()?.split('?')[0]
      window.open(`https://www.youtube.com/watch?v=${videoId}`, '_blank')
    } else {
      window.open(currentVideoData.url, '_blank')
    }
  }

  // DISABLED: Video validation to prevent API spam
  // useEffect(() => {
  //   if (videoList.length > 0) {
  //     validateCurrentVideo(videoList[0])
  //   }
  // }, [videoList])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Create a fallback thumbnail that won't fail to load
  const getFallbackThumbnail = (title: string) => {
    return `data:image/svg+xml;base64,${btoa(`
      <svg width="400" height="225" xmlns="http://www.w3.org/2000/svg">
        <rect width="400" height="225" fill="#1a1a1a"/>
        <text x="200" y="112" font-family="Arial, sans-serif" font-size="16" fill="#ffffff" text-anchor="middle" dominant-baseline="middle">
          ${title.substring(0, 30)}${title.length > 30 ? '...' : ''}
        </text>
      </svg>
    `)}`
  }

  return (
    <div className="glass-effect rounded-2xl p-6 border border-white/20 sticky top-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-white">{title}</h3>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          <span className="text-xs text-gray-400">Live</span>
        </div>
      </div>

      {/* Main Video Player */}
      <div className="relative mb-6">
        <div className="aspect-video bg-black rounded-lg overflow-hidden relative group">
          {/* Error Message */}
          {videoError && (
            <div className="absolute inset-0 bg-red-900/80 flex items-center justify-center z-20">
              <div className="text-center p-6">
                <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                <h4 className="text-white font-medium mb-2">Video Unavailable</h4>
                <p className="text-red-200 text-sm mb-4">{videoError}</p>
                <button
                  onClick={openInNewTab}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm transition-colors"
                >
                  Try Opening in YouTube
                </button>
              </div>
            </div>
          )}

          {/* Validation Loading */}
          {isValidating && (
            <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-10">
              <div className="text-center">
                <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                <p className="text-white text-sm">Checking video availability...</p>
              </div>
            </div>
          )}

          {/* Video Status Badges */}
          <div className="absolute top-4 left-4 z-10 flex flex-col space-y-2">
            {currentVideoData.working_video && (
              <div className="bg-green-600/90 text-white px-3 py-1 rounded-full text-xs">
                ✓ Working Video
              </div>
            )}
            {currentVideoData.demo_video && (
              <div className="bg-yellow-600/90 text-white px-3 py-1 rounded-full text-xs">
                Demo Video
              </div>
            )}
            {currentVideoData.relevance_score && currentVideoData.relevance_score < 0.7 && (
              <div className="bg-blue-600/90 text-white px-3 py-1 rounded-full text-xs">
                Related Content
              </div>
            )}
          </div>

          {/* Video Thumbnail/Iframe */}
          {currentVideoData.url.includes('youtube.com') || currentVideoData.url.includes('embed') ? (
            <iframe
              src={currentVideoData.embed_url || currentVideoData.url}
              title={currentVideoData.title}
              className="w-full h-full"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          ) : (
            <>
              <img
                src={currentVideoData.thumbnail || getFallbackThumbnail(currentVideoData.title)}
                alt={currentVideoData.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  const target = e.target as HTMLImageElement
                  target.src = getFallbackThumbnail(currentVideoData.title)
                }}
              />

              {/* Play Overlay */}
              <div className="absolute inset-0 bg-black/50 flex items-center justify-center group-hover:bg-black/30 transition-colors">
                <button
                  onClick={togglePlay}
                  className="w-20 h-20 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110"
                  disabled={!!videoError}
                >
                  {isPlaying ? (
                    <Pause className="w-10 h-10 text-white" />
                  ) : (
                    <Play className="w-10 h-10 text-white ml-1" />
                  )}
                </button>
              </div>
            </>
          )}

          {/* Video Info Overlay */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
            <h4 className="text-white font-medium text-sm mb-2 line-clamp-2">
              {currentVideoData.title}
            </h4>
            <div className="flex items-center justify-between text-xs text-gray-300">
              <span>{currentVideoData.source}</span>
              <div className="flex items-center space-x-2">
                <span>{currentVideoData.duration}</span>
                <button
                  onClick={openInNewTab}
                  className="p-1 hover:bg-white/20 rounded transition-colors"
                  title="Open in new tab"
                >
                  <ExternalLink className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
            <span>{formatTime(currentTime)}</span>
            <span>{currentVideoData.duration || "0:00"}</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-1">
            <div 
              className="bg-gradient-to-r from-purple-500 to-pink-500 h-1 rounded-full transition-all duration-300"
              style={{ width: isPlaying ? '45%' : '20%' }}
            ></div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center space-x-4 mb-6">
        <button
          onClick={prevVideo}
          className="p-3 hover:bg-white/10 rounded-full transition-colors"
          disabled={videoList.length <= 1}
        >
          <SkipBack className="w-5 h-5 text-gray-400 hover:text-white" />
        </button>
        
        <button
          onClick={togglePlay}
          className="p-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-full transition-all duration-200 hover:scale-105"
        >
          {isPlaying ? (
            <Pause className="w-6 h-6 text-white" />
          ) : (
            <Play className="w-6 h-6 text-white ml-0.5" />
          )}
        </button>
        
        <button
          onClick={nextVideo}
          className="p-3 hover:bg-white/10 rounded-full transition-colors"
          disabled={videoList.length <= 1}
        >
          <SkipForward className="w-5 h-5 text-gray-400 hover:text-white" />
        </button>
        
        <button className="p-3 hover:bg-white/10 rounded-full transition-colors">
          <Volume2 className="w-5 h-5 text-gray-400 hover:text-white" />
        </button>
        
        <button 
          onClick={openInNewTab}
          className="p-3 hover:bg-white/10 rounded-full transition-colors"
        >
          <Maximize className="w-5 h-5 text-gray-400 hover:text-white" />
        </button>
      </div>

      {/* Video Playlist */}
      {videoList.length > 1 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-gray-300 mb-3">
            Playlist ({videoList.length} videos)
          </h4>
          <div className="max-h-64 overflow-y-auto space-y-2">
            {videoList.map((video, index) => (
              <div
                key={index}
                onClick={() => selectVideo(index)}
                className={`flex items-center space-x-3 p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                  index === currentVideo
                    ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30'
                    : 'hover:bg-white/5'
                }`}
              >
                <div className="relative flex-shrink-0">
                  <img
                    src={video.thumbnail || getFallbackThumbnail(video.title)}
                    alt={video.title}
                    className="w-20 h-11 object-cover rounded"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      target.src = getFallbackThumbnail(video.title)
                    }}
                  />
                  {index === currentVideo && isPlaying && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded">
                      <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                    </div>
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <h5 className="text-sm font-medium text-white truncate">
                    {video.title}
                  </h5>
                  <div className="flex items-center justify-between text-xs text-gray-400 mt-1">
                    <span>{video.source}</span>
                    <span>{video.duration}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Video Info */}
      <div className="mt-6 pt-4 border-t border-white/10">
        <div className="text-center">
          <p className="text-xs text-gray-400 mb-2">
            🎲 AI-Curated Related Content
          </p>
          <p className="text-xs text-gray-500">
            Videos automatically selected based on news analysis
          </p>
        </div>
      </div>
    </div>
  )
}