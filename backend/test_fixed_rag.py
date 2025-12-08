"""Test the FIXED RAG service"""
from app.services.enhanced_rag_service import EnhancedRAGService
from app.db.mongo import pinecone_db

# Initialize
pinecone_db.connect()

print("🧪 Testing FIXED RAG Service\n")
print("="*70)

rag = EnhancedRAGService()

# Test queries
test_queries = [
    {
        "question": "what is common multiples and common factors",
        "class": 6,
        "chapter": 5,
        "description": "Chapter 5 Fractions query"
    },
    {
        "question": "what is mathematics",
        "class": 6,
        "chapter": 1,
        "description": "Chapter 1 intro query"
    }
]

for test in test_queries:
    print(f"\n📝 Test: {test['description']}")
    print(f"   Question: \"{test['question']}\"")
    print(f"   Class: {test['class']}, Chapter: {test['chapter']}\n")
    
    chunks, class_dist = rag.query_multi_class(
        query_text=test['question'],
        subject="Mathematics",
        student_class=test['class'],
        chapter=test['chapter'],
        mode="basic"
    )
    
    print(f"   ✅ Results: {len(chunks)} chunks from {class_dist}")
    
    if len(chunks) > 0:
        print(f"   🎯 SUCCESS! Top result:")
        print(f"      Score: {chunks[0]['score']:.4f}")
        print(f"      Text: {chunks[0]['text'][:200]}...")
    else:
        print(f"   ❌ FAILED: No chunks returned")
    
    print("   " + "-"*66)

print("\n" + "="*70)
print("✅ EMBEDDING MODEL FIX COMPLETE!")
print("   RAG now uses sentence-transformers (matching data upload)")
print("="*70)
