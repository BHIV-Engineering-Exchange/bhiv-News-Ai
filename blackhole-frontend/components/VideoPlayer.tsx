'use client'

import { useState, useEffect, useRef } from 'react'
import { Play, Pause, SkipForward, SkipBack, Volume2, Maximize, ExternalLink, AlertCircle } from 'lucide-react'

// YouTube IFrame API types
declare global {
  interface Window {
    YT: any
    onYouTubeIframeAPIReady: () => void
  }
}

interface Video {
  title: string
  url: string
  thumbnail?: string
  duration?: string
  source: string
  video_id?: string
  mock_data?: boolean
  demo_video?: boolean
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
  const [youtubePlayer, setYoutubePlayer] = useState<any>(null)
  const [isYoutubeAPIReady, setIsYoutubeAPIReady] = useState(false)
  const [isMounted, setIsMounted] = useState(false)
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const playerContainerRef = useRef<HTMLDivElement>(null)
  const playerRef = useRef<any>(null)

  // Prevent hydration errors by only rendering iframe on client
  useEffect(() => {
    setIsMounted(true)
  }, [])

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

  // Extract YouTube video ID from URL
  const getYouTubeVideoId = (url: string): string | null => {
    if (!url) return null
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([A-Za-z0-9_-]+)/,
      /youtube\.com\/embed\/([A-Za-z0-9_-]+)/
    ]
    for (const pattern of patterns) {
      const match = url.match(pattern)
      if (match) return match[1]
    }
    return null
  }

  const isYouTubeVideo = (url: string): boolean => {
    return url.includes('youtube.com') || url.includes('youtu.be') || url.includes('embed')
  }

  // Load YouTube IFrame API with reduced warnings
  useEffect(() => {
    if (typeof window === 'undefined') return

    // Check if API is already loaded
    if (window.YT && window.YT.Player) {
      setIsYoutubeAPIReady(true)
      return
    }

    // Load the script if not already loaded
    const existingScript = document.querySelector('script[src*="youtube.com/iframe_api"]')
    if (existingScript) {
      // Wait for API to be ready
      window.onYouTubeIframeAPIReady = () => {
        setIsYoutubeAPIReady(true)
      }
      return
    }

    const tag = document.createElement('script')
    tag.src = 'https://www.youtube.com/iframe_api'
    tag.async = true
    tag.defer = true
    const firstScriptTag = document.getElementsByTagName('script')[0]
    firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag)

    window.onYouTubeIframeAPIReady = () => {
      setIsYoutubeAPIReady(true)
    }
  }, [])

  // Initialize YouTube player when video changes
  useEffect(() => {
    if (!isYoutubeAPIReady || !window.YT || !currentVideoData) return
    if (!isYouTubeVideo(currentVideoData.url)) return

    const videoId = getYouTubeVideoId(currentVideoData.url)
    if (!videoId || !playerContainerRef.current) return

    // Destroy existing player
    if (playerRef.current) {
      try {
        playerRef.current.destroy()
      } catch (e) {
        console.warn('Error destroying YouTube player:', e)
      }
      playerRef.current = null
    }

    // Clear the container
    if (playerContainerRef.current) {
      playerContainerRef.current.innerHTML = ''
    }

    // Create new player
    try {
      const player = new window.YT.Player(playerContainerRef.current, {
        videoId: videoId,
        playerVars: {
          autoplay: 0,
          controls: 0,
          modestbranding: 1,
          rel: 0,
          showinfo: 0,
          iv_load_policy: 3,
          fs: 0,
          cc_load_policy: 0,
          disablekb: 1
        },
        events: {
          onReady: (event: any) => {
            playerRef.current = event.target
            setYoutubePlayer(event.target)
            setIsPlaying(false)
            setCurrentTime(0)
          },
          onStateChange: (event: any) => {
            // YT.PlayerState.PLAYING = 1, PAUSED = 2, ENDED = 0
            if (event.data === 1) {
              setIsPlaying(true)
            } else if (event.data === 2 || event.data === 0) {
              setIsPlaying(false)
            }
          },
          onError: (event: any) => {
            // YouTube error codes: 2=invalid video, 5=HTML5 error, 100=not found, 101/150=not allowed
            const errorCodes: { [key: number]: string } = {
              2: 'Invalid video parameter',
              5: 'HTML5 player error',
              100: 'Video not found',
              101: 'Video not allowed to be played in embedded players',
              150: 'Video not allowed to be played in embedded players'
            }
            const errorMessage = errorCodes[event.data] || 'Video playback error'
            console.warn('YouTube player error:', errorMessage, 'Code:', event.data)
            setVideoError(errorMessage)
            setIsPlaying(false)
          }
        }
      })
    } catch (error) {
      console.error('Error creating YouTube player:', error)
      setVideoError('Failed to load video player')
    }

    return () => {
      if (playerRef.current) {
        try {
          playerRef.current.destroy()
        } catch (e) {
          console.warn('Error destroying YouTube player on cleanup:', e)
        }
        playerRef.current = null
      }
    }
  }, [currentVideo, isYoutubeAPIReady, currentVideoData?.url])

  // Update current time for YouTube videos
  useEffect(() => {
    if (!playerRef.current || !isPlaying) return

    const interval = setInterval(() => {
      try {
        if (playerRef.current) {
          const time = playerRef.current.getCurrentTime()
          setCurrentTime(Math.floor(time))
        }
      } catch (e) {
        // Player might not be ready
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [youtubePlayer, isPlaying])

  const togglePlay = () => {
    if (playerRef.current && isYouTubeVideo(currentVideoData.url)) {
      try {
        if (isPlaying) {
          playerRef.current.pauseVideo()
        } else {
          playerRef.current.playVideo()
        }
      } catch (error) {
        console.error('Error toggling YouTube playback:', error)
        setIsPlaying(!isPlaying)
      }
    } else {
      setIsPlaying(!isPlaying)
    }
  }

  const nextVideo = () => {
    if (playerRef.current) {
      try {
        playerRef.current.stopVideo()
      } catch (e) {
        // Ignore errors
      }
    }
    setCurrentVideo((prev) => (prev + 1) % videoList.length)
    setCurrentTime(0)
    setIsPlaying(false)
  }

  const prevVideo = () => {
    if (playerRef.current) {
      try {
        playerRef.current.stopVideo()
      } catch (e) {
        // Ignore errors
      }
    }
    setCurrentVideo((prev) => (prev - 1 + videoList.length) % videoList.length)
    setCurrentTime(0)
    setIsPlaying(false)
  }

  const selectVideo = (index: number) => {
    if (playerRef.current) {
      try {
        playerRef.current.stopVideo()
      } catch (e) {
        // Ignore errors
      }
    }
    setCurrentVideo(index)
    setCurrentTime(0)
    setIsPlaying(false)
    setVideoError(null)
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
          {!isMounted ? (
            <div className="w-full h-full flex items-center justify-center bg-black/50">
              <div className="text-center text-white">
                <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                <p className="text-sm">Loading...</p>
              </div>
            </div>
          ) : isYouTubeVideo(currentVideoData.url) && isYoutubeAPIReady ? (
            <div ref={playerContainerRef} className="w-full h-full"></div>
          ) : isYouTubeVideo(currentVideoData.url) ? (
            <div className="w-full h-full flex items-center justify-center bg-black/50">
              <div className="text-center text-white">
                <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                <p className="text-sm">Loading player...</p>
              </div>
            </div>
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
                className={`flex items-center space-x-3 p-3 rounded-lg cursor-pointer transition-all duration-200 ${index === currentVideo
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