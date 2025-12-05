"""
Script to create subject-wise Pinecone indexes for the new architecture.

This script creates 7 subject-specific indexes in Pinecone:
- Mathematics (Classes 5-12)
- Physics (Classes 9-12)
- Chemistry (Classes 9-12)
- Biology (Classes 9-12)
- Social Science (Classes 5-10)
- English (Classes 5-12)
- Hindi (Classes 5-12)

Each index uses dimension 768 (matching Gemini text-embedding-004)
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Subject configurations
SUBJECT_INDEXES = {
    "Mathematics": {
        "index_name": settings.PINECONE_MATH_INDEX,
        "classes": "5-12",
        "description": "NCERT Mathematics content for Classes 5-12"
    },
    "Physics": {
        "index_name": settings.PINECONE_PHYSICS_INDEX,
        "classes": "9-12",
        "description": "NCERT Physics content for Classes 9-12"
    },
    "Chemistry": {
        "index_name": settings.PINECONE_CHEMISTRY_INDEX,
        "classes": "9-12",
        "description": "NCERT Chemistry content for Classes 9-12"
    },
    "Biology": {
        "index_name": settings.PINECONE_BIOLOGY_INDEX,
        "classes": "9-12",
        "description": "NCERT Biology content for Classes 9-12"
    },
    "Social Science": {
        "index_name": settings.PINECONE_SOCIAL_INDEX,
        "classes": "5-10",
        "description": "NCERT Social Science content for Classes 5-10"
    },
    "English": {
        "index_name": settings.PINECONE_ENGLISH_INDEX,
        "classes": "5-12",
        "description": "NCERT English content for Classes 5-12"
    },
    "Hindi": {
        "index_name": settings.PINECONE_HINDI_INDEX,
        "classes": "5-12",
        "description": "NCERT Hindi content for Classes 5-12"
    }
}


def create_subject_indexes():
    """Create all subject-wise Pinecone indexes."""
    
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        logger.info("="*70)
        logger.info("🚀 Creating Subject-Wise Pinecone Indexes")
        logger.info("="*70)
        
        # Get existing indexes
        existing_indexes = [index.name for index in pc.list_indexes()]
        logger.info(f"\n📋 Existing indexes: {len(existing_indexes)}")
        for idx in existing_indexes:
            logger.info(f"   - {idx}")
        
        # Create each subject index
        created_count = 0
        skipped_count = 0
        
        for subject, config in SUBJECT_INDEXES.items():
            index_name = config["index_name"]
            
            logger.info(f"\n{'='*70}")
            logger.info(f"📚 Subject: {subject}")
            logger.info(f"   Index: {index_name}")
            logger.info(f"   Classes: {config['classes']}")
            logger.info(f"   Description: {config['description']}")
            
            if index_name in existing_indexes:
                logger.info(f"   ⚠️  Index already exists - SKIPPING")
                skipped_count += 1
                continue
            
            try:
                # Create index with serverless spec
                pc.create_index(
                    name=index_name,
                    dimension=768,  # Gemini text-embedding-004 dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                
                logger.info(f"   ✅ Index created successfully!")
                created_count += 1
                
                # Wait a bit between creations to avoid rate limits
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"   ❌ Failed to create index: {e}")
        
        # Summary
        logger.info(f"\n{'='*70}")
        logger.info("📊 SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"✅ Created: {created_count} indexes")
        logger.info(f"⚠️  Skipped: {skipped_count} indexes (already exist)")
        logger.info(f"📚 Total: {len(SUBJECT_INDEXES)} subject indexes")
        logger.info(f"{'='*70}")
        
        # Wait for indexes to be ready
        if created_count > 0:
            logger.info("\n⏳ Waiting for new indexes to be ready...")
            time.sleep(10)
            
            # Check status of newly created indexes
            logger.info("\n📊 Checking index status:")
            for subject, config in SUBJECT_INDEXES.items():
                index_name = config["index_name"]
                try:
                    index = pc.Index(index_name)
                    stats = index.describe_index_stats()
                    logger.info(f"   ✅ {subject}: Ready (vectors: {stats.get('total_vector_count', 0)})")
                except Exception as e:
                    logger.warning(f"   ⚠️  {subject}: {e}")
        
        logger.info("\n🎉 Subject-wise index setup complete!")
        logger.info("\n📝 Next steps:")
        logger.info("   1. Run the data migration script to populate indexes")
        logger.info("   2. Update your application to use subject-wise queries")
        logger.info("   3. Test cross-class learning functionality")
        
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")
        raise


if __name__ == "__main__":
    logger.info("Starting Pinecone subject-wise index creation...\n")
    create_subject_indexes()
