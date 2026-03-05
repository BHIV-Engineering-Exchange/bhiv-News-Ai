import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from unified_pipeline import unified_pipeline
from queue_worker import background_queue

logger = logging.getLogger(__name__)

class NewsAIScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            jobstores={
                'default': MemoryJobStore()
            },
            executors={
                'default': AsyncIOExecutor()
            },
            job_defaults={
                'coalesce': True,
                'max_instances': 3,
                'misfire_grace_time': 30
            },
            timezone='UTC'
        )

        # News source configurations
        self.news_sources = {
            'live': {
                'interval': '*/15',  # Every 15 minutes
                'sources': [
                    'https://www.bbc.com/news',
                    'https://www.reuters.com/',
                    'https://www.nytimes.com/',
                    'https://www.aljazeera.com/',
                    'https://www.theguardian.com/international'
                ]
            },
            'finance': {
                'interval': '0 * * * *',  # Every hour
                'sources': [
                    'https://www.bloomberg.com/',
                    'https://www.wsj.com/',
                    'https://www.ft.com/',
                    'https://www.cnbc.com/',
                    'https://www.marketwatch.com/'
                ]
            },
            'world': {
                'interval': '0 */6 * * *',  # Every 6 hours
                'sources': [
                    'https://www.bbc.com/news/world',
                    'https://www.reuters.com/world/',
                    'https://www.aljazeera.com/news/',
                    'https://www.dw.com/en/top-stories/s-9097'
                ]
            },
            'regional': {
                'interval': '0 */6 * * *',  # Every 6 hours
                'sources': [
                    'https://www.thehindu.com/',
                    'https://indianexpress.com/',
                    'https://www.ndtv.com/',
                    'https://timesofindia.indiatimes.com/'
                ]
            },
            'kids': {
                'interval': '0 */6 * * *',  # Every 6 hours
                'sources': [
                    'https://www.scholastic.com/',
                    'https://www.timeforkids.com/',
                    'https://www.nationalgeographic.com/for-kids/',
                    'https://www.bbc.co.uk/newsround'
                ]
            }
        }

        self.running = False
        self.stats = {
            'jobs_scheduled': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'last_run': None,
            'next_runs': {}
        }

    async def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return

        logger.info("Starting News AI Scheduler...")

        # Schedule all news processing jobs
        await self._schedule_news_jobs()

        # Start the scheduler
        self.scheduler.start()
        self.running = True

        logger.info("News AI Scheduler started successfully")

    async def stop(self):
        """Stop the scheduler"""
        if not self.running:
            logger.warning("Scheduler not running")
            return

        logger.info("Stopping News AI Scheduler...")
        self.scheduler.shutdown(wait=True)
        self.running = False
        logger.info("News AI Scheduler stopped")

    async def _schedule_news_jobs(self):
        """Schedule all news processing jobs"""
        for category, config in self.news_sources.items():
            # Schedule each source in the category
            for i, source_url in enumerate(config['sources']):
                job_id = f"{category}_{i}"

                # Stagger the jobs slightly to avoid overwhelming the system
                minute_offset = i * 2  # 2-minute stagger

                if category == 'live':
                    # Every 15 minutes
                    cron_expr = "*/15 * * * *"
                elif category == 'finance':
                    # Every hour, staggered by minutes
                    cron_expr = f"{minute_offset} * * * *"
                else:
                    # Every 6 hours, staggered by minutes
                    cron_expr = f"{minute_offset} */6 * * *"

                self.scheduler.add_job(
                    func=self._process_news_source,
                    trigger=CronTrigger.from_crontab(cron_expr),
                    args=[source_url, category],
                    id=job_id,
                    name=f"Process {category} news from {source_url}",
                    max_instances=1,
                    replace_existing=True
                )

                self.stats['jobs_scheduled'] += 1
                logger.info(f"Scheduled job {job_id}: {cron_expr}")

    async def _process_news_source(self, source_url: str, category: str):
        """Process a news source through the unified pipeline"""
        try:
            logger.info(f"Processing {category} news from: {source_url}")

            # Prepare pipeline options based on category
            options = self._get_pipeline_options_for_category(category)

            # Create pipeline request
            request = {
                "url": source_url,
                "options": options
            }

            # Submit to background queue instead of processing directly
            await background_queue.add_job(
                job_type="news_processing",
                payload=request,
                priority=self._get_priority_for_category(category)
            )

            self.stats['jobs_completed'] += 1
            self.stats['last_run'] = datetime.now().isoformat()

            logger.info(f"Successfully queued {category} news processing for: {source_url}")

        except Exception as e:
            logger.error(f"Failed to process {category} news from {source_url}: {str(e)}")
            self.stats['jobs_failed'] += 1

    def _get_pipeline_options_for_category(self, category: str) -> Dict[str, Any]:
        """Get pipeline options based on news category"""
        base_options = {
            "enable_bhiv_push": True,
            "enable_audio": True,
            "force_correction": False
        }

        category_configs = {
            'live': {
                "channels": ["news_channel_live"],
                "avatars": ["avatar_breaking"],
                "voice": "urgent"
            },
            'finance': {
                "channels": ["news_channel_finance"],
                "avatars": ["avatar_business"],
                "voice": "professional"
            },
            'world': {
                "channels": ["news_channel_world"],
                "avatars": ["avatar_global"],
                "voice": "neutral"
            },
            'regional': {
                "channels": ["news_channel_regional"],
                "avatars": ["avatar_local"],
                "voice": "conversational"
            },
            'kids': {
                "channels": ["news_channel_kids"],
                "avatars": ["avatar_fun"],
                "voice": "friendly",
                "enable_audio": False  # Kids content might not need audio
            }
        }

        return {**base_options, **category_configs.get(category, {})}

    def _get_priority_for_category(self, category: str) -> int:
        """Get job priority based on category"""
        priorities = {
            'live': 10,      # Highest priority
            'finance': 7,
            'world': 5,
            'regional': 3,
            'kids': 1        # Lowest priority
        }
        return priorities.get(category, 5)

    async def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        jobs = []
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time.isoformat() if job.next_run_time else None
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": next_run,
                "trigger": str(job.trigger)
            })

        return {
            "running": self.running,
            "stats": self.stats,
            "jobs": jobs,
            "timestamp": datetime.now().isoformat()
        }

    async def trigger_manual_run(self, category: str = None, source_url: str = None):
        """Manually trigger a news processing run"""
        if category and source_url:
            # Process specific source
            options = self._get_pipeline_options_for_category(category)
            request = {
                "url": source_url,
                "options": options
            }
            await background_queue.add_job(
                job_type="news_processing",
                payload=request,
                priority=self._get_priority_for_category(category)
            )
            return {"message": f"Manual run triggered for {category}: {source_url}"}

        elif category:
            # Process all sources in category
            config = self.news_sources.get(category)
            if not config:
                return {"error": f"Unknown category: {category}"}

            for source_url in config['sources']:
                options = self._get_pipeline_options_for_category(category)
                request = {
                    "url": source_url,
                    "options": options
                }
                await background_queue.add_job(
                    job_type="news_processing",
                    payload=request,
                    priority=self._get_priority_for_category(category)
                )
            return {"message": f"Manual run triggered for all {category} sources"}

        else:
            # Process one source from each category
            for cat, config in self.news_sources.items():
                source_url = config['sources'][0]  # First source
                options = self._get_pipeline_options_for_category(cat)
                request = {
                    "url": source_url,
                    "options": options
                }
                await background_queue.add_job(
                    job_type="news_processing",
                    payload=request,
                    priority=self._get_priority_for_category(cat)
                )
            return {"message": "Manual run triggered for one source from each category"}

# Global instance
scheduler = NewsAIScheduler()