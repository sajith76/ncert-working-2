"""Debug RAG service step by step"""
from app.services.enhanced_rag_service import EnhancedRAGService
from app.db.mongo import pinecone_db
from app.services.gemini_service import gemini_service

# Initialize properly
pinecone_db.connect()

print("🔍 Debugging RAG Service Query\n")

# Create RAG instance
rag = EnhancedRAGService()

# Test query
question = "what is common multiples and common factors"
subject = "Mathematics"
student_class = 6
chapter = 5
mode = "basic"

print(f"Query: {question}")
print(f"Class: {student_class}, Chapter: {chapter}, Mode: {mode}\n")

# Step 1: Generate embedding
print("[Step 1] Generating embedding...")
try:
    query_embedding = gemini_service.generate_embedding(question)
    print(f"✅ Embedding generated: {len(query_embedding)} dimensions")
    print(f"   Sample values: {query_embedding[:5]}\n")
except Exception as e:
    print(f"❌ Embedding failed: {e}\n")
    import sys
    sys.exit(1)

# Step 2: Get prerequisite classes
print("[Step 2] Getting prerequisite classes...")
classes_to_search = rag.get_prerequisite_classes(subject, student_class, mode)
print(f"✅ Classes to search: {classes_to_search}\n")

# Step 3: Get namespace
print("[Step 3] Getting namespace...")
namespace = rag.get_namespace(subject)
print(f"✅ Namespace: {namespace}\n")

# Step 4: Check textbook_db
print("[Step 4] Checking textbook_db connection...")
print(f"   textbook_db: {rag.textbook_db}")
print(f"   textbook_db.index: {rag.textbook_db.index}")
print(f"   Index is None: {rag.textbook_db.index is None}\n")

if rag.textbook_db.index is None:
    print("❌ ERROR: textbook_db.index is None!")
    print("   This is why RAG returns 0 results!\n")
    import sys
    sys.exit(1)

# Step 5: Manual query for each class
print("[Step 5] Querying Pinecone directly...")

for class_level in classes_to_search:
    print(f"\n   Testing Class {class_level}:")
    
    metadata_filter = {
        "class": str(class_level),
        "subject": subject
    }
    
    if chapter is not None:
        metadata_filter["chapter"] = str(chapter)
    
    print(f"   Filter: {metadata_filter}")
    
    try:
        results = rag.textbook_db.index.query(
            namespace=namespace,
            vector=query_embedding,
            top_k=5,
            filter=metadata_filter,
            include_metadata=True
        )
        
        matches = results.get('matches', [])
        print(f"   ✅ Raw matches: {len(matches)}")
        
        if len(matches) > 0:
            print(f"   Top match:")
            print(f"      ID: {matches[0].id}")
            print(f"      Score: {matches[0].score:.4f}")
            print(f"      Metadata: {matches[0].metadata}")
            
            # Check threshold
            threshold = 0.3 if mode == "basic" else 0.2
            above_threshold = [m for m in matches if m.score >= threshold]
            print(f"   Matches above threshold ({threshold}): {len(above_threshold)}")
            
            if len(above_threshold) == 0:
                print(f"   ⚠️  All scores below threshold!")
                print(f"   Scores: {[round(m.score, 4) for m in matches]}")
        else:
            print(f"   ❌ No matches found")
            
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*70)
print("🎯 ROOT CAUSE IDENTIFICATION")
print("="*70)
