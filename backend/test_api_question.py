"""Test the API with the user's question"""
import requests
import json

# API endpoint
url = "http://localhost:8000/api/v1/chat/progressive"

# User's question
payload = {
    "message": "What is the number of children who always slept at least 9 hours at night?",
    "student_class": 6,
    "subject": "Mathematics",
    "chapter": 4,
    "mode": "basic"
}

print(f"🔍 Testing Question: {payload['message']}\n")
print(f"📚 Context: Class {payload['student_class']}, Subject: {payload['subject']}, Chapter: {payload['chapter']}")
print(f"🎯 Mode: {payload['mode']}\n")

print("📡 Sending request to API...")

try:
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Status: SUCCESS\n")
        print(f"📊 Sources Found: {result.get('sources_count', 0)}")
        print(f"📚 Classes Searched: {result.get('classes_searched', [])}\n")
        print(f"💬 AI Response:\n")
        print("="*60)
        print(result.get('response', 'No response'))
        print("="*60)
        print(f"\n📖 Sources Used:")
        for i, source in enumerate(result.get('sources', [])[:5], 1):
            print(f"\n  {i}. Class {source['class']}, Chapter {source['chapter']}, Page {source['page']}")
            print(f"     Score: {source['score']:.4f}")
            print(f"     {source['text'][:200]}...")
    else:
        print(f"\n❌ Error: Status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
