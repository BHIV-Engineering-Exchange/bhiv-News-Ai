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
    def __init__(self):
        """Initialize MongoDB connection from environment"""
        self.mongodb_url = os.getenv("MONGODB_URL")
        self.database_name = os.getenv("DATABASE_NAME", "news_ai_db")
        self.client = None
        self.db = None
        
        # Validate required environment variable
        if not self.mongodb_url:
            error_msg = (
                "ERROR: MONGODB_URL environment variable is not set.\n"
                "Required for production deployment on Render.\n"
                "Please set MONGODB_URL in Render environment variables.\n"
                "Connection string must include:"
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
        # scraped_news collection
        if "scraped_news" not in self.db.list_collection_names():
            self.db.create_collection("scraped_news")
        
        scraped_news = self.db["scraped_news"]
        scraped_news.create_index("id", unique=True, sparse=True)
        scraped_news.create_index("url")
        scraped_news.create_index("scrapedAt")
        scraped_news.create_index("category")
        
        # api_usage collection
        if "api_usage" not in self.db.list_collection_names():
            self.db.create_collection("api_usage")
        
        api_usage = self.db["api_usage"]
        api_usage.create_index("endpoint")
        api_usage.create_index("timestamp")
        api_usage.create_index("user_id")
        
        # user_sessions collection
        if "user_sessions" not in self.db.list_collection_names():
            self.db.create_collection("user_sessions")
        
        user_sessions = self.db["user_sessions"]
        user_sessions.create_index("user_id", unique=True)
        user_sessions.create_index("expires_at", expireAfterSeconds=0)
    
    def get_scraped_news(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get scraped news articles"""
        try:
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
            scraped_news = self.db["scraped_news"]
            result = scraped_news.delete_one({"id": news_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting scraped news: {e}")
            return False
    
    def get_scraped_news_count(self) -> int:
        """Get total count of scraped news items"""
        try:
            scraped_news = self.db["scraped_news"]
            return scraped_news.count_documents({})
        except Exception as e:
            print(f"Error counting scraped news: {e}")
            return 0
    
    def log_api_usage(self, endpoint: str, user_id: Optional[str], response_status: int, response_time: float) -> bool:
        """Log API usage for analytics"""
        try:
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