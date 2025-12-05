#!/usr/bin/env python3
"""
File system watcher for Calibre library changes.

Watches for:
1. New books added to Calibre ingest directory
2. Changes to Calibre metadata.db
3. Automatically triggers ingestion for new books

Usage:
    python scripts/calibre_watcher.py &  # Run in background
    python scripts/calibre_watcher.py --dry-run  # Show what would be processed
"""

import argparse
import sys
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.auto_ingest_daemon import process_batch

# Configuration
CALIBRE_LIBRARY = Path("./calibre/library")
CALIBRE_INGEST = Path("./calibre/ingest")
CALIBRE_DB = Path("./calibre/library/metadata.db")
LOG_FILE = Path("logs/calibre_watcher.log")

# Set up logging
LOG_FILE.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CalibreEventHandler(FileSystemEventHandler):
    """Handle Calibre library file system events."""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.last_db_change = 0
        self.debounce_delay = 5  # 5 second debounce
        
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        path = Path(event.src_path)
        
        # Watch for metadata.db changes (new books added)
        if path.name == "metadata.db":
            self._handle_db_change()
            
        # Watch for new epub/pdf files in ingest directory
        elif path.suffix.lower() in ['.epub', '.pdf'] and 'ingest' in str(path):
            self._handle_new_book_file(path)
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
            
        path = Path(event.src_path)
        
        # New book files in ingest directory
        if path.suffix.lower() in ['.epub', '.pdf'] and 'ingest' in str(path):
            self._handle_new_book_file(path)
    
    def _handle_db_change(self):
        """Handle Calibre database changes."""
        current_time = time.time()
        
        # Debounce - Calibre makes multiple DB writes
        if current_time - self.last_db_change < self.debounce_delay:
            return
            
        self.last_db_change = current_time
        logger.info("Calibre database changed - new book(s) may have been added")
        
        if self.dry_run:
            logger.info("[DRY RUN] Would trigger batch processing in 10 seconds")
        else:
            # Wait a bit for Calibre to finish all operations
            logger.info("Waiting 10 seconds for Calibre to complete operations...")
            time.sleep(10)
            
            # Trigger batch processing
            logger.info("Triggering automatic book processing")
            processed = process_batch()
            
            if processed > 0:
                logger.info(f"Auto-processed {processed} new book(s)")
            else:
                logger.info("No new books to process")
    
    def _handle_new_book_file(self, path):
        """Handle new book files in ingest directory."""
        logger.info(f"New book file detected: {path.name}")
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would wait for Calibre to import: {path.name}")
        else:
            logger.info(f"Waiting for Calibre to import: {path.name}")
            # Calibre will import and trigger DB change event


def main():
    parser = argparse.ArgumentParser(description="Calibre library file watcher")
    parser.add_argument("--dry-run", action="store_true", help="Show events without processing")
    
    args = parser.parse_args()
    
    # Ensure directories exist
    CALIBRE_INGEST.mkdir(exist_ok=True)
    
    if not CALIBRE_LIBRARY.exists():
        logger.error(f"Calibre library not found: {CALIBRE_LIBRARY}")
        sys.exit(1)
    
    logger.info("Starting Calibre library watcher")
    logger.info(f"Watching: {CALIBRE_LIBRARY}")
    logger.info(f"Ingest dir: {CALIBRE_INGEST}")
    
    if args.dry_run:
        logger.info("DRY RUN MODE - no actual processing")
    
    # Set up file system watcher
    event_handler = CalibreEventHandler(dry_run=args.dry_run)
    observer = Observer()
    
    # Watch both library and ingest directories
    observer.schedule(event_handler, str(CALIBRE_LIBRARY), recursive=True)
    observer.schedule(event_handler, str(CALIBRE_INGEST), recursive=True)
    
    try:
        observer.start()
        logger.info("File watcher started - waiting for changes...")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Stopping file watcher...")
        observer.stop()
    
    observer.join()
    logger.info("File watcher stopped")


if __name__ == "__main__":
    main()