import asyncio
import httpx
import json
import sys

# Configuration
INSIGHT_NODE_URL = "http://localhost:8001"
TEST_URL = "https://www.npr.org/sections/news/"  # NPR is usually scraper-friendly

async def test_insight_node():
    print(f"Testing Insight Node at {INSIGHT_NODE_URL}...")
    
    payload = {"url": TEST_URL}
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 1. Health Check
            print("1. Checking Health...")
            resp = await client.get(f"{INSIGHT_NODE_URL}/health")
            if resp.status_code == 200:
                print(f"✅ Health Check Passed: {resp.json()}")
            else:
                print(f"❌ Health Check Failed: {resp.status_code}")
                return False

            # 2. Run Workflow
            print(f"2. Running Workflow for {TEST_URL}...")
            resp = await client.post(
                f"{INSIGHT_NODE_URL}/api/unified-news-workflow",
                json=payload
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    result = data.get("data", {})
                    print("\n✅ Workflow Successful!")
                    print(f"   - Title: {result.get('scraped_data', {}).get('title')}")
                    print(f"   - Authenticity: {result.get('vetting_results', {}).get('authenticity_score')}")
                    print(f"   - Summary: {result.get('summary', {}).get('text')[:100]}...")
                    print(f"   - Video Prompt: {result.get('video_prompt', {}).get('prompt')[:50]}...")
                    return True
                else:
                    print(f"❌ Workflow Failed (Success=False): {data}")
            else:
                print(f"❌ HTTP Request Failed: {resp.status_code} - {resp.text}")

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("   (Ensure the server is running on port 8001)")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_insight_node())
    sys.exit(0 if success else 1)
