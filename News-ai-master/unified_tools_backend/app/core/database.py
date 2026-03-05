from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
import os
from typing import Optional
from datetime import datetime

class DatabaseService:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.database_name = os.getenv("DATABASE_NAME", "news_ai_db")

    async def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.database = self.client[self.database_name]
            # Test the connection
            await self.client.admin.command('ping')
            print("MongoDB connection established")
            return True
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            self.client = None
            self.database = None
            return False

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")

    async def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        if not self.database:
            raise ConnectionError("Database not connected")
        return self.database[collection_name]

    # News Items Operations
    async def save_news_item(self, news_item: dict) -> str:
        """Save a news item to the database"""
        collection = await self.get_collection("news_items")
        news_item["created_at"] = datetime.now().isoformat()
        news_item["updated_at"] = datetime.now().isoformat()

        result = await collection.insert_one(news_item)
        return str(result.inserted_id)

    async def get_news_item(self, item_id: str) -> Optional[dict]:
        """Get a news item by ID"""
        collection = await self.get_collection("news_items")
        return await collection.find_one({"_id": item_id})

    async def update_news_item(self, item_id: str, updates: dict) -> bool:
        """Update a news item"""
        collection = await self.get_collection("news_items")
        updates["updated_at"] = datetime.now().isoformat()

        result = await collection.update_one(
            {"_id": item_id},
            {"$set": updates}
        )
        return result.modified_count > 0

    async def get_news_by_status(self, status: str, limit: int = 100) -> list:
        """Get news items by status"""
        collection = await self.get_collection("news_items")
        cursor = collection.find({"status": status}).limit(limit)
        return await cursor.to_list(length=limit)

    # Agent Tasks Operations
    async def save_agent_task(self, task: dict) -> str:
        """Save an agent task"""
        collection = await self.get_collection("agent_tasks")
        task["created_at"] = datetime.now().isoformat()
        task["updated_at"] = datetime.now().isoformat()

        result = await collection.insert_one(task)
        return str(result.inserted_id)

    async def get_agent_task(self, task_id: str) -> Optional[dict]:
        """Get an agent task by ID"""
        collection = await self.get_collection("agent_tasks")
        return await collection.find_one({"_id": task_id})

    async def update_agent_task(self, task_id: str, updates: dict) -> bool:
        """Update an agent task"""
        collection = await self.get_collection("agent_tasks")
        updates["updated_at"] = datetime.now().isoformat()

        result = await collection.update_one(
            {"_id": task_id},
            {"$set": updates}
        )
        return result.modified_count > 0

    async def get_pending_tasks(self, agent_id: Optional[str] = None, limit: int = 50) -> list:
        """Get pending tasks, optionally filtered by agent"""
        collection = await self.get_collection("agent_tasks")
        query = {"status": "pending"}
        if agent_id:
            query["agent_id"] = agent_id

        cursor = collection.find(query).sort("priority", -1).limit(limit)
        return await cursor.to_list(length=limit)

    # RL Feedback Operations
    async def save_rl_feedback(self, feedback: dict) -> str:
        """Save RL feedback"""
        collection = await self.get_collection("rl_feedback")
        feedback["created_at"] = datetime.now().isoformat()

        result = await collection.insert_one(feedback)
        return str(result.inserted_id)

    async def get_feedback_by_news_item(self, news_item_id: str) -> list:
        """Get all feedback for a news item"""
        collection = await self.get_collection("rl_feedback")
        cursor = collection.find({"news_item_id": news_item_id}).sort("created_at", -1)
        return await cursor.to_list(length=None)

# Global instance
db_service = DatabaseService()