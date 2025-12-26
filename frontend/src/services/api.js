/**
 * API Service - Backend Integration
 * 
 * This file contains all API calls to the FastAPI backend
 * Base URL: http://localhost:8000
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Chat Service - AI Explanations with RAG
 * Integrates with the backend RAG system for annotations and assessment
 */
export const chatService = {
  /**
   * Process annotation with AI (Define, Elaborate, Stick Flow)
   * UNIFIED ENDPOINT - Main function for text annotations
   * @param {string} text - The selected text to process
   * @param {string} action - Action type: "define", "elaborate", or "stick_flow"
   * @param {number} classLevel - User's class level (5-10)
   * @param {string} subject - Subject name
   * @param {number} chapter - Chapter number
   * @returns {Promise<{answer: string, action_type: string, source_count: number}>}
   */
  async processAnnotation(text, action, classLevel, subject, chapter) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/annotation/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          selected_text: text,
          action: action,
          class_level: classLevel,
          subject: subject,
          chapter: chapter,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API Error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        answer: data.answer,
        actionType: data.action_type,
        sourceCount: data.source_count,
      };
    } catch (error) {
      console.error("Annotation API Error:", error);
      throw error;
    }
  },

  /**
   * @deprecated Use processAnnotation() instead
   * Get AI explanation for selected text
   */
  async getExplanation(text, mode, classLevel, subject, chapter) {
    return this.processAnnotation(text, mode, classLevel, subject, chapter);
  },

  /**
   * @deprecated Use processAnnotation() with action="stick_flow" instead
   * Get Stick Flow visual diagram
   */
  async getStickFlow(text, classLevel, subject, chapter) {
    return this.processAnnotation(text, "stick_flow", classLevel, subject, chapter);
  },

  /**
   * Student chatbot - Open-ended questions with RAG
   * @param {string} question - Student's question
   * @param {number} classLevel - User's class level (5-10)
   * @param {string} subject - Subject name
   * @param {number} chapter - Chapter number
   * @param {string} mode - Chat mode: "quick" (exam-style) or "deepdive" (comprehensive)
   * @returns {Promise<{answer: string, sources: array}>}
   */
  async studentChat(question, classLevel, subject, chapter, mode = "quick") {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/student`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
          class_level: classLevel,
          subject: subject,
          chapter: chapter,
          mode: mode,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Student Chat API Error: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        answer: data.answer,
        sources: data.source_chunks || [],
      };
    } catch (error) {
      console.error("Student Chat API Error:", error);
      throw error;
    }
  },
};

/**
 * Assessment Service - Voice Assessment Integration
 */
export const assessmentService = {
  /**
   * Get enhanced assessment questions (15 questions for 10-page interval)
   */
  async getEnhancedQuestions(classLevel, subject, chapter, lessonName, pageRange, studentId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/assessment/questions/enhanced`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          class_level: classLevel,
          subject: subject,
          chapter: chapter,
          lesson_name: lessonName,
          page_range: pageRange,
          student_id: studentId,
          force_regenerate: false,
        }),
      });

      if (!response.ok) {
        throw new Error(`Enhanced Questions API Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Enhanced Questions API Error:", error);
      throw error;
    }
  },

  /**
   * Get assessment questions from textbook content (RAG-based)
   */
  async getQuestions(classLevel, subject, chapter, numQuestions = 3) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/assessment/questions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          class_level: classLevel,
          subject: subject,
          chapter: chapter,
          num_questions: numQuestions,
        }),
      });

      if (!response.ok) {
        throw new Error(`Assessment API Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Assessment Questions API Error:", error);
      throw error;
    }
  },

  /**
   * Evaluate voice assessment answers
   */
  async evaluateAnswers(classLevel, subject, chapter, answers) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/assessment/evaluate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          class_level: classLevel,
          subject: subject,
          chapter: chapter,
          answers: answers,
        }),
      });

      if (!response.ok) {
        throw new Error(`Evaluation API Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Assessment Evaluation API Error:", error);
      throw error;
    }
  },
};

/**
 * User Stats Service - Dashboard data (progress, streaks, notes)
 */
export const userStatsService = {
  /**
   * Get all dashboard data in one call
   * @param {string} studentId - Student identifier
   * @param {string} subject - Optional subject filter
   * @returns {Promise<{streak, progress, recent_notes, total_notes}>}
   */
  async getDashboardData(studentId, subject = null) {
    try {
      let url = `${API_BASE_URL}/api/user/dashboard/${studentId}`;
      if (subject) {
        url += `?subject=${encodeURIComponent(subject)}`;
      }
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Dashboard API Error: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Dashboard API Error:", error);
      throw error;
    }
  },

  /**
   * Get streak data only
   * @param {string} studentId - Student identifier
   * @returns {Promise<{current_streak, longest_streak, weekly_activity}>}
   */
  async getStreakData(studentId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/user/streak/${studentId}`);
      
      if (!response.ok) {
        throw new Error(`Streak API Error: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Streak API Error:", error);
      throw error;
    }
  },

  /**
   * Get progress data only
   * @param {string} studentId - Student identifier
   * @param {string} subject - Optional subject filter
   * @returns {Promise<{overall_progress, total_tests, completed_tests, average_score}>}
   */
  async getProgressData(studentId, subject = null) {
    try {
      let url = `${API_BASE_URL}/api/user/progress/${studentId}`;
      if (subject) {
        url += `?subject=${encodeURIComponent(subject)}`;
      }
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Progress API Error: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Progress API Error:", error);
      throw error;
    }
  },

  /**
   * Log user activity for streak tracking
   * @param {string} studentId - Student identifier
   * @param {number} hours - Hours of activity (default 0.5)
   */
  async logActivity(studentId, hours = 0.5) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/user/activity/log?student_id=${studentId}&hours=${hours}`,
        { method: "POST" }
      );
      
      if (!response.ok) {
        throw new Error(`Activity Log API Error: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Activity Log API Error:", error);
      // Don't throw - activity logging shouldn't break the app
    }
  },
};

/**
 * Notes Service - User saved notes
 */
export const notesService = {
  /**
   * Get notes for a student
   * @param {string} studentId - Student identifier
   * @param {object} filters - Optional filters (class_level, subject, chapter)
   * @returns {Promise<{notes: array, total: number}>}
   */
  async getNotes(studentId, filters = {}) {
    try {
      let url = `${API_BASE_URL}/api/notes/${studentId}`;
      const params = new URLSearchParams();
      
      if (filters.class_level) params.append("class_level", filters.class_level);
      if (filters.subject) params.append("subject", filters.subject);
      if (filters.chapter) params.append("chapter", filters.chapter);
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Notes API Error: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Notes API Error:", error);
      throw error;
    }
  },

  /**
   * Create a new note
   * @param {object} noteData - Note data
   * @returns {Promise<Note>}
   */
  async createNote(noteData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/notes/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(noteData),
      });
      
      if (!response.ok) {
        throw new Error(`Create Note API Error: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Create Note API Error:", error);
      throw error;
    }
  },
};

/**
 * Utility: Check backend health
 */
export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    console.error("Backend health check failed:", error);
    return false;
  }
};

export default {
  chatService,
  assessmentService,
  userStatsService,
  notesService,
  healthCheck,
};
