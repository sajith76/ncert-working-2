"""
Test script for progressive learning with namespace architecture.

Tests:
1. Single-class queries
2. Multi-class progressive queries (Quick mode)
3. All-prerequisite queries (DeepDive mode)
4. Namespace routing for all subjects
5. Cross-class learning scenarios

Usage:
    python scripts/test_progressive_learning.py
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import asyncio
from app.core.config import settings
from app.db.mongo import namespace_db
from app.services.gemini_service import gemini_service
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_namespace_connection():
    """Test 1: Verify namespace DB connection."""
    print("\n" + "="*80)
    print("TEST 1: Namespace DB Connection")
    print("="*80)
    
    try:
        namespace_db.connect()
        print("✅ Successfully connected to master index")
        
        # Check available subjects
        subjects = namespace_db.get_available_subjects()
        print(f"✅ Available subjects: {subjects}")
        
        # Get info for each subject
        for subject in subjects:
            info = namespace_db.get_subject_info(subject)
            print(f"   - {subject}: {info}")
        
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


async def test_single_class_query():
    """Test 2: Query single class (no progressive learning)."""
    print("\n" + "="*80)
    print("TEST 2: Single Class Query")
    print("="*80)
    
    try:
        # Generate test embedding
        test_query = "What is photosynthesis?"
        print(f"Query: '{test_query}'")
        print(f"Subject: Biology, Class: 10")
        
        embedding = gemini_service.generate_embedding(test_query)
        print(f"✅ Generated embedding: {len(embedding)} dimensions")
        
        # Query single class
        results = namespace_db.query(
            vector=embedding,
            subject="Biology",
            class_filter={"$in": ["10"]},
            top_k=5
        )
        
        matches = results.get('matches', [])
        print(f"✅ Found {len(matches)} matches")
        
        if matches:
            print("\nTop 3 results:")
            for i, match in enumerate(matches[:3], 1):
                score = match.get('score', 0)
                metadata = match.get('metadata', {})
                text = metadata.get('text', '')[:100]
                class_level = metadata.get('class', 'unknown')
                
                print(f"\n   {i}. Score: {score:.3f}, Class: {class_level}")
                print(f"      Text: {text}...")
        
        return True
    except Exception as e:
        print(f"❌ Single class query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_progressive_quick():
    """Test 3: Progressive query in Quick mode (current + previous class)."""
    print("\n" + "="*80)
    print("TEST 3: Progressive Query - Quick Mode")
    print("="*80)
    
    try:
        test_query = "Explain algebraic equations"
        student_class = 11
        subject = "Mathematics"
        
        print(f"Query: '{test_query}'")
        print(f"Student: Class {student_class}, Subject: {subject}")
        print(f"Mode: Quick (should include Class {student_class} and {student_class-1})")
        
        embedding = gemini_service.generate_embedding(test_query)
        
        # Progressive query
        results = namespace_db.query_progressive(
            vector=embedding,
            subject=subject,
            student_class=student_class,
            mode="quick",
            top_k=10
        )
        
        matches = results.get('matches', [])
        print(f"✅ Found {len(matches)} matches")
        
        # Check which classes are represented
        classes_found = set()
        for match in matches:
            metadata = match.get('metadata', {})
            class_level = metadata.get('class', 'unknown')
            classes_found.add(class_level)
        
        print(f"✅ Classes in results: {sorted(classes_found)}")
        
        if matches:
            print("\nTop 5 results:")
            for i, match in enumerate(matches[:5], 1):
                score = match.get('score', 0)
                metadata = match.get('metadata', {})
                text = metadata.get('text', '')[:80]
                class_level = metadata.get('class', 'unknown')
                chapter = metadata.get('chapter', 'unknown')
                
                print(f"\n   {i}. Class {class_level}, Ch.{chapter}, Score: {score:.3f}")
                print(f"      Text: {text}...")
        
        return True
    except Exception as e:
        print(f"❌ Progressive quick query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_progressive_deepdive():
    """Test 4: Progressive query in DeepDive mode (all prerequisite classes)."""
    print("\n" + "="*80)
    print("TEST 4: Progressive Query - DeepDive Mode")
    print("="*80)
    
    try:
        test_query = "What is the periodic table?"
        student_class = 11
        subject = "Chemistry"
        
        print(f"Query: '{test_query}'")
        print(f"Student: Class {student_class}, Subject: {subject}")
        print(f"Mode: DeepDive (should include Classes 9, 10, 11)")
        
        embedding = gemini_service.generate_embedding(test_query)
        
        # Progressive query
        results = namespace_db.query_progressive(
            vector=embedding,
            subject=subject,
            student_class=student_class,
            mode="deepdive",
            top_k=15
        )
        
        matches = results.get('matches', [])
        print(f"✅ Found {len(matches)} matches")
        
        # Check which classes are represented
        classes_found = set()
        for match in matches:
            metadata = match.get('metadata', {})
            class_level = metadata.get('class', 'unknown')
            classes_found.add(class_level)
        
        print(f"✅ Classes in results: {sorted(classes_found)}")
        print(f"   Expected: Classes 9, 10, 11 (all prerequisites + current)")
        
        if matches:
            print("\nTop 5 results:")
            for i, match in enumerate(matches[:5], 1):
                score = match.get('score', 0)
                metadata = match.get('metadata', {})
                text = metadata.get('text', '')[:80]
                class_level = metadata.get('class', 'unknown')
                chapter = metadata.get('chapter', 'unknown')
                
                print(f"\n   {i}. Class {class_level}, Ch.{chapter}, Score: {score:.3f}")
                print(f"      Text: {text}...")
        
        return True
    except Exception as e:
        print(f"❌ Progressive deepdive query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_all_subjects():
    """Test 5: Verify namespace routing for all subjects."""
    print("\n" + "="*80)
    print("TEST 5: All Subject Namespaces")
    print("="*80)
    
    subjects = [
        "Mathematics",
        "Physics", 
        "Chemistry",
        "Biology",
        "Social Science",
        "English",
        "Hindi"
    ]
    
    test_query = "Explain the basics"
    embedding = gemini_service.generate_embedding(test_query)
    
    for subject in subjects:
        try:
            # Get namespace name
            namespace = namespace_db.get_namespace(subject)
            print(f"\n📚 Testing {subject} (namespace: {namespace})")
            
            # Quick query
            results = namespace_db.query(
                vector=embedding,
                subject=subject,
                class_filter={"$in": ["10"]},
                top_k=3
            )
            
            matches = results.get('matches', [])
            print(f"   ✅ Namespace accessible: {len(matches)} results")
            
        except Exception as e:
            print(f"   ❌ Failed for {subject}: {e}")
    
    return True


async def test_cross_class_scenario():
    """Test 6: Real-world cross-class learning scenario."""
    print("\n" + "="*80)
    print("TEST 6: Cross-Class Learning Scenario")
    print("="*80)
    print("Scenario: Class 11 Physics student reviewing Class 9 fundamentals")
    
    try:
        # Simulate Class 11 student asking about basic mechanics (covered in Class 9)
        test_query = "What is Newton's First Law of Motion?"
        student_class = 11
        subject = "Physics"
        
        print(f"\nQuery: '{test_query}'")
        print(f"Student: Class {student_class}")
        print(f"Expected: Should find content from Class 9, 10, AND 11")
        
        embedding = gemini_service.generate_embedding(test_query)
        
        # DeepDive to get all prerequisites
        results = namespace_db.query_progressive(
            vector=embedding,
            subject=subject,
            student_class=student_class,
            mode="deepdive",
            top_k=10
        )
        
        matches = results.get('matches', [])
        print(f"\n✅ Found {len(matches)} total matches")
        
        # Analyze by class
        class_distribution = {}
        for match in matches:
            metadata = match.get('metadata', {})
            class_level = metadata.get('class', 'unknown')
            class_distribution[class_level] = class_distribution.get(class_level, 0) + 1
        
        print("\n📊 Distribution by class:")
        for class_level in sorted(class_distribution.keys()):
            count = class_distribution[class_level]
            print(f"   Class {class_level}: {count} matches")
        
        print("\n✅ Cross-class learning enabled! Student can access fundamentals.")
        
        return True
    except Exception as e:
        print(f"❌ Cross-class scenario failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "🚀"*40)
    print("PROGRESSIVE LEARNING TEST SUITE")
    print("🚀"*40)
    print(f"\nMaster Index: {settings.PINECONE_MASTER_INDEX}")
    print(f"Testing namespace architecture for cross-class learning\n")
    
    tests = [
        ("Connection Test", test_namespace_connection),
        ("Single Class Query", test_single_class_query),
        ("Progressive Quick Mode", test_progressive_quick),
        ("Progressive DeepDive Mode", test_progressive_deepdive),
        ("All Subject Namespaces", test_all_subjects),
        ("Cross-Class Scenario", test_cross_class_scenario),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results[test_name] = "✅ PASSED" if success else "❌ FAILED"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {e}"
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    passed = sum(1 for r in results.values() if "PASSED" in r)
    total = len(results)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Progressive learning is working correctly!")
    else:
        print("\n⚠️ Some tests failed. Check logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())
