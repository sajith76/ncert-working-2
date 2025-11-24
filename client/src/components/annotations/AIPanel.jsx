import React, { useState } from "react";
import { Sparkles, Lightbulb, FileText, BookOpen, MessageSquare } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "../ui/sheet";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { ScrollArea } from "../ui/scroll-area";
import { useAnnotations } from "../../contexts/AnnotationContext";
import { chatService } from "../../services/api";

const AI_ACTIONS = [
  {
    id: "simple",
    label: "Simplify",
    icon: Lightbulb,
    description: "Make it easier to understand",
    color: "text-blue-600",
  },
  {
    id: "meaning",
    label: "Meaning",
    icon: FileText,
    description: "Get definitions and meanings",
    color: "text-purple-600",
  },
  {
    id: "example",
    label: "Examples",
    icon: BookOpen,
    description: "Provide practical examples",
    color: "text-green-600",
  },
  {
    id: "story",
    label: "Story",
    icon: MessageSquare,
    description: "Explain as a story",
    color: "text-orange-600",
  },
  {
    id: "summary",
    label: "Summary",
    icon: Sparkles,
    description: "Get a concise summary",
    color: "text-pink-600",
  },
];

export default function AIPanel({ open, onClose, currentLesson, pageNumber }) {
  const { selectedText, addAIAnnotation } = useAnnotations();
  const [selectedAction, setSelectedAction] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [response, setResponse] = useState("");
  const [error, setError] = useState(null);

  const handleActionSelect = async (action) => {
    setSelectedAction(action.id);
    setIsProcessing(true);
    setError(null);

    try {
      // Call real backend API
      const result = await chatService.getExplanation({
        class_level: 6, // Default to Class 6
        subject: "Social Science",
        chapter: currentLesson?.number || 1,
        highlight_text: selectedText?.text || "",
        mode: action.id,
      });

      setResponse(result.answer);
      setIsProcessing(false);
    } catch (err) {
      console.error("AI API Error:", err);
      setError(err.message || "Failed to get AI response");
      setIsProcessing(false);
    }
  };

  const handleSave = () => {
    if (selectedText && selectedAction) {
      addAIAnnotation({
        text: selectedText.text,
        action: selectedAction,
        response: response,
        pageNumber: pageNumber,
        position: selectedText.position,
        lessonId: currentLesson?.id,
      });

      // Reset and close
      setSelectedAction(null);
      setResponse("");
      onClose();
    }
  };

  const handleClose = () => {
    setSelectedAction(null);
    setResponse("");
    onClose();
  };

  return (
    <Sheet open={open} onOpenChange={handleClose}>
      <SheetContent
        side="right"
        onClose={handleClose}
        className="w-[500px] max-w-[90vw] overflow-y-auto"
      >
        <SheetHeader className="mb-6">
          <SheetTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-violet-600" />
            AI Assistant
          </SheetTitle>
        </SheetHeader>

        <div className="space-y-6">
          {/* Selected Text */}
          <div className="rounded-lg border bg-muted/30 p-4">
            <p className="text-xs font-medium text-muted-foreground mb-2">
              Selected Text
            </p>
            <p className="text-sm leading-relaxed">{selectedText?.text}</p>
          </div>

          {/* AI Actions */}
          {!selectedAction && (
            <div className="space-y-3">
              <p className="text-sm font-medium">What would you like to do?</p>
              <div className="grid gap-2">
                {AI_ACTIONS.map((action) => {
                  const Icon = action.icon;
                  return (
                    <Button
                      key={action.id}
                      variant="outline"
                      className="h-auto justify-start p-4"
                      onClick={() => handleActionSelect(action)}
                    >
                      <Icon className={`h-5 w-5 mr-3 ${action.color}`} />
                      <div className="text-left">
                        <div className="font-medium">{action.label}</div>
                        <div className="text-xs text-muted-foreground">
                          {action.description}
                        </div>
                      </div>
                    </Button>
                  );
                })}
              </div>
            </div>
          )}

          {/* AI Response */}
          {selectedAction && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Badge variant="ai">
                  {AI_ACTIONS.find((a) => a.id === selectedAction)?.label}
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSelectedAction(null);
                    setResponse("");
                  }}
                >
                  Change Action
                </Button>
              </div>

              <div className="min-h-[300px] max-h-[500px] overflow-y-auto rounded-lg border bg-background p-4">
                {isProcessing ? (
                  <div className="flex items-center justify-center h-full py-8">
                    <div className="text-center space-y-2">
                      <Sparkles className="h-8 w-8 animate-pulse text-violet-600 mx-auto" />
                      <p className="text-sm text-muted-foreground">
                        AI is thinking...
                      </p>
                    </div>
                  </div>
                ) : error ? (
                  <div className="text-center space-y-2 py-8">
                    <p className="text-sm text-red-600">Error: {error}</p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleActionSelect(
                        AI_ACTIONS.find((a) => a.id === selectedAction)
                      )}
                    >
                      Try Again
                    </Button>
                  </div>
                ) : (
                  <ScrollArea className="h-full">
                    <div className="pr-4">
                      <div className="prose prose-sm max-w-none dark:prose-invert prose-p:text-black dark:prose-p:text-white prose-strong:text-black dark:prose-strong:text-white prose-strong:font-bold prose-em:italic prose-li:text-black dark:prose-li:text-white">
                        <ReactMarkdown>{response}</ReactMarkdown>
                      </div>
                    </div>
                  </ScrollArea>
                )}
              </div>

              {!isProcessing && response && (
                <div className="flex gap-2">
                  <Button
                    variant="default"
                    className="flex-1 bg-violet-600 hover:bg-violet-700"
                    onClick={handleSave}
                  >
                    Save Annotation
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() =>
                      handleActionSelect(
                        AI_ACTIONS.find((a) => a.id === selectedAction)
                      )
                    }
                  >
                    Regenerate
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
