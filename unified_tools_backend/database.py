import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables from .env file (development)
load_dotenv()

class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize DatabaseManager.

        If `db_path` is provided, a lightweight SQLite database is created for
        testing. Otherwise a MongoDB connection is used in production.
        """
        self.use_sqlite = bool(db_path)
        self.sqlite_path = db_path
        self.client = None
        self.db = None

        if self.use_sqlite:
            # Initialize sqlite3 for tests
            # Keep no persistent file handle open so tests can delete the DB file.
            self.sqlite_conn = None
            self._init_sqlite_tables()
            # Provide a simple DB-like attribute for compatibility
            self.db = None
            return

        # MongoDB production path
        self.mongodb_url = os.getenv("MONGODB_URL")
        self.database_name = os.getenv("DATABASE_NAME", "news_ai_db")

        # Validate required environment variable
        if not self.mongodb_url:
            error_msg = (
                "ERROR: MONGODB_URL environment variable is not set.\n"
                "Required for production deployment on Render.\n"
                "Please set MONGODB_URL in Render environment variables.\n"
                "Connection string must include:\n"
                "  - Username and password (URL-encoded)\n"
                "  - MongoDB Atlas cluster URL\n"
                "Example: mongodb+srv://user:pass%40word@cluster.mongodb.net/?appName=YourApp"
            )
            print(error_msg, file=sys.stderr)
            raise EnvironmentError(error_msg)

        # Log connection attempt (mask password for security)
        masked_url = self._mask_connection_string(self.mongodb_url)
        print(f"Attempting MongoDB connection: {masked_url}")
        self._connect()
    
    def _mask_connection_string(self, url: str) -> str:
        """Mask password in connection string for logging"""
        import re
        return re.sub(r'(mongodb\+srv://[^:]+:)([^@]+)(@)', r'\1***\3', url)
    
    def _connect(self):
        """Establish MongoDB connection with retry logic"""
        try:
            print("Initializing PyMongo client...", file=sys.stderr)
            self.client = MongoClient(
                self.mongodb_url,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                retryWrites=True,
                maxPoolSize=50,
                minPoolSize=10
            )
            
            # Verify connection with ping
            print("Pinging MongoDB server...", file=sys.stderr)
            self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            self._init_collections()
            
            print(f"✓ Successfully connected to MongoDB database: {self.database_name}", file=sys.stderr)
            print(f"✓ MongoDB collections initialized", file=sys.stderr)
            
        except ServerSelectionTimeoutError as e:
            error_msg = (
                f"✗ MongoDB Server Selection Timeout: {str(e)}\n"
                f"MongoDB Atlas might be unreachable or connection parameters are incorrect.\n"
                f"Verify:\n"
                f"  1. MONGODB_URL is correctly set in environment\n"
                f"  2. IP is whitelisted in MongoDB Atlas security settings\n"
                f"  3. Database user credentials are correct\n"
                f"  4. Special characters in password are URL-encoded"
            )
            print(error_msg, file=sys.stderr)
            raise ConnectionError(error_msg) from e
            
        except ConnectionFailure as e:
            error_msg = (
                f"✗ MongoDB Connection Failed: {str(e)}\n"
                f"Cannot establish connection to MongoDB Atlas.\n"
                f"Verify MONGODB_URL environment variable."
            )
            print(error_msg, file=sys.stderr)
            raise ConnectionError(error_msg) from e
    
    def _init_collections(self):
        """Initialize collections with indexes"""
        # MongoDB collection initialization handled in _connect
        return

    def _open_sqlite_connection(self):
        """Open a short-lived SQLite connection for a single operation."""
        import sqlite3
        conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite_tables(self):
        """Create SQLite tables used by tests."""
        conn = self._open_sqlite_connection()
        try:
            cur = conn.cursor()
            # scraped_news table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS scraped_news (
                    id TEXT PRIMARY KEY,
                    url TEXT,
                    scrapedAt TEXT,
                    category TEXT,
                    content TEXT
                )
                """
            )

            # api_usage table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT,
                    timestamp TEXT,
                    user_id TEXT,
                    response_status INTEGER,
                    response_time REAL
                )
                """
            )

            # user_sessions table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    user_id TEXT PRIMARY KEY,
                    expires_at TEXT
                )
                """
            )
            conn.commit()
        finally:
            conn.close()
    
    def get_scraped_news(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get scraped news articles"""
        try:
            if self.use_sqlite:
                conn = self._open_sqlite_connection()
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT id, url, scrapedAt, category, content FROM scraped_news ORDER BY scrapedAt DESC LIMIT ? OFFSET ?",
                        (limit, offset)
                    )
                    rows = cur.fetchall()
                    result = []
                    for r in rows:
                        result.append({
                            "id": r[0],
                            "url": r[1],
                            "scrapedAt": r[2],
                            "category": r[3],
                            "content": r[4]
                        })
                    return result
                finally:
                    conn.close()

            scraped_news = self.db["scraped_news"]
            cursor = scraped_news.find({}).sort("scrapedAt", -1).skip(offset).limit(limit)

            result = []
            for doc in cursor:
                doc.pop("_id", None)  # Remove MongoDB's internal ID
                result.append(doc)

            return result
        except Exception as e:
            print(f"Error retrieving scraped news: {e}")
            return []
    
    def add_scraped_news(self, news_item: Dict[str, Any]) -> bool:
        """Add a scraped news item"""
        try:
            if self.use_sqlite:
                conn = self._open_sqlite_connection()
                try:
                    cur = conn.cursor()
                    news_item["scrapedAt"] = news_item.get("scrapedAt", datetime.now().isoformat())
                    cur.execute(
                        "INSERT OR REPLACE INTO scraped_news (id, url, scrapedAt, category, content) VALUES (?, ?, ?, ?, ?)",
                        (
                            news_item.get("id"),
                            news_item.get("url"),
                            news_item.get("scrapedAt"),
                            news_item.get("category"),
                            news_item.get("content"),
                        ),
                    )
                    conn.commit()
                    return cur.rowcount > 0
                finally:
                    conn.close()

            scraped_news = self.db["scraped_news"]
            news_item["scrapedAt"] = news_item.get("scrapedAt", datetime.now().isoformat())

            result = scraped_news.update_one(
                {"id": news_item.get("id")},
                {"$set": news_item},
                upsert=True
            )

            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            print(f"Error adding scraped news: {e}")
            return False
    
    def delete_scraped_news(self, news_id: str) -> bool:
        """Delete a scraped news item by ID"""
        try:
            if self.use_sqlite:
                conn = self._open_sqlite_connection()
                try:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM scraped_news WHERE id = ?", (news_id,))
                    conn.commit()
                    return cur.rowcount > 0
                finally:
                    conn.close()

            scraped_news = self.db["scraped_news"]
            result = scraped_news.delete_one({"id": news_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting scraped news: {e}")
            return False
    
    def get_scraped_news_count(self) -> int:
        """Get total count of scraped news items"""
        try:
            if self.use_sqlite:
                conn = self._open_sqlite_connection()
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM scraped_news")
                    return cur.fetchone()[0]
                finally:
                    conn.close()

            scraped_news = self.db["scraped_news"]
            return scraped_news.count_documents({})
        except Exception as e:
            print(f"Error counting scraped news: {e}")
            return 0
    
    def log_api_usage(self, endpoint: str, user_id: Optional[str], response_status: int, response_time: float) -> bool:
        """Log API usage for analytics"""
        try:
            if self.use_sqlite:
                conn = self._open_sqlite_connection()
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO api_usage (endpoint, timestamp, user_id, response_status, response_time) VALUES (?, ?, ?, ?, ?)",
                        (endpoint, datetime.now().isoformat(), user_id, response_status, response_time),
                    )
                    conn.commit()
                    return cur.rowcount > 0
                finally:
                    conn.close()

            api_usage = self.db["api_usage"]
            log_entry = {
                "endpoint": endpoint,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "response_status": response_status,
                "response_time": response_time
            }

            result = api_usage.insert_one(log_entry)
            return result.inserted_id is not None
        except Exception as e:
            print(f"Error logging API usage: {e}")
            return False
    
    def get_api_usage_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get API usage statistics for the last N days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            if self.use_sqlite:
                conn = self._open_sqlite_connection()
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT COUNT(*), AVG(response_time) FROM api_usage WHERE timestamp >= ?",
                        (cutoff_date,)
                    )
                    row = cur.fetchone()
                    total_requests = row[0] or 0
                    avg_response_time = row[1] or 0

                    cur.execute(
                        "SELECT endpoint, COUNT(*), AVG(response_time) FROM api_usage WHERE timestamp >= ? GROUP BY endpoint ORDER BY COUNT(*) DESC",
                        (cutoff_date,)
                    )
                    endpoints = [
                        {"endpoint": r[0], "count": r[1], "avg_time": r[2]} for r in cur.fetchall()
                    ]

                    stats = {
                        "total_requests": total_requests,
                        "avg_response_time": avg_response_time,
                        "unique_endpoints": len(endpoints),
                        "endpoints": endpoints
                    }
                    return stats
                finally:
                    conn.close()

            api_usage = self.db["api_usage"]
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get total requests and avg response time
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_date}}},
                {
                    "$group": {
                        "_id": None,
                        "total_requests": {"$sum": 1},
                        "avg_response_time": {"$avg": "$response_time"},
                        "unique_endpoints": {"$addToSet": "$endpoint"}
                    }
                }
            ]
            
            result = list(api_usage.aggregate(pipeline))
            stats = {
                "total_requests": result[0]["total_requests"] if result else 0,
                "avg_response_time": result[0]["avg_response_time"] if result else 0,
                "unique_endpoints": len(result[0]["unique_endpoints"]) if result else 0,
                "endpoints": []
            }
            
            # Get endpoint breakdown
            endpoint_pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_date}}},
                {
                    "$group": {
                        "_id": "$endpoint",
                        "count": {"$sum": 1},
                        "avg_time": {"$avg": "$response_time"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            endpoints = list(api_usage.aggregate(endpoint_pipeline))
            stats["endpoints"] = [
                {"endpoint": ep["_id"], "count": ep["count"], "avg_time": ep["avg_time"]}
                for ep in endpoints
            ]
            
            return stats
        except Exception as e:
            print(f"Error getting API usage stats: {e}")
            return {"total_requests": 0, "avg_response_time": 0, "unique_endpoints": 0, "endpoints": []}
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """Clean up old scraped news and API usage data"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            deleted_count = 0
            if self.use_sqlite:
                conn = self._open_sqlite_connection()
                try:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM scraped_news WHERE scrapedAt < ?", (cutoff_date,))
                    deleted_count += cur.rowcount
                    cur.execute("DELETE FROM api_usage WHERE timestamp < ?", (cutoff_date,))
                    deleted_count += cur.rowcount
                    cur.execute("DELETE FROM user_sessions WHERE expires_at < ?", (datetime.now().isoformat(),))
                    deleted_count += cur.rowcount
                    conn.commit()
                    return deleted_count
                finally:
                    conn.close()

            # Delete old scraped news
            scraped_news = self.db["scraped_news"]
            result1 = scraped_news.delete_many({"scrapedAt": {"$lt": cutoff_date}})
            deleted_count += result1.deleted_count
            
            # Delete old API usage logs
            api_usage = self.db["api_usage"]
            result2 = api_usage.delete_many({"timestamp": {"$lt": cutoff_date}})
            deleted_count += result2.deleted_count
            
            # Delete expired sessions
            user_sessions = self.db["user_sessions"]
            result3 = user_sessions.delete_many({"expires_at": {"$lt": datetime.now().isoformat()}})
            deleted_count += result3.deleted_count
            
            return deleted_count
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            return 0
    
    def close(self):
        """Close MongoDB connection"""
        if self.use_sqlite:
            # SQLite uses short-lived connections per operation.
            return

        if self.client:
            try:
                self.client.close()
                print("✓ MongoDB connection closed", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Error closing MongoDB connection: {e}", file=sys.stderr)
    
    def __del__(self):
        """Ensure connection is closed on cleanup"""
        try:
            self.close()
        except Exception as e:
            # Silently ignore errors during cleanup
            pass

# Global database instance (lazy initialization)
_db_manager = None
_db_connection_error = None

def init_db():
    """Initialize database connection at app startup"""
    global _db_manager, _db_connection_error
    try:
        # If no MongoDB URL is configured (common in test runs), create
        # an in-memory SQLite manager so the app startup does not fail.
        mongodb_url = os.getenv("MONGODB_URL")
        if not mongodb_url:
            _db_manager = DatabaseManager(db_path=":memory:")
        else:
            _db_manager = DatabaseManager()
        _db_connection_error = None
        return _db_manager
    except (EnvironmentError, ConnectionError) as e:
        _db_connection_error = str(e)
        print(f"Database initialization failed: {e}", file=sys.stderr)
        return None

def get_db() -> DatabaseManager:
    """Get database manager instance"""
    global _db_manager, _db_connection_error
    if _db_manager is None:
        if _db_connection_error:
            raise RuntimeError(f"Database unavailable: {_db_connection_error}")
        # Try to initialize if not already attempted
        result = init_db()
        if result is None:
            raise RuntimeError("Failed to initialize database connection")
    return _db_manager

def is_db_ready() -> bool:
    """Check if database is ready"""
    global _db_manager
    return _db_manager is not None