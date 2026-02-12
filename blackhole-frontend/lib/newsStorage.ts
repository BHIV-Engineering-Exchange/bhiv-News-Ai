export interface SavedNewsItem {
  id: string
  title: string
  description: string
  url: string
  source: string
  category: string
  imageUrl?: string
  publishedAt: string
  readTime?: string
  scrapedAt: string
  scrapedData?: any
  summary?: string
  insights?: any
  relatedVideos?: Array<{
    title?: string
    url?: string
    thumbnail?: string
    duration?: string
    source?: string
  }>
}

export function saveScrapedNews(scrapedData: any, url: string): SavedNewsItem | null {
  try {
    if (!scrapedData || !url) return null

    const title = scrapedData.title ||
      scrapedData.scraped_data?.title ||
      scrapedData.scraped_data?.metadata?.title ||
      scrapedData.scraped_data?.h1 ||
      extractTitleFromUrl(url) ||
      'No title found'

    const description = scrapedData.brief_description ||
      (typeof scrapedData.summary === 'string' ? scrapedData.summary : scrapedData.summary?.text) ||
      scrapedData.scraped_data?.content?.substring(0, 200) ||
      'No description available'

    // Use backend category if available, otherwise detect from content
    const detectedCategory = scrapedData.scraped_data?.category || 
                             detectCategory(title, description)
    
    const newsItem: SavedNewsItem = {
      id: `scraped_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title,
      description: description.length > 200 ? description.substring(0, 200) + '...' : description,
      url,
      source: extractSourceFromUrl(url),
      category: detectedCategory,
      imageUrl: findBestImage(scrapedData, title),
      publishedAt: formatTimeAgo(scrapedData.scraped_data?.date || new Date().toISOString()),
      readTime: Math.ceil((scrapedData.scraped_data?.content_length || description.length) / 1000) + ' min read',
      scrapedAt: new Date().toISOString(),
      scrapedData,
      summary: typeof scrapedData.summary === 'string' ? scrapedData.summary : (scrapedData.summary?.text || ''),
      insights: scrapedData.vetting_results,
      relatedVideos: extractRelatedVideos(scrapedData)
    }

    fetch('/api/scraped-news', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newsItem)
    }).catch(error => console.error('Failed to save:', error))

    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('newsArticleSaved', { detail: newsItem }))
    }

    return newsItem
  } catch (error) {
    console.error('Error saving:', error)
    return null
  }
}

export async function getSavedNews(): Promise<SavedNewsItem[]> {
  try {
    const response = await fetch('/api/scraped-news')
    const data = await response.json()
    return data.success ? data.data : []
  } catch {
    return []
  }
}

export async function removeSavedNews(id: string): Promise<boolean> {
  try {
    const response = await fetch(`/api/scraped-news?id=${id}`, { method: 'DELETE' })
    const data = await response.json()
    return data.success
  } catch {
    return false
  }
}

function extractSourceFromUrl(url: string): string {
  try {
    const urlObj = new URL(url)
    const hostname = urlObj.hostname.replace(/^www\./, '')
    return hostname.split('.').slice(0, -1).join(' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') || 'Unknown'
  } catch {
    return 'Unknown'
  }
}

function extractTitleFromUrl(url: string): string {
  try {
    const urlObj = new URL(url)
    const pathParts = urlObj.pathname.split('/').filter(p => p.length > 0)
    if (pathParts.length > 0) {
      return pathParts[pathParts.length - 1].replace(/[-_]/g, ' ').replace(/\.(html|htm|php)$/, '').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
    }
    return urlObj.hostname.replace(/^www\./, '').charAt(0).toUpperCase() + urlObj.hostname.slice(1) + ' Homepage'
  } catch {
    return 'News Article'
  }
}

function detectCategory(title: string, description: string): string {
  const text = (title + ' ' + description).toLowerCase()
  
  // Sports (high priority - specific match patterns)
  if (text.match(/\b(sports?|football|soccer|basketball|baseball|tennis|cricket|rugby|hockey|golf|olympics?|athlete|match|game|team|player|championship|tournament|league|score|win|goal|nfl|nba|mlb|nhl|fifa|uefa|ipl)\b/)) return 'sports'
  
  // Politics
  if (text.match(/\b(politics?|political|election|vote|voting|government|minister|prime minister|president|parliament|congress|senate|policy|law|legislation|party|democrat|republican|campaign|candidate|politician|diplomacy|brexit)\b/)) return 'politics'
  
  // Entertainment
  if (text.match(/\b(entertainment|movie|film|cinema|actor|actress|celebrity|music|album|song|concert|hollywood|bollywood|show|series|tv|television|netflix|streaming|performance|award|premiere)\b/)) return 'entertainment'
  
  // Technology
  if (text.match(/\b(tech|technology|software|ai|artificial intelligence|computer|digital|internet|app|startup|gadget|device|smartphone|iphone|android|cyber|data|programming|robot|automation|blockchain|crypto|bitcoin)\b/)) return 'technology'
  
  // Business
  if (text.match(/\b(business|economy|economic|market|stock|finance|financial|investment|investor|company|corporate|ceo|entrepreneur|trade|commerce|industry|manufacturing|revenue|profit|loss|earnings|gdp|inflation|banking|bank)\b/)) return 'business'
  
  // Science
  if (text.match(/\b(science|scientific|research|study|discovery|space|nasa|mars|moon|astronomy|physics|chemistry|biology|experiment|scientist|laboratory|dna|gene|quantum)\b/)) return 'science'
  
  // Health
  if (text.match(/\b(health|medical|medicine|healthcare|doctor|hospital|clinic|patient|disease|illness|virus|pandemic|vaccine|treatment|cure|surgery|mental health|wellness|fitness|nutrition|diet|cancer|covid)\b/)) return 'health'
  
  // Crime
  if (text.match(/\b(crime|criminal|police|arrest|murder|theft|robbery|assault|investigation|court|trial|lawyer|judge|sentence|prison|jail|fraud|scam|corruption|illegal|drug|weapon|gun|shooting)\b/)) return 'crime'
  
  // Environment
  if (text.match(/\b(environment|climate change|global warming|pollution|carbon|emissions|green|sustainable|renewable|energy|solar|wind|recycling|conservation|wildlife|nature|forest|ocean|weather|disaster|flood|earthquake|hurricane)\b/)) return 'environment'
  
  // Education
  if (text.match(/\b(education|school|university|college|student|teacher|professor|academic|study|exam|test|grade|degree|scholarship|learning|campus|admission|enrollment|curriculum)\b/)) return 'education'
  
  // Travel
  if (text.match(/\b(travel|tourism|tourist|vacation|holiday|trip|journey|flight|airline|airport|hotel|resort|destination|passport|visa|booking|adventure|explore)\b/)) return 'travel'
  
  // Food
  if (text.match(/\b(food|cuisine|restaurant|chef|cooking|recipe|meal|dish|flavor|taste|dining|gastronomy|organic|vegan|vegetarian|diet|nutrition|culinary|bakery|cafe)\b/)) return 'food'
  
  return 'general'
}

function formatTimeAgo(timestamp: string): string {
  try {
    const date = new Date(timestamp)
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000)
    if (seconds < 60) return 'Just now'
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`
    if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`
    return date.toLocaleDateString()
  } catch {
    return 'Recently'
  }
}

function findBestImage(scrapedData: any, title: string): string | undefined {
  const candidates = [
    scrapedData.scraped_data?.images?.[0]?.url,
    scrapedData.scraped_data?.metadata?.image,
    scrapedData.scraped_data?.metadata?.ogImage,
    scrapedData.sidebar_videos?.videos?.[0]?.thumbnail,
  ]
  const valid = candidates.find(url => {
    if (!url || typeof url !== 'string') return false
    try {
      const u = new URL(url)
      return u.protocol === 'http:' || u.protocol === 'https:'
    } catch {
      return false
    }
  })
  return valid || `https://source.unsplash.com/800x600/?news,${encodeURIComponent(title.split(' ').slice(0, 4).join(' '))}`
}

function extractRelatedVideos(scrapedData: any) {
  const videos = scrapedData.sidebar_videos?.videos || scrapedData.related_videos || []
  if (!Array.isArray(videos)) return undefined
  const mapped = videos.filter((v: any) => v && v.url).map((v: any) => ({
    title: v.title || 'Related Video',
    url: v.url,
    thumbnail: v.thumbnail,
    duration: v.duration,
    source: v.source
  }))
  return mapped.length ? mapped : undefined
}
