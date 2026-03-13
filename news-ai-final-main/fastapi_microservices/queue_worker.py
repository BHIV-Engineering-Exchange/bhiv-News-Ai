import asyncio
import os
import httpx

UNIFIED_ENDPOINT = os.getenv("UNIFIED_ENDPOINT", "http://localhost:8000/v1/run_pipeline")
BHIV_STATUS_ENDPOINT = os.getenv("BHIV_STATUS_ENDPOINT", "http://localhost:3000/api/bhiv/status")

class Task:
    def __init__(self, payload: dict):
        self.payload = payload
        self.retries = 0

async def process_task(task: Task):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(UNIFIED_ENDPOINT, json=task.payload)
            if resp.status_code == 504:
                if task.retries < 3:
                    task.retries += 1
                    return False  # retry
            if resp.status_code != 200:
                return True  # drop or log
            data = resp.json()
            return True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 504 and task.retries < 3:
            task.retries += 1
            return False
        return True
    except Exception:
        return True

async def worker(queue: asyncio.Queue):
    while True:
        task: Task = await queue.get()
        done = await process_task(task)
        if not done:
            await asyncio.sleep(1)
            await queue.put(task)
        queue.task_done()

async def enqueue(queue: asyncio.Queue, payload: dict):
    await queue.put(Task(payload))

def start_workers():
    loop = asyncio.get_event_loop()
    q = asyncio.Queue()
    for _ in range(3):
        loop.create_task(worker(q))
    loop.run_until_complete(q.join())

if __name__ == "__main__":
    start_workers()
