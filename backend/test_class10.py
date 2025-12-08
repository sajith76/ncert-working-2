"""
Test RAG with Class 10 content that's already in Pinecone
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

async def test_class10_questions():
    """Test with Class 10 Math content that's already processed"""
    
    # Initialize databases
    logger.info("🔌 Initializing databases...")
    await init_databases()
    
    logger.info("="*80)
    logger.info("🧪 Testing RAG with Class 10 Mathematics")
    logger.info("="*80)
    
    # Test questions from topics likely in Class 10
    test_cases = [
        {
            "question": "What is a quadratic equation? Give an example.",
            "class": 10,
            "chapter": None,  # Search all chapters
            "description": "Basic algebra concept"
        },
        {
            "question": "Explain the Pythagorean theorem",
            "class": 10,
            "chapter": None,
            "description": "Geometry fundamentals"
        },
        {
            "question": "What is probability? How do you calculate it?",
            "class": 10,
            "chapter": None,
            "description": "Probability basics"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST {i}/3: {test['description']}")
        logger.info(f"{'='*80}")
        logger.info(f"Question: {test['question']}")
        logger.info(f"Class: {test['class']}, Chapter: {test['chapter'] or 'All'}")
        
        try:
            # Test with Basic Mode
            logger.info("\n🔍 BASIC MODE...")
            answer, chunks = enhanced_rag_service.answer_question_basic(
                question=test['question'],
                subject="Mathematics",
                student_class=test['class'],
                chapter=test['chapter']
            )
            
            logger.info(f"✅ Results:")
            logger.info(f"   Chunks found: {len(chunks)}")
            logger.info(f"   Answer length: {len(answer)} chars")
            
            if chunks:
                logger.info(f"\n   📚 Top 3 sources:")
                for j, chunk in enumerate(chunks[:3], 1):
                    logger.info(f"   {j}. Class {chunk.get('class')}, Ch{chunk.get('chapter')}, "
                              f"Page {chunk.get('page')} - Score: {chunk.get('score', 0):.3f}")
                    logger.info(f"      {chunk.get('text', '')[:150]}...")
                
                logger.info(f"\n   📝 Answer Preview:")
                preview = answer[:300] + "..." if len(answer) > 300 else answer
                logger.info(f"   {preview}")
                
                logger.info(f"\n   ✅ RAG SYSTEM WORKING! Found relevant content.")
            else:
                logger.warning(f"\n   ⚠️ NO CHUNKS FOUND for this question")
        
        except Exception as e:
            logger.error(f"   ❌ Test failed: {e}", exc_info=True)
    
    logger.info("\n" + "="*80)
    logger.info("🎉 Class 10 Testing Complete!")
    logger.info("="*80)

if __name__ == "__main__":
    asyncio.run(test_class10_questions())
