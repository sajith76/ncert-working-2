"""
Verify Pinecone data completeness for Class 5-12 Mathematics
Checks vector counts per class and chapter to answer:
"Are embeddings of the maths subject from class 5 to 12 perfect in pinecone?"
"""

from pinecone import Pinecone
import os
from dotenv import load_dotenv
from collections import defaultdict

# Load environment
load_dotenv()

def verify_maths_data():
    """Check all Class 5-12 Math data in Pinecone"""
    
    # Initialize Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("ncert-all-subjects")
    
    print("=" * 80)
    print("📊 PINECONE MATHEMATICS DATA VERIFICATION (Class 5-12)")
    print("=" * 80)
    print()
    
    # Get index stats
    stats = index.describe_index_stats()
    total_vectors = stats.get('namespaces', {}).get('mathematics', {}).get('vector_count', 0)
    
    print(f"📦 Total Mathematics Namespace Vectors: {total_vectors:,}")
    print()
    print("=" * 80)
    
    # Check each class
    class_data = {}
    
    for class_num in range(5, 13):  # Class 5 to 12
        print(f"\n📚 CLASS {class_num}")
        print("-" * 80)
        
        # Query with filter for this class
        try:
            # Dummy query vector (not used for stats, just to trigger filter)
            dummy_vector = [0.1] * 768
            
            results = index.query(
                namespace="mathematics",
                vector=dummy_vector,
                filter={
                    "class": {"$eq": str(class_num)}  # Pinecone stores as string
                },
                top_k=10000,  # Get as many as possible
                include_metadata=True
            )
            
            # Count vectors per chapter
            chapter_counts = defaultdict(int)
            for match in results.get('matches', []):
                metadata = match.get('metadata', {})
                chapter = metadata.get('chapter', 'unknown')
                chapter_counts[chapter] += 1
            
            total_class_vectors = sum(chapter_counts.values())
            class_data[class_num] = {
                'total': total_class_vectors,
                'chapters': dict(chapter_counts)
            }
            
            if total_class_vectors > 0:
                print(f"   ✅ Total Vectors: {total_class_vectors:,}")
                print(f"   📖 Chapters Found: {len(chapter_counts)}")
                
                # Show chapter breakdown
                if chapter_counts:
                    print(f"   📑 Chapter Distribution:")
                    for chapter in sorted(chapter_counts.keys(), key=lambda x: int(x) if str(x).isdigit() else 999):
                        count = chapter_counts[chapter]
                        print(f"      • Chapter {chapter}: {count:,} vectors")
            else:
                print(f"   ❌ No data found for Class {class_num}")
                
        except Exception as e:
            print(f"   ⚠️  Error querying Class {class_num}: {e}")
            class_data[class_num] = {'total': 0, 'chapters': {}}
    
    # Summary
    print()
    print("=" * 80)
    print("📊 SUMMARY REPORT")
    print("=" * 80)
    print()
    
    total_found = sum(d['total'] for d in class_data.values())
    classes_with_data = [c for c, d in class_data.items() if d['total'] > 0]
    classes_without_data = [c for c, d in class_data.items() if d['total'] == 0]
    
    print(f"✅ Classes with Data: {len(classes_with_data)}/8")
    if classes_with_data:
        print(f"   • {', '.join(f'Class {c}' for c in classes_with_data)}")
    print()
    
    if classes_without_data:
        print(f"❌ Classes without Data: {len(classes_without_data)}/8")
        print(f"   • {', '.join(f'Class {c}' for c in classes_without_data)}")
        print()
    
    print(f"📦 Total Verified Vectors: {total_found:,} (Query Result)")
    print(f"📦 Total Namespace Vectors: {total_vectors:,} (Index Stats)")
    print()
    
    # Coverage analysis
    print("=" * 80)
    print("🎯 COVERAGE ANALYSIS")
    print("=" * 80)
    print()
    
    if len(classes_with_data) == 8:
        print("✅ EXCELLENT: All classes (5-12) have data!")
    elif len(classes_with_data) >= 6:
        print("⚠️  PARTIAL: Most classes have data, but some are missing")
    elif len(classes_with_data) >= 4:
        print("⚠️  LIMITED: About half the classes have data")
    else:
        print("❌ POOR: Very limited class coverage")
    
    print()
    
    # Data quality check
    avg_vectors_per_class = total_found / len(classes_with_data) if classes_with_data else 0
    
    print(f"📊 Average Vectors per Class (with data): {avg_vectors_per_class:,.0f}")
    print()
    
    if avg_vectors_per_class > 5000:
        print("✅ GOOD: High vector density suggests complete chapter coverage")
    elif avg_vectors_per_class > 1000:
        print("⚠️  MODERATE: Partial coverage - some chapters may be incomplete")
    else:
        print("❌ LOW: Limited coverage - likely missing many chapters")
    
    print()
    print("=" * 80)
    print("💡 RECOMMENDATION")
    print("=" * 80)
    print()
    
    if len(classes_without_data) == 0 and avg_vectors_per_class > 5000:
        print("✅ DATA IS PERFECT!")
        print("   All classes (5-12) have comprehensive data.")
        print("   You can use any content from these classes confidently.")
    elif len(classes_without_data) > 0:
        print("⚠️  DATA IS PARTIALLY COMPLETE")
        print(f"   Missing: {', '.join(f'Class {c}' for c in classes_without_data)}")
        print("   Available classes can be used, but missing classes need processing.")
        print()
        print("   To add missing data, run:")
        for c in classes_without_data:
            print(f"   python scripts/process_ncert_maths.py --class {c}")
    else:
        print("⚠️  DATA EXISTS BUT MAY BE INCOMPLETE")
        print("   All classes have some data, but coverage may be partial.")
        print("   Consider reprocessing classes with low vector counts.")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    verify_maths_data()
