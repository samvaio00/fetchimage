#!/usr/bin/env python
"""Initialize database for Image Fetcher Bot."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from storage.state_manager import StateManager
from utils.logger import setup_logging, get_logger

def main():
    """Initialize the database."""
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info("Initializing database...")
    
    try:
        # Create state manager (this will init the database)
        state_manager = StateManager()
        logger.info("Database initialized successfully!")
        
        # Print stats
        stats = state_manager.get_processing_stats()
        logger.info(f"Current stats: {stats}")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
