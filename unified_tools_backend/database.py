import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import threading

class DatabaseManager:
    def __init__(self, db_path: str = "news_ai.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scraped_news (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    url TEXT NOT NULL,
                    source TEXT,
                    category TEXT,
                    publishedAt TEXT,
                    scrapedAt TEXT NOT NULL,
                    content TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT NOT NULL,
                    user_id TEXT,
                    timestamp TEXT NOT NULL,
                    response_status INTEGER,
                    response_time REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    user_id TEXT PRIMARY KEY,
                    token TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL
                )
            """)
            conn.commit()
    
    def get_scraped_news(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get scraped news articles"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM scraped_news ORDER BY scrapedAt DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                item = dict(row)
                # Parse JSON fields if they exist
                if item.get('metadata'):
                    try:
                        item['metadata'] = json.loads(item['metadata'])
                    except:
                        item['metadata'] = {}
                result.append(item)
            
            return result
    
    def add_scraped_news(self, news_item: Dict[str, Any]) -> bool:
        """Add a scraped news item"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                try:
                    # Prepare metadata as JSON string
                    metadata = json.dumps(news_item.get('metadata', {}))
                    
                    conn.execute("""
                        INSERT OR REPLACE INTO scraped_news 
                        (id, title, description, url, source, category, publishedAt, scrapedAt, content, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        news_item.get('id'),
                        news_item.get('title'),
                        news_item.get('description'),
                        news_item.get('url'),
                        news_item.get('source'),
                        news_item.get('category'),
                        news_item.get('publishedAt'),
                        news_item.get('scrapedAt', datetime.now().isoformat()),
                        news_item.get('content'),
                        metadata
                    ))
                    conn.commit()
                    return True
                except Exception as e:
                    print(f"Error adding scraped news: {e}")
                    return False
    
    def delete_scraped_news(self, news_id: str) -> bool:
        """Delete a scraped news item by ID"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                try:
                    cursor = conn.execute("DELETE FROM scraped_news WHERE id = ?", (news_id,))
                    conn.commit()
                    return cursor.rowcount > 0
                except Exception as e:
                    print(f"Error deleting scraped news: {e}")
                    return False
    
    def get_scraped_news_count(self) -> int:
        """Get total count of scraped news items"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM scraped_news")
            result = cursor.fetchone()
            return result[0] if result else 0
    
    def log_api_usage(self, endpoint: str, user_id: Optional[str], response_status: int, response_time: float) -> bool:
        """Log API usage for analytics"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                try:
                    conn.execute("""
                        INSERT INTO api_usage (endpoint, user_id, timestamp, response_status, response_time)
                        VALUES (?, ?, ?, ?, ?)
                    """, (endpoint, user_id, datetime.now().isoformat(), response_status, response_time))
                    conn.commit()
                    return True
                except Exception as e:
                    print(f"Error logging API usage: {e}")
                    return False
    
    def get_api_usage_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get API usage statistics for the last N days"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get total requests
            cursor = conn.execute("""
                SELECT COUNT(*) as total_requests, 
                       AVG(response_time) as avg_response_time,
                       COUNT(DISTINCT endpoint) as unique_endpoints
                FROM api_usage 
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days))
            
            stats = dict(cursor.fetchone())
            
            # Get endpoint breakdown
            cursor = conn.execute("""
                SELECT endpoint, COUNT(*) as count, AVG(response_time) as avg_time
                FROM api_usage 
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY endpoint
                ORDER BY count DESC
            """.format(days))
            
            stats['endpoints'] = [dict(row) for row in cursor.fetchall()]
            
            return stats
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """Clean up old scraped news and API usage data"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                try:
                    # Delete old scraped news
                    cursor1 = conn.execute("""
                        DELETE FROM scraped_news 
                        WHERE scrapedAt < datetime('now', '-{} days')
                    """.format(days))
                    
                    # Delete old API usage logs
                    cursor2 = conn.execute("""
                        DELETE FROM api_usage 
                        WHERE timestamp < datetime('now', '-{} days')
                    """.format(days))
                    
                    # Delete expired sessions
                    cursor3 = conn.execute("""
                        DELETE FROM user_sessions 
                        WHERE expires_at < datetime('now')
                    """)
                    
                    conn.commit()
                    return cursor1.rowcount + cursor2.rowcount + cursor3.rowcount
                except Exception as e:
                    print(f"Error cleaning up old data: {e}")
                    return 0

# Global database instance
db_manager = DatabaseManager()

def get_db() -> DatabaseManager:
    """Get database manager instance"""
    return db_manager