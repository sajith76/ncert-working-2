"""
Interactive NCERT Math Search System

This script allows users to:
1. Enter their name, age, and class
2. Select a subject (currently Mathematics only)
3. Search with natural language queries
4. Get results with similarity scores
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.multimodal.math.math_embedder import MultimodalEmbedder
from app.services.multimodal.math.math_uploader import PineconeUploader
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class InteractiveSearchSystem:
    """Interactive search system for NCERT content"""
    
    def __init__(self):
        """Initialize the search system"""
        print("\n" + "="*60)
        print("🎓 NCERT INTERACTIVE SEARCH SYSTEM")
        print("="*60)
        print("\n⏳ Initializing AI models...")
        
        # Get Pinecone credentials from environment
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME", "ncert-all-subjects")
        
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        # Initialize embedder and uploader
        self.embedder = MultimodalEmbedder()
        self.uploader = PineconeUploader(api_key=api_key, index_name=index_name)
        
        print("✅ System ready!\n")
    
    def get_user_info(self):
        """Get user information"""
        print("=" * 60)
        print("📋 USER INFORMATION")
        print("=" * 60)
        
        name = input("\n👤 Enter your name: ").strip()
        
        while True:
            try:
                age = int(input("🎂 Enter your age: ").strip())
                if age < 5 or age > 100:
                    print("   ⚠️  Please enter a valid age (5-100)")
                    continue
                break
            except ValueError:
                print("   ⚠️  Please enter a valid number")
        
        while True:
            try:
                class_num = int(input("📚 Enter your class (5-12): ").strip())
                if class_num < 5 or class_num > 12:
                    print("   ⚠️  Please enter a class between 5 and 12")
                    continue
                break
            except ValueError:
                print("   ⚠️  Please enter a valid number")
        
        return {
            "name": name,
            "age": age,
            "class": class_num
        }
    
    def select_subject(self, user_info):
        """Select a subject from available options"""
        print("\n" + "=" * 60)
        print("📖 AVAILABLE SUBJECTS")
        print("=" * 60)
        
        # For now, only Mathematics is available
        subjects = {
            "1": {"name": "Mathematics", "namespace": "mathematics"}
        }
        
        print("\n1. Mathematics ✓ (Available)")
        print("\n   Note: More subjects coming soon!")
        
        while True:
            choice = input("\n🔢 Select subject (enter number): ").strip()
            if choice in subjects:
                return subjects[choice]
            else:
                print("   ⚠️  Invalid choice. Please enter 1 for Mathematics")
    
    def search(self, query: str, subject: dict, user_class: int, top_k: int = 5):
        """
        Search for content based on query
        
        Args:
            query: Search query
            subject: Subject dictionary with namespace
            user_class: User's class number
            top_k: Number of results to return
        
        Returns:
            Search results
        """
        print(f"\n🔍 Searching for: '{query}'")
        print("⏳ Generating query embedding...")
        
        # Generate query embedding (text only)
        query_embedding = self.embedder.text_model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        print("🔍 Querying database...")
        
        # Query Pinecone with class filter
        results = self.uploader.query_namespace(
            query_vector=query_embedding,
            namespace=subject["namespace"],
            top_k=top_k,
            filter_dict={"class": str(user_class)}  # Filter by user's class
        )
        
        return results
    
    def display_results(self, results: dict):
        """Display search results in a user-friendly format"""
        matches = results.get('matches', [])
        
        if not matches:
            print("\n❌ No results found. Try a different query.")
            return
        
        print("\n" + "=" * 60)
        print(f"📊 SEARCH RESULTS ({len(matches)} found)")
        print("=" * 60)
        
        for i, match in enumerate(matches, 1):
            score = match.get('score', 0)
            similarity_percent = score * 100  # Score is 0-1, convert to percentage
            metadata = match.get('metadata', {})
            
            print(f"\n┌─ Result {i} " + "─" * 48)
            print(f"│ 🎯 Similarity: {similarity_percent:.2f}%")
            print(f"│ 📚 Class: {metadata.get('class', 'N/A')}")
            print(f"│ 📖 Chapter: {metadata.get('chapter', 'N/A')}")
            print(f"│ 📄 Page: {metadata.get('page', 'N/A')}")
            print(f"│ 📝 Type: {metadata.get('content_type', 'N/A')}")
            
            # Show if it has formula or image
            has_formula = metadata.get('has_formula', 'false')
            has_image = metadata.get('has_image', 'false')
            
            if has_formula == 'true':
                print(f"│ 🧮 Contains Formula: Yes")
                if 'formula' in metadata:
                    formula = metadata['formula'][:100]
                    print(f"│    Formula: {formula}...")
            
            if has_image == 'true':
                print(f"│ 🖼️  Contains Image: Yes")
            
            # Show text content
            text = metadata.get('text', '')
            if text:
                # Truncate long text
                display_text = text[:200] + "..." if len(text) > 200 else text
                print(f"│")
                print(f"│ 📄 Content:")
                for line in display_text.split('\n'):
                    if line.strip():
                        print(f"│    {line[:70]}")
            
            print(f"└" + "─" * 59)
    
    def run(self):
        """Run the interactive search system"""
        # Get user information
        user_info = self.get_user_info()
        
        print(f"\n✅ Welcome, {user_info['name']}!")
        print(f"   Age: {user_info['age']}, Class: {user_info['class']}")
        
        # Select subject
        subject = self.select_subject(user_info)
        print(f"\n✅ Selected: {subject['name']}")
        
        # Search loop
        print("\n" + "=" * 60)
        print("🔍 SEARCH")
        print("=" * 60)
        print("\nTips:")
        print("  • Ask questions in natural language")
        print("  • Example: 'What is Pythagoras theorem?'")
        print("  • Example: 'Solve quadratic equations'")
        print("  • Type 'exit' or 'quit' to stop")
        print("=" * 60)
        
        while True:
            # Get query
            print("\n")
            query = input("💬 Enter your question: ").strip()
            
            if not query:
                print("   ⚠️  Please enter a question")
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print(f"\n👋 Goodbye, {user_info['name']}! Happy learning!")
                break
            
            # Get number of results (optional)
            try:
                num_results_input = input("📊 How many results? (default: 5): ").strip()
                num_results = int(num_results_input) if num_results_input else 5
                num_results = max(1, min(num_results, 20))  # Limit between 1-20
            except ValueError:
                num_results = 5
            
            # Search
            try:
                results = self.search(
                    query=query,
                    subject=subject,
                    user_class=user_info['class'],
                    top_k=num_results
                )
                
                # Display results
                self.display_results(results)
                
                # Ask if user wants to continue
                print("\n" + "-" * 60)
                continue_search = input("\n🔄 Search again? (y/n): ").strip().lower()
                if continue_search not in ['y', 'yes', '']:
                    print(f"\n👋 Goodbye, {user_info['name']}! Happy learning!")
                    break
                
            except Exception as e:
                logger.error(f"❌ Search error: {e}")
                print(f"\n❌ An error occurred: {e}")
                print("Please try again with a different query.")


def main():
    """Main entry point"""
    try:
        system = InteractiveSearchSystem()
        system.run()
    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted. Goodbye!")
    except Exception as e:
        logger.error(f"❌ System error: {e}", exc_info=True)
        print(f"\n❌ System error: {e}")


if __name__ == "__main__":
    main()
