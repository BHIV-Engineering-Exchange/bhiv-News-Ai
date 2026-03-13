'use client'

import { useState, useEffect } from 'react'
import { Play, Pause, SkipForward, SkipBack, Shuffle, Volume2 } from 'lucide-react'

export default function VideoSidebar() {
  const [currentVideo, setCurrentVideo] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [videos] = useState([
    {
      id: 1,
      title: "AI News Analysis Demo",
      duration: "2:34",
      thumbnail: "https://via.placeholder.com/300x200/1a1a1a/ffffff?text=AI+News",
      source: "Demo"
    },
    {
      id: 2,
      title: "Blackhole Infiverse Overview",
      duration: "1:45",
      thumbnail: "https://via.placeholder.com/300x200/2a2a2a/ffffff?text=Overview",
      source: "Demo"
    },
    {
      id: 3,
      title: "Web Scraping in Action",
      duration: "3:12",
      thumbnail: "https://via.placeholder.com/300x200/3a3a3a/ffffff?text=Scraping",
      source: "Demo"
    }
  ])

  const togglePlay = () => {
    setIsPlaying(!isPlaying)
  }

  const nextVideo = () => {
    setCurrentVideo((prev) => (prev + 1) % videos.length)
  }

  const prevVideo = () => {
    setCurrentVideo((prev) => (prev - 1 + videos.length) % videos.length)
  }

  const selectVideo = (index: number) => {
    setCurrentVideo(index)
    setIsPlaying(true)
  }

  return (
    <div className="glass-effect rounded-2xl p-6 border border-white/20 sticky top-8">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Video Sidebar</h3>
        <div className="flex items-center space-x-1">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-xs text-gray-400">Live</span>
        </div>
      </div>

      {/* Main Video Player */}
      <div className="relative mb-6">
        <div className="aspect-video bg-black rounded-lg overflow-hidden relative group">
          <img
            src={videos[currentVideo].thumbnail}
            alt={videos[currentVideo].title}
            className="w-full h-full object-cover"
          />
          
          {/* Play Overlay */}
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center group-hover:bg-black/30 transition-colors">
            <button
              onClick={togglePlay}
              className="w-16 h-16 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110"
            >
              {isPlaying ? (
                <Pause className="w-8 h-8 text-white" />
              ) : (
                <Play className="w-8 h-8 text-white ml-1" />
              )}
            </button>
          </div>

          {/* Video Info Overlay */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
            <h4 className="text-white font-medium text-sm mb-1">
              {videos[currentVideo].title}
            </h4>
            <div className="flex items-center justify-between text-xs text-gray-300">
              <span>{videos[currentVideo].source}</span>
              <span>{videos[currentVideo].duration}</span>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-3">
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
          className="p-2 hover:bg-white/10 rounded-full transition-colors"
        >
          <SkipBack className="w-5 h-5 text-gray-400 hover:text-white" />
        </button>
        
        <button
          onClick={togglePlay}
          className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-full transition-all duration-200 hover:scale-105"
        >
          {isPlaying ? (
            <Pause className="w-5 h-5 text-white" />
          ) : (
            <Play className="w-5 h-5 text-white ml-0.5" />
          )}
        </button>
        
        <button
          onClick={nextVideo}
          className="p-2 hover:bg-white/10 rounded-full transition-colors"
        >
          <SkipForward className="w-5 h-5 text-gray-400 hover:text-white" />
        </button>
        
        <button className="p-2 hover:bg-white/10 rounded-full transition-colors">
          <Shuffle className="w-5 h-5 text-gray-400 hover:text-white" />
        </button>
        
        <button className="p-2 hover:bg-white/10 rounded-full transition-colors">
          <Volume2 className="w-5 h-5 text-gray-400 hover:text-white" />
        </button>
      </div>

      {/* Video Playlist */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-300 mb-3">Related Videos</h4>
        {videos.map((video, index) => (
          <div
            key={video.id}
            onClick={() => selectVideo(index)}
            className={`flex items-center space-x-3 p-3 rounded-lg cursor-pointer transition-all duration-200 ${
              index === currentVideo
                ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30'
                : 'hover:bg-white/5'
            }`}
          >
            <div className="relative flex-shrink-0">
              <img
                src={video.thumbnail}
                alt={video.title}
                className="w-16 h-10 object-cover rounded"
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

      {/* Random Video Info */}
      <div className="mt-6 pt-4 border-t border-white/10">
        <div className="text-center">
          <p className="text-xs text-gray-400 mb-2">
            🎲 Random Video Playback
          </p>
          <p className="text-xs text-gray-500">
            Videos from any source • Auto-updated
          </p>
        </div>
      </div>
    </div>
  )
}
