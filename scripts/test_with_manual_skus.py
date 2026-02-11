#!/usr/bin/env python3
"""Test script for running the bot with a manual list of SKUs.

This script bypasses the get_skus_without_images() limitation by accepting
a manual list of SKUs to test the image search and upload functionality.

Features:
- Automatically skips SKUs that were already successfully processed
- Only reprocesses failed or needs_review SKUs
- Use --force to reprocess all SKUs regardless of previous status

Usage:
    python scripts/test_with_manual_skus.py --skus "SKU1,SKU2,SKU3"
    python scripts/test_with_manual_skus.py --file test_skus.txt
    python scripts/test_with_manual_skus.py --file real_skus.txt --limit 100
    python scripts/test_with_manual_skus.py --file test_skus.txt --force  # Force reprocess all
"""

import sys
import argparse
from pathlib import Path

# Add project root to path to enable absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import Config
from src.utils.logger import setup_logging
from src.storage.state_manager import StateManager
from src.storage.models import SKU, ProcessingStatus
from src.services.sku_processor import SKUProcessor
import logging


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test the image fetcher bot with manual SKU list"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--skus",
        type=str,
        help="Comma-separated list of SKU IDs (e.g., 'SKU1,SKU2,SKU3')"
    )
    group.add_argument(
        "--file",
        type=str,
        help="Path to file containing SKU IDs (one per line)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of SKUs to process (default: 10)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reprocess all SKUs, even if already successful"
    )
    
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip database check and process all SKUs (faster but may duplicate)"
    )
    
    return parser.parse_args()


def load_skus_from_file(filepath: str) -> list:
    """Load SKU IDs from a text file (one per line)."""
    skus = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                sku = line.strip()
                if sku and not sku.startswith('#'):  # Skip empty lines and comments
                    skus.append(sku)
        return skus
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)


def filter_already_processed(sku_ids: list, state_manager: StateManager, force: bool, logger) -> tuple:
    """Filter out SKUs that were already successfully processed.
    
    Args:
        sku_ids: List of SKU IDs to check
        state_manager: StateManager instance
        force: If True, include all SKUs regardless of status
        logger: Logger instance
    
    Returns:
        Tuple of (skus_to_process, already_processed_count)
    """
    if force:
        logger.info("Force mode enabled - will reprocess all SKUs")
        return sku_ids, 0
    
    skus_to_process = []
    already_successful = 0
    
    for sku_id in sku_ids:
        record = state_manager.get_processing_record(sku_id)
        
        if record is None:
            # Never processed before
            skus_to_process.append(sku_id)
        elif record.status == ProcessingStatus.SUCCESS:
            # Already successfully processed - skip
            already_successful += 1
            logger.debug(f"Skipping {sku_id} - already processed successfully")
        else:
            # Failed or needs review - retry
            skus_to_process.append(sku_id)
            logger.debug(f"Will retry {sku_id} - previous status: {record.status.value}")
    
    if already_successful > 0:
        logger.info(f"Skipping {already_successful} SKUs that were already processed successfully")
        logger.info(f"Processing {len(skus_to_process)} SKUs (new + failed + needs_review)")
    
    return skus_to_process, already_successful


def main():
    """Main test function."""
    args = parse_arguments()
    
    # Load configuration
    print("Loading configuration...")
    try:
        config = Config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("\nMake sure you have:")
        print("  1. Created a .env file with your API keys")
        print("  2. See docs/GET_API_KEYS.md for instructions")
        sys.exit(1)
    
    # Set up logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    # Parse SKU list
    if args.skus:
        all_sku_ids = [sku.strip() for sku in args.skus.split(',')]
    else:
        all_sku_ids = load_skus_from_file(args.file)
    
    logger.info(f"Loaded {len(all_sku_ids)} SKUs from input")
    
    # Filter already processed SKUs (unless --skip-check or --force)
    if args.skip_check:
        logger.info("Skipping database check - processing all SKUs")
        sku_ids_to_process = all_sku_ids[:args.limit]
        skipped_count = 0
    else:
        state_manager = StateManager(config.env.database_path)
        sku_ids_to_process, skipped_count = filter_already_processed(
            all_sku_ids, 
            state_manager, 
            args.force, 
            logger
        )
        # Apply limit AFTER filtering
        sku_ids_to_process = sku_ids_to_process[:args.limit]
    
    if not sku_ids_to_process:
        print("\n" + "="*60)
        print("✅ ALL SKUs ALREADY PROCESSED!")
        print("="*60)
        print(f"All {len(all_sku_ids)} SKUs have been successfully processed.")
        print("Use --force to reprocess them anyway.")
        print("="*60)
        return
    
    # Create SKU objects
    test_skus = [
        SKU(
            id=sku_id,
            sku=sku_id,
            name=f"Product {sku_id}",  # Placeholder - will use SKU for keyword extraction
            description=None
        )
        for sku_id in sku_ids_to_process
    ]
    
    # Run the processor
    print("\n" + "="*60)
    print("STARTING TEST RUN")
    print("="*60)
    print(f"Total SKUs in file: {len(all_sku_ids)}")
    if skipped_count > 0:
        print(f"Already processed: {skipped_count}")
    print(f"SKUs to process: {len(test_skus)}")
    print(f"Image sources: Freepik → Pexels → Pixabay")
    print("="*60 + "\n")
    
    try:
        processor = SKUProcessor(config)
        
        success_count = 0
        failed_count = 0
        needs_review_count = 0
        
        # Process each SKU individually for better visibility
        for i, sku in enumerate(test_skus, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing SKU {i}/{len(test_skus)}: {sku.sku}")
            logger.info(f"{'='*60}")
            
            result = processor.process_single_sku(sku.sku, sku.name or sku.sku)
            
            if result.success:
                success_count += 1
                logger.info(f"✅ SUCCESS: Image attached for {sku.sku}")
                logger.info(f"   Source: {result.image_source}")
                logger.info(f"   Relevance: {result.relevance_score:.2f}")
            elif result.error and "No suitable image found" in result.error:
                needs_review_count += 1
                logger.warning(f"⚠️  NEEDS REVIEW: {sku.sku}")
                logger.warning(f"   No suitable image found")
            else:
                failed_count += 1
                logger.error(f"❌ FAILED: {sku.sku}")
                logger.error(f"   Error: {result.error}")
        
        # Print summary
        print("\n" + "="*60)
        print("TEST RUN COMPLETE")
        print("="*60)
        print(f"Total in file: {len(all_sku_ids)}")
        if skipped_count > 0:
            print(f"Already processed (skipped): {skipped_count}")
        print(f"Attempted this run: {len(test_skus)}")
        print(f"✅ Successful: {success_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"⚠️  Needs Review: {needs_review_count}")
        if len(test_skus) > 0:
            success_rate = (success_count / len(test_skus)) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        print("="*60)
        print(f"\nCheck logs/app.log for detailed output")
        print(f"Check data/state.db for processing records")
        if needs_review_count > 0:
            print(f"Check reports/ folder for SKUs needing review")
        print("="*60)
        
    except Exception as e:
        logger.exception(f"Test run failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
