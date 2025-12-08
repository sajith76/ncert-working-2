"""
Quick Backend Restart Script
Restarts the backend server with the fixed RAG service
"""

import subprocess
import sys
import os

print("="*70)
print("🔄 RESTARTING BACKEND SERVER")
print("="*70)
print("\n✅ Fixed Issues:")
print("   • Embedding model mismatch resolved")
print("   • RAG now uses sentence-transformers")
print("   • Queries will return proper results\n")

print("📋 Starting server...")
print("   Backend will run on: http://0.0.0.0:8000")
print("   Press Ctrl+C to stop\n")
print("="*70)
print()

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Start uvicorn
try:
    subprocess.run([
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
    ])
except KeyboardInterrupt:
    print("\n\n✅ Server stopped gracefully")
except Exception as e:
    print(f"\n❌ Error: {e}")
