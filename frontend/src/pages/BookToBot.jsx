import { useState, useEffect, useMemo } from "react";
import PDFViewer from "../features/pdf/PDFViewer";
import LessonNavigation from "../features/lessons/LessonNavigation";
import UserSettingsPanel from "../components/UserSettingsPanel";
import ChatbotPanel from "../components/dashboard/ChatbotPanel";
import { getLessonsBySubject, SUBJECTS_WITH_RAG } from "../constants/lessons";
import { Menu, X, Settings, MessageCircle, AlertTriangle } from "lucide-react";
import { Button } from "../components/ui/button";
import useUserStore from "../stores/userStore";

/**
 * BookToBot Component
 *
 * PDF viewer interface with lesson navigation and AI chatbot.
 * Dynamically loads lessons based on user's preferred subject.
 * AI features (chatbot, annotations) only work for subjects with RAG support.
 *
 * Currently supported subjects with AI:
 * - Mathematics (Class 5-12)
 * 
 * Other subjects available for reading only.
 */

function BookToBot() {
  const { user } = useUserStore();
  
  // Get lessons based on user's preferred subject
  const lessons = useMemo(() => {
    return getLessonsBySubject(user.preferredSubject);
  }, [user.preferredSubject]);
  
  const [currentLesson, setCurrentLesson] = useState(lessons[0]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [chatbotOpen, setChatbotOpen] = useState(false);
  
  // Check if current subject has AI/RAG support
  const hasAISupport = SUBJECTS_WITH_RAG.includes(user.preferredSubject);
  
  // Update current lesson when subject changes
  useEffect(() => {
    const newLessons = getLessonsBySubject(user.preferredSubject);
    setCurrentLesson(newLessons[0]);
  }, [user.preferredSubject]);

  const handleLessonSelect = (lesson) => {
    setCurrentLesson(lesson);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      {/* Sidebar - Lesson Navigation */}
      <div
        className={`flex-shrink-0 transition-all duration-300 ease-in-out ${
          sidebarOpen ? "w-80" : "w-0"
        } overflow-hidden border-r`}
      >
        <LessonNavigation
          lessons={lessons}
          currentLesson={currentLesson}
          onLessonSelect={handleLessonSelect}
        />
      </div>

      {/* Main Content - PDF Viewer */}
      <div className="flex-1 flex flex-col">
        {/* AI Support Warning Banner */}
        {!hasAISupport && (
          <div className="px-4 py-2 bg-amber-50 border-b border-amber-200 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-600" />
            <p className="text-sm text-amber-800">
              AI features are not available for {user.preferredSubject} yet. 
              Switch to <strong>Mathematics</strong> in Settings for full AI support.
            </p>
          </div>
        )}
        
        {/* Header */}
        <div className="px-6 py-4 border-b bg-card flex items-center gap-4">
          {/* Toggle Sidebar Button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="hover:bg-primary/10"
          >
            {sidebarOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </Button>

          <div className="flex-1">
            <h1 className="text-2xl font-bold text-primary">
              {currentLesson?.title || "Select a lesson"}
            </h1>
            {currentLesson?.description && (
              <p className="text-sm text-muted-foreground mt-1">
                {currentLesson.description}
              </p>
            )}
          </div>

          {/* User Settings & Chatbot Buttons */}
          <div className="flex items-center gap-3">
            <div className="text-right mr-2">
              <p className="text-xs text-muted-foreground">Class {user.classLevel}</p>
              <p className="text-xs font-medium">{user.preferredSubject}</p>
            </div>
            
            {/* AI Chatbot Button */}
            <Button
              variant="default"
              size="sm"
              onClick={() => setChatbotOpen(true)}
              className="bg-primary hover:bg-primary/90"
            >
              <MessageCircle className="h-4 w-4 mr-2" />
              AI Chat
            </Button>

            {/* Settings Button */}
            <Button
              variant="outline"
              size="icon"
              onClick={() => setSettingsOpen(true)}
              className="hover:bg-primary/10"
            >
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* PDF Viewer */}
        <div className="flex-1 overflow-hidden">
          <PDFViewer
            pdfUrl={currentLesson.pdfUrl}
            currentLesson={currentLesson}
          />
        </div>
      </div>

      {/* User Settings Panel */}
      <UserSettingsPanel
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />

      {/* Chatbot Panel - Backend Connected */}
      <ChatbotPanel
        isOpen={chatbotOpen}
        onClose={() => setChatbotOpen(false)}
      />
    </div>
  );
}

export default BookToBot;
