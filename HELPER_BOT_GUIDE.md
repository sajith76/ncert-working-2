# Helper Bot (Student Chatbot) - Quick & DeepDive Modes

## Overview

The Helper Bot is a floating chatbot that appears on the PDF reader page. It has two modes:

1. **Quick Mode** 🚀 - Exam-style direct answers from textbook only
2. **DeepDive Mode** 🧠 - Comprehensive explanations with web-scraped content

## Quick Mode

### Purpose
Provide direct, concise answers from the textbook - perfect for exam preparation.

### Features
- ✅ Direct answers (2-3 sentences max)
- ✅ High relevance threshold (0.70 similarity score)
- ✅ Only textbook content
- ✅ If not found in book, provides helpful redirect to related chapter topics
- ✅ No extra explanations or context

### Use Cases
- Quick fact checking before exams
- Getting straight answers to specific questions
- Verifying understanding of concepts

### Example
**Question:** "What is photosynthesis?"
**Quick Mode Answer:** "Photosynthesis is the process by which green plants make their own food using sunlight, water, and carbon dioxide. This process produces oxygen as a byproduct."

## DeepDive Mode

### Purpose
Provide comprehensive, detailed explanations covering all aspects of a topic.

### Features
- ✅ Comprehensive answers covering "Wh-questions" (What, Why, When, Where, Who, How)
- ✅ Uses both textbook AND web-scraped content
- ✅ Structured with headers and bullet points
- ✅ Includes background context and related information
- ✅ Perfect for deep understanding

### Use Cases
- Understanding complex topics thoroughly
- Preparing presentations or projects
- Learning beyond the textbook
- Understanding historical/scientific context

### Example
**Question:** "Explain World War 2"
**DeepDive Mode Answer:** (Comprehensive multi-paragraph response covering causes, timeline, key events, outcomes, significance, etc.)

## Technical Implementation

### Frontend (StudentChatbot.jsx)

```jsx
// Mode state
const [chatMode, setChatMode] = useState("quick"); // "quick" or "deepdive"

// Mode selector UI
<button onClick={() => handleModeChange("quick")}>
  <Zap className="w-4 h-4" />
  Quick
</button>
<button onClick={() => handleModeChange("deepdive")}>
  <Brain className="w-4 h-4" />
  DeepDive
</button>

// API call with mode
const result = await chatService.studentChat(
  userMessage.content,
  user.classLevel,
  user.preferredSubject,
  currentLesson?.number,
  chatMode // Pass mode to backend
);
```

### Backend (chat.py)

```python
class StudentChatRequest(BaseModel):
    question: str
    class_level: int
    subject: str
    chapter: int
    mode: Literal["quick", "deepdive"] = "quick"

@router.post("/student")
async def student_chatbot(request: StudentChatRequest):
    if request.mode == "quick":
        # High threshold, textbook only
        answer, chunks = rag_service.query_with_rag(
            query_text=request.question,
            mode="quick",
            top_k=8,
            min_score=0.70  # High relevance threshold
        )
    else:
        # Comprehensive with web content
        answer, chunks = rag_service.query_with_rag_deepdive(
            query_text=request.question,
            top_k=15
        )
```

### RAG Service (rag_service.py)

#### Quick Mode
- Uses `query_with_rag()` with `min_score=0.70`
- Returns direct, concise answers
- If relevance too low, provides helpful redirect

#### DeepDive Mode
- Uses `query_with_rag_deepdive()`
- Queries both Pinecone indexes:
  1. Textbook content (ncert-learning-rag)
  2. Web content (ncert-web-content)
- Combines contexts and generates comprehensive answer

## Database Setup

### Pinecone Indexes

#### 1. Textbook Content (existing)
```
Index: ncert-learning-rag
Host: https://ncert-learning-rag-nitw5zb.svc.aped-4627-b74a.pinecone.io
Content: NCERT textbook PDFs
```

#### 2. Web Content (new)
```
Index: ncert-web-content
Host: https://ncert-web-content-nitw5zb.svc.aped-4627-b74a.pinecone.io
Content: Web-scraped educational content
```

### Environment Variables (.env)

```env
# Textbook Content
PINECONE_API_KEY=your_api_key
PINECONE_INDEX=ncert-learning-rag
PINECONE_HOST=https://ncert-learning-rag-nitw5zb.svc.aped-4627-b74a.pinecone.io

# Web Content (for DeepDive)
PINECONE_WEB_INDEX=ncert-web-content
PINECONE_WEB_HOST=https://ncert-web-content-nitw5zb.svc.aped-4627-b74a.pinecone.io
```

## Web Scraping for DeepDive Content

### Script: `web_scraper_deepdive.py`

Located in `backend/scripts/web_scraper_deepdive.py`

### Usage

```bash
# Scrape Wikipedia content for a topic
cd backend
python scripts/web_scraper_deepdive.py \
  --topic "World War 2" \
  --class 10 \
  --subject "History"

# Another example
python scripts/web_scraper_deepdive.py \
  --topic "Photosynthesis" \
  --class 10 \
  --subject "Science"
```

### What it does
1. Searches Wikipedia for the topic
2. Scrapes top 3 relevant articles
3. Extracts clean text content (removes ads, navigation, etc.)
4. Chunks content into 1000-character pieces with 200-char overlap
5. Generates Gemini embeddings for each chunk
6. Uploads to Pinecone web content index with metadata

### Features
- ✅ Rate limiting (respectful scraping)
- ✅ Clean text extraction (no junk)
- ✅ Proper metadata (class, subject, source, URL)
- ✅ Batch uploads (100 vectors at a time)
- ✅ Error handling

### Trusted Sources
Currently supports:
- Wikipedia (high quality, open license)
- Britannica (planned)
- Khan Academy (planned)

### Example Workflow

```bash
# 1. Scrape content for a chapter topic
python scripts/web_scraper_deepdive.py \
  --topic "French Revolution" \
  --class 9 \
  --subject "History"

# Output:
# 🚀 Starting web scraping for: French Revolution
#    Class: 9, Subject: History
# Found 5 Wikipedia articles for 'French Revolution'
# Scraped: French Revolution (15234 chars)
# Split into 16 chunks
# Generating embedding for chunk 1/16...
# ...
# Uploaded batch of 16 vectors
# ✅ DONE! Uploaded 16 total chunks for 'French Revolution'
#    These will be available in DeepDive mode for History Class 9

# 2. Now students can ask about French Revolution in DeepDive mode
#    and get comprehensive answers!
```

## Testing

### Frontend Testing

1. Open the app: `http://localhost:5173`
2. Navigate to a lesson (e.g., Class 6 Social Science Chapter 1)
3. Click the purple floating bot button (bottom-right)
4. Test Quick Mode:
   - Click "Quick" button
   - Ask: "What is diversity?"
   - Expected: 2-3 sentence direct answer from textbook
5. Test DeepDive Mode:
   - Click "DeepDive" button  
   - Ask: "Explain diversity in detail"
   - Expected: Comprehensive multi-paragraph response

### Backend Testing

```bash
# Test Quick Mode
curl -X POST http://localhost:8000/api/chat/student \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is photosynthesis?",
    "class_level": 10,
    "subject": "Science",
    "chapter": 1,
    "mode": "quick"
  }'

# Test DeepDive Mode
curl -X POST http://localhost:8000/api/chat/student \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain photosynthesis in detail",
    "class_level": 10,
    "subject": "Science",
    "chapter": 1,
    "mode": "deepdive"
  }'
```

## Troubleshooting

### White Screen Issue
**Fixed!** The StudentChatbot component was corrupted. It's now rewritten with:
- ✅ Proper imports (Zap, Brain icons)
- ✅ Mode selector UI
- ✅ Mode state management
- ✅ Conditional API calls based on mode

### DeepDive Mode Not Finding Web Content
1. Check if web content index is populated:
   ```bash
   # Check Pinecone dashboard
   # Index: ncert-web-content should have vectors
   ```
2. Run web scraper for the topic:
   ```bash
   python scripts/web_scraper_deepdive.py --topic "Your Topic" --class 10 --subject "Subject"
   ```
3. Check backend logs for web DB connection:
   ```
   INFO - Connected to Pinecone Web Content DB successfully
   INFO - Total web vectors: 156
   ```

### Quick Mode Always Says "Not Found"
- Relevance threshold might be too high (0.70)
- Check if textbook has the topic in that specific chapter
- Try asking more specific questions from the chapter

## Future Enhancements

### 1. More Web Sources
- [ ] Add Britannica scraper
- [ ] Add Khan Academy scraper
- [ ] Add NCERT official explanatory notes

### 2. Smart Web Scraping
- [ ] Automatic scraping when student asks unknown topic
- [ ] Background scraping during idle time
- [ ] Topic suggestion based on chapter content

### 3. Content Quality
- [ ] Relevance scoring for web content
- [ ] Fact verification
- [ ] Source credibility rating

### 4. UI Improvements
- [ ] Show sources/references in DeepDive mode
- [ ] Visualize textbook vs web content ratio
- [ ] "Learn More" links to original sources

### 5. Analytics
- [ ] Track which mode students prefer
- [ ] Identify topics needing more web content
- [ ] Student satisfaction ratings

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   Student Chatbot UI                    │
│  ┌─────────────────┐       ┌─────────────────┐         │
│  │  Quick Mode 🚀  │       │ DeepDive Mode 🧠│         │
│  └────────┬────────┘       └────────┬────────┘         │
└───────────┼─────────────────────────┼──────────────────┘
            │                         │
            ▼                         ▼
┌─────────────────────────────────────────────────────────┐
│              Backend API (/api/chat/student)            │
│  ┌──────────────────────┐  ┌──────────────────────┐    │
│  │   Quick Handler      │  │  DeepDive Handler    │    │
│  │  - High threshold    │  │  - Dual DB query     │    │
│  │  - Textbook only     │  │  - Comprehensive     │    │
│  └──────────┬───────────┘  └──────────┬───────────┘    │
└─────────────┼──────────────────────────┼────────────────┘
              │                          │
              ▼                          ▼
┌─────────────────────────────────────────────────────────┐
│                    RAG Service                          │
│  ┌──────────────────────┐  ┌──────────────────────┐    │
│  │  query_with_rag()    │  │ query_with_rag_      │    │
│  │  - Single DB         │  │  deepdive()          │    │
│  │  - min_score=0.70    │  │  - Dual DB query     │    │
│  └──────────┬───────────┘  └──────────┬───────────┘    │
└─────────────┼──────────────────────────┼────────────────┘
              │                          │
              ▼                          ▼
    ┌─────────────────┐       ┌─────────────────┐
    │  Pinecone DB 1  │       │  Pinecone DB 2  │
    │  (Textbook)     │       │  (Web Content)  │
    │  2193 vectors   │       │  ?? vectors     │
    └─────────────────┘       └─────────────────┘
                                      ▲
                                      │
                            ┌─────────┴─────────┐
                            │  Web Scraper     │
                            │  - Wikipedia     │
                            │  - Britannica    │
                            │  - Khan Academy  │
                            └──────────────────┘
```

## Summary

The Helper Bot now has two powerful modes:

1. **Quick Mode**: Fast, direct answers for exam prep
2. **DeepDive Mode**: Comprehensive explanations with web content

Students can switch between modes based on their needs. The web scraper allows you to continuously expand the knowledge base with high-quality educational content from trusted sources.

**Key Differentiators:**
- Quick Mode enforces high relevance (prevents wrong answers)
- DeepDive Mode covers all aspects of a topic (perfect for deep learning)
- Both modes use RAG (no hallucinations)
- Web content is properly sourced and metadata-tagged
