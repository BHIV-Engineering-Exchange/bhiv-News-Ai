import { NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET() {
  try {
    const articles = await prisma.scrapedNews.findMany({
      orderBy: { createdAt: 'desc' },
      take: 100
    })
    return NextResponse.json({ success: true, data: articles })
  } catch (error) {
    console.error('Failed to load articles:', error)
    return NextResponse.json({ success: false, message: 'Failed to load articles' }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    if (!body || !body.url) {
      return NextResponse.json({ success: false, message: 'Invalid payload' }, { status: 400 })
    }

    const article = await prisma.scrapedNews.upsert({
      where: { url: body.url },
      update: {
        title: body.title,
        description: body.description,
        source: body.source,
        category: body.category,
        imageUrl: body.imageUrl,
        publishedAt: body.publishedAt,
        readTime: body.readTime,
        scrapedAt: body.scrapedAt,
        scrapedData: body.scrapedData,
        summary: body.summary,
        insights: body.insights,
        relatedVideos: body.relatedVideos,
        storedAt: new Date().toISOString()
      },
      create: {
        customId: body.id,
        title: body.title,
        description: body.description,
        url: body.url,
        source: body.source,
        category: body.category,
        imageUrl: body.imageUrl,
        publishedAt: body.publishedAt,
        readTime: body.readTime,
        scrapedAt: body.scrapedAt,
        scrapedData: body.scrapedData,
        summary: body.summary,
        insights: body.insights,
        relatedVideos: body.relatedVideos,
        storedAt: new Date().toISOString()
      }
    })

    return NextResponse.json({ success: true, data: article })
  } catch (error) {
    console.error('Failed to store article:', error)
    return NextResponse.json({ success: false, message: 'Failed to store article' }, { status: 500 })
  }
}

export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const id = searchParams.get('id')
    
    if (!id) {
      return NextResponse.json({ success: false, message: 'Article ID required' }, { status: 400 })
    }

    await prisma.scrapedNews.delete({
      where: { customId: id }
    })

    return NextResponse.json({ success: true, message: 'Article deleted' })
  } catch (error) {
    console.error('Failed to delete article:', error)
    return NextResponse.json({ success: false, message: 'Failed to delete article' }, { status: 500 })
  }
}
