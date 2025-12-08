"""
Test with actual embedding to find the sleeping hours question
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from app.db.mongo import init_databases, pinecone_db
from app.services.gemini_service import gemini_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def search_sleeping_question():
    """Search for content about children sleeping hours"""
    
    # Initialize databases
    logger.info("🔌 Initializing databases...")
    await init_databases()
    
    logger.info("="*80)
    logger.info("🔍 Searching for 'children sleeping 9 hours' content")
    logger.info("="*80)
    
    try:
        # Generate embedding for the question
        question = "What is the number of children who always slept at least 9 hours at night?"
        logger.info(f"\nQuestion: {question}")
        
        embedding = gemini_service.generate_embedding(question)
        logger.info(f"✓ Generated embedding (dim={len(embedding)})")
        
        # Search WITHOUT any filters first
        logger.info("\n1️⃣ Searching WITHOUT filters (top 10)...")
        results_no_filter = pinecone_db.index.query(
            namespace="mathematics",
            vector=embedding,
            top_k=10,
            include_metadata=True
        )
        
        logger.info(f"   Found {len(results_no_filter.get('matches', []))} results")
        for i, match in enumerate(results_no_filter.get('matches', [])[:5], 1):
            meta = match.get('metadata', {})
            logger.info(f"\n   {i}. Score: {match.get('score', 0):.3f}")
            logger.info(f"      Class {meta.get('class')}, Ch{meta.get('chapter')}, Page {meta.get('page')}")
            logger.info(f"      {meta.get('text', '')[:200]}...")
        
        # Search with Class 6 filter
        logger.info("\n\n2️⃣ Searching WITH Class 6 filter...")
        results_class6 = pinecone_db.index.query(
            namespace="mathematics",
            vector=embedding,
            top_k=10,
            filter={"class": "6"},
            include_metadata=True
        )
        
        logger.info(f"   Found {len(results_class6.get('matches', []))} results")
        for i, match in enumerate(results_class6.get('matches', [])[:5], 1):
            meta = match.get('metadata', {})
            logger.info(f"\n   {i}. Score: {match.get('score', 0):.3f}")
            logger.info(f"      Class {meta.get('class')}, Ch{meta.get('chapter')}, Page {meta.get('page')}")
            logger.info(f"      {meta.get('text', '')[:200]}...")
        
        # Search with Class 6 Chapter 4 filter
        logger.info("\n\n3️⃣ Searching WITH Class 6, Chapter 4 filter...")
        results_ch4 = pinecone_db.index.query(
            namespace="mathematics",
            vector=embedding,
            top_k=10,
            filter={"class": "6", "chapter": "4"},
            include_metadata=True
        )
        
        logger.info(f"   Found {len(results_ch4.get('matches', []))} results")
        for i, match in enumerate(results_ch4.get('matches', [])[:5], 1):
            meta = match.get('metadata', {})
            logger.info(f"\n   {i}. Score: {match.get('score', 0):.3f}")
            logger.info(f"      Class {meta.get('class')}, Ch{meta.get('chapter')}, Page {meta.get('page')}")
            logger.info(f"      {meta.get('text', '')[:200]}...")
        
        logger.info("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(search_sleeping_question())
