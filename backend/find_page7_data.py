"""Find all text chunks from page 7 (where the data table is)"""
from app.db.mongo import pinecone_db
from sentence_transformers import SentenceTransformer

# Initialize
print("🔌 Connecting to Pinecone...")
pinecone_db.connect()

# Load embedding model
print("📦 Loading embedding model...")
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Search broadly for page 7 content
question = "hours of sleep children data"
query_vector = model.encode(question).tolist()

# Get more results from pages 6-8
results = pinecone_db.index.query(
    namespace="mathematics",
    vector=query_vector,
    top_k=20,  # Get more results
    filter={"class": "6", "chapter": "4"},
    include_metadata=True
)

print(f"✅ Found {len(results.matches)} results\n")

# Group by page
by_page = {}
for match in results.matches:
    page = match.metadata.get('page', '?')
    if page not in by_page:
        by_page[page] = []
    by_page[page].append(match)

# Show pages 6-8
for page in sorted(by_page.keys()):
    if page in ['6', '7', '8']:
        print(f"\n{'='*60}")
        print(f"PAGE {page}")
        print(f"{'='*60}\n")
        
        for i, match in enumerate(by_page[page][:5], 1):
            content_type = match.metadata.get('content_type', 'unknown')
            ncert_id = match.metadata.get('ncert_id', '')
            text = match.metadata.get('text', '')
            print(f"--- Chunk {i} ({content_type}) ID: {ncert_id} ---")
            print(f"Score: {match.score:.4f}")
            print(f"{text[:600]}\n")
