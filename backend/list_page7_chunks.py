"""Find the pictograph image or its description"""
from app.db.mongo import pinecone_db
from sentence_transformers import SentenceTransformer

# Initialize
print("🔌 Connecting to Pinecone...")
pinecone_db.connect()

# Get all chunks from page 7, ordered by ID
results = pinecone_db.index.query(
    namespace="mathematics",
    vector=[0.0] * 768,  # Dummy vector to get all results
    top_k=100,
    filter={"class": "6", "chapter": "4", "page": "7"},
    include_metadata=True
)

print(f"✅ Total chunks on page 7: {len(results.matches)}\n")

# Sort by ncert_id to see them in order
sorted_matches = sorted(results.matches, key=lambda x: x.metadata.get('ncert_id', ''))

# Show all chunks from page 7
for i, match in enumerate(sorted_matches, 1):
    content_type = match.metadata.get('content_type', 'unknown')
    ncert_id = match.metadata.get('ncert_id', '')
    has_image = match.metadata.get('has_image', 'False')
    text = match.metadata.get('text', '')
    
    print(f"--- {i}. ID: {ncert_id} ---")
    print(f"Type: {content_type}, Has Image: {has_image}")
    print(f"Text: {text[:500]}")
    print()
