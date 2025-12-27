import { useState } from "react";
import { 
  FileText, 
  Download, 
  Upload, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Eye,
  Loader2,
  Calendar,
  User
} from "lucide-react";
import { Button } from "../ui/button";
import { testService } from "../../services/api";

/**
 * StaffTestCard Component
 * 
 * Displays a staff-assigned test with download/upload functionality.
 */

export default function StaffTestCard({ test, studentId, onRefresh }) {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const getStatusBadge = () => {
    switch (test.status) {
      case "pending":
        return (
          <span className="flex items-center gap-1 px-2 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-medium">
            <Clock className="w-3 h-3" />
            Pending
          </span>
        );
      case "submitted":
        return (
          <span className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
            <CheckCircle className="w-3 h-3" />
            Submitted
          </span>
        );
      case "evaluated":
        return (
          <span className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
            <CheckCircle className="w-3 h-3" />
            Evaluated
          </span>
        );
      default:
        return null;
    }
  };

  const handleDownloadPaper = () => {
    // Open question paper PDF
    window.open(test.questionPaperUrl, "_blank");
  };

  const handleUploadAnswer = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (file.type !== "application/pdf") {
      setUploadError("Please upload a PDF file");
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setUploadError("File size must be less than 10MB");
      return;
    }

    setUploading(true);
    setUploadError(null);

    try {
      await testService.uploadAnswerSheet(test.id, studentId, file);
      onRefresh(); // Refresh to update status
    } catch (error) {
      console.error("Upload failed:", error);
      setUploadError("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const handleViewResult = () => {
    // Open evaluated result
    window.open(test.evaluatedUrl, "_blank");
  };

  const isOverdue = new Date(test.dueDate) < new Date() && test.status === "pending";

  return (
    <div className={`bg-white rounded-2xl p-6 shadow-sm border transition-all hover:shadow-md ${
      isOverdue ? "border-red-200" : "border-gray-100"
    }`}>
      <div className="flex items-start justify-between gap-4">
        {/* Left: Test Info */}
        <div className="flex items-start gap-4 flex-1">
          <div className={`p-3 rounded-xl ${
            test.status === "evaluated" ? "bg-green-100" : 
            test.status === "submitted" ? "bg-blue-100" : "bg-amber-100"
          }`}>
            <FileText className={`w-6 h-6 ${
              test.status === "evaluated" ? "text-green-600" : 
              test.status === "submitted" ? "text-blue-600" : "text-amber-600"
            }`} />
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-gray-800">{test.title}</h3>
              {getStatusBadge()}
            </div>
            
            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500 mb-3">
              <span className="flex items-center gap-1">
                <User className="w-3.5 h-3.5" />
                {test.uploadedBy}
              </span>
              <span className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                Due: {new Date(test.dueDate).toLocaleDateString()}
              </span>
              <span className="font-medium text-gray-700">
                Max: {test.maxMarks} marks
              </span>
            </div>

            {/* Score (if evaluated) */}
            {test.status === "evaluated" && test.score !== undefined && (
              <div className="flex items-center gap-2 mb-3">
                <span className="text-2xl font-bold text-green-600">{test.score}</span>
                <span className="text-gray-500">/ {test.maxMarks}</span>
                <span className="text-sm text-gray-500">
                  ({Math.round((test.score / test.maxMarks) * 100)}%)
                </span>
              </div>
            )}

            {/* Overdue Warning */}
            {isOverdue && (
              <div className="flex items-center gap-2 text-red-600 text-sm mb-2">
                <AlertCircle className="w-4 h-4" />
                <span>This test is overdue!</span>
              </div>
            )}

            {/* Upload Error */}
            {uploadError && (
              <div className="flex items-center gap-2 text-red-600 text-sm mb-2">
                <AlertCircle className="w-4 h-4" />
                <span>{uploadError}</span>
              </div>
            )}
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex flex-col gap-2">
          {/* Download Question Paper */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownloadPaper}
            className="gap-2"
          >
            <Download className="w-4 h-4" />
            Question Paper
          </Button>

          {/* Upload Answer Sheet (only if pending) */}
          {test.status === "pending" && (
            <label className="cursor-pointer">
              <input
                type="file"
                accept="application/pdf"
                onChange={handleUploadAnswer}
                className="hidden"
                disabled={uploading}
              />
              <Button
                variant="default"
                size="sm"
                className="gap-2 w-full"
                disabled={uploading}
                asChild
              >
                <span>
                  {uploading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Upload className="w-4 h-4" />
                  )}
                  {uploading ? "Uploading..." : "Upload Answer"}
                </span>
              </Button>
            </label>
          )}

          {/* View Result (if evaluated) */}
          {test.status === "evaluated" && test.evaluatedUrl && (
            <Button
              variant="default"
              size="sm"
              onClick={handleViewResult}
              className="gap-2 bg-green-600 hover:bg-green-700"
            >
              <Eye className="w-4 h-4" />
              View Result
            </Button>
          )}

          {/* Submitted confirmation */}
          {test.status === "submitted" && (
            <div className="text-center text-sm text-blue-600">
              Awaiting evaluation
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
