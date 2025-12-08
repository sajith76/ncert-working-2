"""Test the user's sleeping hours question"""
from app.services.enhanced_rag_service import EnhancedRAGService
from app.db.mongo import pinecone_db

def test_question():
    # Initialize Pinecone connection
    print("🔌 Connecting to Pinecone...")
    pinecone_db.connect()
    
    rag = EnhancedRAGService()
    
    question = "What is the number of children who always slept at least 9 hours at night?"
    
    print(f"\n🔍 Testing Question: {question}\n")
    
    chunks, class_distribution = rag.query_multi_class(
        query_text=question,
        subject="Mathematics",
        student_class=6,
        chapter=4,
        mode="basic"
    )
    
    print(f"✅ Found {len(chunks)} relevant chunks\n")
    print(f"📚 Class distribution: {class_distribution}\n")
    
    # Show top 3 results
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"--- Result {i} ---")
        print(f"Class: {chunk['metadata']['class']}, Chapter: {chunk['metadata']['chapter']}")
        print(f"Score: {chunk['score']:.4f}")
        print(f"Content: {chunk['text'][:400]}...")
        print()

if __name__ == "__main__":
    test_question()
