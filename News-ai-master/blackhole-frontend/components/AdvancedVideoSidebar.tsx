'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Play, 
  Pause, 
  Volume2, 
  Maximize, 
  SkipForward, 
  SkipBack,
  ExternalLink,
  Shuffle,
  Repeat,
  Heart,
  Share2
} from 'lucide-react'

interface Video {
  id: number
  title: string
  thumbnail: string
  duration: string
  views: string
  source: string
  url?: string
}

interface AdvancedVideoSidebarProps {
  videos?: Video[]
  title?: string
}

export default function AdvancedVideoSidebar({ videos, title = "Related Videos" }: AdvancedVideoSidebarProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentVideo, setCurrentVideo] = useState(0)
  const [volume, setVolume] = useState(75)
  const [progress, setProgress] = useState(0)
  const [isLiked, setIsLiked] = useState(false)

  const defaultVideos: Video[] = [
    {
      id: 1,
      title: "AI News Analysis with Blackhole Infiverse LLP",
      thumbnail: "https://via.placeholder.com/400x225/1a1a1a/ffffff?text=AI+News+Demo",
      duration: "3:24",
      views: "1.2K",
      source: "Demo Channel",
      url: "https://example.com/video1"
    },
    {
      id: 2,
      title: "Advanced Web Scraping Techniques for News",
      thumbnail: "https://via.placeholder.com/400x225/2a2a2a/ffffff?text=Web+Scraping",
      duration: "5:17",
      views: "856",
      source: "Tech Tutorials",
      url: "https://example.com/video2"
    },
    {
      id: 3,
      title: "News Authenticity Verification with AI",
      thumbnail: "https://via.placeholder.com/400x225/3a3a3a/ffffff?text=News+Vetting",
      duration: "4:52",
      views: "2.1K",
      source: "AI Research",
      url: "https://example.com/video3"
    },
    {
      id: 4,
      title: "Neural Network Summarization Models",
      thumbnail: "https://via.placeholder.com/400x225/4a4a4a/ffffff?text=AI+Summary",
      duration: "6:33",
      views: "3.4K",
      source: "Deep Learning",
      url: "https://example.com/video4"
    }
  ]

  const videoList = videos && videos.length > 0 ? videos : defaultVideos
  const currentVideoData = videoList[currentVideo]

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isPlaying) {
      interval = setInterval(() => {
        setProgress(prev => (prev >= 100 ? 0 : prev + 0.5))
      }, 100)
    }
    return () => clearInterval(interval)
  }, [isPlaying])

  const togglePlay = () => {
    setIsPlaying(!isPlaying)
  }

  const nextVideo = () => {
    setCurrentVideo((prev) => (prev + 1) % videoList.length)
    setProgress(0)
  }

  const prevVideo = () => {
    setCurrentVideo((prev) => (prev - 1 + videoList.length) % videoList.length)
    setProgress(0)
  }

  const selectVideo = (index: number) => {
    setCurrentVideo(index)
    setProgress(0)
    setIsPlaying(true)
  }

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
      className="glass-effect rounded-3xl p-6 border border-white/20 sticky top-8 overflow-hidden"
    >
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 via-blue-900/10 to-pink-900/10 rounded-3xl"></div>
      
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="relative z-10 flex items-center justify-between mb-6"
      >
        <h3 className="text-xl font-semibold text-white flex items-center space-x-2">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          >
            📹
          </motion.div>
          <span>{title}</span>
        </h3>
        <div className="flex items-center space-x-2">
          <motion.div 
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-2 h-2 bg-red-500 rounded-full"
          />
          <span className="text-xs text-gray-400">Live</span>
        </div>
      </motion.div>

      {/* Main Video Player */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
        className="relative z-10 mb-6"
      >
        <div className="aspect-video bg-black rounded-2xl overflow-hidden relative group shadow-2xl">
          <motion.img
            key={currentVideo}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            src={currentVideoData.thumbnail}
            alt={currentVideoData.title}
            className="w-full h-full object-cover"
          />
          
          {/* Play Overlay */}
          <motion.div 
            whileHover={{ backgroundColor: 'rgba(0, 0, 0, 0.3)' }}
            className="absolute inset-0 bg-black/50 flex items-center justify-center transition-colors"
          >
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={togglePlay}
              className="w-20 h-20 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center transition-all duration-200 backdrop-blur-sm"
            >
              <motion.div
                animate={{ scale: isPlaying ? [1, 1.1, 1] : 1 }}
                transition={{ duration: 0.5, repeat: isPlaying ? Infinity : 0 }}
              >
                {isPlaying ? (
                  <Pause className="w-10 h-10 text-white" />
                ) : (
                  <Play className="w-10 h-10 text-white ml-1" />
                )}
              </motion.div>
            </motion.button>
          </motion.div>

          {/* Video Info Overlay */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-4"
          >
            <h4 className="text-white font-medium text-sm mb-2 line-clamp-2">
              {currentVideoData.title}
            </h4>
            <div className="flex items-center justify-between text-xs text-gray-300">
              <span>{currentVideoData.source}</span>
              <div className="flex items-center space-x-3">
                <span>{currentVideoData.views} views</span>
                <span>{currentVideoData.duration}</span>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => window.open(currentVideoData.url, '_blank')}
                  className="p-1 hover:bg-white/20 rounded transition-colors"
                >
                  <ExternalLink className="w-3 h-3" />
                </motion.button>
              </div>
            </div>
          </motion.div>

          {/* Progress Bar */}
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-700">
            <motion.div 
              animate={{ width: `${progress}%` }}
              className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
            />
          </div>
        </div>

        {/* Enhanced Controls */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="flex items-center justify-between mt-4 px-2"
        >
          {/* Left Controls */}
          <div className="flex items-center space-x-2">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={prevVideo}
              className="p-2 hover:bg-white/10 rounded-full transition-colors"
              disabled={videoList.length <= 1}
            >
              <SkipBack className="w-4 h-4 text-gray-400 hover:text-white" />
            </motion.button>
            
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={togglePlay}
              className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-full transition-all duration-200 shadow-lg"
            >
              {isPlaying ? (
                <Pause className="w-5 h-5 text-white" />
              ) : (
                <Play className="w-5 h-5 text-white ml-0.5" />
              )}
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={nextVideo}
              className="p-2 hover:bg-white/10 rounded-full transition-colors"
              disabled={videoList.length <= 1}
            >
              <SkipForward className="w-4 h-4 text-gray-400 hover:text-white" />
            </motion.button>
          </div>

          {/* Right Controls */}
          <div className="flex items-center space-x-2">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setIsLiked(!isLiked)}
              className="p-2 hover:bg-white/10 rounded-full transition-colors"
            >
              <Heart className={`w-4 h-4 ${isLiked ? 'text-red-500 fill-current' : 'text-gray-400 hover:text-white'}`} />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-2 hover:bg-white/10 rounded-full transition-colors"
            >
              <Share2 className="w-4 h-4 text-gray-400 hover:text-white" />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-2 hover:bg-white/10 rounded-full transition-colors"
            >
              <Volume2 className="w-4 h-4 text-gray-400 hover:text-white" />
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => window.open(currentVideoData.url, '_blank')}
              className="p-2 hover:bg-white/10 rounded-full transition-colors"
            >
              <Maximize className="w-4 h-4 text-gray-400 hover:text-white" />
            </motion.button>
          </div>
        </motion.div>
      </motion.div>

      {/* Video Playlist */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="relative z-10"
      >
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-sm font-medium text-gray-300">
            Playlist ({videoList.length} videos)
          </h4>
          <div className="flex items-center space-x-2">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-1 hover:bg-white/10 rounded transition-colors"
            >
              <Shuffle className="w-3 h-3 text-gray-400 hover:text-white" />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-1 hover:bg-white/10 rounded transition-colors"
            >
              <Repeat className="w-3 h-3 text-gray-400 hover:text-white" />
            </motion.button>
          </div>
        </div>
        
        <div className="max-h-80 overflow-y-auto space-y-2 scrollbar-thin scrollbar-thumb-purple-500 scrollbar-track-gray-800">
          <AnimatePresence>
            {videoList.map((video, index) => (
              <motion.div
                key={video.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => selectVideo(index)}
                className={`flex items-center space-x-3 p-3 rounded-xl cursor-pointer transition-all duration-300 ${
                  index === currentVideo
                    ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 shadow-lg'
                    : 'hover:bg-white/5 hover:shadow-md'
                }`}
              >
                <div className="relative flex-shrink-0">
                  <motion.img
                    whileHover={{ scale: 1.05 }}
                    src={video.thumbnail}
                    alt={video.title}
                    className="w-20 h-12 object-cover rounded-lg"
                  />
                  {index === currentVideo && isPlaying && (
                    <motion.div
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 1, repeat: Infinity }}
                      className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg"
                    >
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </motion.div>
                  )}
                  <div className="absolute bottom-1 right-1 bg-black/70 text-white text-xs px-1 rounded">
                    {video.duration}
                  </div>
                </div>
                
                <div className="flex-1 min-w-0">
                  <h5 className="text-sm font-medium text-white truncate leading-tight">
                    {video.title}
                  </h5>
                  <div className="flex items-center justify-between text-xs text-gray-400 mt-1">
                    <span className="truncate">{video.source}</span>
                    <span>{video.views} views</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Footer */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="relative z-10 mt-6 pt-4 border-t border-white/10"
      >
        <div className="text-center">
          <motion.p 
            animate={{ opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="text-xs text-gray-400 mb-2 flex items-center justify-center space-x-1"
          >
            <span>🎲</span>
            <span>AI-Curated Related Content</span>
          </motion.p>
          <p className="text-xs text-gray-500">
            Videos automatically selected based on news analysis
          </p>
        </div>
      </motion.div>
    </motion.div>
  )
}
