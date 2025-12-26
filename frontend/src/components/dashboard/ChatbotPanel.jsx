import { useState, useRef, useEffect } from "react";
import { 
  X, 
  Send, 
  Plus, 
  Clock, 
  BookOpen, 
  GraduationCap,
  ChevronLeft,
  Settings,
  Sparkles,
  Zap,
  Brain
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import Spline from '@splinetool/react-spline';
import useUserStore from "../../stores/userStore";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { ScrollArea } from "../ui/scroll-area";
import { chatService, userStatsService } from "../../services/api";

/**
 * ChatbotPanel Component
 * 
 * Full-featured AI chatbot interface with history sidebar.
 * Backend connected via chatService.studentChat()
 */

export default function ChatbotPanel({ isOpen, onClose }) {
  const { user } = useUserStore();
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatMode, setChatMode] = useState("quick"); // "quick" or "deepdive"
  const messagesEndRef = useRef(null);

  // Dummy chat history - TODO: Fetch from API
  const chatHistory = [
    { id: 1, title: "Research Assistance Request", date: "Today" },
    { id: 2, title: "Summarizing Last Chapter", date: "Today" },
    { id: 3, title: "Math Problem Help", date: "Yesterday" },
    { id: 4, title: "Science Notes Review", date: "Yesterday" },
  ];

  const starterCards = [
    {
      id: 1,
      icon: BookOpen,
      title: "Preview test and learn",
      description: "Get a quick review of key concepts before your test"
    },
    {
      id: 2,
      icon: GraduationCap,
      title: "Help me with exam tomorrow",
      description: "Prepare for your upcoming exam with focused study"
    }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getAvatarUrl = () => {
    if (user.avatarSeed && user.avatarStyle) {
      return `https://api.dicebear.com/7.x/${user.avatarStyle}/svg?seed=${user.avatarSeed}`;
    }
    return `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.id || 'default'}`;
  };

  const handleModeChange = (mode) => {
    setChatMode(mode);
    const modeMessage = {
      role: "assistant",
      content: mode === "quick" 
        ? "**Quick Mode activated!** I'll give you direct, exam-style answers from your textbook."
        : "**DeepDive Mode activated!** I'll provide comprehensive explanations covering all aspects of the topic.",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, modeMessage]);
  };

  const handleSend = async () => {
    if (!message.trim() || isLoading) return;
    
    const userMessage = { 
      role: 'user', 
      content: message,
      timestamp: new Date()
    };
    setMessages([...messages, userMessage]);
    setMessage("");
    setIsLoading(true);

    try {
      // Use Mathematics as default since that's what we have in the backend
      const effectiveSubject = user.preferredSubject || "Mathematics";
      
      console.log("🚀 Sending chat request:", {
        question: userMessage.content,
        classLevel: user.classLevel || 6,
        subject: effectiveSubject,
        mode: chatMode
      });
      
      // Call backend API
      const result = await chatService.studentChat(
        userMessage.content,
        user.classLevel || 6,
        effectiveSubject,
        1, // Default lesson number
        chatMode
      );

      const assistantMessage = {
        role: "assistant",
        content: result.answer,
        timestamp: new Date(),
        sources: result.sources,
        mode: chatMode,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      
      // Log activity for streak tracking
      const studentId = user.id || "guest";
      userStatsService.logActivity(studentId, 0.1); // 6 minutes per question
      
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage = {
        role: "assistant",
        content: "Sorry, I couldn't process that. Please try again.",
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStarterClick = (title) => {
    setMessage(title);
  };

  const handleNewChat = () => {
    setMessages([]);
  };

  const renderMessageContent = (content) => {
    return (
      <div className="prose prose-sm max-w-none
        [&_strong]:font-bold [&_strong]:text-gray-900
        [&_em]:italic
        [&_p]:my-2
        [&_ul]:list-disc [&_ul]:ml-5 [&_ul]:my-2
        [&_ol]:list-decimal [&_ol]:ml-5 [&_ol]:my-2
        [&_li]:my-1
        [&_h3]:font-bold [&_h3]:text-base [&_h3]:my-2
        [&_h2]:font-bold [&_h2]:text-lg [&_h2]:my-2
        [&_h1]:font-bold [&_h1]:text-xl [&_h1]:my-2
      ">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/20"
        onClick={onClose}
      />
      
      {/* Panel - Full Screen */}
      <div className="relative flex h-full w-full bg-white">
        {/* Left Sidebar - History */}
        <div className="w-64 border-r border-gray-200 flex flex-col bg-gray-50">
          {/* Profile Section */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <img
                src={getAvatarUrl()}
                alt="Avatar"
                className="w-10 h-10 rounded-full bg-gray-200"
              />
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-900 truncate">
                  {user.name || 'Student'}
                </p>
                <p className="text-xs text-gray-500">Class {user.classLevel}</p>
              </div>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <ChevronLeft className="w-4 h-4 text-gray-500" />
              </button>
            </div>
          </div>

          {/* New Chat Button */}
          <div className="p-3">
            <Button
              variant="outline"
              className="w-full justify-start gap-2 text-gray-700"
              onClick={handleNewChat}
            >
              <Plus className="w-4 h-4" />
              New Chat
            </Button>
          </div>

          {/* Chat History */}
          

          {/* Bottom Settings */}
          <div className="p-3 border-t border-gray-200">
            <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-200 transition-colors">
              <Settings className="w-4 h-4" />
              Settings
            </button>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Header with Mode Toggle */}
          <div className="h-14 border-b border-gray-200 flex items-center justify-between px-6">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-gray-800" />
              <span className="font-semibold text-gray-800">AI Study Assistant</span>
              <span className="text-xs text-gray-400 ml-2">
                {chatMode === "quick" ? "Quick Mode" : "DeepDive Mode"}
              </span>
            </div>
            
            {/* Mode Toggle */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleModeChange("quick")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  chatMode === "quick"
                    ? "bg-gray-900 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                <Zap className="w-3.5 h-3.5" />
                Quick
              </button>
              <button
                onClick={() => handleModeChange("deepdive")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  chatMode === "deepdive"
                    ? "bg-gray-900 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                <Brain className="w-3.5 h-3.5" />
                DeepDive
              </button>
              
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors ml-4"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
          </div>

          {/* Chat Content */}
          <ScrollArea className="flex-1 p-6">
            {messages.length === 0 ? (
              /* Welcome State with Spline 3D Animation */
              <div className="flex flex-col items-center justify-center h-full max-w-2xl mx-auto">
                {/* Spline 3D Animation Container */}
                <div className="spline-container w-full h-[400px] rounded-2xl overflow-hidden mb-6 relative">
                  <Spline
                    scene="https://prod.spline.design/hHmZKO2t5979mD-2/scene.splinecode"
                    onLoad={() => console.log('Spline scene loaded')}
                    style={{ width: '100%', height: '100%' }}
                  />
                </div>
                
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    Hi, {user.name || 'Student'}!
                  </h2>
                  <p className="text-gray-500">
                    Ask me anything about your studies
                  </p>
                </div>
              </div>
            ) : (
              /* Messages */
              <div className="space-y-4 max-w-2xl mx-auto">
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}
                  >
                    {msg.role === 'assistant' && (
                      <div className="w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center flex-shrink-0">
                        <Sparkles className="w-4 h-4 text-white" />
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] px-4 py-3 rounded-2xl ${
                        msg.role === 'user'
                          ? 'bg-gray-900 text-white'
                          : msg.isError
                          ? 'bg-red-50 text-red-800 border border-red-200'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      <div className="text-sm leading-relaxed whitespace-pre-wrap">
                        {msg.role === 'assistant' 
                          ? renderMessageContent(msg.content)
                          : msg.content
                        }
                      </div>
                      <div className={`text-xs mt-2 ${
                        msg.role === 'user' ? 'text-gray-400' : 'text-gray-500'
                      }`}>
                        {new Date(msg.timestamp).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </div>
                    </div>
                    {msg.role === 'user' && (
                      <img
                        src={getAvatarUrl()}
                        alt="You"
                        className="w-8 h-8 rounded-full bg-gray-200 flex-shrink-0"
                      />
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center flex-shrink-0">
                      <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-gray-100 rounded-2xl px-4 py-3">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </ScrollArea>

          {/* Input Area */}
          <div className="p-4 border-t border-gray-200">
            <div className="max-w-2xl mx-auto flex gap-3">
              <div className="flex-1 relative">
                <Input
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                  placeholder={
                    chatMode === "quick"
                      ? "Ask a direct question..."
                      : "Ask anything for deep explanation..."
                  }
                  className="h-12 pl-4 pr-12 rounded-xl border-gray-200 focus:border-gray-400 focus:ring-gray-400"
                  disabled={isLoading}
                />
                <button
                  onClick={handleSend}
                  disabled={!message.trim() || isLoading}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-gray-900 text-white disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-gray-800 transition-colors"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
