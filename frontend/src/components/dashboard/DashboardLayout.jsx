import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { 
  BookOpen, 
  MessageCircle, 
  FileText, 
  BarChart3, 
  User, 
  Settings, 
  LogOut,
  Menu,
  X
} from "lucide-react";
import useUserStore from "../../stores/userStore";
import ChatbotPanel from "./ChatbotPanel";

/**
 * DashboardLayout Component
 * 
 * Main layout with colorful sidebar navigation.
 * 
 * TODO: Backend Integration
 * - Fetch unread notifications count
 * - Sync user preferences
 */

const navItems = [
  { 
    id: "dashboard", 
    label: "Dashboard", 
    icon: BarChart3, 
    path: "/dashboard",
    color: "#ffc801" // Yellow
  },
  { 
    id: "book-to-bot", 
    label: "Book to Bot", 
    icon: BookOpen, 
    path: "/book-to-bot",
    color: "#f928a9" // Pink
  },
  { 
    id: "test", 
    label: "Test", 
    icon: FileText, 
    path: "/test",
    color: "#b4ff06" // Lime
  },
  { 
    id: "report-card", 
    label: "Report Card", 
    icon: BarChart3, 
    path: "/report-card",
    color: "#00d9ff" // Cyan
  },
  { 
    id: "about-you", 
    label: "Settings", 
    icon: User, 
    path: "/about-you",
    color: "#ef4444" // Red
  },
];

export default function DashboardLayout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useUserStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [chatbotOpen, setChatbotOpen] = useState(false);

  const getAvatarUrl = () => {
    if (user.avatarSeed && user.avatarStyle) {
      return `https://api.dicebear.com/7.x/${user.avatarStyle}/svg?seed=${user.avatarSeed}`;
    }
    return `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.id || 'default'}`;
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleNavClick = (path) => {
    navigate(path);
  };

  const isActive = (path) => location.pathname === path;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <aside 
        className={`flex-shrink-0 transition-all duration-300 bg-white border-r border-gray-200 flex flex-col ${
          sidebarOpen ? "w-64" : "w-20"
        }`}
      >
        {/* Logo */}
        <div className="p-4 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-red-500 flex items-center justify-center">
              <span className="text-white font-bold text-lg">B</span>
            </div>
            {sidebarOpen && (
              <span 
                className="font-bold text-lg text-gray-800"
                style={{ fontFamily: "'Space Grotesk', sans-serif" }}
              >
                Brainwave
              </span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.path)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  active 
                    ? "text-white shadow-lg" 
                    : "text-gray-600 hover:bg-gray-100"
                }`}
                style={active ? { backgroundColor: item.color } : {}}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {sidebarOpen && (
                  <span className="font-medium">{item.label}</span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Chatbot Button */}
        <div className="p-3">
          <button
            onClick={() => setChatbotOpen(true)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-gray-900 text-white transition-all duration-200 hover:bg-gray-800"
          >
            <MessageCircle className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && (
              <span className="font-medium">AI Chatbot</span>
            )}
          </button>
        </div>

        {/* User Section */}
        <div className="p-3 border-t border-gray-100">
          <div className="flex items-center gap-3 px-3 py-2">
            <img
              src={getAvatarUrl()}
              alt="Avatar"
              className="w-10 h-10 rounded-full bg-gray-200"
            />
            {sidebarOpen && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate">
                  {user.name || 'Student'}
                </p>
                <p className="text-xs text-gray-500">Class {user.classLevel}</p>
              </div>
            )}
          </div>
          
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => navigate('/about-you')}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
            >
              <Settings className="w-4 h-4" />
              {sidebarOpen && <span className="text-sm">Settings</span>}
            </button>
            <button
              onClick={handleLogout}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-red-500 hover:bg-red-50 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              {sidebarOpen && <span className="text-sm">Logout</span>}
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-6 gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          
          <div className="flex-1">
            <h1 className="text-xl font-semibold text-gray-800">
              {navItems.find(item => isActive(item.path))?.label || 'Dashboard'}
            </h1>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto p-6">
          {children}
        </div>
      </main>

      {/* Chatbot Panel */}
      <ChatbotPanel 
        isOpen={chatbotOpen} 
        onClose={() => setChatbotOpen(false)} 
      />
    </div>
  );
}
