"""
Check what Class 6 Math content exists in Pinecone
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from app.db.mongo import init_databases, pinecone_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_class6_content():
    """Query Pinecone to see what Class 6 Math content exists"""
    
    # Initialize databases
    logger.info("🔌 Initializing databases...")
    await init_databases()
    
    logger.info("="*80)
    logger.info("🔍 Checking What Classes Exist in Pinecone Mathematics Namespace")
    logger.info("="*80)
    
    try:
        # Query without filters to see what's there
        logger.info("\n1️⃣ Querying ALL vectors (no filter)...")
        all_results = pinecone_db.index.query(
            namespace="mathematics",
            vector=[0.0] * 768,
            top_k=100,
            include_metadata=True
        )
        
        classes_found = {}
        subjects_found = set()
        
        for match in all_results.get('matches', []):
            meta = match.get('metadata', {})
            class_val = meta.get('class', 'NONE')
            subject = meta.get('subject', 'NONE')
            chapter = meta.get('chapter', 'NONE')
            
            if class_val not in classes_found:
                classes_found[class_val] = {'count': 0, 'chapters': set(), 'subjects': set()}
            classes_found[class_val]['count'] += 1
            classes_found[class_val]['chapters'].add(chapter)
            classes_found[class_val]['subjects'].add(subject)
            subjects_found.add(subject)
        
        logger.info(f"\n📊 Summary of {len(all_results.get('matches', []))} sampled vectors:")
        logger.info(f"\n   Classes found: {sorted(classes_found.keys())}")
        logger.info(f"   Subjects found: {sorted(subjects_found)}")
        
        logger.info(f"\n   Details per class:")
        for class_val in sorted(classes_found.keys()):
            info = classes_found[class_val]
            logger.info(f"   • Class '{class_val}': {info['count']} vectors")
            logger.info(f"      Subjects: {sorted(info['subjects'])}")
            logger.info(f"      Chapters: {sorted(info['chapters'])}")
        
        # Now test Class 6 specifically
        logger.info(f"\n\n2️⃣ Testing Class 6 filter...")
        class6_results = pinecone_db.index.query(
            namespace="mathematics",
            vector=[0.0] * 768,
            top_k=5,
            filter={"class": "6"},
            include_metadata=True
        )
        
        if class6_results.get('matches'):
            logger.info(f"   ✅ Found {len(class6_results['matches'])} Class 6 vectors")
            for i, match in enumerate(class6_results['matches'][:3], 1):
                meta = match.get('metadata', {})
                logger.info(f"   {i}. ID: {match.get('id')}")
                logger.info(f"      Class: '{meta.get('class')}' (type: {type(meta.get('class')).__name__})")
                logger.info(f"      Subject: {meta.get('subject')}")
                logger.info(f"      Chapter: {meta.get('chapter')}")
        else:
            logger.warning("   ⚠️ NO CLASS 6 VECTORS FOUND with filter!")
        
        # Test Class 10
        logger.info(f"\n\n3️⃣ Testing Class 10 filter...")
        class10_results = pinecone_db.index.query(
            namespace="mathematics",
            vector=[0.0] * 768,
            top_k=5,
            filter={"class": "10"},
            include_metadata=True
        )
        
        if class10_results.get('matches'):
            logger.info(f"   ✅ Found {len(class10_results['matches'])} Class 10 vectors")
        else:
            logger.warning("   ⚠️ NO CLASS 10 VECTORS FOUND with filter!")
        
    except Exception as e:
        logger.error(f"❌ Query failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(check_class6_content())
