"""
Quick test script to verify RAG service is finding answers.
Tests the exact question from the user's screenshot.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from app.services.enhanced_rag_service import enhanced_rag_service
from app.db.mongo import init_databases
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_user_question():
    """Test the exact question from the user: children sleeping data"""
    
    # Initialize databases first
    logger.info("🔌 Initializing databases...")
    await init_databases()
    
    question = "What is the number of children who always slept at least 9 hours at night?"
    
    logger.info("="*80)
    logger.info("🧪 Testing RAG Service with User's Question")
    logger.info("="*80)
    logger.info(f"Question: {question}")
    logger.info(f"Context: Class 6, Mathematics, Chapter 4 (likely Data Handling)")
    logger.info("")
    
    try:
        # Test Basic Mode
        logger.info("🔍 Testing BASIC MODE...")
        answer, chunks = enhanced_rag_service.answer_question_basic(
            question=question,
            subject="Mathematics",
            student_class=6,
            chapter=4
        )
        
        logger.info(f"✅ Basic Mode Results:")
        logger.info(f"   Chunks found: {len(chunks)}")
        logger.info(f"   Answer length: {len(answer)} chars")
        
        if chunks:
            logger.info(f"\n   Sample chunks:")
            for i, chunk in enumerate(chunks[:3], 1):
                logger.info(f"   Chunk {i}: {chunk.get('text', '')[:100]}...")
                logger.info(f"            Class: {chunk.get('class')}, Score: {chunk.get('score', 0):.2f}")
        
        logger.info(f"\n📝 Answer Preview:")
        logger.info(answer[:500] + "..." if len(answer) > 500 else answer)
        
        # Test Deep Dive Mode
        logger.info("\n\n🔍 Testing DEEP DIVE MODE...")
        answer_dd, chunks_dd = enhanced_rag_service.answer_question_deepdive(
            question=question,
            subject="Mathematics",
            student_class=6,
            chapter=4
        )
        
        logger.info(f"✅ Deep Dive Mode Results:")
        logger.info(f"   Chunks found: {len(chunks_dd)}")
        logger.info(f"   Answer length: {len(answer_dd)} chars")
        
        logger.info("\n" + "="*80)
        
        if not chunks:
            logger.warning("⚠️ NO CHUNKS FOUND! This means:")
            logger.warning("   1. Class 6 Chapter 4 data might not be in Pinecone")
            logger.warning("   2. Metadata filters might still have issues")
            logger.warning("   3. Question embedding might not match content")
        else:
            logger.info("✅ RAG SERVICE IS WORKING!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_user_question())
