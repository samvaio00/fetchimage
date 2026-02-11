#!/usr/bin/env python3
"""Test script for running the bot with a manual list of SKUs.

This script bypasses the get_skus_without_images() limitation by accepting
a manual list of SKUs to test the image search and upload functionality.

Usage:
    python scripts/test_with_manual_skus.py --skus "MEN-SHIRT-BLUE-L,LAPTOP-DELL-15IN,WIDGET-XYZ-123"
    python scripts/test_with_manual_skus.py --file test_skus.txt
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import Config
from utils.logger import setup_logging
from storage.state_manager import StateManager
from storage.models import SKU, ProcessingStatus
from services.sku_processor import SKUProcessor
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
#!/usr/bin/env python3
"""Test script for running the bot with a manual list of SKUs.

This script bypasses the get_skus_without_images() limitation by accepting
a manual list of SKUs to test the image search and upload functionality.

Usage:
    python scripts/test_with_manual_skus.py --skus "MEN-SHIRT-BLUE-L,LAPTOP-DELL-15IN,WIDGET-XYZ-123"
    python scripts/test_with_manual_skus.py --file test_skus.txt
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import Config
from utils.logger import setup_logging
from storage.state_manager import StateManager
from storage.models import SKU, ProcessingStatus
from services.sku_processor import SKUProcessor
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
        "--reset-state",
        action="store_true",
        help="Clear previous processing state before running"
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
        sku_ids = [sku.strip() for sku in args.skus.split(',')]
    else:
        sku_ids = load_skus_from_file(args.file)
    
    # Apply limit
    sku_ids = sku_ids[:args.limit]
    
    logger.info(f"Testing with {len(sku_ids)} SKUs: {', '.join(sku_ids)}")
    
    # Reset state if requested
    if args.reset_state:
        logger.warning("Resetting processing state...")
        state_manager = StateManager(config)
        for sku_id in sku_ids:
            # Delete from database if exists
            conn = state_manager._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM processed_skus WHERE sku_id = ?", (sku_id,))
            conn.commit()
            conn.close()
        logger.info("State reset complete")
    
    # Create fake SKU objects (we don't have product names from Replit yet)
    # The bot will use the SKU ID itself to extract keywords
    test_skus = [
        SKU(
            id=sku_id,
            sku=sku_id,
            name=f"Product {sku_id}",  # Placeholder name
            description=None
        )
        for sku_id in sku_ids
    ]
    
    # Run the processor
    print("\n" + "="*60)
    print("STARTING TEST RUN")
    print("="*60)
    print(f"SKUs to process: {len(test_skus)}")
    print(f"Image sources: Unsplash → Pexels → Pixabay")
    print("="*60 + "\n")
    
    try:
        processor = SKUProcessor(config)
        
        # Process each SKU individually for better visibility
        for sku in test_skus:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing SKU: {sku.sku}")
            logger.info(f"{'='*60}")
            
            result = processor.process_single_sku(sku)
            
            if result.success:
                logger.info(f"✅ SUCCESS: Image attached for {sku.sku}")
                logger.info(f"   Source: {result.image_source}")
                logger.info(f"   Relevance: {result.relevance_score:.2f}")
            else:
                logger.error(f"❌ FAILED: {sku.sku}")
                logger.error(f"   Error: {result.error}")
        
        print("\n" + "="*60)
        print("TEST RUN COMPLETE")
        print("="*60)
        print(f"Check logs/app.log for detailed output")
        print(f"Check data/state.db for processing records")
        print(f"Check reports/ folder for any SKUs needing review")
        print("="*60)
        
    except Exception as e:
        logger.exception(f"Test run failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
