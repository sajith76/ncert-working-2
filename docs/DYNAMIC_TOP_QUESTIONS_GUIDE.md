# Dynamic Top Questions - Frontend Integration Guide

## Overview

This guide shows how to integrate the **dynamic** top questions feature where:
1. **Subject dropdown** shows only subjects with data in the database for the selected class
2. **Top questions** displays actual questions from the database based on selected subject and mode
3. Shows "No questions" message when database is empty

## New API Endpoints

### 1. Get Available Subjects
```javascript
GET /api/top-questions/subjects/{class_level}

// Example
GET /api/top-questions/subjects/10

Response:
{
  "success": true,
  "class_level": 10,
  "subjects": [
    {"name": "Hindi", "value": "hindi"},
    {"name": "Mathematics", "value": "mathematics"},
    {"name": "Science", "value": "science"}
  ],
  "count": 3
}
```

### 2. Get Top Questions
```javascript
POST /api/top-questions/top

Body:
{
  "subject": "hindi",
  "class_level": 10,
  "mode": "quick",
  "limit": 5
}

Response:
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
  "count": 1
}
```

## React Component Implementation

### Complete Component with Hooks

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TopQuestionsWidget.css';

const TopQuestionsWidget = ({ classLevel, userId, sessionId }) => {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [mode, setMode] = useState('quick');
  const [topQuestions, setTopQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE = 'http://localhost:8000';

  // Fetch available subjects
  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        setLoading(true);
        const { data } = await axios.get(
          `${API_BASE}/api/top-questions/subjects/${classLevel}`
        );
        
        if (data.success && data.subjects.length > 0) {
          setSubjects(data.subjects);
          setSelectedSubject(data.subjects[0].value);
        } else {
          setSubjects([]);
          setError('No subjects available for this class');
        }
      } catch (err) {
        console.error('Error:', err);
        setError('Failed to load subjects');
      } finally {
        setLoading(false);
      }
    };

    if (classLevel) fetchSubjects();
  }, [classLevel]);

  // Fetch top questions
  useEffect(() => {
    const fetchQuestions = async () => {
      if (!selectedSubject) return;

      try {
        setLoading(true);
        setError(null);
        
        const { data } = await axios.post(
          `${API_BASE}/api/top-questions/top`,
          {
            subject: selectedSubject,
            class_level: classLevel,
            mode: mode,
            limit: 5
          }
        );

        setTopQuestions(data.questions || []);
      } catch (err) {
        console.error('Error:', err);
        setTopQuestions([]);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, [selectedSubject, mode, classLevel]);

  const handleQuestionClick = async (question) => {
    // Ask the question through chat
    try {
      const { data } = await axios.post(`${API_BASE}/chat`, {
        class_level: classLevel,
        subject: selectedSubject,
        chapter: question.chapter || 1,
        highlight_text: question.question,
        mode: mode === 'quick' ? 'define' : 'elaborate',
        user_id: userId,
        session_id: sessionId
      });

      // Handle response (show in chat, modal, etc.)
      console.log('Answer:', data.answer);
    } catch (err) {
      console.error('Error asking question:', err);
    }
  };

  return (
    <div className="top-questions-widget">
      {/* Subject Selector */}
      <div className="subject-selector">
        <label>Subject</label>
        <select
          value={selectedSubject}
          onChange={(e) => setSelectedSubject(e.target.value)}
          disabled={loading || subjects.length === 0}
          className="subject-dropdown"
        >
          {subjects.length === 0 ? (
            <option>No subjects available</option>
          ) : (
            subjects.map((s) => (
              <option key={s.value} value={s.value}>
                {s.name}
              </option>
            ))
          )}
        </select>
      </div>

      {/* Mode Selector */}
      <div className="mode-selector">
        <label>Mode</label>
        <div className="mode-buttons">
          <button
            className={`mode-btn ${mode === 'quick' ? 'active' : ''}`}
            onClick={() => setMode('quick')}
          >
            ⚡ Quick
          </button>
          <button
            className={`mode-btn ${mode === 'deep' ? 'active' : ''}`}
            onClick={() => setMode('deep')}
          >
            🎯 Deep
          </button>
        </div>
      </div>

      {/* Top Questions */}
      <div className="top-questions-section">
        <h3>Top Questions</h3>
        
        {loading && <div className="loading">Loading...</div>}
        
        {error && <div className="error-message">{error}</div>}
        
        {!loading && !error && topQuestions.length === 0 && (
          <div className="no-questions">
            <p>No questions asked yet</p>
            <p className="hint">Be the first to ask!</p>
          </div>
        )}
        
        {!loading && !error && topQuestions.length > 0 && (
          <div className="questions-list">
            {topQuestions.map((q, i) => (
              <div
                key={i}
                className="question-item"
                onClick={() => handleQuestionClick(q)}
              >
                <div className="question-text">{q.question}</div>
                <div className="question-meta">
                  <span className="subject-tag">{q.subject}</span>
                  <span className="ask-count">
                    Asked {q.ask_count} times
                  </span>
                  {q.chapter && (
                    <span className="chapter-tag">Ch. {q.chapter}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TopQuestionsWidget;
```

## Usage in Your App

### 1. In Dashboard/Home Page

```jsx
import TopQuestionsWidget from './components/TopQuestionsWidget';

function Dashboard() {
  const user = useSelector(state => state.user);
  
  return (
    <div className="dashboard">
      <TopQuestionsWidget
        classLevel={user.classLevel}
        userId={user.userId}
        sessionId={user.sessionId}
      />
    </div>
  );
}
```

### 2. In Sidebar

```jsx
<aside className="sidebar">
  <TopQuestionsWidget
    classLevel={10}
    userId="STU001"
    sessionId="session-123"
  />
</aside>
```

## State Management (Redux/Context)

### Redux Action to Fetch Subjects

```javascript
// actions/subjectActions.js
export const fetchAvailableSubjects = (classLevel) => async (dispatch) => {
  try {
    dispatch({ type: 'SUBJECTS_LOADING' });
    
    const { data } = await axios.get(
      `/api/top-questions/subjects/${classLevel}`
    );
    
    dispatch({
      type: 'SUBJECTS_LOADED',
      payload: data.subjects
    });
  } catch (error) {
    dispatch({
      type: 'SUBJECTS_ERROR',
      payload: error.message
    });
  }
};

export const fetchTopQuestions = (subject, classLevel, mode) => async (dispatch) => {
  try {
    dispatch({ type: 'TOP_QUESTIONS_LOADING' });
    
    const { data } = await axios.post('/api/top-questions/top', {
      subject,
      class_level: classLevel,
      mode,
      limit: 5
    });
    
    dispatch({
      type: 'TOP_QUESTIONS_LOADED',
      payload: data.questions
    });
  } catch (error) {
    dispatch({
      type: 'TOP_QUESTIONS_ERROR',
      payload: error.message
    });
  }
};
```

### Redux Reducer

```javascript
// reducers/topQuestionsReducer.js
const initialState = {
  subjects: [],
  selectedSubject: null,
  mode: 'quick',
  questions: [],
  loading: false,
  error: null
};

export default function topQuestionsReducer(state = initialState, action) {
  switch (action.type) {
    case 'SUBJECTS_LOADING':
    case 'TOP_QUESTIONS_LOADING':
      return { ...state, loading: true, error: null };
      
    case 'SUBJECTS_LOADED':
      return {
        ...state,
        subjects: action.payload,
        selectedSubject: action.payload[0]?.value || null,
        loading: false
      };
      
    case 'TOP_QUESTIONS_LOADED':
      return {
        ...state,
        questions: action.payload,
        loading: false
      };
      
    case 'SUBJECTS_ERROR':
    case 'TOP_QUESTIONS_ERROR':
      return { ...state, loading: false, error: action.payload };
      
    case 'SET_SUBJECT':
      return { ...state, selectedSubject: action.payload };
      
    case 'SET_MODE':
      return { ...state, mode: action.payload };
      
    default:
      return state;
  }
}
```

## API Service Layer

```javascript
// services/topQuestionsService.js
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class TopQuestionsService {
  async getAvailableSubjects(classLevel) {
    const { data } = await axios.get(
      `${API_BASE}/api/top-questions/subjects/${classLevel}`
    );
    return data;
  }

  async getTopQuestions(subject, classLevel, mode, limit = 5) {
    const { data } = await axios.post(
      `${API_BASE}/api/top-questions/top`,
      { subject, class_level: classLevel, mode, limit }
    );
    return data;
  }

  async getRecommendations(userId, subject, classLevel, mode, limit = 5) {
    const { data } = await axios.post(
      `${API_BASE}/api/top-questions/recommendations`,
      { user_id: userId, subject, class_level: classLevel, mode, limit }
    );
    return data;
  }

  async getTrending(subject, classLevel, mode, days = 7, limit = 5) {
    const { data } = await axios.post(
      `${API_BASE}/api/top-questions/trending`,
      { subject, class_level: classLevel, mode, days, limit }
    );
    return data;
  }

  async trackQuestion(questionData) {
    const { data } = await axios.post(
      `${API_BASE}/api/top-questions/track`,
      questionData
    );
    return data;
  }
}

export default new TopQuestionsService();
```

## Error Handling

```jsx
const [error, setError] = useState(null);

try {
  const response = await fetchTopQuestions();
  setTopQuestions(response.data.questions);
} catch (err) {
  if (err.response?.status === 404) {
    setError('No questions found');
  } else if (err.response?.status === 500) {
    setError('Server error. Please try again later.');
  } else {
    setError('Failed to load questions');
  }
}
```

## Loading States

```jsx
{loading ? (
  <div className="loading-spinner">
    <div className="spinner"></div>
    <p>Loading questions...</p>
  </div>
) : questions.length === 0 ? (
  <div className="empty-state">
    <p>No questions available yet</p>
    <button onClick={handleAskQuestion}>Ask a Question</button>
  </div>
) : (
  <QuestionsList questions={questions} />
)}
```

## Testing

### Test Empty State
```javascript
// When no data in database
GET /api/top-questions/subjects/7
Response: { subjects: [], count: 0 }

GET /api/top-questions/top
Response: { questions: [], count: 0 }
```

### Test With Data
```javascript
// After students ask questions
GET /api/top-questions/subjects/10
Response: { 
  subjects: [
    {"name": "Hindi", "value": "hindi"},
    {"name": "Science", "value": "science"}
  ]
}
```

## Summary

### What Changes:
1. ✅ Subjects dropdown is now **dynamic** - populated from database
2. ✅ Top questions are **real** - fetched from actual student questions
3. ✅ Shows **"No questions"** when database is empty
4. ✅ Updates automatically as students ask more questions

### API Endpoints Used:
- `GET /api/top-questions/subjects/{class_level}` - Get available subjects
- `POST /api/top-questions/top` - Get top questions
- `POST /chat` - Ask a question (with tracking)

### Files to Use:
- Component: `docs/examples/TopQuestionsWidget.jsx`
- Styles: `docs/examples/TopQuestionsWidget.css`
- Service: Create `services/topQuestionsService.js`

**Ready to integrate! 🚀**
