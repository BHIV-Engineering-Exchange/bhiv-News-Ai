from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from app.core.database import db_service
from app.services.uniguru import uniguru_service

class BaseAgent:
    def __init__(self, agent_id: str, name: str, role: str, capabilities: List[str], priority: int = 1):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.priority = priority
        self.status = "active"

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement process_task")

class FetchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="fetch_agent",
            name="News Fetch Agent",
            role="fetch",
            capabilities=["web_scraping", "content_extraction"],
            priority=1
        )

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch and extract news content from URL"""
        url = task_data.get("url")
        if not url:
            return {"error": "No URL provided"}

        try:
            # Simple web scraping (in real implementation, use proper scraping service)
            import requests
            from bs4 import BeautifulSoup

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract basic content
            title = soup.find('title').text.strip() if soup.find('title') else "No title"
            content = ""
            for p in soup.find_all('p')[:10]:  # First 10 paragraphs
                content += p.text.strip() + " "

            return {
                "url": url,
                "title": title,
                "content": content.strip(),
                "scraped_at": datetime.now().isoformat(),
                "status": "fetched"
            }

        except Exception as e:
            return {"error": f"Fetching failed: {str(e)}"}

class FilterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="filter_agent",
            name="Content Filter Agent",
            role="filter",
            capabilities=["content_filtering", "relevance_scoring"],
            priority=2
        )

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter and score content relevance"""
        content = task_data.get("content", "")
        title = task_data.get("title", "")

        if not content:
            return {"error": "No content provided"}

        # Simple relevance scoring
        score = 0
        relevance_keywords = ["news", "breaking", "update", "report", "announcement"]

        text_to_check = (title + " " + content).lower()
        for keyword in relevance_keywords:
            if keyword in text_to_check:
                score += 20

        if len(content.split()) > 100:
            score += 30

        return {
            "relevance_score": min(100, score),
            "is_relevant": score >= 50,
            "filter_criteria": ["keyword_matching", "content_length"],
            "processed_at": datetime.now().isoformat()
        }

class VerifyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="verify_agent",
            name="Authenticity Verification Agent",
            role="verify",
            capabilities=["fact_checking", "source_verification", "bias_detection"],
            priority=3
        )

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify authenticity and credibility"""
        content = task_data.get("content", "")
        title = task_data.get("title", "")
        url = task_data.get("url", "")

        if not content:
            return {"error": "No content provided"}

        # Simple authenticity scoring
        score = 70  # Base score

        # Check for source indicators
        source_indicators = ["according to", "reported by", "confirmed", "official"]
        indicator_count = sum(1 for indicator in source_indicators if indicator in content.lower())
        score += min(20, indicator_count * 5)

        # Check content quality
        if len(content.split()) > 200:
            score += 10

        return {
            "authenticity_score": min(100, score),
            "credibility_rating": "HIGH" if score >= 80 else "MEDIUM" if score >= 60 else "LOW",
            "verification_method": "content_analysis",
            "processed_at": datetime.now().isoformat()
        }

class ScriptAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="script_agent",
            name="Video Script Generation Agent",
            role="script",
            capabilities=["script_writing", "video_prompts", "content_adaptation"],
            priority=4
        )

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video scripts and prompts"""
        title = task_data.get("title", "")
        content = task_data.get("content", "")
        summary = task_data.get("summary", "")

        if not title and not content:
            return {"error": "No content provided"}

        # Generate simple video script
        script = f"Breaking News: {title}\n\n"
        if summary:
            script += f"{summary}\n\n"
        else:
            script += f"{content[:200]}...\n\n"

        script += "Stay tuned for more updates."

        return {
            "video_script": script,
            "script_length": len(script.split()),
            "video_prompt": f"Create a professional news video about: {title}",
            "estimated_duration": "30-45 seconds",
            "processed_at": datetime.now().isoformat()
        }

class RLFeedbackAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="rl_feedback_agent",
            name="RL Feedback Agent",
            role="rl_feedback",
            capabilities=["reward_calculation", "performance_analysis", "adaptive_learning"],
            priority=5
        )

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate RL reward scores"""
        content = task_data.get("content", "")
        script = task_data.get("script", "")
        authenticity_score = task_data.get("authenticity_score", 50)

        if not content:
            return {"error": "No content provided"}

        # Calculate reward components
        tone_score = self._calculate_tone_score(content)
        engagement_score = self._calculate_engagement_score(content, script)
        quality_score = min(100, authenticity_score + len(content.split()) // 10)

        # Overall reward (weighted average)
        reward_score = (tone_score * 0.3) + (engagement_score * 0.4) + (quality_score * 0.3)

        return {
            "reward_score": round(reward_score, 2),
            "tone_score": tone_score,
            "engagement_score": engagement_score,
            "quality_score": quality_score,
            "correction_needed": reward_score < 60,
            "feedback": "Good quality" if reward_score >= 80 else "Needs improvement" if reward_score >= 60 else "Requires correction",
            "processed_at": datetime.now().isoformat()
        }

    def _calculate_tone_score(self, content: str) -> float:
        """Calculate tone appropriateness score"""
        emotional_words = ["shocking", "outrageous", "unbelievable", "devastating"]
        neutral_words = ["according to", "reported", "stated", "confirmed"]

        emotional_count = sum(1 for word in emotional_words if word in content.lower())
        neutral_count = sum(1 for word in neutral_words if word in content.lower())

        if neutral_count > emotional_count:
            return 90
        elif emotional_count <= 2:
            return 70
        else:
            return 40

    def _calculate_engagement_score(self, content: str, script: str) -> float:
        """Calculate engagement potential score"""
        score = 50

        if len(content.split()) > 150:
            score += 20

        if script and len(script.split()) > 20:
            score += 20

        if any(word in content.lower() for word in ["breaking", "urgent", "important"]):
            score += 10

        return min(100, score)

class AgentRegistry:
    def __init__(self):
        self.agents = {
            "fetch_agent": FetchAgent(),
            "filter_agent": FilterAgent(),
            "verify_agent": VerifyAgent(),
            "script_agent": ScriptAgent(),
            "rl_feedback_agent": RLFeedbackAgent()
        }

    async def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    async def get_agents_by_role(self, role: str) -> List[BaseAgent]:
        """Get all agents with specific role"""
        return [agent for agent in self.agents.values() if agent.role == role]

    async def submit_task(self, agent_id: str, task_data: Dict[str, Any]) -> Optional[str]:
        """Submit task to agent and return task ID"""
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]

        # Create task record
        task = {
            "agent_id": agent_id,
            "task_type": agent.role,
            "priority": agent.priority,
            "status": "pending",
            "data": task_data
        }

        if db_service.database:
            task_id = await db_service.save_agent_task(task)
            return task_id

        return None

    async def process_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Process a task using the appropriate agent"""
        if not db_service.database:
            return None

        # Get task from database
        task = await db_service.get_agent_task(task_id)
        if not task:
            return None

        agent = await self.get_agent(task["agent_id"])
        if not agent:
            return None

        # Update task status to processing
        await db_service.update_agent_task(task_id, {"status": "processing"})

        try:
            # Process the task
            result = await agent.process_task(task["data"])

            # Update task with result
            update_data = {
                "status": "completed",
                "result": result,
                "completed_at": datetime.now().isoformat()
            }
            await db_service.update_agent_task(task_id, update_data)

            return result

        except Exception as e:
            # Update task with error
            update_data = {
                "status": "failed",
                "error": str(e)
            }
            await db_service.update_agent_task(task_id, update_data)
            return {"error": str(e)}

# Global instance
agent_registry = AgentRegistry()