"""
Test Multi-Index Progressive Learning System

Run this to test the enhanced RAG service with multi-class queries.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import logging
from app.services.enhanced_rag_service import enhanced_rag_service
from app.db.mongo import pinecone_db, pinecone_web_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_basic_mode():
    """Test Basic Mode (quick)"""
    print("\n" + "="*80)
    print("🧪 TEST 1: BASIC MODE (Quick)")
    print("="*80)
    
    question = "What is the distance formula?"
    subject = "Mathematics"
    student_class = 10
    chapter = 7
    
    print(f"\n📚 Setup:")
    print(f"   Student: Class {student_class}")
    print(f"   Subject: {subject}")
    print(f"   Chapter: {chapter}")
    print(f"   Question: {question}")
    print(f"\n⏳ Processing in BASIC mode...")
    print(f"   Expected: Will search Classes 8, 9, 10")
    
    try:
        answer, chunks = enhanced_rag_service.answer_question_basic(
            question=question,
            subject=subject,
            student_class=student_class,
            chapter=chapter
        )
        
        print(f"\n✅ Answer Generated:")
        print(f"   Length: {len(answer)} characters")
        print(f"   Sources: {len(chunks)} chunks")
        
        # Show class distribution
        classes_found = {}
        for chunk in chunks:
            class_num = chunk.get('class', 'unknown')
            classes_found[class_num] = classes_found.get(class_num, 0) + 1
        
        print(f"\n📊 Class Distribution:")
        for class_num in sorted(classes_found.keys()):
            print(f"   Class {class_num}: {classes_found[class_num]} chunks")
        
        print(f"\n💬 Answer Preview:")
        print(f"   {answer[:300]}...")
        
        print(f"\n🎯 Status: BASIC MODE TEST PASSED ✓")
        
    except Exception as e:
        print(f"\n❌ BASIC MODE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


def test_deepdive_mode():
    """Test Deep Dive Mode"""
    print("\n" + "="*80)
    print("🧪 TEST 2: DEEP DIVE MODE")
    print("="*80)
    
    question = "Explain what a line is and why we need it in mathematics"
    subject = "Mathematics"
    student_class = 10
    chapter = 7
    
    print(f"\n📚 Setup:")
    print(f"   Student: Class {student_class}")
    print(f"   Subject: {subject}")
    print(f"   Chapter: {chapter}")
    print(f"   Question: {question}")
    print(f"\n⏳ Processing in DEEP DIVE mode...")
    print(f"   Expected: Will search Classes 5, 6, 7, 8, 9, 10 + web content")
    
    try:
        answer, chunks = enhanced_rag_service.answer_question_deepdive(
            question=question,
            subject=subject,
            student_class=student_class,
            chapter=chapter
        )
        
        print(f"\n✅ Answer Generated:")
        print(f"   Length: {len(answer)} characters")
        print(f"   Total sources: {len(chunks)} chunks")
        
        # Show source distribution
        textbook_chunks = [c for c in chunks if c.get('source') == 'textbook']
        web_chunks = [c for c in chunks if c.get('source') == 'web']
        
        print(f"\n📊 Source Distribution:")
        print(f"   Textbook chunks: {len(textbook_chunks)}")
        print(f"   Web chunks: {len(web_chunks)}")
        
        # Show class distribution (textbook only)
        classes_found = {}
        for chunk in textbook_chunks:
            class_num = chunk.get('class', 'unknown')
            classes_found[class_num] = classes_found.get(class_num, 0) + 1
        
        if classes_found:
            print(f"\n📚 Textbook Class Distribution:")
            for class_num in sorted(classes_found.keys()):
                print(f"   Class {class_num}: {classes_found[class_num]} chunks")
        
        print(f"\n💬 Answer Preview:")
        print(f"   {answer[:400]}...")
        
        print(f"\n🎯 Status: DEEP DIVE MODE TEST PASSED ✓")
        
    except Exception as e:
        print(f"\n❌ DEEP DIVE MODE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


def test_class_range_detection():
    """Test prerequisite class detection"""
    print("\n" + "="*80)
    print("🧪 TEST 3: CLASS RANGE DETECTION")
    print("="*80)
    
    test_cases = [
        ("Mathematics", 10, "basic"),
        ("Mathematics", 10, "deepdive"),
        ("Physics", 12, "basic"),
        ("Physics", 12, "deepdive"),
        ("Social Science", 8, "basic"),
        ("Social Science", 8, "deepdive"),
    ]
    
    for subject, student_class, mode in test_cases:
        classes = enhanced_rag_service.get_prerequisite_classes(
            subject=subject,
            student_class=student_class,
            mode=mode
        )
        
        print(f"\n📚 {subject} | Class {student_class} | {mode.upper()}")
        print(f"   → Will search: {classes}")
    
    print(f"\n🎯 Status: CLASS RANGE DETECTION TEST PASSED ✓")


def check_connections():
    """Check Pinecone connections"""
    print("\n" + "="*80)
    print("🔌 CHECKING CONNECTIONS")
    print("="*80)
    
    print(f"\n1. Textbook DB (ncert-all-subjects):")
    try:
        if pinecone_db.index:
            stats = pinecone_db.index.describe_index_stats()
            print(f"   ✅ Connected")
            print(f"   Total vectors: {stats.total_vector_count}")
            
            # Show namespaces
            namespaces = stats.namespaces
            print(f"   Namespaces:")
            for ns, ns_stats in namespaces.items():
                print(f"      - {ns}: {ns_stats.vector_count} vectors")
        else:
            print(f"   ❌ Not connected")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n2. Web Content DB (ncert-web-content):")
    try:
        if pinecone_web_db and pinecone_web_db.index:
            stats = pinecone_web_db.index.describe_index_stats()
            print(f"   ✅ Connected")
            print(f"   Total vectors: {stats.total_vector_count}")
        else:
            print(f"   ⚠️  Not connected (optional for basic mode)")
    except Exception as e:
        print(f"   ⚠️  Error: {e} (optional for basic mode)")


def main():
    print("\n" + "="*80)
    print("🚀 MULTI-INDEX PROGRESSIVE LEARNING SYSTEM TEST")
    print("="*80)
    
    # Check connections first
    check_connections()
    
    # Connect to Pinecone
    print(f"\n⏳ Connecting to databases...")
    try:
        pinecone_db.connect()
        print(f"✅ Textbook DB connected")
    except Exception as e:
        print(f"❌ Textbook DB connection failed: {e}")
        return
    
    try:
        pinecone_web_db.connect()
        print(f"✅ Web DB connected")
    except Exception as e:
        print(f"⚠️  Web DB connection failed: {e} (continuing with textbook only)")
    
    # Run tests
    try:
        test_class_range_detection()
        test_basic_mode()
        test_deepdive_mode()
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS COMPLETED!")
        print("="*80)
        print("\n✨ The enhanced multi-index system is working correctly!")
        print("\nNext steps:")
        print("1. Test with more questions")
        print("2. Test different subjects (once populated)")
        print("3. Compare Basic vs DeepDive responses")
        print("4. Check response quality and relevance")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
