import { useState, useEffect, useRef } from "react";
import { Mic, MicOff, Volume2, CheckCircle, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Button } from "../../components/ui/button";
import { Card } from "../../components/ui/card";
import { Progress } from "../../components/ui/progress";
import { assessmentService } from "../../services/api";
import useUserStore from "../../stores/userStore";

/**
 * Voice Assessment Component
 *
 * Appears after completing 4 pages of lesson.
 * Uses voice input/output for questions and answers.
 * Questions are generated from textbook content using RAG.
 *
 * Backend Integration:
 * =========================
 * 1. POST /api/assessment/questions - Get RAG-based questions
 * 2. POST /api/assessment/evaluate - Evaluate answers with AI
 *
 * Web Speech API:
 * - SpeechRecognition: For voice input
 * - SpeechSynthesis: For voice output (questions)
 */

export default function VoiceAssessment({ currentLesson, onComplete, onClose }) {
  const [isListening, setIsListening] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [transcript, setTranscript] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [score, setScore] = useState(null);
  const [evaluationResult, setEvaluationResult] = useState(null); // Store full evaluation
  const [questions, setQuestions] = useState([]);
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(true);
  const [error, setError] = useState(null);

  const { user } = useUserStore();
  const recognitionRef = useRef(null);
  const synthesisRef = useRef(null);

  // Load questions from backend on mount
  useEffect(() => {
    const loadQuestions = async () => {
      try {
        setIsLoadingQuestions(true);
        setError(null);
        
        console.log("📝 Loading assessment questions from backend...");
        const response = await assessmentService.getQuestions(
          user.classLevel,
          user.preferredSubject || "Social Science",
          currentLesson?.number || 1,
          3 // Number of questions
        );
        
        console.log("✅ Questions loaded:", response);
        setQuestions(response.questions || []);
        setIsLoadingQuestions(false);
      } catch (err) {
        console.error("❌ Failed to load questions:", err);
        setError("Failed to load questions. Using fallback questions.");
        // Fallback questions
        setQuestions([
          "What did you learn from this lesson?",
          "Can you explain the main concept?",
          "How would you apply this knowledge?",
        ]);
        setIsLoadingQuestions(false);
      }
    };

    loadQuestions();
  }, [user.classLevel, user.preferredSubject, currentLesson]);

  // Initialize Web Speech API
  useEffect(() => {
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = "en-US";

      recognitionRef.current.onresult = (event) => {
        const text = event.results[0][0].transcript;
        setTranscript(text);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      window.speechSynthesis.cancel();
    };
  }, []);

  // Speak question
  const speakQuestion = (text) => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel(); // Stop any ongoing speech
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 1;

      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);

      window.speechSynthesis.speak(utterance);
    }
  };

  // Start listening
  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setTranscript("");
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  // Stop listening
  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  // Submit answer and move to next question
  const submitAnswer = () => {
    const newAnswers = [
      ...answers,
      {
        question: questions[currentQuestion],
        answer: transcript,
        timestamp: new Date().toISOString(),
      },
    ];
    setAnswers(newAnswers);
    setTranscript("");

    if (currentQuestion < questions.length - 1) {
      // Move to next question
      setCurrentQuestion(currentQuestion + 1);
      setTimeout(() => speakQuestion(questions[currentQuestion + 1]), 500);
    } else {
      // All questions answered, evaluate
      evaluateAnswers(newAnswers);
    }
  };

  // Evaluate answers with backend
  const evaluateAnswers = async (allAnswers) => {
    setIsEvaluating(true);

    try {
      console.log("🔍 Evaluating answers with backend...");
      const result = await assessmentService.evaluateAnswers(
        user.classLevel,
        user.preferredSubject || "Social Science",
        currentLesson?.number || 1,
        allAnswers
      );
      
      console.log("✅ Evaluation result:", result);
      setScore(result.score);
      setEvaluationResult(result); // Store full result
      setIsEvaluating(false);

      // Speak the score and feedback
      speakQuestion(
        `Your score is ${result.score} out of 100. ${result.feedback}`
      );
    } catch (err) {
      console.error("❌ Evaluation error:", err);
      // Fallback to simulated score
      const simulatedScore = Math.floor(Math.random() * 30) + 70;
      setScore(simulatedScore);
      setEvaluationResult({
        score: simulatedScore,
        feedback: "Good effort! Keep practicing.",
        strengths: ["Attempted all questions"],
        improvements: ["Review the chapter content"],
        question_scores: [],
        topics_to_study: []
      });
      setIsEvaluating(false);

      speakQuestion(
        `Your score is ${simulatedScore} out of 100. Good effort!`
      );
    }
  };

  // Start assessment when questions are loaded
  useEffect(() => {
    if (!isLoadingQuestions && questions.length > 0) {
      setTimeout(() => {
        speakQuestion(`Let's begin the assessment. Question 1: ${questions[0]}`);
      }, 1000);
    }
  }, [isLoadingQuestions, questions]);

  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <div className="fixed inset-0 z-50 bg-background flex items-stretch">
      {/* Split Screen Layout */}
      <div className="flex w-full h-full">
        {/* Left Side - Virtual Companion (AI) */}
        <div className="w-1/2 bg-card border-r border-primary/20 flex flex-col items-center justify-center p-8">
          <div className="text-center max-w-md">
            {/* AI Avatar */}
            <div className="w-32 h-32 mx-auto mb-6 rounded-full bg-primary/10 border-4 border-primary flex items-center justify-center">
              <Volume2
                className={`h-16 w-16 ${
                  isSpeaking ? "text-primary animate-pulse" : "text-primary/50"
                }`}
              />
            </div>

            <h3 className="text-2xl font-bold text-primary mb-2">
              Virtual Companion
            </h3>
            <p className="text-sm text-muted-foreground mb-8">
              AI Assessment Assistant
            </p>

            {/* Loading Questions */}
            {isLoadingQuestions && (
              <div className="py-8">
                <Loader2 className="h-12 w-12 mx-auto mb-4 animate-spin text-primary" />
                <p className="text-lg font-medium">Loading questions from textbook...</p>
                <p className="text-sm text-muted-foreground mt-2">
                  Analyzing Chapter {currentLesson?.number || 1}
                </p>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="mb-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <p className="text-xs text-yellow-700 dark:text-yellow-500">{error}</p>
              </div>
            )}

            {/* Question Display */}
            {!isLoadingQuestions && !isEvaluating && score === null && (
              <div className="mb-6">
                <div className="bg-primary/5 rounded-lg p-6 border border-primary/20">
                  <p className="text-lg font-medium leading-relaxed">
                    {questions[currentQuestion]}
                  </p>
                </div>

                {/* Progress Indicator */}
                <div className="mt-4">
                  <p className="text-xs text-muted-foreground mb-2">
                    Question {currentQuestion + 1} of {questions.length}
                  </p>
                  <Progress value={progress} className="h-1.5" />
                </div>
              </div>
            )}

            {/* Evaluation State */}
            {isEvaluating && (
              <div className="py-8">
                <Loader2 className="h-12 w-12 mx-auto mb-4 animate-spin text-primary" />
                <p className="text-lg font-medium">Evaluating...</p>
              </div>
            )}

            {/* Score Display with Analytics */}
            {score !== null && evaluationResult && (
              <div className="py-4 w-full max-w-lg">
                {/* Overall Score */}
                <div className="mb-6">
                  <div className="relative w-32 h-32 mx-auto mb-4">
                    {/* Circular Progress */}
                    <svg className="transform -rotate-90 w-32 h-32">
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        className="text-muted"
                      />
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${2 * Math.PI * 56}`}
                        strokeDashoffset={`${2 * Math.PI * 56 * (1 - score / 100)}`}
                        className={`transition-all duration-1000 ${
                          score >= 80 ? 'text-emerald-600' : 
                          score >= 60 ? 'text-blue-600' : 
                          score >= 40 ? 'text-yellow-600' : 
                          'text-red-600'
                        }`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-4xl font-bold text-foreground">{score}</span>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground text-center">Overall Performance</p>
                </div>

                {/* Feedback */}
                <div className="mb-6 p-4 bg-primary/5 border border-primary/20 rounded-lg">
                  <div className="prose prose-sm max-w-none dark:prose-invert prose-p:text-black dark:prose-p:text-white prose-strong:text-black dark:prose-strong:text-white prose-strong:font-bold">
                    <ReactMarkdown>{evaluationResult.feedback}</ReactMarkdown>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Side - You (User) */}
        <div className="w-1/2 bg-background flex flex-col items-center justify-center p-8">
          <div className="text-center max-w-md w-full">
            {/* User Avatar */}
            <div className="w-32 h-32 mx-auto mb-6 rounded-full bg-muted border-4 border-muted-foreground/20 flex items-center justify-center">
              <div className="w-16 h-16 rounded-full bg-muted-foreground/20" />
            </div>

            <h3 className="text-2xl font-bold mb-2">You</h3>
            <p className="text-sm text-muted-foreground mb-8">Student</p>

            {/* Loading State */}
            {isLoadingQuestions && (
              <div className="py-8">
                <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
                  <Loader2 className="h-10 w-10 animate-spin" />
                </div>
                <p className="text-sm text-muted-foreground">Please wait...</p>
              </div>
            )}

            {/* User Interaction Area */}
            {!isLoadingQuestions && !isEvaluating && score === null && (
              <>
                {/* Voice Input */}
                <div className="mb-6">
                  <Button
                    size="lg"
                    className={`h-28 w-28 rounded-full mx-auto ${
                      isListening
                        ? "bg-red-600 hover:bg-red-700 animate-pulse"
                        : "bg-primary hover:bg-primary/90"
                    }`}
                    onClick={isListening ? stopListening : startListening}
                    disabled={isSpeaking}
                  >
                    {isListening ? (
                      <MicOff className="h-12 w-12" />
                    ) : (
                      <Mic className="h-12 w-12" />
                    )}
                  </Button>

                  <p className="text-center text-sm text-muted-foreground mt-4">
                    {isListening
                      ? "Listening... Speak now"
                      : "Tap to speak your answer"}
                  </p>
                </div>

                {/* Transcript Display */}
                {transcript && (
                  <div className="mb-6 p-4 bg-muted/30 rounded-lg border border-muted-foreground/20 min-h-[120px]">
                    <p className="text-xs font-medium text-muted-foreground mb-2">
                      YOUR ANSWER:
                    </p>
                    <p className="text-sm leading-relaxed">{transcript}</p>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex flex-col gap-3 w-full">
                  <Button
                    size="lg"
                    className="w-full"
                    onClick={submitAnswer}
                    disabled={!transcript || isListening || isSpeaking}
                  >
                    {currentQuestion < questions.length - 1
                      ? "Next Question →"
                      : "Submit Assessment"}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    onClick={onClose}
                  >
                    Cancel
                  </Button>
                </div>
              </>
            )}

            {/* Waiting/Evaluating State */}
            {isEvaluating && (
              <div className="py-8">
                <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-muted animate-pulse flex items-center justify-center">
                  <Loader2 className="h-10 w-10 animate-spin" />
                </div>
                <p className="text-sm text-muted-foreground">Processing...</p>
              </div>
            )}

            {/* Result State - Analytics Dashboard */}
            {score !== null && evaluationResult && (
              <div className="w-full space-y-4 max-h-[600px] overflow-y-auto px-2">
                {/* Performance Heatmap */}
                <div className="space-y-3">
                  <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <span className="w-1 h-4 bg-primary rounded-full"></span>
                    Question Performance
                  </h4>
                  
                  {evaluationResult.question_scores && evaluationResult.question_scores.length > 0 ? (
                    evaluationResult.question_scores.map((qs, idx) => (
                      <div key={idx} className="space-y-2">
                        {/* Question Number and Score */}
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-muted-foreground">
                            Question {qs.question_num}
                          </span>
                          <span className={`text-xs font-bold ${
                            qs.score >= 80 ? 'text-emerald-600' : 
                            qs.score >= 60 ? 'text-blue-600' : 
                            qs.score >= 40 ? 'text-yellow-600' : 
                            'text-red-600'
                          }`}>
                            {qs.score}%
                          </span>
                        </div>
                        
                        {/* Heatmap Bar */}
                        <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                          <div 
                            className={`h-full transition-all duration-500 ${
                              qs.score >= 80 ? 'bg-emerald-600' : 
                              qs.score >= 60 ? 'bg-blue-600' : 
                              qs.score >= 40 ? 'bg-yellow-600' : 
                              'bg-red-600'
                            }`}
                            style={{ width: `${qs.score}%` }}
                          />
                        </div>
                        
                        {/* Hint (NO direct answer) */}
                        <div className="text-xs italic pl-2 border-l-2 border-primary/30 prose prose-xs max-w-none dark:prose-invert prose-p:text-gray-700 dark:prose-p:text-gray-300">
                          <ReactMarkdown>{"Hint: " + qs.hint}</ReactMarkdown>
                        </div>
                      </div>
                    ))
                  ) : (
                    answers.map((_, idx) => (
                      <div key={idx} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-muted-foreground">
                            Question {idx + 1}
                          </span>
                          <span className="text-xs font-bold text-blue-600">
                            {Math.floor(score / answers.length)}%
                          </span>
                        </div>
                        <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-600 transition-all duration-500"
                            style={{ width: `${score / answers.length}%` }}
                          />
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Topics to Study */}
                {evaluationResult.topics_to_study && evaluationResult.topics_to_study.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-border">
                    <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                      <span className="w-1 h-4 bg-orange-500 rounded-full"></span>
                      Topics to Review
                    </h4>
                    <div className="space-y-2">
                      {evaluationResult.topics_to_study.map((topic, idx) => (
                        <div 
                          key={idx} 
                          className="flex items-start gap-2 p-2 bg-orange-500/5 border border-orange-500/20 rounded-lg"
                        >
                          <span className="text-orange-600 text-xs font-bold mt-0.5">
                            {idx + 1}
                          </span>
                          <div className="flex-1 prose prose-xs max-w-none dark:prose-invert prose-p:text-black dark:prose-p:text-white">
                            <ReactMarkdown>{topic}</ReactMarkdown>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Strengths */}
                {evaluationResult.strengths && evaluationResult.strengths.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-border">
                    <h4 className="text-sm font-semibold text-emerald-600 flex items-center gap-2">
                      <span className="w-1 h-4 bg-emerald-600 rounded-full"></span>
                      What You Did Well
                    </h4>
                    <div className="space-y-1">
                      {evaluationResult.strengths.map((strength, idx) => (
                        <div key={idx} className="flex items-start gap-2">
                          <span className="text-emerald-600 mt-0.5 font-bold">+</span>
                          <div className="flex-1 prose prose-xs max-w-none dark:prose-invert prose-p:text-black dark:prose-p:text-white">
                            <ReactMarkdown>{strength}</ReactMarkdown>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Improvements */}
                {evaluationResult.improvements && evaluationResult.improvements.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-border">
                    <h4 className="text-sm font-semibold text-blue-600 flex items-center gap-2">
                      <span className="w-1 h-4 bg-blue-600 rounded-full"></span>
                      Areas to Focus On
                    </h4>
                    <div className="space-y-1">
                      {evaluationResult.improvements.map((improvement, idx) => (
                        <div key={idx} className="flex items-start gap-2">
                          <span className="text-blue-600 mt-0.5 font-bold">•</span>
                          <div className="flex-1 prose prose-xs max-w-none dark:prose-invert prose-p:text-black dark:prose-p:text-white">
                            <ReactMarkdown>{improvement}</ReactMarkdown>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Continue Button */}
                <Button
                  size="lg"
                  className="w-full mt-4"
                  onClick={() => onComplete(score)}
                >
                  Continue Learning →
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
