# Top Questions & Recommendations Feature

## Overview

This feature implements a comprehensive top questions tracking and recommendation system that works seamlessly with both **Quick** and **Deep** modes. The system automatically tracks questions asked by students, provides subject-wise recommendations, and helps students discover commonly asked questions in their subject and class.

## Key Features

### 1. **Subject-Wise Filtering**
- ✅ If student chooses **Hindi** → Top questions shown are from Hindi
- ✅ If student chooses **Math** → Top questions shown are from Math
- ✅ Works for all subjects: Science, Social Science, English, etc.

### 2. **Mode Support**
- **Quick Mode**: Fast, concise answers
- **Deep Mode**: Detailed, comprehensive explanations
- Questions tracked separately for each mode

### 3. **Automatic Question Tracking**
- Questions and answers are automatically saved when students ask questions
- Tracking happens in both `/chat` and `/v1/chat/optimized` endpoints
- Completely transparent to students - no extra steps required

### 4. **Personalized Recommendations**
- System analyzes which questions a student has already asked
- Recommends popular questions the student hasn't explored yet
- Prioritizes questions from chapters the student is currently studying

### 5. **Trending Questions**
- Shows most popular questions from the last 7 days
- Helps students discover what others are currently learning about

## MongoDB Collections

### Collection 1: `top_questions`
Stores aggregated data about frequently asked questions.

**Schema:**
```json
{
  "_id": ObjectId,
  "question": "Explain photosynthesis",
  "subject": "science",
  "class_level": 10,
  "chapter": 6,
  "mode": "quick",
  "category": "concept",
  "ask_count": 25,
  "last_asked": ISODate("2026-01-06T10:30:00Z"),
  "difficulty": "medium",
  "tags": ["photosynthesis", "biology"],
  "related_concepts": ["chlorophyll", "sunlight"]
}
```

**Indexes:**
- `{ subject: 1, class_level: 1, mode: 1, ask_count: -1 }` - Fast retrieval of top questions
- `{ last_asked: -1 }` - Trending questions query

### Collection 2: `question_answer_pairs`
Stores individual Q&A interactions with user context.

**Schema:**
```json
{
  "_id": ObjectId,
  "user_id": "STU001",
  "session_id": "abc-123-xyz",
  "question": "Explain photosynthesis",
  "answer": "Photosynthesis is the process by which...",
  "subject": "science",
  "class_level": 10,
  "chapter": 6,
  "mode": "quick",
  "timestamp": ISODate("2026-01-06T10:30:00Z"),
  "difficulty": null,
  "time_spent_seconds": 120,
  "user_rating": 5,
  "was_helpful": true,
  "follow_up_questions": [],
  "concepts_covered": ["photosynthesis", "chlorophyll"],
  "formulas_used": [],
  "examples_provided": true
}
```

**Indexes:**
- `{ user_id: 1, subject: 1, timestamp: -1 }` - Fast user history lookup
- `{ subject: 1, class_level: 1, mode: 1 }` - Cross-user analysis

## API Endpoints

### 1. Get Top Questions
**POST** `/api/top-questions/top`

Get the most frequently asked questions for a subject and class.

**Request:**
```json
{
  "subject": "hindi",
  "class_level": 10,
  "mode": "quick",
  "limit": 5
}
```

**Response:**
```json
{
  "success": true,
  "questions": [
    {
      "question": "व्याकरण क्या है?",
      "subject": "hindi",
      "class_level": 10,
      "chapter": 1,
      "mode": "quick",
      "category": "concept",
      "ask_count": 45,
      "difficulty": "easy"
    }
  ],
  "count": 5,
  "subject": "hindi",
  "class_level": 10,
  "mode": "quick"
}
```

**Alternative GET endpoint:**
```
GET /api/top-questions/top/hindi/10?mode=quick&limit=5
```

### 2. Get Personalized Recommendations
**POST** `/api/top-questions/recommendations`

Get personalized question recommendations based on user's study history.

**Request:**
```json
{
  "user_id": "STU001",
  "subject": "math",
  "class_level": 10,
  "mode": "deep",
  "limit": 5
}
```

**Response:**
```json
{
  "success": true,
  "recommendations": [
    {
      "question": "Prove the Pythagorean theorem",
      "subject": "math",
      "class_level": 10,
      "chapter": 6,
      "mode": "deep",
      "category": "theory",
      "ask_count": 32,
      "difficulty": "hard"
    }
  ],
  "count": 5,
  "personalized": true
}
```

**Alternative GET endpoint:**
```
GET /api/top-questions/recommendations/STU001/math/10?mode=deep&limit=5
```

### 3. Track Question-Answer Pair
**POST** `/api/top-questions/track`

Manually track a question-answer interaction (usually done automatically).

**Request:**
```json
{
  "user_id": "STU001",
  "session_id": "abc-123-xyz",
  "question": "Explain photosynthesis",
  "answer": "Photosynthesis is the process...",
  "subject": "science",
  "class_level": 10,
  "chapter": 6,
  "mode": "quick"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Question tracked successfully",
  "question_id": "507f1f77bcf86cd799439011"
}
```

### 4. Update Feedback
**POST** `/api/top-questions/feedback`

Update user feedback for a question-answer pair.

**Request:**
```json
{
  "qa_id": "507f1f77bcf86cd799439011",
  "user_rating": 5,
  "was_helpful": true,
  "time_spent_seconds": 120
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback updated successfully"
}
```

### 5. Get Trending Questions
**POST** `/api/top-questions/trending`

Get trending questions from the last N days.

**Request:**
```json
{
  "subject": "math",
  "class_level": 10,
  "mode": "quick",
  "limit": 5,
  "days": 7
}
```

**Response:**
```json
{
  "success": true,
  "trending": [
    {
      "question": "What are prime numbers?",
      "subject": "math",
      "class_level": 10,
      "chapter": 1,
      "mode": "quick",
      "category": "concept",
      "ask_count": 18,
      "difficulty": "easy"
    }
  ],
  "count": 5,
  "days": 7
}
```

## Automatic Tracking Integration

### Chat Endpoint (`/chat`)
Questions are automatically tracked when students include `user_id` and `session_id`:

```json
{
  "class_level": 10,
  "subject": "hindi",
  "chapter": 1,
  "highlight_text": "व्याकरण क्या है?",
  "mode": "define",
  "user_id": "STU001",
  "session_id": "abc-123-xyz"
}
```

### Optimized Chat Endpoint (`/v1/chat/optimized`)
Same automatic tracking applies:

```json
{
  "question": "Explain photosynthesis",
  "class_level": 10,
  "subject": "science",
  "mode": "quick",
  "chapter": 6,
  "user_id": "STU001",
  "session_id": "abc-123-xyz"
}
```

## Frontend Integration Example

### Get Top Questions for Current Subject
```javascript
// When student selects a subject
const getTopQuestions = async (subject, classLevel, mode) => {
  const response = await fetch('/api/top-questions/top', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      subject: subject,
      class_level: classLevel,
      mode: mode,
      limit: 5
    })
  });
  
  const data = await response.json();
  return data.questions;
};

// Display in UI
const questions = await getTopQuestions('hindi', 10, 'quick');
questions.forEach(q => {
  console.log(`${q.question} (asked ${q.ask_count} times)`);
});
```

### Get Personalized Recommendations
```javascript
const getRecommendations = async (userId, subject, classLevel, mode) => {
  const response = await fetch('/api/top-questions/recommendations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      subject: subject,
      class_level: classLevel,
      mode: mode,
      limit: 5
    })
  });
  
  const data = await response.json();
  return data.recommendations;
};
```

### Ask Question with Auto-Tracking
```javascript
const askQuestion = async (userId, sessionId, question, classLevel, subject, chapter, mode) => {
  const response = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      class_level: classLevel,
      subject: subject,
      chapter: chapter,
      highlight_text: question,
      mode: mode,
      user_id: userId,        // Include for auto-tracking
      session_id: sessionId   // Include for auto-tracking
    })
  });
  
  const data = await response.json();
  return data.answer;
};
```

## Question Categorization

Questions are automatically categorized based on keywords:

- **Concept**: "explain", "what is", "define", "meaning"
- **Problem**: "solve", "calculate", "find", "compute"
- **Theory**: "why", "how does", "reason"
- **Application**: "example", "application", "real life"
- **Numerical**: Contains numbers
- **General**: Default category

## Recommendation Algorithm

1. **Get user's question history** (last 20 questions)
2. **Extract studied chapters and concepts**
3. **Find popular questions** the user hasn't asked yet
4. **Prioritize questions from:**
   - Same chapters user is studying
   - Related concepts user has explored
   - High ask_count (popular with other students)
5. **Return top N recommendations**

## Benefits

### For Students
- ✅ Discover commonly asked questions in their subject
- ✅ Get personalized recommendations based on study patterns
- ✅ See trending topics other students are exploring
- ✅ Quick access to popular questions as study aids

### For Teachers/Admins
- ✅ Understand which topics students find difficult
- ✅ Identify knowledge gaps by subject and chapter
- ✅ Track learning patterns across the platform
- ✅ Create targeted content based on popular questions

### For System
- ✅ Builds knowledge base automatically
- ✅ Improves over time with more usage
- ✅ No manual curation required
- ✅ Works across all subjects and classes

## Performance Optimizations

1. **MongoDB Indexes**: Fast query performance for millions of questions
2. **Caching**: Frequently accessed top questions can be cached
3. **Batch Processing**: Question tracking doesn't slow down chat responses
4. **Async Tracking**: Tracking happens asynchronously (doesn't block responses)

## Future Enhancements

1. **Answer Quality Score**: Track which answers students find most helpful
2. **Difficulty Prediction**: ML model to predict question difficulty
3. **Concept Extraction**: NLP to extract concepts from answers
4. **Smart Grouping**: Group similar questions together
5. **Multi-language Support**: Track questions across languages
6. **Analytics Dashboard**: Visual insights for teachers and admins

## Testing

### Test Top Questions
```bash
curl -X POST http://localhost:8000/api/top-questions/top \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "hindi",
    "class_level": 10,
    "mode": "quick",
    "limit": 5
  }'
```

### Test Recommendations
```bash
curl -X POST http://localhost:8000/api/top-questions/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "STU001",
    "subject": "math",
    "class_level": 10,
    "mode": "deep",
    "limit": 5
  }'
```

### Test Tracking
```bash
curl -X POST http://localhost:8000/api/top-questions/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "STU001",
    "session_id": "test-session-123",
    "question": "What is photosynthesis?",
    "answer": "Photosynthesis is...",
    "subject": "science",
    "class_level": 10,
    "chapter": 6,
    "mode": "quick"
  }'
```

## Troubleshooting

### Issue: No questions returned
**Solution**: Database may be empty. Generate some questions by using the chat feature with user tracking enabled.

### Issue: Recommendations not personalized
**Solution**: User needs to ask at least a few questions first. System needs history to personalize.

### Issue: Tracking not working
**Solution**: Ensure `user_id` and `session_id` are included in chat requests.

## Documentation

- API documentation: `http://localhost:8000/docs`
- Models: `backend/app/models/top_questions.py`
- Service: `backend/app/services/top_question_service.py`
- Router: `backend/app/routers/top_questions.py`
