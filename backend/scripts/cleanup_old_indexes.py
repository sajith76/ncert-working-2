"""
Script to clean up old/unused Pinecone indexes.

This will delete:
1. ncert-learning-rag (OLD chapter-based architecture)
2. ncert-mathematics (created by mistake - will use namespaces instead)
3. ncert-physics (created by mistake - will use namespaces instead)  
4. intel-working (if confirmed not needed)

Keeps:
- ncert-web-content (for DeepDive web scraping)
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pinecone import Pinecone
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


INDEXES_TO_DELETE = [
    "ncert-learning-rag",  # OLD chapter-based
    "ncert-mathematics",   # Partial creation - will use namespaces
    "ncert-physics",       # Partial creation - will use namespaces
    "intel-working"        # Not needed
]


def cleanup_indexes():
    """Delete old/unused indexes."""
    
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        logger.info("="*70)
        logger.info("🧹 Cleaning Up Old Pinecone Indexes")
        logger.info("="*70)
        
        # Get existing indexes
        existing_indexes = [index.name for index in pc.list_indexes()]
        logger.info(f"\n📋 Current indexes: {len(existing_indexes)}")
        for idx in existing_indexes:
            logger.info(f"   - {idx}")
        
        # Confirm deletion
        logger.info(f"\n⚠️  INDEXES TO DELETE:")
        for idx in INDEXES_TO_DELETE:
            if idx in existing_indexes:
                logger.info(f"   🗑️  {idx}")
        
        # Ask for confirmation
        print("\n" + "="*70)
        response = input("⚠️  Are you sure you want to delete these indexes? (yes/no): ")
        
        if response.lower() not in ['yes', 'y']:
            logger.info("\n❌ Deletion cancelled by user")
            return
        
        # Delete indexes
        deleted_count = 0
        skipped_count = 0
        
        logger.info(f"\n{'='*70}")
        logger.info("Deleting indexes...")
        logger.info(f"{'='*70}\n")
        
        for index_name in INDEXES_TO_DELETE:
            if index_name in existing_indexes:
                try:
                    logger.info(f"🗑️  Deleting: {index_name}")
                    pc.delete_index(index_name)
                    logger.info(f"   ✅ Deleted successfully")
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"   ❌ Failed to delete: {e}")
            else:
                logger.info(f"⏭️  Skipping: {index_name} (does not exist)")
                skipped_count += 1
        
        # Summary
        logger.info(f"\n{'='*70}")
        logger.info("📊 CLEANUP SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"✅ Deleted: {deleted_count} indexes")
        logger.info(f"⏭️  Skipped: {skipped_count} indexes")
        
        # Check remaining indexes
        remaining_indexes = [index.name for index in pc.list_indexes()]
        logger.info(f"\n📋 Remaining indexes: {len(remaining_indexes)}")
        for idx in remaining_indexes:
            logger.info(f"   - {idx}")
        
        logger.info(f"\n✅ Cleanup complete!")
        logger.info(f"\n🎯 Next step: Run setup_namespace_architecture.py to create master index")
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    logger.info("Starting index cleanup...\n")
    cleanup_indexes()
