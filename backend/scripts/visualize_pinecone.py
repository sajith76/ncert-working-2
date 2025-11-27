"""
Pinecone Database Visualization
Shows statistics, sample data, and vector distribution
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from pinecone import Pinecone
from dotenv import load_dotenv
from collections import defaultdict
import json

load_dotenv()


def visualize_pinecone():
    """Visualize Pinecone database contents"""
    
    print("=" * 80)
    print("  📊 PINECONE DATABASE VISUALIZATION")
    print("=" * 80)
    
    try:
        # Connect to Pinecone
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index = pc.Index(host=os.getenv('PINECONE_HOST'))
        
        # Get stats
        stats = index.describe_index_stats()
        
        print(f"\n📈 Index Statistics:")
        print(f"  ├─ Total Vectors: {stats.total_vector_count:,}")
        print(f"  ├─ Dimension: {stats.dimension}")
        print(f"  ├─ Index Fullness: {stats.index_fullness * 100:.2f}%")
        
        if hasattr(stats, 'namespaces') and stats.namespaces:
            print(f"  └─ Namespaces: {len(stats.namespaces)}")
            for ns_name, ns_stats in stats.namespaces.items():
                print(f"      └─ {ns_name}: {ns_stats.vector_count:,} vectors")
        else:
            print(f"  └─ Namespaces: 1 (default)")
        
        if stats.total_vector_count == 0:
            print("\n⚠️  No vectors found in database!")
            print("💡 Run: python scripts\\upload_pdfs_to_pinecone.py")
            return
        
        # Query for sample data
        print(f"\n🔍 Sample Vectors (Top 5):")
        print("=" * 80)
        
        try:
            # Query with a dummy vector to get some results
            results = index.query(
                vector=[0.0] * stats.dimension,
                top_k=5,
                include_metadata=True
            )
            
            if results.matches:
                for i, match in enumerate(results.matches, 1):
                    print(f"\n{i}. Vector ID: {match.id}")
                    print(f"   Score: {match.score:.4f}")
                    
                    if match.metadata:
                        metadata = match.metadata
                        
                        # Key metadata
                        if 'lesson_title' in metadata:
                            print(f"   📚 Lesson: {metadata['lesson_title']}")
                        if 'lesson_number' in metadata:
                            print(f"   📖 Lesson #: {metadata['lesson_number']}")
                        if 'chunk_id' in metadata:
                            print(f"   🔢 Chunk: {metadata['chunk_id']}")
                        if 'chunk_length' in metadata:
                            print(f"   📏 Length: {metadata['chunk_length']} chars")
                        
                        # Text preview
                        if 'text' in metadata:
                            text = metadata['text']
                            preview = text[:150] + "..." if len(text) > 150 else text
                            print(f"   📝 Preview: {preview}")
            else:
                print("   No results returned")
                
        except Exception as e:
            print(f"   ⚠️  Could not fetch sample data: {e}")
        
        # Analyze distribution by lesson
        print(f"\n\n📚 Content Distribution by Lesson:")
        print("=" * 80)
        
        # We'll estimate based on vector IDs (lesson_XX_chunk_YY format)
        lesson_distribution = defaultdict(int)
        
        # Since we can't easily scan all vectors, we'll query multiple times
        print("   Analyzing vector distribution...")
        
        # Sample queries to get distribution
        sample_vectors = []
        for _ in range(10):
            try:
                results = index.query(
                    vector=[0.0] * stats.dimension,
                    top_k=100,
                    include_metadata=True
                )
                sample_vectors.extend(results.matches)
            except:
                break
        
        # Count by lesson
        for match in sample_vectors:
            if match.metadata and 'lesson_number' in match.metadata:
                lesson_num = match.metadata['lesson_number']
                lesson_title = match.metadata.get('lesson_title', f'Lesson {lesson_num}')
                lesson_distribution[f"Lesson {lesson_num}: {lesson_title}"] += 1
        
        if lesson_distribution:
            print(f"\n   Sampled {len(sample_vectors)} vectors:")
            for lesson, count in sorted(lesson_distribution.items()):
                bar_length = int((count / max(lesson_distribution.values())) * 40)
                bar = "█" * bar_length
                print(f"   {lesson[:50]:50s} {bar} {count}")
        else:
            print("   Could not determine distribution")
        
        # Storage info
        print(f"\n\n💾 Storage Information:")
        print("=" * 80)
        estimated_size = stats.total_vector_count * stats.dimension * 4 / (1024 * 1024)  # 4 bytes per float
        print(f"   Estimated Vector Storage: {estimated_size:.2f} MB")
        print(f"   Free Tier Limit: 100,000 vectors")
        print(f"   Usage: {(stats.total_vector_count / 100000) * 100:.2f}%")
        
        # RAG Readiness
        print(f"\n\n✅ RAG System Status:")
        print("=" * 80)
        if stats.total_vector_count > 100:
            print("   🟢 READY - Sufficient vectors for RAG")
            print(f"   ✓ {stats.total_vector_count:,} vectors indexed")
            print(f"   ✓ Semantic search enabled")
            print(f"   ✓ Can handle complex queries")
        elif stats.total_vector_count > 0:
            print("   🟡 PARTIAL - Some vectors available")
            print(f"   ⚠️  Only {stats.total_vector_count} vectors")
            print(f"   💡 Upload more content for better results")
        else:
            print("   🔴 NOT READY - No vectors")
            print(f"   ❌ Database is empty")
            print(f"   💡 Run upload script first")
        
        # Next steps
        print(f"\n\n🎯 Next Steps:")
        print("=" * 80)
        print("   1. Test RAG Chat:")
        print("      python scripts\\test_chatbot.py")
        print("")
        print("   2. Interactive Mode:")
        print("      python scripts\\test_chatbot.py interactive")
        print("")
        print("   3. Web UI:")
        print("      http://localhost:8000/docs")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure:")
        print("   1. Backend is running")
        print("   2. PINECONE_API_KEY is set in .env")
        print("   3. PINECONE_HOST is set in .env")


if __name__ == "__main__":
    visualize_pinecone()
