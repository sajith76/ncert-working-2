"""
Sample script to upload chapter embeddings to Pinecone.

This is a template script. You'll need to:
1. Prepare your NCERT chapter text data
2. Split it into chunks (e.g., by paragraph or page)
3. Generate embeddings using Gemini
4. Upload to Pinecone with proper metadata

Run this script AFTER setting up your .env file.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pinecone import Pinecone
import google.generativeai as genai
from app.core.config import settings
import time

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

# Initialize Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(name=settings.PINECONE_INDEX, host=settings.PINECONE_HOST)


def generate_embedding(text: str) -> list[float]:
    """Generate embedding using Gemini."""
    result = genai.embed_content(
        model='models/text-embedding-004',
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']


def upload_sample_data():
    """
    Upload sample chapter data to Pinecone.
    
    MODIFY THIS with your actual NCERT chapter content!
    """
    
    # Sample data structure
    sample_chapters = [
        {
            "id": "class6-geography-ch1-section1",
            "text": """
            Latitude is the angular distance of a place north or south of the Earth's equator. 
            Lines of latitude are imaginary lines that run parallel to the equator. 
            The equator is at 0° latitude, and the poles are at 90° north and south latitude.
            """,
            "metadata": {
                "class": 6,
                "subject": "Geography",
                "chapter": 1,
                "page": 1,
                "section": "Locating Places on Earth"
            }
        },
        {
            "id": "class6-geography-ch1-section2",
            "text": """
            Longitude is the angular distance of a place east or west of the prime meridian. 
            Lines of longitude (meridians) run from the North Pole to the South Pole. 
            The prime meridian passes through Greenwich, England, and is at 0° longitude.
            """,
            "metadata": {
                "class": 6,
                "subject": "Geography",
                "chapter": 1,
                "page": 2,
                "section": "Locating Places on Earth"
            }
        },
        {
            "id": "class6-history-ch4-section1",
            "text": """
            History is the study of past events, particularly in human affairs. 
            To measure time in history, we use different calendars and dating systems. 
            The most common system uses BC (Before Christ) and AD (Anno Domini) for dates.
            """,
            "metadata": {
                "class": 6,
                "subject": "History",
                "chapter": 4,
                "page": 1,
                "section": "Timeline and Sources"
            }
        },
        # Add more chapters here...
    ]
    
    print("🚀 Starting data upload to Pinecone...")
    print(f"   Index: {settings.PINECONE_INDEX}")
    print(f"   Total chunks: {len(sample_chapters)}")
    print()
    
    vectors = []
    
    for i, chapter in enumerate(sample_chapters):
        print(f"Processing chunk {i+1}/{len(sample_chapters)}: {chapter['id']}")
        
        # Generate embedding
        embedding = generate_embedding(chapter['text'])
        
        # Prepare vector tuple (id, embedding, metadata)
        vectors.append((
            chapter['id'],
            embedding,
            {
                **chapter['metadata'],
                'text': chapter['text'].strip()  # Store text in metadata for retrieval
            }
        ))
        
        # Rate limiting (Gemini API)
        time.sleep(0.5)
    
    # Upload to Pinecone in batch
    print("\n📤 Uploading vectors to Pinecone...")
    index.upsert(vectors=vectors)
    
    print(f"\n✅ Successfully uploaded {len(vectors)} vectors!")
    
    # Verify upload
    stats = index.describe_index_stats()
    print(f"   Total vectors in index: {stats.get('total_vector_count', 0)}")


def test_query():
    """Test a sample query after upload."""
    print("\n🔍 Testing sample query...")
    
    query_text = "What is latitude?"
    print(f"   Query: {query_text}")
    
    # Generate query embedding
    query_embedding = generate_embedding(query_text)
    
    # Query Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=3,
        filter={"class": 6, "subject": "Geography"},
        include_metadata=True
    )
    
    print(f"\n   Found {len(results.get('matches', []))} matches:")
    for i, match in enumerate(results.get('matches', [])):
        print(f"\n   Match {i+1}:")
        print(f"   ID: {match['id']}")
        print(f"   Score: {match['score']:.4f}")
        print(f"   Text: {match['metadata'].get('text', '')[:100]}...")


if __name__ == "__main__":
    print("=" * 60)
    print("NCERT Chapter Data Upload Script")
    print("=" * 60)
    print()
    
    try:
        # Upload sample data
        upload_sample_data()
        
        # Test query
        test_query()
        
        print("\n" + "=" * 60)
        print("✅ All done! Your Pinecone index is ready.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
