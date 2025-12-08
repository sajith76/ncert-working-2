"""Simple script to check Class 6 chapters in Pinecone"""
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(
    name=os.getenv('PINECONE_INDEX'),
    host=os.getenv('PINECONE_HOST')
)

# Get stats
stats = index.describe_index_stats()
print(f"\n📊 Total vectors in mathematics namespace: {stats.get('namespaces', {}).get('mathematics', {}).get('vector_count', 0)}")

# Try to find Class 6 chapters by fetching some IDs
# Let's query for any Class 6 content
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

query_vector = model.encode("mathematics").tolist()

# Search for Class 6
results = index.query(
    namespace="mathematics",
    vector=query_vector,
    top_k=50,
    filter={"class": "6"},
    include_metadata=True
)

print(f"\n✅ Found {len(results.matches)} Class 6 vectors")

# Group by chapter
chapters = {}
for match in results.matches:
    ch = match.metadata.get('chapter', '?')
    if ch not in chapters:
        chapters[ch] = []
    chapters[ch].append(match.metadata.get('ncert_id', ''))

print(f"\n📚 Class 6 Chapters currently in Pinecone:")
for ch in sorted(chapters.keys()):
    print(f"   Chapter {ch}: {len(chapters[ch])} chunks")
    if len(chapters[ch]) > 0:
        print(f"      Sample IDs: {', '.join(chapters[ch][:3])}")
