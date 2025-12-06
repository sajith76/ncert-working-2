"""
Interactive Search for NCERT Physics

Search physics content using natural language queries.
"""

import sys
from pathlib import Path
import logging

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.multimodal.physics.physics_embedder import PhysicsEmbedder
from app.services.multimodal.physics.physics_retrieval import PhysicsRetrieval

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)


class InteractivePhysicsSearch:
    """Interactive search interface for physics"""
    
    def __init__(self):
        """Initialize search system"""
        print("\n" + "="*80)
        print("🔬 NCERT PHYSICS INTERACTIVE SEARCH")
        print("="*80)
        print("\nInitializing search system...")
        
        self.embedder = PhysicsEmbedder()
        self.retrieval = PhysicsRetrieval(self.embedder)
        
        print("✅ Search system ready!\n")
    
    def get_user_info(self):
        """Get user information"""
        print("=" * 80)
        print("👤 USER INFORMATION")
        print("=" * 80)
        
        name = input("\n📝 Enter your name: ").strip()
        
        while True:
            age_str = input("🎂 Enter your age: ").strip()
            try:
                age = int(age_str)
                if age > 0:
                    break
                else:
                    print("   ⚠️  Age must be positive")
            except ValueError:
                print("   ⚠️  Please enter a valid number")
        
        while True:
            class_str = input("🎓 Enter your class (11 or 12): ").strip()
            try:
                class_num = int(class_str)
                if class_num in [11, 12]:
                    break
                else:
                    print("   ⚠️  Please enter 11 or 12")
            except ValueError:
                print("   ⚠️  Please enter 11 or 12")
        
        print(f"\n👋 Hello {name}! Welcome to NCERT Physics search (Class {class_num})")
        
        return {
            'name': name,
            'age': age,
            'class': class_num
        }
    
    def display_result(self, result: dict, rank: int):
        """Display single search result"""
        print(f"\n{'─'*80}")
        print(f"📌 Result #{rank}")
        print(f"{'─'*80}")
        
        print(f"🎯 Score: {result['score']:.4f}")
        print(f"📂 Type: {result['content_type']}")
        print(f"📚 Class {result['class']}, Chapter {result['chapter']}, Page {result['page']}")
        
        # Content type specific display
        if result['content_type'] == 'formula' and result.get('latex_formula'):
            print(f"\n📐 Formula:")
            print(f"   {result['latex_formula']}")
            print(f"\n📝 Context:")
            print(f"   {result['raw_text'][:300]}...")
        
        elif result['content_type'] == 'diagram' and result.get('diagram_path'):
            print(f"\n🖼️  Diagram: {result['diagram_path']}")
            print(f"\n📝 Description:")
            print(f"   {result['raw_text'][:300]}...")
        
        elif result['content_type'] == 'table' and result.get('table_data'):
            print(f"\n📊 Table:")
            print(f"   {result['table_data'][:200]}...")
            print(f"\n📝 Context:")
            print(f"   {result['raw_text'][:200]}...")
        
        elif result['content_type'] == 'experiment':
            print(f"\n🔬 Experiment:")
            print(f"   {result['raw_text'][:400]}...")
        
        elif result['content_type'] == 'numerical_question':
            print(f"\n🔢 Numerical Problem:")
            print(f"   {result['raw_text'][:400]}...")
        
        elif result['content_type'] == 'solution_step':
            print(f"\n✅ Solution Step {result.get('step_number', '?')}:")
            print(f"   {result['raw_text'][:400]}...")
        
        else:
            # Concept, law, derivation, example
            print(f"\n📝 Content:")
            print(f"   {result['raw_text'][:400]}...")
        
        # Show formula/image/table indicators
        indicators = []
        if result['has_formula']:
            indicators.append("📐 Has Formula")
        if result['has_image']:
            indicators.append("🖼️  Has Diagram")
        if result['has_table']:
            indicators.append("📊 Has Table")
        
        if indicators:
            print(f"\n🏷️  Features: {' | '.join(indicators)}")
    
    def search_loop(self, user_info: dict):
        """Main search loop"""
        print("\n" + "="*80)
        print("🔍 SEARCH")
        print("="*80)
        print("\nEnter physics queries to search NCERT content")
        print("Commands: 'quit' to exit, 'info' to change user info\n")
        
        while True:
            query = input("\n🔎 Query: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if query.lower() == 'info':
                user_info = self.get_user_info()
                continue
            
            # Search
            print(f"\n⏳ Searching for: '{query}'...")
            
            try:
                results = self.retrieval.search(
                    query=query,
                    class_num=user_info['class'],
                    top_k=5
                )
                
                if not results:
                    print("\n❌ No results found")
                    continue
                
                print(f"\n✅ Found {len(results)} results:")
                
                for i, result in enumerate(results, 1):
                    self.display_result(result, i)
                
                print("\n" + "─"*80)
                
            except Exception as e:
                print(f"\n❌ Search failed: {e}")
    
    def run(self):
        """Run interactive search"""
        user_info = self.get_user_info()
        self.search_loop(user_info)


def main():
    try:
        search = InteractivePhysicsSearch()
        search.run()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
