'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import { Menu, X, LogOut, User } from 'lucide-react'
import { useAuth } from '@/lib/auth'

interface HeaderProps {
  backendStatus: 'online' | 'offline' | 'checking'
}

export default function Header({ backendStatus }: HeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const pathname = usePathname()
  const { user, isAuthenticated, logout } = useAuth()

  const navItems = [
    { href: '/', label: '🏠 Home', id: 'home' },
    { href: '/live', label: '🔴 Live Dashboard', id: 'live' },
    { href: '/analyze', label: '🔬 Analyze', id: 'analyze' },
    { href: '/dashboard', label: '📊 Analytics', id: 'dashboard' },
    { href: '/ttv', label: '🎬 TTV', id: 'ttv' },
    { href: '/stt', label: '🎙️ STT', id: 'stt' },
    { href: '/ingest', label: '📥 Ingest', id: 'ingest' },
  ]

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname.startsWith(href)
  }

  // Don't show navigation if not authenticated
  if (!isAuthenticated) {
    return (
      <header className="glass-effect border-b border-white/10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Brand */}
            <Link href="/" className="flex items-center space-x-4 hover:opacity-80 transition-opacity">
              <div className="relative w-12 h-12">
                <Image
                  src="/infiverse-logo.svg"
                  alt="Infiverse logo"
                  fill
                  className="object-contain rounded-full"
                  priority
                />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Blackhole Infiverse LLP</h1>
                <p className="text-sm text-gray-400">Advanced AI Pipeline</p>
              </div>
            </Link>

            {/* Login Button */}
            <Link
              href="/login"
              className="px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/10 rounded-lg text-sm font-medium text-white transition-all"
            >
              Login
            </Link>
          </div>
        </div>
      </header>
    )
  }

  return (
    <header className="glass-effect border-b border-white/10">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Brand */}
          <Link href="/" className="flex items-center space-x-4 hover:opacity-80 transition-opacity">
            <div className="relative w-12 h-12">
              <Image
                src="/infiverse-logo.svg"
                alt="Infiverse logo"
                fill
                className="object-contain rounded-full"
                priority
              />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Blackhole Infiverse LLP</h1>
              <p className="text-sm text-gray-400">Advanced AI Pipeline</p>
            </div>
          </Link>

          {/* Navigation - Desktop */}
          <nav className="hidden md:flex flex-1 items-center justify-evenly">
            {navItems.map((item) => (
              <Link
                key={item.id}
                href={item.href}
                className={`transition-colors ${isActive(item.href)
                  ? 'text-purple-400 font-medium'
                  : 'text-gray-300 hover:text-white'
                  }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          {/* User Info */}
          <div className="hidden lg:flex items-center">
            {/* User Info */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 px-3 py-1.5 bg-white/5 rounded-lg border border-white/10">
                <User className="w-4 h-4 text-purple-400" />
                <span className="text-sm text-gray-300">{user?.email?.split('@')[0] || 'User'}</span>
              </div>
              
              {/* Logout Button */}
              <button
                onClick={logout}
                className="flex items-center space-x-1 px-3 py-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 rounded-lg transition-all text-sm"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-white"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-white/10">
            <nav className="flex flex-col space-y-4 mt-4">
              {navItems.map((item) => (
                <Link
                  key={`mobile-${item.id}`}
                  href={item.href}
                  className={`transition-colors ${isActive(item.href)
                    ? 'text-purple-400 font-medium'
                    : 'text-gray-300 hover:text-white'
                    }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.label}
                </Link>
              ))}

              {/* Mobile Status & User */}
              <div className="pt-4 border-t border-white/10 space-y-3">
                {user && (
                  <div className="flex items-center space-x-2 text-sm text-gray-300">
                    <User className="w-4 h-4 text-purple-400" />
                    <span>{user.email}</span>
                  </div>
                )}
                
                <button
                  onClick={() => {
                    logout()
                    setIsMenuOpen(false)
                  }}
                  className="flex items-center space-x-2 text-red-400 hover:text-red-300"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
