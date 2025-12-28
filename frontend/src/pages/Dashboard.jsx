import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useUserStore from "../stores/userStore";
import DashboardLayout from "../components/dashboard/DashboardLayout";
import ProgressCard from "../components/dashboard/ProgressCard";
import StreakCard from "../components/dashboard/StreakCard";
import QuoteCard from "../components/dashboard/QuoteCard";
import SupportCard from "../components/dashboard/SupportCard";
import NotesDeckCard from "../components/dashboard/NotesDeckCard";
import StickyNotesCard from "../components/dashboard/StickyNotesCard";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Dashboard Page
 * 
 * Main dashboard hub with all feature cards.
 */

export default function Dashboard() {
  const navigate = useNavigate();
  const { user } = useUserStore();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    fetchNotifications();
  }, [user.id]);

  const fetchNotifications = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/support-tickets/notifications/user/${user.id}`);
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      }
    } catch (err) {
      console.error("Failed to fetch notifications:", err);
    }
  };

  const markNotificationRead = async (notificationId) => {
    try {
      await fetch(`${API_BASE}/api/support-tickets/notifications/${notificationId}/mark-read`, {
        method: "POST"
      });
      fetchNotifications();
    } catch (err) {
      console.error("Failed to mark notification as read:", err);
    }
  };

  // Get greeting based on time of day
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 17) return "Good Afternoon";
    return "Good Evening";
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Welcome Section with Notifications */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">
              {getGreeting()}, {user.name || 'Student'}! 👋
            </h1>
            <p className="text-gray-500">
              Ready to continue your learning journey?
            </p>
          </div>
          
          {/* Notification Bell */}
          <div className="relative">
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-3 bg-white rounded-full shadow-sm hover:shadow-md transition relative"
            >
              <span className="text-xl">🔔</span>
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>
            
            {/* Notifications Dropdown */}
            {showNotifications && (
              <div className="absolute right-0 top-14 w-80 bg-white rounded-2xl shadow-xl z-50 max-h-96 overflow-hidden border border-gray-100">
                <div className="p-4 border-b bg-gray-50">
                  <div className="flex justify-between items-center">
                    <h3 className="font-semibold text-gray-800">Notifications</h3>
                    <button 
                      onClick={() => { navigate("/support-tickets"); setShowNotifications(false); }}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      View All
                    </button>
                  </div>
                </div>
                <div className="max-h-72 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="p-6 text-center text-gray-500">
                      <span className="text-3xl mb-2 block">📭</span>
                      No notifications yet
                    </div>
                  ) : (
                    notifications.slice(0, 5).map(n => (
                      <div 
                        key={n.id}
                        onClick={() => {
                          markNotificationRead(n.id);
                          navigate("/support-tickets");
                          setShowNotifications(false);
                        }}
                        className={`p-4 border-b hover:bg-gray-50 cursor-pointer ${!n.is_read ? 'bg-blue-50' : ''}`}
                      >
                        <p className="text-sm font-medium text-gray-800">{n.title}</p>
                        <p className="text-xs text-gray-500 mt-1">{n.message}</p>
                        <p className="text-xs text-gray-400 mt-1">{new Date(n.created_at).toLocaleString()}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Progress & Streak */}
          <div className="lg:col-span-2 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ProgressCard />
              <StreakCard />
            </div>
            
            {/* Quote Card - Full Width */}
            <QuoteCard />
            
            {/* Notes Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <NotesDeckCard />
              <StickyNotesCard />
            </div>
          </div>

          {/* Right Column - Support */}
          <div className="space-y-6">
            <SupportCard />
            
            {/* My Tests Card */}
            <div 
              onClick={() => navigate("/my-tests")}
              className="bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl p-6 shadow-sm cursor-pointer hover:shadow-md transition"
            >
              <div className="flex items-center justify-between text-white">
                <div>
                  <h3 className="text-lg font-semibold mb-1">📝 My Tests</h3>
                  <p className="text-sm opacity-80">View and submit assigned tests</p>
                </div>
                <span className="text-3xl">→</span>
              </div>
            </div>
            
            {/* Quick Stats Card */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-gray-500">Class Level</span>
                  <span className="font-semibold text-gray-800">Class {user.classLevel}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-gray-500">All Subjects</span>
                  <span className="font-semibold text-gray-800">Access Available</span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-gray-500">Member Since</span>
                  <span className="font-semibold text-gray-800">Dec 2024</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
