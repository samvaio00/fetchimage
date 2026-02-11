"""Job scheduler using APScheduler."""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from ..utils.logger import get_logger


def start_scheduler(config, interval_hours: int = 6):
    """Start the job scheduler."""
    logger = get_logger(__name__)
    
    from ..main import run_job
    
    scheduler = BlockingScheduler()
    
    trigger = IntervalTrigger(hours=interval_hours)
    
    scheduler.add_job(
        func=lambda: run_job(config),
        trigger=trigger,
        id="image_fetcher_job",
        name="Image Fetcher Bot Job",
        misfire_grace_time=3600,
        replace_existing=True
    )
    
    logger.info(f"Scheduler started. Job will run every {interval_hours} hours")
    logger.info("Press Ctrl+C to exit")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
