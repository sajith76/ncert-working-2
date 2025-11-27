"""
Quick Pinecone Status Checker
Shows current vector count and sample data
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()


def main():
    """Check Pinecone status"""
    
    print("=" * 70)
    print("  🔍 Pinecone Status Check")
    print("=" * 70)
    
    # Connect to Pinecone
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    index = pc.Index(host=os.getenv('PINECONE_HOST'))
    
    # Get stats
    stats = index.describe_index_stats()
    
    print(f"\n📊 Index Statistics:")
    print(f"  ├─ Total Vectors: {stats.total_vector_count}")
    print(f"  ├─ Index Fullness: {stats.index_fullness}")
    print(f"  └─ Dimension: {stats.dimension}")
    
    # Get namespaces if any
    if hasattr(stats, 'namespaces') and stats.namespaces:
        print(f"\n📂 Namespaces:")
        for ns_name, ns_stats in stats.namespaces.items():
            print(f"  ├─ {ns_name}: {ns_stats.vector_count} vectors")
    
    # Try to query a sample
    if stats.total_vector_count > 0:
        print(f"\n🔎 Sample Query (first vector):")
        try:
            # Query with a dummy vector to get any result
            results = index.query(
                vector=[0.0] * 768,  # Dummy vector
                top_k=1,
                include_metadata=True
            )
            
            if results.matches:
                match = results.matches[0]
                print(f"  ├─ ID: {match.id}")
                print(f"  ├─ Score: {match.score:.4f}")
                if match.metadata:
                    print(f"  ├─ Metadata:")
                    for key, value in match.metadata.items():
                        if key == 'text':
                            print(f"      ├─ {key}: {value[:100]}...")
                        else:
                            print(f"      ├─ {key}: {value}")
        except Exception as e:
            print(f"  └─ Error querying: {str(e)}")
    
    print("\n" + "=" * 70)
    if stats.total_vector_count > 0:
        print(f"  ✅ Pinecone is ready with {stats.total_vector_count} vectors!")
    else:
        print(f"  ⚠️  No vectors found. Run upload script first.")
    print("=" * 70)


if __name__ == "__main__":
    main()
