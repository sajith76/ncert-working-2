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
   * UNIFIED ENDPOINT - Replaces getExplanation and getStickFlow
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
          action: action, // "define", "elaborate", or "stick_flow"
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
    // Redirect to new unified endpoint
    return this.processAnnotation(text, mode, classLevel, subject, chapter);
  },

  /**
   * @deprecated Use processAnnotation() with action="stick_flow" instead
   * Get Stick Flow visual diagram
   */
  async getStickFlow(text, classLevel, subject, chapter) {
    // Redirect to new unified endpoint
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
          mode: mode, // Pass mode to backend
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
 * For future assessment features
 */
export const assessmentService = {
  /**
   * Get enhanced assessment questions (15 questions for 10-page interval)
   * Uses cached questions from MongoDB if available
   * @param {number} classLevel - User's class level
   * @param {string} subject - Subject name
   * @param {number} chapter - Chapter number
   * @param {string} lessonName - Lesson/chapter name
   * @param {string} pageRange - Page range (e.g., "1-10")
   * @param {string} studentId - Student ID
  * @returns {Promise<{questions: Array<{question:string,type:string,difficulty:string,expected_keywords?:string[],page_range?:string}>, cached: boolean}>}
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
   * @param {number} classLevel - User's class level (5-10)
   * @param {string} subject - Subject name
   * @param {number} chapter - Chapter number
   * @param {number} numQuestions - Number of questions to generate (default: 3)
   * @returns {Promise<{questions: array}>}
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
   * @param {number} classLevel - User's class level
   * @param {string} subject - Subject name
   * @param {number} chapter - Chapter number
   * @param {array} answers - Array of {question, answer} objects
   * @returns {Promise<{score: number, feedback: string}>}
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

  /**
   * Submit voice assessment (legacy - for audio file upload)
   * @param {Blob} audioBlob - Recorded audio
   * @param {object} metadata - Assessment metadata (chapter, question, etc.)
   * @returns {Promise<object>}
   */
  async submitAssessment(audioBlob, metadata) {
    try {
      const formData = new FormData();
      formData.append("audio", audioBlob, "assessment.webm");
      formData.append("metadata", JSON.stringify(metadata));

      const response = await fetch(`${API_BASE_URL}/api/assessment`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Assessment API Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Assessment API Error:", error);
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
  healthCheck,
};
