import httpx
import websockets
import json
import asyncio
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.database import db_service

class BHIVPushService:
    def __init__(self):
        self.bhiv_core_url = os.getenv("BHIV_CORE_URL", "http://localhost:8080")
        self.bhiv_api_key = os.getenv("BHIV_API_KEY")
        self.websocket_host = os.getenv("WEBSOCKET_HOST", "localhost")
        self.websocket_port = int(os.getenv("WEBSOCKET_PORT", "8765"))
        self.connected_clients: List[websockets.WebSocketServerProtocol] = []
        self.timeout = 30.0

    async def push_to_bhiv_core(self, channel: str, avatar: str, content: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Push processed content to BHIV Core for TTV/Vaani generation"""
        try:
            if not self.bhiv_api_key:
                return {"error": "BHIV API key not configured"}

            # Prepare Seeya-compatible JSON payload
            payload = self._format_seeya_payload(channel, avatar, content, metadata)

            url = f"{self.bhiv_core_url}/api/content/push"
            headers = {
                "Authorization": f"Bearer {self.bhiv_api_key}",
                "Content-Type": "application/json",
                "X-Source": "news-ai-backend"
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    push_record = {
                        "channel": channel,
                        "avatar": avatar,
                        "content_id": content.get("id", ""),
                        "push_timestamp": datetime.now().isoformat(),
                        "bhiv_response": result,
                        "status": "pushed"
                    }

                    # Log push to database
                    if db_service.database:
                        await db_service.save_bhiv_push(push_record)

                    # Broadcast to WebSocket clients
                    await self._broadcast_websocket_update({
                        "type": "bhiv_push",
                        "channel": channel,
                        "avatar": avatar,
                        "content": content,
                        "timestamp": datetime.now().isoformat()
                    })

                    return {
                        "success": True,
                        "push_id": result.get("push_id", ""),
                        "status": "pushed",
                        "channel": channel,
                        "avatar": avatar,
                        "processed_at": datetime.now().isoformat()
                    }
                else:
                    return {
                        "error": f"BHIV push failed: {response.status_code}",
                        "response": response.text
                    }

        except Exception as e:
            return {"error": f"BHIV push error: {str(e)}"}

    def _format_seeya_payload(self, channel: str, avatar: str, content: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format content into Seeya orchestration compatible JSON structure"""
        return {
            "orchestration_request": {
                "request_id": f"news_ai_{datetime.now().timestamp()}",
                "timestamp": datetime.now().isoformat(),
                "source": "news_ai_backend",
                "version": "1.0"
            },
            "content": {
                "id": content.get("id", f"news_{datetime.now().timestamp()}"),
                "type": "news_article",
                "title": content.get("title", ""),
                "summary": content.get("summary", ""),
                "full_content": content.get("content", ""),
                "categories": content.get("categories", []),
                "sentiment": content.get("sentiment_analysis", {}),
                "authenticity_score": content.get("authenticity_score", 0),
                "metadata": {
                    "word_count": len(content.get("content", "").split()),
                    "reading_time_minutes": max(1, len(content.get("content", "").split()) // 200),
                    "source_url": content.get("url", ""),
                    "scraped_at": content.get("scraped_at", ""),
                    "processed_at": datetime.now().isoformat()
                }
            },
            "video_generation": {
                "channel": channel,
                "avatar": avatar,
                "script": content.get("video_script", ""),
                "style": "news_broadcast",
                "duration_target": "30-60_seconds",
                "quality": "high",
                "platform_optimization": {
                    "youtube": True,
                    "tiktok": False,
                    "instagram": False
                }
            },
            "distribution": {
                "channels": [channel],
                "avatars": [avatar],
                "auto_publish": True,
                "schedule": "immediate"
            },
            "analytics": {
                "track_performance": True,
                "measure_engagement": True,
                "rl_feedback_enabled": True,
                "reward_score": content.get("reward_score", 0.0)
            },
            "additional_metadata": metadata or {}
        }

    async def check_bhiv_status(self) -> Dict[str, Any]:
        """Check BHIV Core connectivity and status"""
        try:
            if not self.bhiv_api_key:
                return {"status": "not_configured", "message": "BHIV API key not set"}

            url = f"{self.bhiv_core_url}/health"
            headers = {
                "Authorization": f"Bearer {self.bhiv_api_key}"
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    health_data = response.json()
                    return {
                        "status": "healthy",
                        "bhiv_core_url": self.bhiv_core_url,
                        "response_time_ms": None,  # Could measure this
                        "services": health_data.get("services", {}),
                        "last_checked": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}",
                        "bhiv_core_url": self.bhiv_core_url,
                        "last_checked": datetime.now().isoformat()
                    }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "bhiv_core_url": self.bhiv_core_url,
                "last_checked": datetime.now().isoformat()
            }

    async def push_channel_avatar_matrix(self, content: Dict[str, Any], channels: List[str], avatars: List[str]) -> Dict[str, Any]:
        """Push content to multiple channel-avatar combinations (3x3 matrix)"""
        results = []
        successful_pushes = 0

        for channel in channels:
            for avatar in avatars:
                try:
                    push_result = await self.push_to_bhiv_core(channel, avatar, content)
                    results.append({
                        "channel": channel,
                        "avatar": avatar,
                        "success": push_result.get("success", False),
                        "push_id": push_result.get("push_id", ""),
                        "error": push_result.get("error", "")
                    })

                    if push_result.get("success"):
                        successful_pushes += 1

                    # Small delay to avoid overwhelming BHIV Core
                    await asyncio.sleep(0.1)

                except Exception as e:
                    results.append({
                        "channel": channel,
                        "avatar": avatar,
                        "success": False,
                        "error": str(e)
                    })

        # Broadcast matrix completion to WebSocket clients
        await self._broadcast_websocket_update({
            "type": "matrix_push_complete",
            "total_combinations": len(channels) * len(avatars),
            "successful_pushes": successful_pushes,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "matrix_push_complete": True,
            "total_combinations": len(channels) * len(avatars),
            "successful_pushes": successful_pushes,
            "success_rate": successful_pushes / (len(channels) * len(avatars)) if channels and avatars else 0,
            "results": results,
            "completed_at": datetime.now().isoformat()
        }

    async def start_websocket_server(self):
        """Start WebSocket server for real-time updates"""
        try:
            server = await websockets.serve(
                self._handle_websocket_connection,
                self.websocket_host,
                self.websocket_port
            )
            print(f"✅ WebSocket server started on ws://{self.websocket_host}:{self.websocket_port}")
            return server
        except Exception as e:
            print(f"❌ WebSocket server failed to start: {e}")
            return None

    async def _handle_websocket_connection(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle individual WebSocket connections"""
        self.connected_clients.append(websocket)
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                "type": "connection_established",
                "message": "Connected to News AI Backend WebSocket",
                "timestamp": datetime.now().isoformat()
            }))

            # Keep connection alive and handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    # Handle client messages if needed
                    if data.get("type") == "ping":
                        await websocket.send(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }))
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON received",
                        "timestamp": datetime.now().isoformat()
                    }))

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)

    async def _broadcast_websocket_update(self, data: Dict[str, Any]):
        """Broadcast update to all connected WebSocket clients"""
        if not self.connected_clients:
            return

        message = json.dumps(data)

        # Send to all connected clients
        disconnected_clients = []
        for client in self.connected_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client)

        # Remove disconnected clients
        for client in disconnected_clients:
            if client in self.connected_clients:
                self.connected_clients.remove(client)

    async def get_push_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent BHIV push history"""
        try:
            if not db_service.database:
                return []

            collection = await db_service.get_collection("bhiv_pushes")
            cursor = collection.find().sort("push_timestamp", -1).limit(limit)
            pushes = await cursor.to_list(length=limit)
            return pushes
        except Exception as e:
            print(f"Error retrieving push history: {e}")
            return []

    async def get_websocket_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "connected_clients": len(self.connected_clients),
            "websocket_host": self.websocket_host,
            "websocket_port": self.websocket_port,
            "server_status": "running",
            "last_updated": datetime.now().isoformat()
        }

# Extend database service for BHIV operations
async def save_bhiv_push(push_record: dict) -> str:
    """Save BHIV push record to database"""
    if not db_service.database:
        return ""

    collection = await db_service.get_collection("bhiv_pushes")
    push_record["created_at"] = datetime.now().isoformat()

    result = await collection.insert_one(push_record)
    return str(result.inserted_id)

# Add method to database service
db_service.save_bhiv_push = save_bhiv_push

# Global instance
bhiv_service = BHIVPushService()