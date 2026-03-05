import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Blackhole Infiverse LLP - Advanced AI News Analysis',
  description: 'Professional AI-powered news analysis platform with web scraping, authenticity vetting, and intelligent summarization.',
  keywords: ['AI', 'News Analysis', 'Web Scraping', 'Authenticity Vetting', 'Summarization', 'Blackhole Infiverse'],
  authors: [{ name: 'Blackhole Infiverse LLP' }],
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen bg-gradient-to-br from-blackhole-950 via-blackhole-900 to-infiverse-950`}>
        <div className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  )
}
