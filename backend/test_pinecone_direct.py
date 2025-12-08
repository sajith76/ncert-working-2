"""Test Pinecone directly to see what's in Class 6 Chapter 4"""
from app.db.mongo import pinecone_db
from sentence_transformers import SentenceTransformer

# Initialize
print("🔌 Connecting to Pinecone...")
pinecone_db.connect()

# Load embedding model
print("📦 Loading embedding model...")
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Test query
question = "What is the number of children who always slept at least 9 hours at night?"
print(f"\n🔍 Question: {question}\n")

# Generate embedding
print("🔢 Generating embedding...")
query_vector = model.encode(question).tolist()

# Test with different filter variations
test_filters = [
    {"class": "6", "subject": "Mathematics", "chapter": "4"},
    {"class": "6", "subject": "Mathematics"},
    {"class": "6"},
    {}  # No filter
]

for i, filter_dict in enumerate(test_filters, 1):
    print(f"\n--- Test {i}: Filter = {filter_dict} ---")
    try:
        results = pinecone_db.index.query(
            namespace="mathematics",
            vector=query_vector,
            top_k=3,
            filter=filter_dict,
            include_metadata=True
        )
        
        print(f"✅ Found {len(results.matches)} results")
        if results.matches:
            for j, match in enumerate(results.matches[:2], 1):
                print(f"\n  Match {j}:")
                print(f"    Score: {match.score:.4f}")
                print(f"    Metadata: {match.metadata}")
                text = match.metadata.get('text', '')[:200]
                print(f"    Text: {text}...")
    except Exception as e:
        print(f"❌ Error: {e}")
