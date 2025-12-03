import { useState, useEffect } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";
import { Button } from "../../components/ui/button";
import {
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  History,
  Eye,
  EyeOff,
} from "lucide-react";
import useAnnotationStore from "../../stores/annotationStore";
import SelectionDialog from "../annotations/SelectionDialog";
import AIPanel from "../annotations/AIPanel";
import NotesPanel from "../annotations/NotesPanel";
import HistoryPanel from "../annotations/HistoryPanel";
import HighlightOverlay from "../annotations/HighlightOverlay";
import VoiceAssessment from "../assessment/VoiceAssessment";
import StudentChatbot from "../annotations/StudentChatbot";
import { useState as ReactUseState } from "react";

/**
 * PDF Viewer Component
 *
 * Main component for displaying and interacting with PDF documents.
 * Handles text selection, zoom, navigation, and annotation creation.
 */

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export default function PDFViewer({ pdfUrl, currentLesson }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.2);
  const [dialogPosition, setDialogPosition] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [direction, setDirection] = useState("next"); // 'next' or 'prev'
  const [pagesCompleted, setPagesCompleted] = useState(0);
  const [showAssessment, setShowAssessment] = useState(false);
  const [lastAssessmentPage, setLastAssessmentPage] = useState(0);
  const [showAssessmentPrompt, setShowAssessmentPrompt] = useState(false);
  const [assessmentRange, setAssessmentRange] = useState("1-10");
  const [showAnnotations, setShowAnnotations] = useState(true);

  const setSelectedText = useAnnotationStore((state) => state.setSelectedText);
  const activePanel = useAnnotationStore((state) => state.activePanel);
  const setActivePanel = useAnnotationStore((state) => state.setActivePanel);

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
  }

  // Keyboard navigation for natural book reading
  useEffect(() => {
    const handleKeyPress = (e) => {
      // Prevent navigation when typing in inputs
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") {
        return;
      }

      switch (e.key) {
        case "ArrowRight":
        case " ": // Spacebar
        case "PageDown":
          e.preventDefault();
          goToNextPage();
          break;
        case "ArrowLeft":
        case "PageUp":
          e.preventDefault();
          goToPrevPage();
          break;
        case "Home":
          e.preventDefault();
          setDirection("prev");
          setPageNumber(1);
          break;
        case "End":
          e.preventDefault();
          setDirection("next");
          setPageNumber(numPages);
          break;
      }
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [pageNumber, numPages, isTransitioning]);

  const handleTextSelection = (e) => {
    const selection = window.getSelection();
    const text = selection?.toString().trim();

    if (text && text.length > 0) {
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();

      // Get PDF container position for accurate positioning
      const pdfContainer = e.currentTarget.querySelector(".react-pdf__Page");
      const containerRect = pdfContainer?.getBoundingClientRect() || rect;

      // Calculate position relative to PDF page
      const relativeX = rect.left - containerRect.left + rect.width / 2;
      const relativeY = rect.top - containerRect.top + rect.height / 2;

      // Store selected text and position
      setSelectedText({
        text,
        position: {
          x: relativeX,
          y: relativeY,
        },
      });

      // Show selection dialog at absolute screen position
      setDialogPosition({
        x: rect.left + rect.width / 2,
        y: rect.top,
      });
    } else {
      setDialogPosition(null);
    }
  };

  const goToPrevPage = () => {
    if (pageNumber <= 1 || isTransitioning) return;
    setDirection("prev");
    setIsTransitioning(true);
    setTimeout(() => {
      setPageNumber((prev) => Math.max(prev - 1, 1));
      setTimeout(() => setIsTransitioning(false), 100);
    }, 300);
  };

  const goToNextPage = () => {
    if (pageNumber >= numPages || isTransitioning) return;
    setDirection("next");
    setIsTransitioning(true);
    setTimeout(() => {
      setPageNumber((prev) => {
        const nextPage = Math.min(prev + 1, numPages);
        // Track page completion
        if (nextPage > pagesCompleted) {
          setPagesCompleted(nextPage);

          // ✅ Change: Show a prompt after completing each 10 pages (10, 20, 30, ...)
          if (prev % 10 === 0 && prev !== 0 && prev !== lastAssessmentPage) {
            const start = prev - 9;
            const end = prev;
            setAssessmentRange(`${start}-${end}`);
            setShowAssessmentPrompt(true); // non-blocking notification
            setLastAssessmentPage(prev);
          }
        }
        return nextPage;
      });
      setTimeout(() => setIsTransitioning(false), 100);
    }, 300);
  };

  const zoomIn = () => {
    setScale((prev) => Math.min(prev + 0.2, 3));
  };

  const zoomOut = () => {
    setScale((prev) => Math.max(prev - 0.2, 0.5));
  };

  const handleAIClick = () => {
    setDialogPosition(null);
    setActivePanel("ai");
  };

  const handleNoteClick = () => {
    setDialogPosition(null);
    setActivePanel("note");
  };

  const handleClosePanel = () => {
    setActivePanel(null);
    setSelectedText(null);
  };

  const handleAssessmentComplete = (score) => {
    setShowAssessment(false);
    // TODO: Save assessment score to backend
    // POST /api/assessments/scores
    // Body: { lessonId, score, completedAt: new Date().toISOString() }
    console.log("Assessment completed with score:", score);
  };

  const handleAssessmentClose = () => {
    setShowAssessment(false);
  };

  const startAssessmentNow = () => {
    setShowAssessmentPrompt(false);
    setShowAssessment(true);
  };

  const dismissAssessmentPrompt = () => setShowAssessmentPrompt(false);

  return (
    <div className="flex flex-col h-full relative ">
      {/* Voice Assessment Modal */}
      {showAssessment && (
        <VoiceAssessment
          currentLesson={currentLesson}
          pageRange={assessmentRange}
          onComplete={handleAssessmentComplete}
          onClose={handleAssessmentClose}
        />
      )}

      {/* 10-page completion prompt */}
      {showAssessmentPrompt && (
        <div className="fixed bottom-4 right-4 z-40 max-w-sm w-full bg-card border rounded-lg shadow-lg p-4">
          <div className="text-sm font-medium mb-1">Completed {assessmentRange} pages</div>
          <div className="text-xs text-muted-foreground mb-3">
            You can attend a quick test for these pages now.
          </div>
          <div className="flex gap-2 justify-end">
            <Button variant="outline" size="sm" onClick={dismissAssessmentPrompt}>Later</Button>
            <Button size="sm" onClick={startAssessmentNow}>Start Test</Button>
          </div>
        </div>
      )}

      {/* Selection Dialog */}
      {/* Selection Dialog */}
      <SelectionDialog
        position={dialogPosition}
        onAI={handleAIClick}
        onNote={handleNoteClick}
      />

      {/* Panels */}
      <AIPanel
        open={activePanel === "ai"}
        onClose={handleClosePanel}
        currentLesson={currentLesson}
        pageNumber={pageNumber}
      />
      <NotesPanel
        open={activePanel === "note"}
        onClose={handleClosePanel}
        currentLesson={currentLesson}
        pageNumber={pageNumber}
      />
      <HistoryPanel
        open={showHistory || activePanel === "history"}
        onClose={() => {
          setShowHistory(false);
          setActivePanel(null);
        }}
        currentLesson={currentLesson}
      />

      {/* PDF Controls */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-card">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={goToPrevPage}
            disabled={pageNumber <= 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm font-medium min-w-[100px] text-center">
            Page {pageNumber} of {numPages || "--"}
          </span>
          <Button
            variant="outline"
            size="icon"
            onClick={goToNextPage}
            disabled={pageNumber >= numPages}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setShowAnnotations(!showAnnotations)}
            title={showAnnotations ? "Hide annotations" : "Show annotations"}
          >
            {showAnnotations ? (
              <Eye className="h-4 w-4" />
            ) : (
              <EyeOff className="h-4 w-4" />
            )}
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowHistory(true)}
            className="mr-4"
          >
            <History className="h-4 w-4 mr-2" />
            History
          </Button>

          <Button variant="outline" size="icon" onClick={zoomOut}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm font-medium min-w-[60px] text-center">
            {Math.round(scale * 100)}%
          </span>
          <Button variant="outline" size="icon" onClick={zoomIn}>
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* PDF Content */}
      <div className="flex-1  overflow-auto bg-muted/30 p-4">
        <div
          className="flex justify-center relative"
          onMouseUp={handleTextSelection}
        >
          <div
            className={`relative transition-all duration-500 ease-out  ${
              isTransitioning
                ? direction === "next"
                  ? "page-turn-next"
                  : "page-turn-prev"
                : "page-turn-idle"
            }`}
            style={{
              transformStyle: "preserve-3d",
              perspective: "1000px",
            }}
          >
            <Document
              file={pdfUrl}
              className=" page page-turn"
              onLoadSuccess={onDocumentLoadSuccess}
              loading={
                <div className="flex items-center justify-center h-[600px]">
                  <div className="text-muted-foreground">Loading PDF...</div>
                </div>
              }
              error={
                <div className="flex items-center justify-center h-[600px]">
                  <div className="text-destructive">Failed to load PDF</div>
                </div>
              }
            >
              <Page
                pageNumber={pageNumber}
                scale={scale}
                className="shadow-2xl rounded-lg overflow-hidden"
                renderTextLayer={true}
                renderAnnotationLayer={true}
              />
            </Document>

            {/* Highlight Overlay */}
            {showAnnotations && (
              <HighlightOverlay
                pageNumber={pageNumber}
                scale={scale}
                currentLesson={currentLesson}
              />
            )}
          </div>
        </div>
      </div>

      {/* Student Chatbot - Floating on bottom right */}
      <StudentChatbot currentLesson={currentLesson} />
    </div>
  );
}
