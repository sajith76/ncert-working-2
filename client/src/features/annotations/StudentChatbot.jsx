import React, { useState, useRef, useEffect } from "react";
import { MessageCircle, Send, X, Sparkles, Minimize2 } from "lucide-react";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { ScrollArea } from "../../components/ui/scroll-area";
import useUserStore from "../../stores/userStore";
import { chatService } from "../../services/api";
import ReactMarkdown from "react-markdown";

/**
 * Student Chatbot - Floating chatbot for open-ended questions
 * Appears on PDF reader page, uses RAG with Pinecone
 */
export default function StudentChatbot({ currentLesson }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "👋 Hi! I'm your study assistant. Ask me anything about this chapter!",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const { user } = useUserStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isTyping) return;

    const userMessage = {
      role: "user",
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    try {
      const result = await chatService.studentChat(
        userMessage.content,
        user.classLevel || 10,
        user.preferredSubject || "Social Science",
        currentLesson?.number || 1
      );

      const assistantMessage = {
        role: "assistant",
        content: result.answer,
        timestamp: new Date(),
        sources: result.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Student chat error:", error);
      const errorMessage = {
        role: "assistant",
        content: "Sorry, I couldn't process that. Please try again.",
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 group"
        aria-label="Open student chatbot"
      >
        <div className="relative">
          {/* Pulsing ring effect */}
          <span className="absolute inset-0 rounded-full bg-violet-500 opacity-75 animate-ping"></span>
          
          {/* Main button */}
          <div className="relative flex items-center justify-center w-16 h-16 bg-gradient-to-br from-violet-600 to-purple-700 rounded-full shadow-lg transition-all duration-300 group-hover:scale-110 group-hover:shadow-xl">
            <MessageCircle className="w-8 h-8 text-white" />
            
            {/* Sparkle indicator */}
            <span className="absolute -top-1 -right-1 flex h-5 w-5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-5 w-5 bg-yellow-500">
                <Sparkles className="w-3 h-3 text-white m-auto" />
              </span>
            </span>
          </div>

          {/* Tooltip */}
          <div className="absolute bottom-full right-0 mb-2 px-3 py-1 bg-gray-900 text-white text-sm rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
            Ask me anything!
            <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
          </div>
        </div>
      </button>
    );
  }

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 bg-white rounded-2xl shadow-2xl border border-gray-200 transition-all duration-300 ${
        isMinimized ? "w-80 h-16" : "w-96 h-[600px]"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-violet-600 to-purple-700 rounded-t-2xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
            <MessageCircle className="w-6 h-6 text-white" />
          </div>
          <div className="text-white">
            <h3 className="font-semibold text-sm">Study Assistant</h3>
            <p className="text-xs text-white/80">Always here to help</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsMinimized(!isMinimized)}
            className="h-8 w-8 text-white hover:bg-white/20"
          >
            <Minimize2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsOpen(false)}
            className="h-8 w-8 text-white hover:bg-white/20"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Messages */}
          <ScrollArea className="h-[calc(100%-8rem)] p-4">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.role === "user"
                        ? "bg-violet-600 text-white"
                        : message.isError
                        ? "bg-red-50 text-red-800 border border-red-200"
                        : "bg-gray-100 text-gray-900"
                    }`}
                  >
                    <div className="text-sm leading-relaxed">
                      {message.role === "assistant" ? (
                        <ReactMarkdown
                          className="prose prose-sm max-w-none
                          [&_p]:my-1
                          [&_ul]:my-2 [&_ul]:ml-4
                          [&_li]:list-disc
                          [&_strong]:font-semibold
                          [&_code]:bg-gray-200 [&_code]:px-1 [&_code]:rounded"
                        >
                          {message.content}
                        </ReactMarkdown>
                      ) : (
                        message.content
                      )}
                    </div>
                    <div
                      className={`text-xs mt-1 ${
                        message.role === "user"
                          ? "text-violet-200"
                          : "text-gray-500"
                      }`}
                    >
                      {new Date(message.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </div>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-2xl px-4 py-3">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></span>
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Input */}
          <div className="absolute bottom-0 left-0 right-0 p-4 bg-white border-t rounded-b-2xl">
            <div className="flex gap-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask anything about this chapter..."
                disabled={isTyping}
                className="flex-1 rounded-full"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isTyping}
                size="icon"
                className="rounded-full bg-violet-600 hover:bg-violet-700"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
