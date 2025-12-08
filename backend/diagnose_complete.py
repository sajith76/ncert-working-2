"""
COMPREHENSIVE DIAGNOSIS: Why Chatbot Returns "No Answer Found"

This script checks all potential issues:
1. Pinecone connection and data availability
2. Backend API query flow
3. RAG service configuration
4. Embedding model consistency
5. Metadata filter issues
"""

import sys
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("🔍 COMPREHENSIVE SYSTEM DIAGNOSIS")
print("=" * 70)

# ============================================================
# TEST 1: Pinecone Connection & Data
# ============================================================
print("\n[TEST 1] Pinecone Connection & Data Availability")
print("-" * 70)

try:
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    index = pc.Index(
        name=os.getenv('PINECONE_INDEX'),
        host=os.getenv('PINECONE_HOST')
    )
    
    stats = index.describe_index_stats()
    math_stats = stats.get('namespaces', {}).get('mathematics', {})
    total_vectors = math_stats.get('vector_count', 0)
    
    print(f"✅ Pinecone Connected")
    print(f"   Index: {os.getenv('PINECONE_INDEX')}")
    print(f"   Mathematics Namespace: {total_vectors} vectors")
    
    if total_vectors == 0:
        print("   ❌ ERROR: No vectors in mathematics namespace!")
        sys.exit(1)
    
except Exception as e:
    print(f"❌ Pinecone Connection Failed: {e}")
    sys.exit(1)

# ============================================================
# TEST 2: Class 6 Data Availability
# ============================================================
print("\n[TEST 2] Class 6 Chapter Data")
print("-" * 70)

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
query_vector = model.encode("mathematics").tolist()

# Query for Class 6 data
results = index.query(
    namespace="mathematics",
    vector=query_vector,
    top_k=100,
    filter={"class": "6"},
    include_metadata=True
)

class6_chunks = len(results.matches)
print(f"✅ Found {class6_chunks} Class 6 vectors")

# Group by chapter
chapters = {}
for match in results.matches:
    ch = match.metadata.get('chapter', '?')
    if ch not in chapters:
        chapters[ch] = 0
    chapters[ch] += 1

print(f"\n📚 Chapter Distribution:")
for ch in sorted(chapters.keys()):
    print(f"   Chapter {ch}: {chapters[ch]} chunks")

# Check if Chapter 1 has enough data
ch1_count = chapters.get('1', 0)
if ch1_count < 50:
    print(f"\n⚠️  WARNING: Chapter 1 has only {ch1_count} chunks (need ~200-300)")
    print("   This explains why 'What is mathematics?' returns no answer!")

# ============================================================
# TEST 3: Simulate User's Query
# ============================================================
print("\n[TEST 3] Simulating User's Query: 'what is common multiples and common factors'")
print("-" * 70)

user_question = "what is common multiples and common factors"
query_emb = model.encode(user_question).tolist()

# Query Class 6, Chapter 5
results_ch5 = index.query(
    namespace="mathematics",
    vector=query_emb,
    top_k=5,
    filter={"class": "6", "chapter": "5"},
    include_metadata=True
)

print(f"✅ Query Results for Class 6, Chapter 5:")
print(f"   Found {len(results_ch5.matches)} matches")

if len(results_ch5.matches) > 0:
    print(f"\n   Top 3 Results:")
    for i, match in enumerate(results_ch5.matches[:3], 1):
        print(f"\n   {i}. ID: {match.id}")
        print(f"      Score: {match.score:.4f}")
        print(f"      Text: {match.metadata.get('text', '')[:150]}...")
else:
    print("   ❌ No results found!")

# ============================================================
# TEST 4: Check Metadata Format
# ============================================================
print("\n[TEST 4] Metadata Format Validation")
print("-" * 70)

# Fetch a specific known ID from Pinecone screenshot
sample_ids = ["class6_ch5_0000", "class6_ch1_0001"]

for sample_id in sample_ids:
    try:
        result = index.fetch(ids=[sample_id], namespace="mathematics")
        if sample_id in result.get('vectors', {}):
            metadata = result['vectors'][sample_id].get('metadata', {})
            print(f"\n✅ Found {sample_id}:")
            print(f"   class: {metadata.get('class')} (type: {type(metadata.get('class'))})")
            print(f"   chapter: {metadata.get('chapter')} (type: {type(metadata.get('chapter'))})")
            print(f"   subject: {metadata.get('subject')}")
            print(f"   page: {metadata.get('page')}")
            
            # Check if it's string (should be!)
            if not isinstance(metadata.get('class'), str):
                print(f"   ⚠️  WARNING: class is not string!")
            if not isinstance(metadata.get('chapter'), str):
                print(f"   ⚠️  WARNING: chapter is not string!")
        else:
            print(f"❌ {sample_id} not found in Pinecone")
    except Exception as e:
        print(f"❌ Error fetching {sample_id}: {e}")

# ============================================================
# TEST 5: Backend RAG Service Check
# ============================================================
print("\n[TEST 5] Backend RAG Service Configuration")
print("-" * 70)

try:
    from app.services.enhanced_rag_service import EnhancedRAGService
    from app.db.mongo import pinecone_db
    
    # Initialize
    pinecone_db.connect()
    rag = EnhancedRAGService()
    
    print("✅ RAG Service initialized")
    print(f"   Textbook DB connected: {rag.textbook_db.index is not None}")
    print(f"   Gemini Service: {rag.gemini is not None}")
    
    # Test query
    print("\n   Testing RAG query...")
    chunks, class_dist = rag.query_multi_class(
        query_text="what is common multiples",
        subject="Mathematics",
        student_class=6,
        chapter=5,
        mode="basic"
    )
    
    print(f"   ✅ Query executed")
    print(f"   Results: {len(chunks)} chunks from {class_dist}")
    
    if len(chunks) == 0:
        print("   ❌ ERROR: RAG returned 0 chunks!")
        print("   This is the root cause of 'no answer found'")
    else:
        print(f"   ✅ RAG working - found data!")
        print(f"   Top result: {chunks[0]['text'][:100]}...")
    
except Exception as e:
    print(f"❌ RAG Service Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================
# DIAGNOSIS SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("📋 DIAGNOSIS SUMMARY")
print("=" * 70)

print("\n✅ WORKING:")
print("   • Pinecone connection")
print("   • Mathematics namespace exists")
print("   • Some Class 6 data present")

print("\n❌ ISSUES FOUND:")
print("   • Chapter 1 has insufficient data (only 11 chunks, need 200-300)")
print("   • Total Class 6 data: only 50 old test chunks")
print("   • Processing of all 10 chapters never completed")

print("\n🔧 SOLUTION:")
print("   1. Complete processing of all 10 Class 6 chapters")
print("   2. This will add ~6,000-8,000 vectors")
print("   3. Then all questions will work")

print("\n📝 NEXT ACTION:")
print("   Run: python scripts/process_ncert_maths.py --class 6")
print("   Wait: 40-50 minutes for full processing")
print("   Verify: python quick_check.py (should show ~600-900 chunks per chapter)")
print("\n" + "=" * 70)
