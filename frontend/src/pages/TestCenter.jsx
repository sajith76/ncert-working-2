import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import DashboardLayout from "../components/dashboard/DashboardLayout";
import useUserStore from "../stores/userStore";
import { 
  FileText, 
  Brain, 
  Award,
  BookOpen,
  Target,
  TrendingUp
} from "lucide-react";
import { Button } from "../components/ui/button";
import StaffTestCard from "../components/test/StaffTestCard";
import TopicSelector from "../components/test/TopicSelector";
import { testService } from "../services/api";

/**
 * TestCenter Page
 * 
 * Two types of tests:
 * 1. Staff Tests - Download question paper, upload answer sheet (PDF)
 * 2. AI Tests - Topic-based tests with subject → chapter → topic selection
 */

export default function TestCenter() {
  const navigate = useNavigate();
  const { user } = useUserStore();
  const [activeTab, setActiveTab] = useState("ai"); // "staff" or "ai"
  const [staffTests, setStaffTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTopicSelector, setShowTopicSelector] = useState(false);

  useEffect(() => {
    fetchTests();
  }, [user.id, user.preferredSubject]);

  const fetchTests = async () => {
    setLoading(true);
    try {
      // Fetch staff tests
      const staffData = await testService.getStaffTests(
        user.preferredSubject, 
        null, 
        user.id
      );
      setStaffTests(Array.isArray(staffData) ? staffData : []);
    } catch (error) {
      console.error("Failed to fetch tests:", error);
      setStaffTests([]);
    } finally {
      setLoading(false);
    }
  };

  const handleTopicSelected = async (config) => {
    setShowTopicSelector(false);
    
    // Navigate to test session with configuration
    navigate("/test-session", { 
      state: { 
        testConfig: {
          student_id: user.id,
          class_level: user.classLevel || 10,
          ...config
        }
      } 
    });
  };

  const tabs = [
    { id: "ai", label: "AI Tests", icon: Brain, color: "text-purple-600" },
    { id: "staff", label: "Staff Tests", icon: FileText, color: "text-blue-600" },
  ];

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Test Center 📝</h1>
            <p className="text-gray-500">
              Take tests and track your progress
            </p>
          </div>
          <Button 
            variant="outline" 
            onClick={() => navigate("/report-card")}
            className="gap-2"
          >
            <Award className="w-4 h-4" />
            View Reports
          </Button>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-2xl p-2 shadow-sm border border-gray-100">
          <div className="flex gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl transition-all ${
                  activeTab === tab.id
                    ? "bg-gray-900 text-white"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <tab.icon className={`w-5 h-5 ${activeTab === tab.id ? "text-white" : tab.color}`} />
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-800" />
          </div>
        ) : (
          <>
            {/* AI Tests Tab */}
            {activeTab === "ai" && (
              <div className="space-y-6">
                {/* Info Banner */}
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-6 border border-purple-100">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-purple-100 rounded-xl">
                      <Brain className="w-6 h-6 text-purple-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-800 mb-1">Topic-Based AI Tests</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Select a topic from your syllabus and take a personalized AI test. 
                        Get instant evaluation with detailed feedback on your understanding.
                      </p>
                      <div className="flex flex-wrap gap-3 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <BookOpen className="w-4 h-4 text-purple-600" />
                          <span>Choose Subject & Chapter</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Target className="w-4 h-4 text-purple-600" />
                          <span>Select Topic</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <TrendingUp className="w-4 h-4 text-purple-600" />
                          <span>Get Recommendations</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Start Test Button */}
                <div className="flex justify-center">
                  <Button 
                    onClick={() => setShowTopicSelector(true)}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-6 text-lg gap-3"
                  >
                    <Brain className="w-6 h-6" />
                    Start New AI Test
                  </Button>
                </div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-white rounded-xl p-6 border border-gray-100">
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                      <Target className="w-6 h-6 text-purple-600" />
                    </div>
                    <h4 className="font-semibold text-gray-800 mb-2">Topic-Focused</h4>
                    <p className="text-sm text-gray-600">
                      Pre-generated questions for every topic in your syllabus. No duplicate questions.
                    </p>
                  </div>

                  <div className="bg-white rounded-xl p-6 border border-gray-100">
                    <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center mb-4">
                      <TrendingUp className="w-6 h-6 text-amber-600" />
                    </div>
                    <h4 className="font-semibold text-gray-800 mb-2">Smart Recommendations</h4>
                    <p className="text-sm text-gray-600">
                      Get topic recommendations based on your weak areas and untested topics.
                    </p>
                  </div>

                  <div className="bg-white rounded-xl p-6 border border-gray-100">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                      <Brain className="w-6 h-6 text-green-600" />
                    </div>
                    <h4 className="font-semibold text-gray-800 mb-2">AI Evaluation</h4>
                    <p className="text-sm text-gray-600">
                      RAG-based answer evaluation using textbook context for accurate assessment.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Staff Tests Tab */}
            {activeTab === "staff" && (
              <div className="space-y-6">
                {/* Info Banner */}
                <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl p-6 border border-blue-100">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-blue-100 rounded-xl">
                      <FileText className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800 mb-1">Staff Assigned Tests</h3>
                      <p className="text-sm text-gray-600">
                        Download question papers, write your answers, and upload your answer sheets.
                        Your teacher will evaluate and provide feedback.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Tests List */}
                {staffTests.length === 0 ? (
                  <div className="bg-white rounded-2xl p-12 text-center border border-gray-100">
                    <FileText className="w-12 h-12 mx-auto text-gray-300 mb-4" />
                    <h3 className="text-lg font-medium text-gray-800 mb-2">No Tests Available</h3>
                    <p className="text-gray-500">
                      Your teacher hasn't uploaded any tests yet.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {staffTests.map((test) => (
                      <StaffTestCard 
                        key={test.id} 
                        test={test}
                        studentId={user.id}
                        onRefresh={fetchTests}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>

      {/* Topic Selector Modal */}
      {showTopicSelector && (
        <TopicSelector
          studentId={user.id}
          classLevel={user.classLevel || 10}
          onSelectTopic={handleTopicSelected}
          onCancel={() => setShowTopicSelector(false)}
        />
      )}
    </DashboardLayout>
  );
}
