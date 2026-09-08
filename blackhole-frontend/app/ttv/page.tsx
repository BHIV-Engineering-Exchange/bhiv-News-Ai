'use client'

import { useState } from 'react'
import Header from '@/components/Header'
import { Video, Sparkles, Loader2, AlertCircle, RotateCcw } from 'lucide-react'

type GenerationResult =
  | { status: 'not-configured'; message: string }
  | { status: 'success'; videoUrl: string }

// Integration point for the future external TTV service.
async function generateVideo(_prompt: string): Promise<GenerationResult> {
  return {
    status: 'not-configured',
    message: 'Video generation is not configured yet. Connect the external TTV API to continue.'
  }
}

export default function TTVPage() {
  const [prompt, setPrompt] = useState('')
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    const trimmedPrompt = prompt.trim()
    if (!trimmedPrompt) return

    setError(null)
    setVideoUrl(null)
    setIsGenerating(true)

    try {
      const result = await generateVideo(trimmedPrompt)
      if (result.status === 'success') {
        setVideoUrl(result.videoUrl)
      } else {
        setError(result.message)
      }
    } catch {
      setError('Video generation failed. Please try again later.')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleNewPrompt = () => {
    setPrompt('')
    setVideoUrl(null)
    setError(null)
  }

  return (
    <div className="min-h-screen">
      <Header backendStatus="online" />

      <main className="container mx-auto px-6 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-10">
            <div className="inline-flex w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-3xl items-center justify-center shadow-2xl mb-5">
              <Video className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent mb-3">
              Text-To-Video
            </h1>
            <p className="text-lg text-gray-400">Generate videos from text descriptions.</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <section className="glass-effect rounded-3xl p-8 border border-white/20">
              <div className="flex items-center space-x-3 mb-6">
                <Sparkles className="w-7 h-7 text-purple-400" />
                <h2 className="text-2xl font-semibold text-white">Video Prompt</h2>
              </div>

              <textarea
                value={prompt}
                onChange={(event) => {
                  setPrompt(event.target.value)
                  setError(null)
                }}
                placeholder="Describe the video you want to generate..."
                rows={10}
                disabled={isGenerating}
                className="w-full resize-none bg-black/50 border-2 border-white/20 rounded-2xl px-5 py-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              />
              <div className="flex items-center justify-between mt-3 mb-6 text-sm text-gray-500">
                <span>{prompt.length} characters</span>
                <span>Describe the scene, style, and mood.</span>
              </div>

              <button
                onClick={handleGenerate}
                disabled={!prompt.trim() || isGenerating}
                className="w-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-600 hover:from-purple-600 hover:via-pink-600 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 text-white px-6 py-4 rounded-2xl font-bold text-lg transition-all flex items-center justify-center space-x-3 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    <span>Generating Video...</span>
                  </>
                ) : (
                  <>
                    <Video className="w-6 h-6" />
                    <span>Generate Video</span>
                  </>
                )}
              </button>

              {error && (
                <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-xl flex items-start space-x-3">
                  <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-yellow-200">{error}</p>
                </div>
              )}
            </section>

            <section className="glass-effect rounded-3xl p-8 border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold text-white">Generated Video</h2>
                {(videoUrl || error) && (
                  <button
                    onClick={handleNewPrompt}
                    className="flex items-center space-x-2 text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>New prompt</span>
                  </button>
                )}
              </div>

              {videoUrl ? (
                <video
                  src={videoUrl}
                  controls
                  className="w-full aspect-video rounded-2xl bg-black object-contain"
                />
              ) : (
                <div className="aspect-video rounded-2xl border border-dashed border-white/20 bg-black/30 flex items-center justify-center text-center p-6">
                  <p className="text-gray-500">Your generated video will appear here.</p>
                </div>
              )}
            </section>
          </div>
        </div>
      </main>
    </div>
  )
}
