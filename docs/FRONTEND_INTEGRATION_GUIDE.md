# Top Questions - Frontend Integration Guide

## Quick Start for Frontend Developers

This guide shows how to integrate the Top Questions feature into your React/Vue/Angular application.

## 🎯 What This Feature Does

1. **Shows popular questions** students are asking in each subject
2. **Recommends questions** based on what each student has studied
3. **Displays trending questions** from the past week
4. **Automatically tracks** all questions for future recommendations

## 📍 Where to Display This Feature

### Suggested UI Locations:

#### 1. **Subject Dashboard** (Main Location)
When student selects a subject (Hindi, Math, Science, etc.), show:
```
┌──────────────────────────────────────────┐
│  📚 Hindi - Class 10                     │
├──────────────────────────────────────────┤
│                                          │
│  💡 Top Questions                        │
│  ────────────────────                    │
│  1. व्याकरण क्या है? (45 students asked) │
│  2. संज्ञा के कितने भेद होते हैं?        │
│  3. विशेषण किसे कहते हैं?               │
│                                          │
│  [See All Questions →]                   │
│                                          │
└──────────────────────────────────────────┘
```

#### 2. **Student Dashboard Sidebar**
```
┌─────────────────────────┐
│ 🎯 Recommended for You │
├─────────────────────────┤
│ • What is photosynthesis?│
│ • Prime numbers         │
│ • World War 1 causes    │
│                         │
│ [View More →]          │
└─────────────────────────┘
```

#### 3. **Chapter Page**
When viewing a chapter, show trending questions from that chapter

#### 4. **Home Page**
Show trending questions across all subjects

## 🔌 API Integration

### 1. Get Top Questions (By Subject)

```javascript
// Function to fetch top questions
async function getTopQuestions(subject, classLevel, mode = 'quick') {
  const response = await fetch('http://localhost:8000/api/top-questions/top', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      subject: subject,      // 'hindi', 'math', 'science', etc.
      class_level: classLevel, // 6-12
      mode: mode,            // 'quick' or 'deep'
      limit: 5               // Number of questions to fetch
    })
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch top questions');
  }
  
  const data = await response.json();
  return data.questions;
}

// Usage in React
import { useState, useEffect } from 'react';

function SubjectDashboard({ subject, classLevel }) {
  const [topQuestions, setTopQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadQuestions() {
      try {
        const questions = await getTopQuestions(subject, classLevel, 'quick');
        setTopQuestions(questions);
      } catch (error) {
        console.error('Error loading questions:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadQuestions();
  }, [subject, classLevel]);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="top-questions-section">
      <h3>💡 Top Questions in {subject}</h3>
      <ul>
        {topQuestions.map((q, index) => (
          <li key={index}>
            <span className="question">{q.question}</span>
            <span className="count">({q.ask_count} students asked)</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### 2. Get Personalized Recommendations

```javascript
// Function to fetch recommendations
async function getRecommendations(userId, subject, classLevel, mode = 'quick') {
  const response = await fetch('http://localhost:8000/api/top-questions/recommendations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      subject: subject,
      class_level: classLevel,
      mode: mode,
      limit: 5
    })
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch recommendations');
  }
  
  const data = await response.json();
  return data.recommendations;
}

// Usage in React
function RecommendationsWidget({ userId, subject, classLevel }) {
  const [recommendations, setRecommendations] = useState([]);
  
  useEffect(() => {
    async function loadRecommendations() {
      const recs = await getRecommendations(userId, subject, classLevel);
      setRecommendations(recs);
    }
    
    loadRecommendations();
  }, [userId, subject, classLevel]);
  
  return (
    <div className="recommendations-widget">
      <h4>🎯 Recommended for You</h4>
      <ul>
        {recommendations.map((q, index) => (
          <li key={index} onClick={() => askQuestion(q.question)}>
            {q.question}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### 3. Enable Auto-Tracking in Chat

**IMPORTANT:** To enable automatic question tracking, simply include `user_id` and `session_id` in your chat requests.

```javascript
// Modified chat function with tracking
async function askQuestion(question, subject, classLevel, chapter, userId, sessionId) {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      class_level: classLevel,
      subject: subject,
      chapter: chapter,
      highlight_text: question,
      mode: 'define',
      // 👇 ADD THESE TWO FIELDS for automatic tracking
      user_id: userId,
      session_id: sessionId
    })
  });
  
  const data = await response.json();
  return data.answer;
}

// Usage
const answer = await askQuestion(
  'What is photosynthesis?',
  'science',
  10,
  6,
  'STU001',              // Current user ID
  'session-abc-123'      // Current session ID
);
```

### 4. Get Trending Questions

```javascript
async function getTrendingQuestions(subject, classLevel, days = 7) {
  const response = await fetch('http://localhost:8000/api/top-questions/trending', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      subject: subject,
      class_level: classLevel,
      mode: 'quick',
      limit: 5,
      days: days  // Look back N days
    })
  });
  
  const data = await response.json();
  return data.trending;
}

// Usage
const trending = await getTrendingQuestions('math', 10, 7);
```

## 🎨 UI Component Examples

### Complete React Component

```jsx
import React, { useState, useEffect } from 'react';
import './TopQuestions.css';

function TopQuestionsPanel({ subject, classLevel, userId, sessionId, onQuestionClick }) {
  const [activeTab, setActiveTab] = useState('top');
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Load questions based on active tab
  useEffect(() => {
    loadQuestions();
  }, [activeTab, subject, classLevel]);
  
  async function loadQuestions() {
    setLoading(true);
    try {
      let data;
      
      if (activeTab === 'top') {
        const response = await fetch('http://localhost:8000/api/top-questions/top', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            subject: subject,
            class_level: classLevel,
            mode: 'quick',
            limit: 5
          })
        });
        const result = await response.json();
        data = result.questions;
      } 
      else if (activeTab === 'recommended') {
        const response = await fetch('http://localhost:8000/api/top-questions/recommendations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            subject: subject,
            class_level: classLevel,
            mode: 'quick',
            limit: 5
          })
        });
        const result = await response.json();
        data = result.recommendations;
      }
      else if (activeTab === 'trending') {
        const response = await fetch('http://localhost:8000/api/top-questions/trending', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            subject: subject,
            class_level: classLevel,
            mode: 'quick',
            limit: 5,
            days: 7
          })
        });
        const result = await response.json();
        data = result.trending;
      }
      
      setQuestions(data || []);
    } catch (error) {
      console.error('Error loading questions:', error);
    } finally {
      setLoading(false);
    }
  }
  
  return (
    <div className="top-questions-panel">
      <div className="tabs">
        <button 
          className={activeTab === 'top' ? 'active' : ''} 
          onClick={() => setActiveTab('top')}
        >
          💡 Top Questions
        </button>
        <button 
          className={activeTab === 'recommended' ? 'active' : ''} 
          onClick={() => setActiveTab('recommended')}
        >
          🎯 For You
        </button>
        <button 
          className={activeTab === 'trending' ? 'active' : ''} 
          onClick={() => setActiveTab('trending')}
        >
          🔥 Trending
        </button>
      </div>
      
      <div className="questions-list">
        {loading ? (
          <div className="loading">Loading...</div>
        ) : questions.length === 0 ? (
          <div className="empty">No questions yet. Be the first to ask!</div>
        ) : (
          <ul>
            {questions.map((q, index) => (
              <li key={index} onClick={() => onQuestionClick(q.question)}>
                <div className="question-text">{q.question}</div>
                <div className="question-meta">
                  <span className="count">{q.ask_count} asked</span>
                  {q.chapter && <span className="chapter">Ch. {q.chapter}</span>}
                  <span className="difficulty">{q.difficulty}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default TopQuestionsPanel;
```

### CSS Styling

```css
/* TopQuestions.css */
.top-questions-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 20px;
  margin: 20px 0;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.tabs button {
  background: none;
  border: none;
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.3s;
}

.tabs button.active {
  color: #4F46E5;
  border-bottom-color: #4F46E5;
}

.tabs button:hover {
  color: #4F46E5;
}

.questions-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.questions-list li {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.questions-list li:hover {
  background: #f9fafb;
}

.questions-list li:last-child {
  border-bottom: none;
}

.question-text {
  font-size: 15px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8px;
}

.question-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #6b7280;
}

.question-meta span {
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
}

.loading, .empty {
  text-align: center;
  padding: 40px 20px;
  color: #9ca3af;
}
```

## 🔄 User Flow

### Scenario 1: Student Opens Subject Dashboard

```
1. Student clicks on "Hindi" subject
2. Frontend calls getTopQuestions('hindi', 10, 'quick')
3. Display top 5 Hindi questions
4. Student clicks on a question
5. Chat opens with that question pre-filled
```

### Scenario 2: Student Asks a Question

```
1. Student types "व्याकरण क्या है?" in chat
2. Frontend sends request with user_id and session_id
3. Backend automatically tracks the question
4. Next time student opens dashboard, this influences recommendations
```

### Scenario 3: Personalized Recommendations

```
1. Student has asked 10 questions about Grammar in Hindi
2. Frontend calls getRecommendations('STU001', 'hindi', 10)
3. Backend analyzes: student studied Grammar (Ch. 1)
4. Returns popular questions from Chapter 1 student hasn't asked yet
5. Display as "Recommended for You"
```

## 📱 Mobile Responsive Design

```jsx
// Simplified mobile view
function MobileTopQuestions({ subject, classLevel }) {
  return (
    <div className="mobile-questions">
      <div className="section-title">💡 Popular Questions</div>
      <div className="questions-carousel">
        {/* Horizontal scrollable list */}
        {questions.map(q => (
          <div className="question-card">
            <div className="question">{q.question}</div>
            <div className="meta">{q.ask_count} asked</div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## ⚠️ Important Notes

### 1. User ID Management
- Use the student's user_id from authentication
- Generate a new session_id when student logs in
- Keep session_id consistent throughout the session

```javascript
// On login
const userId = authResponse.user_id;
const sessionId = `session-${Date.now()}-${Math.random()}`;

// Store in state/context
localStorage.setItem('sessionId', sessionId);
```

### 2. Subject Names
Use lowercase for consistency:
- ✅ `"hindi"`, `"math"`, `"science"`
- ❌ `"Hindi"`, `"Math"`, `"Science"`

### 3. Mode Selection
- Use `"quick"` for main dashboard (faster, more popular)
- Use `"deep"` for advanced students or deep dive sections

### 4. Error Handling
```javascript
try {
  const questions = await getTopQuestions(subject, classLevel);
  setQuestions(questions);
} catch (error) {
  console.error('Error:', error);
  // Show fallback UI or error message
  showNotification('Could not load questions. Please try again.');
}
```

## 🧪 Testing

### Test Data
To generate test data for development:

```bash
cd backend
python test_top_questions.py
```

This will create sample questions in the database.

### Test Endpoints in Browser
1. Start backend: `cd backend && python run.py`
2. Open: http://localhost:8000/docs
3. Try "Top Questions" endpoints

## 🎯 Integration Checklist

- [ ] Create UI component for Top Questions display
- [ ] Add to subject dashboard page
- [ ] Implement tab switching (Top / Recommended / Trending)
- [ ] Add click handler to open chat with selected question
- [ ] Update chat request to include user_id and session_id
- [ ] Test with multiple subjects (Hindi, Math, Science)
- [ ] Test recommendations for different users
- [ ] Add loading states
- [ ] Add error handling
- [ ] Style for mobile responsiveness

## 📞 Support

If you have questions:
1. Check API docs: http://localhost:8000/docs
2. Read full documentation: `docs/TOP_QUESTIONS_FEATURE.md`
3. Contact backend team

## 🚀 Quick Start Code

Copy-paste this to get started:

```javascript
// api.js - API functions
export async function getTopQuestions(subject, classLevel, mode = 'quick', limit = 5) {
  const response = await fetch('http://localhost:8000/api/top-questions/top', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ subject, class_level: classLevel, mode, limit })
  });
  const data = await response.json();
  return data.questions;
}

export async function getRecommendations(userId, subject, classLevel, mode = 'quick', limit = 5) {
  const response = await fetch('http://localhost:8000/api/top-questions/recommendations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, subject, class_level: classLevel, mode, limit })
  });
  const data = await response.json();
  return data.recommendations;
}
```

That's it! You're ready to integrate the Top Questions feature. 🎉
