import AnalyzeClient from './AnalyzeClient'

interface AnalyzePageProps {
  searchParams?: {
    [key: string]: string | string[] | undefined
  }
}

export default function AnalyzePage({ searchParams }: AnalyzePageProps) {
  const rawUrl = searchParams?.url
  const initialUrl = Array.isArray(rawUrl) ? rawUrl[0] : rawUrl

  return <AnalyzeClient initialUrl={typeof initialUrl === 'string' ? initialUrl : undefined} />
}

