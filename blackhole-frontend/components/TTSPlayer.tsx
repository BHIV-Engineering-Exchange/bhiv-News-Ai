'use client'

import { useState, useRef, useEffect } from 'react'
import { Play, Pause, RotateCcw, Volume2, VolumeX, Download, Share2 } from 'lucide-react'
import { getAudioUrl } from '@/lib/api'

interface TTSPlayerProps {
  audioUrl?: string | null
  audioPath?: string | null // Sankalp audio_path
  title?: string
  duration?: number
  newsId?: string
  onPlayComplete?: () => void
}

export default function TTSPlayer({
  audioUrl,
  audioPath, // Sankalp audio_path
  title = 'News Audio',
  duration = 0,
  newsId,
  onPlayComplete
}: TTSPlayerProps) {
  // Use audioPath if provided (Sankalp), otherwise fall back to audioUrl
  const resolvedAudioUrl = audioPath ? getAudioUrl(audioPath) : (audioUrl || null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [audioDuration, setAudioDuration] = useState(duration)
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    // Update audio source when URL changes
    if (resolvedAudioUrl) {
      audio.src = resolvedAudioUrl
      audio.load()
    }

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime)
    }

    const handleLoadedMetadata = () => {
      setAudioDuration(audio.duration || duration)
    }

    const handleEnded = () => {
      setIsPlaying(false)
      setCurrentTime(0)
      if (onPlayComplete) onPlayComplete()
    }

    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('loadedmetadata', handleLoadedMetadata)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [resolvedAudioUrl, duration, onPlayComplete])

  const togglePlay = async () => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
      setIsPlaying(false)
    } else {
      try {
        await audio.play()
        setIsPlaying(true)
      } catch (error) {
        console.error('Audio playback failed:', error)
        setIsPlaying(false)
      }
    }
  }
  const handleRestart = () => {
    const audio = audioRef.current
    if (!audio) return
    audio.currentTime = 0
    setCurrentTime(0)
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current
    if (!audio) return
    const newTime = parseFloat(e.target.value)
    audio.currentTime = newTime
    setCurrentTime(newTime)
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current
    if (!audio) return
    const newVolume = parseFloat(e.target.value)
    audio.volume = newVolume
    setVolume(newVolume)
    setIsMuted(newVolume === 0)
  }

  const toggleMute = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isMuted) {
      audio.volume = volume || 0.5
      setIsMuted(false)
    } else {
      audio.volume = 0
      setIsMuted(true)
    }
  }

  const formatTime = (seconds: number) => {
    if (isNaN(seconds)) return '0:00'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleDownload = () => {
    if (audioUrl) {
      const a = document.createElement('a')
      a.href = audioUrl
      a.download = `${title}.mp3`
      a.click()
    }
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: title,
          text: `Listen to: ${title}`,
          url: window.location.href
        })
      } catch (error) {
        console.error('Share failed:', error)
      }
    }
  }

  if (!audioUrl) {
    return (
      <div className="glass-effect rounded-xl p-6 border border-white/20">
        <div className="text-center py-8">
          <Volume2 className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400">No audio available yet</p>
          <p className="text-sm text-gray-500 mt-2">Audio will be generated once processing is complete</p>
        </div>
      </div>
    )
  }

  return (
    <div className="glass-effect rounded-xl p-6 border border-white/20">
      {/* Audio Element */}
      <audio
        ref={audioRef}
        src={resolvedAudioUrl || undefined}
        preload="metadata"
        onError={(e) => console.error('Audio resource error:', e.currentTarget.error, 'URL:', resolvedAudioUrl)}
      />

      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-white flex items-center">
            <Volume2 className="w-5 h-5 mr-2 text-purple-400" />
            AI Voice Summary
          </h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleShare}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Share"
            >
              <Share2 className="w-4 h-4 text-gray-400" />
            </button>
            <button
              onClick={handleDownload}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Download"
            >
              <Download className="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </div>
        <p className="text-sm text-gray-400 line-clamp-1">{title}</p>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <input
          type="range"
          min="0"
          max={audioDuration || 100}
          value={currentTime}
          onChange={handleSeek}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
          style={{
            background: `linear-gradient(to right, #a855f7 0%, #a855f7 ${(currentTime / (audioDuration || 1)) * 100}%, #374151 ${(currentTime / (audioDuration || 1)) * 100}%, #374151 100%)`
          }}
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(audioDuration)}</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {/* Restart Button */}
          <button
            onClick={handleRestart}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            title="Restart"
          >
            <RotateCcw className="w-5 h-5 text-gray-400" />
          </button>

          {/* Play/Pause Button */}
          <button
            onClick={togglePlay}
            className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-full transition-all hover:scale-105"
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? (
              <Pause className="w-6 h-6 text-white" fill="white" />
            ) : (
              <Play className="w-6 h-6 text-white" fill="white" />
            )}
          </button>

          {/* Speed Indicator */}
          <div className="text-sm text-gray-400 ml-2">
            {isPlaying ? (
              <span className="flex items-center">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></span>
                Playing
              </span>
            ) : (
              <span>Paused</span>
            )}
          </div>
        </div>

        {/* Volume Control */}
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleMute}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            title={isMuted ? 'Unmute' : 'Mute'}
          >
            {isMuted ? (
              <VolumeX className="w-5 h-5 text-gray-400" />
            ) : (
              <Volume2 className="w-5 h-5 text-gray-400" />
            )}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={isMuted ? 0 : volume}
            onChange={handleVolumeChange}
            className="w-20 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            style={{
              background: `linear-gradient(to right, #a855f7 0%, #a855f7 ${(isMuted ? 0 : volume) * 100}%, #374151 ${(isMuted ? 0 : volume) * 100}%, #374151 100%)`
            }}
          />
        </div>
      </div>

      {/* Playback Stats */}
      <div className="mt-4 pt-4 border-t border-white/10">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-xs text-gray-500">Duration</div>
            <div className="text-sm text-white font-medium">{formatTime(audioDuration)}</div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Progress</div>
            <div className="text-sm text-white font-medium">
              {Math.round((currentTime / (audioDuration || 1)) * 100)}%
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Remaining</div>
            <div className="text-sm text-white font-medium">
              {formatTime(audioDuration - currentTime)}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

