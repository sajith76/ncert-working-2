import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useUserStore from "../stores/userStore";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function StudentTests() {
  const navigate = useNavigate();
  const { user } = useUserStore();
  const [tests, setTests] = useState([]);
  const [selectedTest, setSelectedTest] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("available"); // available, submitted
  
  // Upload state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  
  // View feedback modal
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  
  // Notifications
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    if (user?.id) {
      fetchTests();
      fetchSubmissions();
      fetchNotifications();
    }
  }, [user]);

  const fetchTests = async () => {
    try {
      setLoading(true);
      const studentId = user?.id || user?.user_id;
      const response = await fetch(`${API_URL}/api/tests/student/${studentId}`);
      if (!response.ok) throw new Error("Failed to fetch tests");
      const data = await response.json();
      setTests(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubmissions = async () => {
    try {
      const studentId = user?.id || user?.user_id;
      const response = await fetch(`${API_URL}/api/tests/my-submissions/${studentId}`);
      if (response.ok) {
        const data = await response.json();
        setSubmissions(data);
      }
    } catch (err) {
      console.error("Failed to fetch submissions:", err);
    }
  };

  const fetchNotifications = async () => {
    try {
      const studentId = user?.id || user?.user_id;
      const response = await fetch(`${API_URL}/api/tests/notifications/${studentId}?unread_only=true`);
      if (response.ok) {
        const data = await response.json();
        setNotifications(data);
      }
    } catch (err) {
      console.error("Failed to fetch notifications:", err);
    }
  };

  const markNotificationRead = async (notificationId) => {
    try {
      await fetch(`${API_URL}/api/tests/notifications/${notificationId}/read`, { method: "PUT" });
      setNotifications(notifications.filter(n => n.id !== notificationId));
    } catch (err) {
      console.error("Failed to mark notification read:", err);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== "application/pdf") {
        alert("Please select a PDF file");
        return;
      }
      setUploadFile(file);
    }
  };

  const handleSubmitTest = async () => {
    if (!uploadFile || !selectedTest) return;
    
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("test_id", selectedTest.id);
      formData.append("student_id", user?.id || user?.user_id);
      formData.append("pdf_file", uploadFile);
      
      const response = await fetch(`${API_URL}/api/tests/submit`, {
        method: "POST",
        body: formData
      });
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Failed to submit test");
      }
      
      const result = await response.json();
      alert("Test submitted successfully!");
      
      setShowUploadModal(false);
      setUploadFile(null);
      setSelectedTest(null);
      
      // Refresh data
      fetchTests();
      fetchSubmissions();
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setUploading(false);
    }
  };

  const openSubmitModal = (test) => {
    setSelectedTest(test);
    setShowUploadModal(true);
  };

  const viewFeedback = (submission) => {
    setSelectedSubmission(submission);
    setShowFeedbackModal(true);
  };

  const getStatusBadge = (status) => {
    const styles = {
      active: "bg-green-100 text-green-700",
      upcoming: "bg-blue-100 text-blue-700",
      closed: "bg-gray-100 text-gray-700"
    };
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || styles.closed}`}>{status}</span>;
  };

  const availableTests = tests.filter(t => !t.has_submitted && t.status !== "closed");
  const submittedTests = tests.filter(t => t.has_submitted);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate("/dashboard")} className="text-white/80 hover:text-white">
                ← Back
              </button>
              <div>
                <h1 className="text-2xl font-bold">My Tests</h1>
                <p className="text-blue-100 text-sm">Class {user?.classLevel} • View and submit tests</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {/* Notification Bell */}
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="p-2 bg-white/20 rounded-lg hover:bg-white/30 relative"
                >
                  🔔
                  {notifications.length > 0 && (
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-xs flex items-center justify-center">
                      {notifications.length}
                    </span>
                  )}
                </button>
                
                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg z-50 max-h-96 overflow-y-auto">
                    <div className="p-4 border-b">
                      <h3 className="font-semibold text-gray-900">Notifications</h3>
                    </div>
                    {notifications.length === 0 ? (
                      <div className="p-4 text-center text-gray-500">
                        No new notifications
                      </div>
                    ) : (
                      notifications.map(n => (
                        <div key={n.id} className="p-4 border-b hover:bg-gray-50">
                          <p className="font-medium text-gray-900 text-sm">{n.title}</p>
                          <p className="text-gray-600 text-sm">{n.message}</p>
                          <div className="flex justify-between items-center mt-2">
                            <span className="text-xs text-gray-400">
                              {new Date(n.created_at).toLocaleString()}
                            </span>
                            <button
                              onClick={() => markNotificationRead(n.id)}
                              className="text-xs text-blue-600 hover:underline"
                            >
                              Mark as read
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
              
              <span className="text-sm bg-white/20 px-3 py-1 rounded-full">{user?.name || user?.user_id}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab("available")}
            className={`px-6 py-3 rounded-lg font-medium transition ${
              activeTab === "available"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 hover:bg-gray-100"
            }`}
          >
            Available Tests ({availableTests.length})
          </button>
          <button
            onClick={() => setActiveTab("submitted")}
            className={`px-6 py-3 rounded-lg font-medium transition ${
              activeTab === "submitted"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-700 hover:bg-gray-100"
            }`}
          >
            Submitted ({submittedTests.length})
          </button>
        </div>

        {loading ? (
          <div className="text-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Loading tests...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {activeTab === "available" && (
              availableTests.length === 0 ? (
                <div className="col-span-full bg-white p-8 rounded-xl text-center text-gray-500">
                  <p className="text-4xl mb-4">📚</p>
                  <p>No tests available right now</p>
                  <p className="text-sm mt-2">Check back later for new tests from your teachers</p>
                </div>
              ) : (
                availableTests.map(test => (
                  <div key={test.id} className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition">
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="font-semibold text-gray-900">{test.title}</h3>
                      {getStatusBadge(test.status)}
                    </div>
                    
                    <div className="text-sm text-gray-500 space-y-1 mb-4">
                      <p>📘 {test.subject}</p>
                      <p>🎓 Class {test.class_level}</p>
                      {test.is_timed && test.end_datetime && (
                        <p className="text-orange-600">
                          ⏰ Due: {new Date(test.end_datetime).toLocaleString()}
                        </p>
                      )}
                    </div>
                    
                    {test.description && (
                      <p className="text-sm text-gray-600 mb-4">{test.description}</p>
                    )}
                    
                    <div className="flex gap-2">
                      <a
                        href={`${API_URL}${test.pdf_url}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg text-center hover:bg-blue-200 text-sm font-medium"
                      >
                        📄 View Questions
                      </a>
                      <button
                        onClick={() => openSubmitModal(test)}
                        className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium"
                      >
                        📤 Submit Answer
                      </button>
                    </div>
                  </div>
                ))
              )
            )}

            {activeTab === "submitted" && (
              submittedTests.length === 0 ? (
                <div className="col-span-full bg-white p-8 rounded-xl text-center text-gray-500">
                  <p className="text-4xl mb-4">✅</p>
                  <p>No submitted tests yet</p>
                  <p className="text-sm mt-2">Complete and submit tests to see them here</p>
                </div>
              ) : (
                submittedTests.map(test => {
                  const submission = submissions.find(s => s.test_id === test.id);
                  return (
                    <div key={test.id} className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition">
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="font-semibold text-gray-900">{test.title}</h3>
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                          ✅ Submitted
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-500 space-y-1 mb-4">
                        <p>📘 {test.subject}</p>
                        <p>🎓 Class {test.class_level}</p>
                        {test.submission_date && (
                          <p>📅 Submitted: {new Date(test.submission_date).toLocaleDateString()}</p>
                        )}
                      </div>
                      
                      <div className="flex gap-2">
                        <a
                          href={`${API_URL}${test.pdf_url}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-1 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg text-center hover:bg-blue-200 text-sm font-medium"
                        >
                          📄 View Test
                        </a>
                        {test.has_feedback && submission ? (
                          <button
                            onClick={() => viewFeedback(submission)}
                            className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium"
                          >
                            💬 View Feedback
                          </button>
                        ) : (
                          <span className="flex-1 px-4 py-2 bg-gray-100 text-gray-500 rounded-lg text-center text-sm">
                            ⏳ Awaiting Feedback
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })
              )
            )}
          </div>
        )}
      </main>

      {/* Upload Modal */}
      {showUploadModal && selectedTest && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-lg mx-4">
            <h2 className="text-xl font-bold mb-4">Submit Test: {selectedTest.title}</h2>
            
            <div className="mb-4">
              <a
                href={`${API_URL}${selectedTest.pdf_url}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm"
              >
                📄 View Test Questions
              </a>
            </div>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition mb-4">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
                id="submission-upload"
              />
              <label htmlFor="submission-upload" className="cursor-pointer">
                {uploadFile ? (
                  <div className="flex flex-col items-center">
                    <span className="text-4xl mb-2">📄</span>
                    <p className="text-green-600 font-medium">{uploadFile.name}</p>
                    <p className="text-sm text-gray-500 mt-1">Click to change file</p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center">
                    <span className="text-4xl mb-2">📤</span>
                    <p className="text-gray-600 font-medium">Upload your answer PDF</p>
                    <p className="text-sm text-gray-400 mt-1">Only PDF files are accepted</p>
                  </div>
                )}
              </label>
            </div>
            
            <p className="text-sm text-gray-500 mb-4">
              ⚠️ You can only submit once. Make sure your answers are complete before submitting.
            </p>
            
            <div className="flex gap-3">
              <button
                onClick={() => { setShowUploadModal(false); setUploadFile(null); }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitTest}
                disabled={uploading || !uploadFile}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {uploading ? "Submitting..." : "Submit Test"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Feedback Modal */}
      {showFeedbackModal && selectedSubmission && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-lg mx-4">
            <h2 className="text-xl font-bold mb-4">Test Feedback</h2>
            
            <div className="mb-4">
              <p className="text-sm text-gray-500">Test: {selectedSubmission.test_title}</p>
              <p className="text-sm text-gray-500">
                Submitted: {new Date(selectedSubmission.submitted_at).toLocaleString()}
              </p>
            </div>
            
            <div className="flex gap-2 mb-4">
              <a
                href={`${API_URL}${selectedSubmission.pdf_url}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm"
              >
                📄 View Your Submission
              </a>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg mb-4">
              <h3 className="font-medium text-purple-900 mb-2">Teacher's Feedback:</h3>
              <p className="text-purple-800">{selectedSubmission.admin_comment || "No comment yet"}</p>
              {selectedSubmission.comment_at && (
                <p className="text-xs text-purple-600 mt-2">
                  Received: {new Date(selectedSubmission.comment_at).toLocaleString()}
                </p>
              )}
            </div>
            
            <button
              onClick={() => { setShowFeedbackModal(false); setSelectedSubmission(null); }}
              className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
