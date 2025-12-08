"""
Quick test to verify the fixed embedding model is working
"""
import sys
sys.path.append('.')

from app.services.enhanced_rag_service import EnhancedRAGService
from app.db.mongo import pinecone_db
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_perimeter_query():
    """Test 'what is perimeter' query"""
    
    print("=" * 80)
    print("🔬 TESTING 'what is perimeter' QUERY")
    print("=" * 80)
    print()
    
    # Initialize
    rag_service = EnhancedRAGService()
    
    # Test query
    question = "what is perimeter"
    subject = "Mathematics"
    student_class = 6
    
    print(f"📝 Question: {question}")
    print(f"📚 Subject: {subject}, Class: {student_class}")
    print()
    
    # Test 1: Direct Pinecone query with sentence-transformers
    print("=" * 80)
    print("TEST 1: Direct Pinecone Query (sentence-transformers)")
    print("=" * 80)
    
    embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    query_embedding = embedding_model.encode(question).tolist()
    
    results = pinecone_db.index.query(
        namespace="mathematics",
        vector=query_embedding,
        filter={"class": {"$eq": "6"}},
        top_k=5,
        include_metadata=True
    )
    
    print(f"✅ Found {len(results.get('matches', []))} results")
    for i, match in enumerate(results.get('matches', [])[:3], 1):
        score = match.get('score', 0)
        metadata = match.get('metadata', {})
        text = metadata.get('text', '')[:200]
        print(f"\n   Match {i}:")
        print(f"   Score: {score:.4f}")
        print(f"   Class: {metadata.get('class')}, Chapter: {metadata.get('chapter')}")
        print(f"   Text: {text}...")
    
    print()
    
    # Test 2: RAG Service Query (Basic Mode)
    print("=" * 80)
    print("TEST 2: RAG Service Query (Basic Mode)")
    print("=" * 80)
    
    try:
        answer, sources = rag_service.answer_question_basic(
            question=question,
            subject=subject,
            student_class=student_class
        )
        
        print(f"✅ Answer generated: {len(answer)} chars")
        print(f"📚 Sources: {len(sources)} chunks")
        print()
        print("Answer:")
        print("-" * 80)
        print(answer[:500] if len(answer) > 500 else answer)
        print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 3: RAG Service Query (DeepDive Mode)
    print("=" * 80)
    print("TEST 3: RAG Service Query (DeepDive Mode)")
    print("=" * 80)
    
    try:
        answer, sources = rag_service.answer_question_deepdive(
            question=question,
            subject=subject,
            student_class=student_class
        )
        
        print(f"✅ Answer generated: {len(answer)} chars")
        print(f"📚 Sources: {len(sources)} chunks")
        print()
        print("Answer:")
        print("-" * 80)
        print(answer[:500] if len(answer) > 500 else answer)
        print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_perimeter_query()
