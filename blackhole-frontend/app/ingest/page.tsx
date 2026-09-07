'use client'

import { useEffect, useState } from 'react'
import Header from '@/components/Header'
import BackendStatus from '@/components/BackendStatus'
import { checkBackendHealth } from '@/lib/api'
import {
  AlertCircle,
  CheckCircle,
  FileUp,
  Loader2,
  Upload,
} from 'lucide-react'

const ACCEPTED_FORMATS = '.pdf,.docx,.txt,.md,.json,.csv'
const ACCEPTED_EXTENSIONS = ['pdf', 'docx', 'txt', 'md', 'json', 'csv']

type IngestionResponse = {
  status?: string
  filename?: string
  content_type?: string
  size_bytes?: number
  detected_format?: string
  selected_route?: string
  execution_id?: string
  trace_id?: string
  input_fingerprint?: string
  processing_status?: string
  [key: string]: unknown
}

function formatBytes(bytes: number | undefined) {
  if (typeof bytes !== 'number') return 'Unknown'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function IngestPage() {
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [result, setResult] = useState<IngestionResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  useEffect(() => {
    checkBackend()
    const interval = setInterval(checkBackend, 30000)
    return () => clearInterval(interval)
  }, [])

  const checkBackend = async () => {
    setBackendStatus('checking')
    try {
      setBackendStatus((await checkBackendHealth()) ? 'online' : 'offline')
    } catch {
      setBackendStatus('offline')
    }
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null
    setError(null)
    setResult(null)

    if (!file) {
      setSelectedFile(null)
      return
    }

    const extension = file.name.split('.').pop()?.toLowerCase()
    if (!extension || !ACCEPTED_EXTENSIONS.includes(extension)) {
      setSelectedFile(null)
      setError('Unsupported file format. Choose a PDF, DOCX, TXT, Markdown, JSON, or CSV file.')
      event.target.value = ''
      return
    }

    if (file.size === 0) {
      setSelectedFile(null)
      setError('The selected file is empty.')
      event.target.value = ''
      return
    }

    setSelectedFile(file)
  }

  const handleUpload = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!selectedFile) {
      setError('Select a file before uploading.')
      return
    }

    setError(null)
    setResult(null)
    setIsUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/ingest`,
        {
          method: 'POST',
          headers: { 'ngrok-skip-browser-warning': 'true' },
          body: formData,
        },
      )
      const payload = await response.json().catch(() => null)

      if (!response.ok) {
        const message = payload && typeof payload.detail === 'string'
          ? payload.detail
          : payload && typeof payload.message === 'string'
            ? payload.message
            : `Ingestion failed with status ${response.status}.`
        throw new Error(message)
      }

      setResult(payload as IngestionResponse)
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : 'Unable to ingest the selected file.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="min-h-screen">
      <Header backendStatus={backendStatus} />
      <main className="container mx-auto px-6 py-8">
        <BackendStatus status={backendStatus} onRetry={checkBackend} />

        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <FileUp className="w-10 h-10 text-purple-400" />
            <h1 className="text-4xl font-bold text-white">Ingest</h1>
          </div>
          <p className="text-gray-400 text-lg">
            Upload a supported document for multimodal intelligence processing.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="glass-effect rounded-2xl p-6 border border-white/10">
            <h2 className="text-xl font-semibold text-white mb-2">Upload a file</h2>
            <p className="text-sm text-gray-400 mb-6">
              Supported formats: PDF, DOCX, TXT, Markdown, JSON, and CSV.
            </p>

            <form onSubmit={handleUpload} className="space-y-5">
              <label
                htmlFor="ingest-file"
                className="flex min-h-48 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-purple-400/50 bg-black/20 px-6 text-center transition-colors hover:border-purple-300 hover:bg-purple-500/10"
              >
                <Upload className="mb-3 h-10 w-10 text-purple-400" />
                <span className="text-sm font-medium text-white">
                  {selectedFile ? selectedFile.name : 'Choose a file to ingest'}
                </span>
                <span className="mt-2 text-xs text-gray-400">
                  {selectedFile ? `${formatBytes(selectedFile.size)} selected` : 'Click to browse your device'}
                </span>
                <input
                  id="ingest-file"
                  type="file"
                  accept={ACCEPTED_FORMATS}
                  onChange={handleFileChange}
                  className="sr-only"
                />
              </label>

              {error && (
                <div className="flex items-start space-x-3 rounded-lg border border-red-500/50 bg-red-500/20 p-4 text-sm text-red-200">
                  <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-400" />
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={!selectedFile || isUploading}
                className="flex w-full items-center justify-center space-x-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-3 font-medium text-white transition-all hover:from-purple-600 hover:to-pink-600 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Processing file...</span>
                  </>
                ) : (
                  <>
                    <FileUp className="h-5 w-5" />
                    <span>Upload and process</span>
                  </>
                )}
              </button>
            </form>
          </section>

          <section className="glass-effect rounded-2xl p-6 border border-white/10">
            <div className="mb-5 flex items-center space-x-3">
              <CheckCircle className="h-6 w-6 text-green-400" />
              <h2 className="text-xl font-semibold text-white">Ingestion result</h2>
            </div>

            {result ? (
              <>
                <div className="grid gap-3 sm:grid-cols-2">
                  {[
                    ['Status', result.status],
                    ['Processing', result.processing_status],
                    ['Format', result.detected_format],
                    ['Execution ID', result.execution_id],
                    ['Trace ID', result.trace_id],
                    [
                      'Timestamp',
                      typeof result.timestamp === 'string'
                        ? result.timestamp
                        : result.canonical_intelligence &&
                            typeof result.canonical_intelligence === 'object' &&
                            'timestamp' in result.canonical_intelligence &&
                            typeof result.canonical_intelligence.timestamp === 'string'
                          ? result.canonical_intelligence.timestamp
                          : undefined,
                    ],
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-lg bg-black/20 p-3">
                      <p className="text-xs uppercase tracking-wide text-gray-500">{label}</p>
                      <p className="mt-1 break-all text-sm text-gray-200">{value || 'Not provided'}</p>
                    </div>
                  ))}
                </div>
                <details className="mt-5">
                  <summary className="cursor-pointer text-sm font-medium text-purple-300 hover:text-purple-200">
                    View complete JSON response
                  </summary>
                  <pre className="custom-scrollbar mt-3 max-h-96 overflow-auto rounded-lg bg-black/40 p-4 text-xs text-gray-300">
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </details>
              </>
            ) : (
              <div className="flex min-h-48 items-center justify-center rounded-xl border border-white/10 bg-black/20 p-6 text-center text-gray-500">
                Upload a file to view its processing details and response.
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  )
}
