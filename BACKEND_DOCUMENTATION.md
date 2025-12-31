# NCERT AI Learning Platform - Backend Documentation

## Complete A-Z Guide

**Version:** 1.0.0  
**Last Updated:** December 30, 2025  
**Framework:** FastAPI (Python)

---

## Table of Contents

1. Project Overview
2. Technology Stack
3. AI Models Used
4. Database Architecture
5. Embedding System
6. RAG System
7. Chat System
8. PDF Processing
9. API Key Management
10. API Endpoints

---

## 1. Project Overview

The NCERT AI Learning Platform is an intelligent tutoring system that helps students learn from NCERT textbooks using AI.

**Key Features:**
- RAG-based Q&A using actual textbook content
- Multi-class Progressive Learning (access content from earlier classes)
- PDF Processing with OCR and image analysis
- MCQ Generation from textbook content
- Multi-key API rotation (10 keys, 200 requests/day)

---

## 2. Technology Stack

### Core Framework
- **Web Framework:** FastAPI
- **Python:** 3.10+
- **Server:** Uvicorn

### AI & ML
- **LLM:** Google Gemini 2.5 Flash (text generation, chat)
- **Embeddings:** Gemini text-embedding-004 (768 dimensions)
- **Vision:** Gemini 2.5 Flash (image/diagram analysis)

### Databases
- **MongoDB Atlas:** User data, metadata, quota tracking
- **Pinecone:** Vector embeddings storage & retrieval

### PDF Processing
- PyPDF2 (text extraction)
- pdf2image (PDF to image)
- Tesseract OCR (scanned pages)
- OpenCV (image preprocessing)

---

## 3. AI Models Used

### Chat/Generation Model
**Model:** models/gemini-2.5-flash

```python
# From gemini_service.py
self.model_name = 'models/gemini-2.5-flash'
```

**Used For:**
- Generating explanations from RAG context
- Answering student questions
- Creating MCQs
- Image/diagram descriptions

### Embedding Model
**Model:** models/text-embedding-004

```python
# From enhanced_rag_service.py
self.embedding_model_name = 'models/text-embedding-004'
```

**Specifications:**
- Dimensions: 768
- Task Type: retrieval_query / retrieval_document
- Provider: Google Gemini

---

## 4. Database Architecture

### MongoDB Atlas
**Database:** ncert_learning_db

**Collections:**
- users - User accounts
- books - Uploaded book metadata
- book_chapters - Chapter info
- tests - Test configurations
- test_submissions - Student results
- gemini_quota_tracker - API key usage
- support_tickets - User support

### Pinecone Vector Database
**Master Index:** ncert-all-subjects

**Namespaces:**
- chemistry (203 vectors currently)
- physics
- mathematics
- biology
- history
- geography
- english

**Vector Specs:**
- Dimensions: 768
- Metric: Cosine similarity
- Spec: Serverless (AWS us-east-1)

**Metadata Schema:**
```json
{
    "class_level": 11,
    "subject": "Chemistry",
    "chapter_number": 1,
    "page_number": 5,
    "text": "Content...",
    "book_title": "Chemistry Class 11"
}
```

---

## 5. Embedding System

### How Embeddings Work
Text -> Gemini text-embedding-004 -> 768-dim Vector -> Pinecone

### Embedding Code
```python
def generate_embedding(self, text: str) -> List[float]:
    from app.services.gemini_key_manager import gemini_key_manager
    api_key = gemini_key_manager.get_available_key()
    genai.configure(api_key=api_key)
    
    result = genai.embed_content(
        model='models/text-embedding-004',
        content=text,
        task_type="retrieval_query"
    )
    return result['embedding']  # 768-dimensional vector
```

**CRITICAL:** Same embedding model MUST be used for upload AND query!

---

## 6. RAG System (Retrieval-Augmented Generation)

### How It Works
1. Student asks question
2. Question -> Embedding (768-dim vector)
3. Vector similarity search in Pinecone
4. Retrieve relevant textbook chunks
5. Send chunks + question to Gemini
6. Gemini generates answer using chunks
7. Return answer to student

### Two Modes

**Quick Mode (Basic):**
- Searches current class + 2 previous
- Example: Class 10 -> searches Classes 8, 9, 10
- Textbook content only
- Fast, focused answers

**DeepDive Mode:**
- Searches ALL classes from fundamentals
- Example: Class 10 -> searches Classes 5-10
- Includes web content
- Comprehensive understanding

### Query Code
```python
def query_multi_class(self, query_text, subject, student_class, mode="basic"):
    query_embedding = self.generate_embedding(query_text)
    classes_to_search = self.get_prerequisite_classes(subject, student_class, mode)
    
    for class_level in classes_to_search:
        results = self.textbook_db.index.query(
            namespace=namespace,
            vector=query_embedding,
            top_k=5,
            filter={"class_level": class_level, "subject": subject},
            include_metadata=True
        )
    return all_chunks
```

### Similarity Threshold
- Basic mode: 0.3
- DeepDive mode: 0.2 (more inclusive)

---

## 7. Chat System

### Main Endpoint
POST /api/v1/chat/student

**Request:**
```json
{
    "question": "What is matter?",
    "class_level": 11,
    "subject": "Chemistry",
    "chapter": 1,
    "mode": "quick"
}
```

**Response:**
```json
{
    "answer": "Matter is anything that has mass...",
    "used_mode": "quick",
    "source_chunks": ["Chunk 1...", "Chunk 2..."]
}
```

### Chat Modes
- quick - Fast answers from recent classes
- deepdive - Comprehensive from fundamentals
- define - Clear definitions
- elaborate - Detailed explanations
- simple - Simplified for younger students
- example - With examples

### Greeting Detection (Saves API quota)
```python
GREETINGS = {
    "hi": ["hi", "hello", "hey"],
    "bye": ["bye", "goodbye"],
    "thanks": ["thank you", "thanks"]
}
# Returns pre-defined response, no Gemini call
```

---

## 8. PDF Processing

### Processing Pipeline
1. Open PDF (PyPDF2)
2. For each page:
   - Extract text (PyPDF2)
   - Convert to image (pdf2image)
   - Run OCR (Tesseract)
   - Detect & describe images (Gemini Vision)
3. Combine all content
4. Chunk text (800 chars, 150 overlap)
5. Generate embeddings
6. Upload to Pinecone

### Configuration
```python
chunk_size = 800      # Characters per chunk
chunk_overlap = 150   # Overlap for context
dpi = 300             # OCR quality
```

### What Gets Extracted
- Regular text (PyPDF2)
- Scanned pages (Tesseract OCR)
- Diagrams (Gemini Vision descriptions)
- Formulas (pattern detection)
- Chemical equations (pattern detection)

---

## 9. API Key Management

### Multi-Key Rotation
Supports up to 10 Gemini API keys

```python
# Environment variables
GEMINI_API_KEY_1=AIza...
GEMINI_API_KEY_2=AIza...
# ... up to GEMINI_API_KEY_10
```

### Quota
- Each key: 20 requests/day (free tier)
- Total: 10 keys x 20 = 200 requests/day
- Resets at midnight Pacific Time
- Tracked in MongoDB gemini_quota_tracker

### Rotation Logic
1. Check current key quota
2. If exhausted, rotate to next key
3. If all exhausted, return error
4. Track usage in MongoDB

---

## 10. API Endpoints

### Chat
- POST /api/v1/chat/ - Basic RAG chat
- POST /api/v1/chat/student - Student chatbot
- POST /api/v1/chat/stick-flow - Flow diagrams

### Auth
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/profile

### Books
- POST /api/v1/books/upload - Upload PDF
- GET /api/v1/books/ - List books
- DELETE /api/v1/books/{id}

### MCQ & Tests
- POST /api/v1/mcq/generate
- POST /api/v1/evaluate/
- GET /api/v1/tests/

### Admin
- GET /api/v1/admin/stats
- GET /api/v1/admin/users

---

## Services Overview

| Service | Purpose |
|---------|---------|
| enhanced_rag_service | Multi-index RAG |
| gemini_service | Gemini AI calls |
| gemini_key_manager | API key rotation |
| pdf_processor | PDF extraction |
| mcq_service | MCQ generation |
| rag_service | Basic RAG |

---

## Running the Backend

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Start server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use script
.\start_backend.ps1
```

---

## Quick Reference

| Component | Technology |
|-----------|-----------|
| LLM | Gemini 2.5 Flash |
| Embeddings | text-embedding-004 (768-dim) |
| Vector DB | Pinecone |
| Document DB | MongoDB Atlas |
| PDF | PyPDF2 + OCR + Gemini Vision |
| API Keys | 10-key rotation |

---

*Documentation: December 30, 2025*
