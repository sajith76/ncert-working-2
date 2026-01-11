/**
 * Dynamic Top Questions Component
 * Shows available subjects and top questions from database
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const TopQuestionsWidget = ({ classLevel, userId, sessionId }) => {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [mode, setMode] = useState('quick');
  const [topQuestions, setTopQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch available subjects when class level changes
  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        setLoading(true);
        const response = await axios.get(
          `${API_BASE_URL}/api/top-questions/subjects/${classLevel}`
        );
        
        if (response.data.success && response.data.subjects.length > 0) {
          setSubjects(response.data.subjects);
          // Auto-select first subject
          setSelectedSubject(response.data.subjects[0].value);
        } else {
          setSubjects([]);
          setError('No subjects available for this class');
        }
      } catch (err) {
        console.error('Error fetching subjects:', err);
        setError('Failed to load subjects');
      } finally {
        setLoading(false);
      }
    };

    if (classLevel) {
      fetchSubjects();
    }
  }, [classLevel]);

  // Fetch top questions when subject or mode changes
  useEffect(() => {
    const fetchTopQuestions = async () => {
      if (!selectedSubject) return;

      try {
        setLoading(true);
        setError(null);
        
        const response = await axios.post(
          `${API_BASE_URL}/api/top-questions/top`,
          {
            subject: selectedSubject,
            class_level: classLevel,
            mode: mode,
            limit: 5
          }
        );

        if (response.data.success) {
          setTopQuestions(response.data.questions);
        }
      } catch (err) {
        console.error('Error fetching top questions:', err);
        setError('Failed to load questions');
        setTopQuestions([]);
      } finally {
        setLoading(false);
      }
    };

    if (selectedSubject) {
      fetchTopQuestions();
    }
  }, [selectedSubject, mode, classLevel]);

  // Handle question click
  const handleQuestionClick = async (question) => {
    try {
      // Ask the question through chat API
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        class_level: classLevel,
        subject: selectedSubject,
        chapter: question.chapter || 1,
        highlight_text: question.question,
        mode: mode === 'quick' ? 'define' : 'elaborate',
        user_id: userId,
        session_id: sessionId
      });

      // Handle the response (show in chat, modal, etc.)
      console.log('Answer:', response.data.answer);
      // You can dispatch to Redux, show modal, or navigate to chat
    } catch (err) {
      console.error('Error asking question:', err);
    }
  };

  return (
    <div className="top-questions-widget">
      {/* Subject Selector */}
      <div className="subject-selector">
        <label htmlFor="subject-select">Subject</label>
        <select
          id="subject-select"
          value={selectedSubject}
          onChange={(e) => setSelectedSubject(e.target.value)}
          disabled={loading || subjects.length === 0}
          className="subject-dropdown"
        >
          {subjects.length === 0 ? (
            <option value="">No subjects available</option>
          ) : (
            subjects.map((subject) => (
              <option key={subject.value} value={subject.value}>
                {subject.name}
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

      {/* Top Questions List */}
      <div className="top-questions-section">
        <h3>Top Questions</h3>
        
        {loading && (
          <div className="loading">Loading questions...</div>
        )}

        {error && (
          <div className="error-message">{error}</div>
        )}

        {!loading && !error && topQuestions.length === 0 && (
          <div className="no-questions">
            <p>No questions asked yet in {selectedSubject}</p>
            <p className="hint">Be the first to ask a question!</p>
          </div>
        )}

        {!loading && !error && topQuestions.length > 0 && (
          <div className="questions-list">
            {topQuestions.map((question, index) => (
              <div
                key={index}
                className="question-item"
                onClick={() => handleQuestionClick(question)}
              >
                <div className="question-text">{question.question}</div>
                <div className="question-meta">
                  <span className="subject-tag">{question.subject}</span>
                  <span className="ask-count">
                    Asked {question.ask_count} times
                  </span>
                  {question.chapter && (
                    <span className="chapter-tag">Ch. {question.chapter}</span>
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
