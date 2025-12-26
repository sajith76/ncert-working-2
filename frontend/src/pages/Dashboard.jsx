import useUserStore from "../stores/userStore";
import DashboardLayout from "../components/dashboard/DashboardLayout";
import ProgressCard from "../components/dashboard/ProgressCard";
import StreakCard from "../components/dashboard/StreakCard";
import QuoteCard from "../components/dashboard/QuoteCard";
import SupportCard from "../components/dashboard/SupportCard";
import NotesDeckCard from "../components/dashboard/NotesDeckCard";
import StickyNotesCard from "../components/dashboard/StickyNotesCard";

/**
 * Dashboard Page
 * 
 * Main dashboard hub with all feature cards.
 * 
 * TODO: Backend Integration
 * - Fetch all dashboard data in parallel on mount
 * - Add real-time updates for streaks/progress
 * - Implement data caching
 */

export default function Dashboard() {
  const { user } = useUserStore();

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
        {/* Welcome Section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">
              {getGreeting()}, {user.name || 'Student'}! 👋
            </h1>
            <p className="text-gray-500">
              Ready to continue your learning journey?
            </p>
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
            
            {/* Quick Stats Card */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-gray-500">Class Level</span>
                  <span className="font-semibold text-gray-800">Class {user.classLevel}</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-gray-500">Subject Focus</span>
                  <span className="font-semibold text-gray-800">{user.preferredSubject}</span>
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
