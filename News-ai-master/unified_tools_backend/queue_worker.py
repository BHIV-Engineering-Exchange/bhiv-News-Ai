import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import heapq
from dataclasses import dataclass, field
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from unified_pipeline import unified_pipeline

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"

class JobPriority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10

@dataclass(order=True)
class Job:
    priority: int
    created_at: datetime
    job_id: str = field(compare=False)
    job_type: str = field(compare=False)
    payload: Dict[str, Any] = field(compare=False)
    status: JobStatus = field(compare=False, default=JobStatus.PENDING)
    retry_count: int = field(compare=False, default=0)
    max_retries: int = field(compare=False, default=3)
    error_message: Optional[str] = field(compare=False, default=None)
    completed_at: Optional[datetime] = field(compare=False, default=None)
    result: Optional[Dict[str, Any]] = field(compare=False, default=None)

    def __post_init__(self):
        # Make priority negative for min-heap behavior (higher priority = lower number)
        self.priority = -self.priority

class BackgroundQueue:
    def __init__(self, max_workers: int = 5, max_queue_size: int = 1000):
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size

        # Priority queue for jobs (min-heap)
        self.job_queue: List[Job] = []
        self.job_counter = 0

        # Job storage
        self.jobs: Dict[str, Job] = {}

        # Worker management
        self.active_workers = 0
        self.worker_tasks: List[asyncio.Task] = []

        # Statistics
        self.stats = {
            "jobs_added": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "jobs_retried": 0,
            "active_workers": 0,
            "queue_size": 0
        }

        # Retry configuration
        self.retry_delays = [30, 60, 300]  # 30s, 1min, 5min

        # Error patterns for special handling
        self.error_patterns = {
            "504": {"action": "retry", "max_retries": 3},
            "uniguru": {"action": "fallback", "max_retries": 0},
            "bhiv": {"action": "requeue", "max_retries": 5},
            "timeout": {"action": "retry", "max_retries": 2}
        }

        self.running = False

        # Thread synchronization
        self.queue_lock = threading.Lock()
        self.stats_lock = threading.Lock()
        self.active_workers_lock = threading.Lock()

    async def start(self):
        """Start the background queue processor"""
        if self.running:
            logger.warning("Queue already running")
            return

        logger.info(f"Starting background queue with {self.max_workers} workers")
        self.running = True

        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        for i in range(self.max_workers):
            self.executor.submit(self._worker_sync_loop, i)

        logger.info("Background queue started successfully")

    async def stop(self):
        """Stop the background queue processor"""
        if not self.running:
            logger.warning("Queue not running")
            return

        logger.info("Stopping background queue...")
        self.running = False

        # Shutdown the thread pool executor
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None

        logger.info("Background queue stopped")

    async def add_job(self, job_type: str, payload: Dict[str, Any],
                     priority: int = JobPriority.NORMAL.value) -> str:
        """Add a job to the queue"""
        if len(self.job_queue) >= self.max_queue_size:
            raise Exception("Queue is full")

        self.job_counter += 1
        job_id = f"job_{self.job_counter}_{int(datetime.now().timestamp())}"

        job = Job(
            priority=priority,
            created_at=datetime.now(),
            job_id=job_id,
            job_type=job_type,
            payload=payload
        )

        # Add to priority queue
        with self.queue_lock:
            heapq.heappush(self.job_queue, job)
        self.jobs[job_id] = job

        with self.stats_lock:
            self.stats["jobs_added"] += 1
            self.stats["queue_size"] = len(self.job_queue)

        logger.info(f"Added job {job_id} to queue (priority: {priority}, type: {job_type})")
        return job_id

    def _worker_sync_loop(self, worker_id: int):
        """Main worker loop"""
        logger.info(f"Worker {worker_id} started")

        while self.running:
            try:
                # Get next job from queue
                with self.queue_lock:
                    if not self.job_queue:
                        time.sleep(1)  # Wait for jobs
                        continue

                    job = heapq.heappop(self.job_queue)
                    with self.stats_lock:
                        self.stats["queue_size"] = len(self.job_queue)
                with self.active_workers_lock:
                    self.active_workers += 1
                    with self.stats_lock:
                        self.stats["active_workers"] = self.active_workers

                # Process the job
                asyncio.run(self._process_job_async(job))

                with self.active_workers_lock:
                    self.active_workers -= 1
                    with self.stats_lock:
                        self.stats["active_workers"] = self.active_workers

            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")
                with self.active_workers_lock:
                    self.active_workers -= 1
                    with self.stats_lock:
                        self.stats["active_workers"] = self.active_workers
                time.sleep(5)  # Back off on errors

        logger.info(f"Worker {worker_id} stopped")

    async def _process_job_async(self, job: Job):
        """Process a single job"""
        try:
            logger.info(f"Processing job {job.job_id} (type: {job.job_type})")
            job.status = JobStatus.PROCESSING

            if job.job_type == "news_processing":
                result = await self._process_news_job(job)
                job.result = result  # Store the result
            else:
                raise Exception(f"Unknown job type: {job.job_type}")

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            with self.stats_lock:
                self.stats["jobs_completed"] += 1

            logger.info(f"Job {job.job_id} completed successfully")

        except Exception as e:
            await self._handle_job_error(job, str(e))

    async def _process_news_job(self, job: Job) -> Dict[str, Any]:
        """Process a news processing job"""
        try:
            # Run the unified pipeline
            result = await unified_pipeline.run_full_pipeline(job.payload)

            if not result.get("success"):
                raise Exception(f"Pipeline failed: {result.get('error', 'Unknown error')}")

            return result

        except Exception as e:
            raise e

    async def _handle_job_error(self, job: Job, error_message: str):
        """Handle job processing errors with retry logic"""
        logger.error(f"Job {job.job_id} failed: {error_message}")

        job.error_message = error_message
        job.retry_count += 1

        # Determine retry action based on error
        retry_action = self._determine_retry_action(error_message)

        if retry_action["should_retry"] and job.retry_count < job.max_retries:
            # Schedule retry
            delay = self._get_retry_delay(job.retry_count)
            job.status = JobStatus.RETRY

            # Re-queue the job with delay
            asyncio.create_task(self._schedule_retry(job, delay))

            with self.stats_lock:
                self.stats["jobs_retried"] += 1
            logger.info(f"Job {job.job_id} scheduled for retry {job.retry_count}/{job.max_retries} in {delay}s")

        else:
            # Mark as failed
            job.status = JobStatus.FAILED
            with self.stats_lock:
                self.stats["jobs_failed"] += 1
            logger.error(f"Job {job.job_id} failed permanently after {job.retry_count} retries")

    def _determine_retry_action(self, error_message: str) -> Dict[str, Any]:
        """Determine retry action based on error message"""
        error_lower = error_message.lower()

        # Check for specific error patterns
        if "504" in error_lower or "gateway timeout" in error_lower:
            return {"should_retry": True, "max_retries": 3}
        elif "uniguru" in error_lower:
            return {"should_retry": False}  # Fallback model used in service
        elif "bhiv" in error_lower:
            return {"should_retry": True, "max_retries": 5}
        elif "timeout" in error_lower or "connection" in error_lower:
            return {"should_retry": True, "max_retries": 2}
        else:
            # Default retry behavior
            return {"should_retry": True, "max_retries": 3}

    def _get_retry_delay(self, retry_count: int) -> int:
        """Get retry delay based on retry count"""
        if retry_count <= len(self.retry_delays):
            return self.retry_delays[retry_count - 1]
        else:
            return self.retry_delays[-1] * 2  # Exponential backoff

    async def _schedule_retry(self, job: Job, delay: int):
        """Schedule a job retry after delay"""
        await asyncio.sleep(delay)

        # Reset job for retry
        job.status = JobStatus.PENDING
        job.error_message = None

        # Re-queue the job
        with self.queue_lock:
            heapq.heappush(self.job_queue, job)
            with self.stats_lock:
                self.stats["queue_size"] = len(self.job_queue)

        logger.info(f"Job {job.job_id} re-queued for retry")

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        pending_jobs = [j for j in self.jobs.values() if j.status == JobStatus.PENDING]
        processing_jobs = [j for j in self.jobs.values() if j.status == JobStatus.PROCESSING]
        failed_jobs = [j for j in self.jobs.values() if j.status == JobStatus.FAILED]

        return {
            "running": self.running,
            "stats": self.stats,
            "queue_size": len(self.job_queue),
            "pending_jobs": len(pending_jobs),
            "processing_jobs": len(processing_jobs),
            "failed_jobs": len(failed_jobs),
            "active_workers": self.active_workers,
            "max_workers": self.max_workers,
            "timestamp": datetime.now().isoformat()
        }

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        job = self.jobs.get(job_id)
        if not job:
            return None

        return {
            "job_id": job.job_id,
            "job_type": job.job_type,
            "status": job.status.value,
            "priority": -job.priority,  # Convert back to positive
            "retry_count": job.retry_count,
            "max_retries": job.max_retries,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
            "result": job.result,
            "payload": job.payload
        }

# Global instance
background_queue = BackgroundQueue()