"""Check for the specific Chapter 4 chunks we just uploaded"""
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(
    name=os.getenv('PINECONE_INDEX'),
    host=os.getenv('PINECONE_HOST')
)

# Try to fetch specific IDs we know should exist from our upload
test_ids = [
    "class6_ch4_0120",  # "What is the number of children who always slept..."
    "class6_ch4_0124",  # The answer "5 × 10 = 50 children"
    "class6_ch4_0125",  # Sometimes answer "25 children"
]

print("🔍 Checking for specific Chapter 4 IDs we just uploaded...\n")

for chunk_id in test_ids:
    try:
        result = index.fetch(ids=[chunk_id], namespace="mathematics")
        if chunk_id in result.get('vectors', {}):
            vector_data = result['vectors'][chunk_id]
            metadata = vector_data.get('metadata', {})
            print(f"✅ Found: {chunk_id}")
            print(f"   Text: {metadata.get('text', '')[:100]}...")
            print(f"   Class: {metadata.get('class')}, Chapter: {metadata.get('chapter')}, Page: {metadata.get('page')}\n")
        else:
            print(f"❌ NOT FOUND: {chunk_id}\n")
    except Exception as e:
        print(f"❌ Error fetching {chunk_id}: {e}\n")

# Also do a broader query for Chapter 4 with page 7
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

query_vector = model.encode("children sleep hours").tolist()

results = index.query(
    namespace="mathematics",
    vector=query_vector,
    top_k=10,
    filter={"class": "6", "chapter": "4", "page": "7"},
    include_metadata=True
)

print(f"\n📊 Query results for Class 6, Chapter 4, Page 7: {len(results.matches)} matches")
for i, match in enumerate(results.matches[:5], 1):
    print(f"\n{i}. ID: {match.id}")
    print(f"   Score: {match.score:.4f}")
    print(f"   Text: {match.metadata.get('text', '')[:150]}...")
