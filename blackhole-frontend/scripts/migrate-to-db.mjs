import fs from 'fs';
import path from 'path';
import pg from 'pg';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config({ path: '.env.local' });

const { Client } = pg;
const connectionString = process.env.DATABASE_URL;
const DATA_FILE = path.join(process.cwd(), 'data', 'news-articles.json');

async function migrate() {
    const client = new Client({ connectionString });

    try {
        console.log('🔌 Connecting to Supabase via Direct PG Driver...');
        await client.connect();
        console.log('✅ Connected!');

        if (!fs.existsSync(DATA_FILE)) {
            console.error('❌ JSON file not found');
            return;
        }

        const articles = JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8'));
        console.log(`📦 Found ${articles.length} articles to move...`);

        for (const article of articles) {
            const query = `
        INSERT INTO "ScrapedNews" 
        ("id", "customId", "title", "description", "url", "source", "category", "imageUrl", "publishedAt", "readTime", "scrapedAt", "scrapedData", "summary", "insights", "relatedVideos", "storedAt", "updatedAt") 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, NOW())
        ON CONFLICT (url) DO UPDATE SET
        "title" = EXCLUDED."title",
        "description" = EXCLUDED."description",
        "updatedAt" = NOW();
      `;

            const values = [
                `scraped_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                article.id,
                article.title,
                article.description,
                article.url,
                article.source,
                article.category,
                article.imageUrl,
                article.publishedAt,
                article.readTime,
                article.scrapedAt,
                JSON.stringify(article.scrapedData || {}),
                article.summary,
                JSON.stringify(article.insights || {}),
                JSON.stringify(article.relatedVideos || []),
                article.storedAt || new Date().toISOString()
            ];

            await client.query(query, values);
            process.stdout.write('🟢');
        }

        console.log('\n\n🏁 Success! Your news is now in Supabase.');
    } catch (err) {
        console.error('\n💥 Migration failed:', err.message);
    } finally {
        await client.end();
        process.exit(0);
    }
}

migrate();
