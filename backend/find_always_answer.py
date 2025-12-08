"""Search for chunks containing 'always' and specific numbers"""
from app.db.mongo import pinecone_db

# Initialize
print("🔌 Connecting to Pinecone...")
pinecone_db.connect()

# Fetch all chunks from page 7-8 and search for "always"
# We'll do this by fetching by IDs we know exist
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Search for text containing "always"
question = "children always slept 9 hours pictograph"
query_vector = model.encode(question).tolist()

results = pinecone_db.index.query(
    namespace="mathematics",
    vector=query_vector,
    top_k=30,
    filter={"class": "6", "chapter": "4"},
    include_metadata=True
)

print(f"✅ Found {len(results.matches)} results\n")

# Find chunks with "always" in the text
always_chunks = []
for match in results.matches:
    text = match.metadata.get('text', '').lower()
    if 'always' in text and '9 hour' in text:
        always_chunks.append(match)

print(f"🎯 Chunks mentioning 'always' and '9 hour': {len(always_chunks)}\n")

for i, match in enumerate(always_chunks[:10], 1):
    content_type = match.metadata.get('content_type', 'unknown')
    page = match.metadata.get('page', '?')
    ncert_id = match.metadata.get('ncert_id', '')
    text = match.metadata.get('text', '')
    print(f"--- Chunk {i} ---")
    print(f"Type: {content_type}, Page: {page}, ID: {ncert_id}")
    print(f"Score: {match.score:.4f}")
    print(f"Text: {text}\n")
