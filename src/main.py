#!/usr/bin/env python
"""Main entry point for Image Fetcher Bot."""

import sys
import click
from utils.config import get_config
from utils.logger import setup_logging, get_logger
from services.sku_processor import SKUProcessor


@click.command()
@click.option("--run-once", is_flag=True, help="Run once and exit")
@click.option("--interval", default=6, help="Interval in hours for scheduled runs")
@click.option("--config", default="config/config.yaml", help="Path to config file")
def main(run_once, interval, config):
    """Image Fetcher Bot - Autonomous SKU image attachment."""
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info("Image Fetcher Bot starting...")
    
    try:
        cfg = get_config(config)
        logger.info(f"Loaded config: {cfg.app_name} v{cfg.app_version}")
        
        if run_once:
            logger.info("Running in single-run mode")
            run_job(cfg)
        else:
            logger.info(f"Starting scheduler (interval: {interval} hours)")
            from scheduler.job_scheduler import start_scheduler
            start_scheduler(cfg, interval)
            
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


def run_job(cfg):
    """Run single image fetching job."""
    logger = get_logger(__name__)
    
    try:
        processor = SKUProcessor(cfg)
        report = processor.process_all_skus()
        
        logger.info("="*60)
        logger.info("PROCESSING REPORT")
        logger.info("="*60)
        logger.info(f"Total SKUs: {report.total}")
        logger.info(f"Successful: {report.successful}")
        logger.info(f"Failed: {report.failed}")
        logger.info(f"Skipped: {report.skipped}")
        logger.info(f"Success Rate: {report.success_rate:.1f}%")
        logger.info(f"Duration: {report.duration_seconds:.1f}s")
        
        if report.source_breakdown:
            logger.info("Source Breakdown:")
            for source, count in report.source_breakdown.items():
                logger.info(f"  {source}: {count}")
        
        if report.error_summary:
            logger.info(f"Errors ({len(report.error_summary)}):")
            for error in report.error_summary[:10]:
                logger.info(f"  {error}")

        if report.needs_review > 0:
            logger.info(f"\nReport: {report.needs_review} SKUs needing review saved to reports/")
            logger.info(f"  Check: reports/needs_review_*.txt")

        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
