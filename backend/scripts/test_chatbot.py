"""
Test RAG Chatbot - Interactive Testing Script
Tests the chatbot with sample questions and shows responses
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import httpx
import asyncio
from typing import Dict, List
import json


class ChatbotTester:
    """Test the RAG chatbot with sample questions"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_chat(self, question: str, class_num: int = 6, subject: str = "Geography", chapter: int = 1, mode: str = "simple") -> Dict:
        """
        Test the chat endpoint
        
        Args:
            question: Question to ask (highlight_text)
            class_num: Class number (5-10)
            subject: Subject name
            chapter: Chapter number
            mode: Explanation mode (simple, meaning, story, example, summary)
            
        Returns:
            Response from API
        """
        url = f"{self.base_url}/api/chat/"
        
        payload = {
            "class_level": class_num,
            "subject": subject,
            "chapter": chapter,
            "highlight_text": question,
            "mode": mode
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def check_health(self) -> bool:
        """Check if backend is running"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    async def check_pinecone_status(self) -> Dict:
        """Get Pinecone status from backend"""
        try:
            # This would be a custom endpoint, for now we'll simulate
            return {"status": "connected", "note": "Use check_pinecone_status.py script"}
        except:
            return {"status": "error"}
    
    def format_response(self, response: Dict, question: str):
        """Format response for display"""
        print("\n" + "=" * 80)
        print(f"❓ QUESTION: {question}")
        print("=" * 80)
        
        if "error" in response:
            print(f"\n❌ Error: {response['error']}")
            return
        
        if "answer" in response:
            print(f"\n💬 ANSWER ({response.get('used_mode', 'N/A')} mode):")
            print(f"{response['answer']}")
            
            if "source_chunks" in response and response["source_chunks"]:
                print(f"\n📚 SOURCE CHUNKS ({len(response['source_chunks'])} chunks used):")
                for i, chunk in enumerate(response["source_chunks"][:3], 1):  # Show first 3
                    preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
                    print(f"  {i}. {preview}")
            
            if "metadata" in response:
                print(f"\n📊 METADATA:")
                for key, value in response["metadata"].items():
                    print(f"  • {key}: {value}")
        else:
            print(f"\n📄 Raw Response:")
            print(json.dumps(response, indent=2))
    
    async def run_tests(self):
        """Run a suite of test questions"""
        
        print("=" * 80)
        print("  🤖 RAG CHATBOT TESTING SUITE")
        print("=" * 80)
        
        # Check backend health
        print("\n1️⃣  Checking backend status...")
        is_healthy = await self.check_health()
        if is_healthy:
            print("   ✅ Backend is running")
        else:
            print("   ❌ Backend is not running!")
            print("   💡 Start backend: uvicorn app.main:app --reload")
            return
        
        # Test questions
        test_questions = [
            {
                "question": "What are the main lines of latitude?",
                "description": "Simple factual question about latitude",
                "class_level": 6,
                "subject": "Social Science",  # Changed from Geography
                "chapter": 1,
                "mode": "simple"
            },
            {
                "question": "Explain the importance of the Equator",
                "description": "Conceptual explanation about Equator",
                "class_level": 6,
                "subject": "Social Science",
                "chapter": 1,
                "mode": "meaning"
            },
            {
                "question": "How do latitude and longitude work together?",
                "description": "Complex multi-concept question",
                "class_level": 6,
                "subject": "Social Science",
                "chapter": 1,
                "mode": "example"
            },
            {
                "question": "What is economic activity?",
                "description": "Economics question",
                "class_level": 6,
                "subject": "Social Science",
                "chapter": 14,
                "mode": "simple"
            },
            {
                "question": "Tell me about democracy",
                "description": "Civics/Government question",
                "class_level": 6,
                "subject": "Social Science",
                "chapter": 10,
                "mode": "story"
            }
        ]
        
        print(f"\n2️⃣  Running {len(test_questions)} test questions...")
        print("=" * 80)
        
        for i, test in enumerate(test_questions, 1):
            print(f"\n\n🧪 TEST {i}/{len(test_questions)}: {test['description']}")
            
            response = await self.test_chat(
                question=test["question"],
                class_num=test.get("class_level", 6),
                subject=test.get("subject", "Geography"),
                chapter=test.get("chapter", 1),
                mode=test.get("mode", "simple")
            )
            
            self.format_response(response, test["question"])
            
            # Wait a bit between requests
            await asyncio.sleep(2)
        
        print("\n\n" + "=" * 80)
        print("  ✅ TESTING COMPLETE")
        print("=" * 80)
        
        # Summary
        print("\n📊 Test Summary:")
        print(f"  • Total tests: {len(test_questions)}")
        print(f"  • Backend: {'✅ Running' if is_healthy else '❌ Down'}")
        print("\n💡 Next Steps:")
        print("  1. Review answers for accuracy")
        print("  2. Check if sources are relevant")
        print("  3. Test with your own questions at: http://localhost:8000/docs")
        print("=" * 80)
    
    async def interactive_mode(self):
        """Interactive question-answer mode"""
        
        print("\n" + "=" * 80)
        print("  🤖 INTERACTIVE CHATBOT MODE")
        print("=" * 80)
        print("\n💡 Tips:")
        print("  • Type your question and press Enter")
        print("  • Type 'quit' or 'exit' to stop")
        print("  • Type 'help' for sample questions")
        print("=" * 80 + "\n")
        
        # Check backend
        is_healthy = await self.check_health()
        if not is_healthy:
            print("❌ Backend is not running!")
            print("💡 Start backend: uvicorn app.main:app --reload")
            return
        
        sample_questions = [
            "What are the main lines of latitude?",
            "Explain the importance of the Equator",
            "What is democracy?",
            "How do latitude and longitude work together?",
            "What does the 'Think about it' section say?"
        ]
        
        while True:
            try:
                question = input("\n❓ Your question: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if question.lower() in ['help', 'h']:
                    print("\n📝 Sample Questions:")
                    for i, q in enumerate(sample_questions, 1):
                        print(f"  {i}. {q}")
                    continue
                
                print("\n⏳ Thinking...")
                response = await self.test_chat(question)
                self.format_response(response, question)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


async def main():
    """Main function"""
    tester = ChatbotTester()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        await tester.interactive_mode()
    else:
        await tester.run_tests()
    
    await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
