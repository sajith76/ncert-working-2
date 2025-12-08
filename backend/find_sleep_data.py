"""Find the data table with the sleep data"""
from app.db.mongo import pinecone_db
from sentence_transformers import SentenceTransformer

# Initialize
print("🔌 Connecting to Pinecone...")
pinecone_db.connect()

# Load embedding model
print("📦 Loading embedding model...")
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Search for the data table
queries = [
    "table showing hours of sleep children per day",
    "data children 9 hours sleep night",
    "number of children slept hours table"
]

for question in queries:
    print(f"\n🔍 Searching: {question}")
    query_vector = model.encode(question).tolist()
    
    results = pinecone_db.index.query(
        namespace="mathematics",
        vector=query_vector,
        top_k=5,
        filter={"class": "6", "chapter": "4"},
        include_metadata=True
    )
    
    print(f"✅ Found {len(results.matches)} results\n")
    for i, match in enumerate(results.matches[:3], 1):
        print(f"--- Match {i} (Score: {match.score:.4f}) ---")
        text = match.metadata.get('text', '')
        content_type = match.metadata.get('content_type', 'unknown')
        page = match.metadata.get('page', '?')
        print(f"Type: {content_type}, Page: {page}")
        print(f"Text: {text[:500]}...")
        print()
