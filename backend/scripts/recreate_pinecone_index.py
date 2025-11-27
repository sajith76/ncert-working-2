"""
Recreate Pinecone Index with Correct Dimensions

This script will:
1. Delete the existing index (if needed)
2. Create a new index with 768 dimensions (for Gemini text-embedding-004)
"""

import os
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()


def main():
    """Recreate Pinecone index with correct dimensions"""
    
    print("=" * 70)
    print("  🔧 Pinecone Index Recreation")
    print("=" * 70)
    
    # Connect to Pinecone
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    
    index_name = "ncert-learning-rag"
    
    # Check if index exists
    existing_indexes = pc.list_indexes()
    print(f"\n📋 Existing indexes: {[idx.name for idx in existing_indexes]}")
    
    # Delete existing index if it exists
    if any(idx.name == index_name for idx in existing_indexes):
        print(f"\n⚠️  Index '{index_name}' exists with wrong dimensions (384)")
        print(f"🗑️  Deleting existing index...")
        
        try:
            pc.delete_index(index_name)
            print(f"✓ Deleted index '{index_name}'")
            
            # Wait for deletion to complete
            print("⏳ Waiting for deletion to complete (10 seconds)...")
            time.sleep(10)
            
        except Exception as e:
            print(f"✗ Error deleting index: {e}")
            print("\n💡 You may need to delete it manually:")
            print("   1. Go to: https://app.pinecone.io/")
            print("   2. Select your index")
            print("   3. Click 'Delete Index'")
            return
    
    # Create new index with correct dimensions
    print(f"\n🆕 Creating new index '{index_name}' with 768 dimensions...")
    
    try:
        pc.create_index(
            name=index_name,
            dimension=768,  # Gemini text-embedding-004 dimension
            metric='cosine',  # Best for semantic similarity
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'  # Free tier region
            )
        )
        
        print(f"✓ Created index '{index_name}'")
        
        # Wait for index to be ready
        print("⏳ Waiting for index to be ready (30 seconds)...")
        time.sleep(30)
        
        # Verify index
        index = pc.Index(name=index_name)
        stats = index.describe_index_stats()
        
        print(f"\n✅ Index created successfully!")
        print(f"📊 Index Statistics:")
        print(f"  ├─ Name: {index_name}")
        print(f"  ├─ Dimension: {stats.dimension}")
        print(f"  ├─ Metric: cosine")
        print(f"  └─ Total Vectors: {stats.total_vector_count}")
        
        # Update .env with new host
        print(f"\n💡 Index Host: {index.host}")
        print(f"💡 Update your .env file with:")
        print(f"   PINECONE_HOST={index.host}")
        
    except Exception as e:
        print(f"✗ Error creating index: {e}")
        return
    
    print("\n" + "=" * 70)
    print("  ✅ Index recreation complete!")
    print("=" * 70)
    print("\n🚀 Next steps:")
    print("  1. Update PINECONE_HOST in .env (if changed)")
    print("  2. Run: python scripts\\upload_pdfs_to_pinecone.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
