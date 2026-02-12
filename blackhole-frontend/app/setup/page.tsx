'use client'

import { useState, useEffect } from 'react'
import { Loader2, CheckCircle, XCircle, Database } from 'lucide-react'

export default function SetupPage() {
  const [status, setStatus] = useState<'checking' | 'setup' | 'success' | 'error'>('checking')
  const [message, setMessage] = useState('Checking database...')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    checkDatabase()
  }, [])

  const checkDatabase = async () => {
    try {
      const response = await fetch('/api/setup-database')
      const data = await response.json()
      
      if (data.setup) {
        setStatus('success')
        setMessage('Database is already setup! You can use the app now.')
      } else {
        setStatus('setup')
        setMessage('Database needs to be initialized.')
      }
    } catch (error) {
      setStatus('setup')
      setMessage('Unable to check database status.')
    }
  }

  const setupDatabase = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/setup-database', {
        method: 'POST'
      })
      const data = await response.json()

      if (data.success) {
        setStatus('success')
        setMessage(data.message)
      } else {
        setStatus('error')
        setMessage(data.error || 'Failed to setup database')
      }
    } catch (error) {
      setStatus('error')
      setMessage('An error occurred while setting up the database')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1 flex items-center justify-center p-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 via-black to-pink-900/10"></div>
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[100px] animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-pink-600/20 rounded-full blur-[100px] animate-pulse delay-1000"></div>

        <div className="w-full max-w-md relative z-10">
          <div className="glass-effect p-8 rounded-2xl border border-white/10 shadow-2xl text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Database className="w-8 h-8 text-white" />
            </div>
            
            <h1 className="text-3xl font-bold text-white mb-2">Database Setup</h1>
            
            {status === 'checking' && (
              <>
                <div className="flex items-center justify-center space-x-2 text-gray-400 mb-4">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>{message}</span>
                </div>
              </>
            )}
            
            {status === 'setup' && (
              <>
                <p className="text-gray-400 mb-6">{message}</p>
                <button
                  onClick={setupDatabase}
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-bold py-3 rounded-xl transition-all duration-300 transform hover:scale-[1.02] disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-lg shadow-purple-500/25"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Setting up...</span>
                    </>
                  ) : (
                    <span>Initialize Database</span>
                  )}
                </button>
              </>
            )}
            
            {status === 'success' && (
              <>
                <div className="flex items-center justify-center space-x-2 text-green-400 mb-4">
                  <CheckCircle className="w-6 h-6" />
                  <span>{message}</span>
                </div>
                <a
                  href="/signup"
                  className="block w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-bold py-3 rounded-xl transition-all"
                >
                  Go to Signup
                </a>
              </>
            )}
            
            {status === 'error' && (
              <>
                <div className="flex items-center justify-center space-x-2 text-red-400 mb-4">
                  <XCircle className="w-6 h-6" />
                  <span>{message}</span>
                </div>
                <button
                  onClick={setupDatabase}
                  className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-bold py-3 rounded-xl transition-all"
                >
                  Try Again
                </button>
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
