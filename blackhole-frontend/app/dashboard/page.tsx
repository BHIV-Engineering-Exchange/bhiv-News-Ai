'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/Header'
import BackendStatus from '@/components/BackendStatus'
import { checkBackendHealth } from '@/lib/api'
import { Activity, Clock, Users, TrendingUp, FileText, Shield, Video, Zap } from 'lucide-react'

export default function Dashboard() {
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking')

  useEffect(() => {
    checkBackend()
    const interval = setInterval(checkBackend, 30000)
    return () => clearInterval(interval)
  }, [])

  const checkBackend = async () => {
    try {
      const isHealthy = await checkBackendHealth()
      setBackendStatus(isHealthy ? 'online' : 'offline')
    } catch (error) {
      setBackendStatus('offline')
    }
  }

  const stats = [
    { label: 'Total Analyses', value: '1,247', icon: FileText, color: 'text-blue-400' },
    { label: 'Success Rate', value: '94.2%', icon: TrendingUp, color: 'text-green-400' },
    { label: 'Avg Processing Time', value: '2.3s', icon: Clock, color: 'text-yellow-400' },
    { label: 'Active Sessions', value: '23', icon: Users, color: 'text-purple-400' },
  ]

  const recentActivity = [
    { id: 1, type: 'analysis', url: 'bbc.com/news/article-1', status: 'completed', time: '2 min ago' },
    { id: 2, type: 'analysis', url: 'cnn.com/news/breaking', status: 'completed', time: '5 min ago' },
    { id: 3, type: 'analysis', url: 'reuters.com/world/asia', status: 'failed', time: '8 min ago' },
    { id: 4, type: 'analysis', url: 'guardian.com/politics', status: 'completed', time: '12 min ago' },
    { id: 5, type: 'analysis', url: 'nytimes.com/section/world', status: 'completed', time: '15 min ago' },
  ]

  const systemHealth = [
    { service: 'Web Scraping', status: 'online', uptime: '99.9%' },
    { service: 'Authenticity Vetting', status: 'online', uptime: '98.7%' },
    { service: 'AI Summarization', status: 'online', uptime: '99.2%' },
    { service: 'Video Search', status: 'online', uptime: '97.8%' },
    { service: 'Prompt Generation', status: 'online', uptime: '99.5%' },
  ]

  return (
    <div className="min-h-screen">
      <Header backendStatus={backendStatus} />

      <main className="container mx-auto px-6 py-8">
        <BackendStatus status={backendStatus} onRetry={checkBackend} />

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">📊 Dashboard</h1>
          <p className="text-gray-400">Monitor your AI news analysis system performance</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <div key={index} className="glass-effect rounded-xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-4">
                <stat.icon className={`w-8 h-8 ${stat.color}`} />
                <div className="text-right">
                  <div className="text-2xl font-bold text-white">{stat.value}</div>
                  <div className="text-sm text-gray-400">{stat.label}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Activity */}
          <div className="glass-effect rounded-xl p-6 border border-white/20">
            <h2 className="text-2xl font-semibold text-white mb-6 flex items-center">
              <Activity className="w-6 h-6 mr-3 text-blue-400" />
              Recent Activity
            </h2>
            
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-center justify-between p-4 bg-black/30 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      activity.status === 'completed' ? 'bg-green-400' : 'bg-red-400'
                    }`}></div>
                    <div>
                      <div className="text-white font-medium">{activity.url}</div>
                      <div className="text-sm text-gray-400">Analysis {activity.status}</div>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">{activity.time}</div>
                </div>
              ))}
            </div>
          </div>

          {/* System Health */}
          <div className="glass-effect rounded-xl p-6 border border-white/20">
            <h2 className="text-2xl font-semibold text-white mb-6 flex items-center">
              <Shield className="w-6 h-6 mr-3 text-green-400" />
              System Health
            </h2>
            
            <div className="space-y-4">
              {systemHealth.map((service, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-black/30 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse"></div>
                    <div>
                      <div className="text-white font-medium">{service.service}</div>
                      <div className="text-sm text-gray-400">Uptime: {service.uptime}</div>
                    </div>
                  </div>
                  <div className="text-sm text-green-400 font-medium">Online</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Performance Chart Placeholder */}
        <div className="mt-8 glass-effect rounded-xl p-6 border border-white/20">
          <h2 className="text-2xl font-semibold text-white mb-6 flex items-center">
            <TrendingUp className="w-6 h-6 mr-3 text-purple-400" />
            Performance Overview
          </h2>
          
          <div className="h-64 bg-black/30 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <TrendingUp className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">Performance charts coming soon</p>
              <p className="text-sm text-gray-500 mt-2">Real-time analytics and insights</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}