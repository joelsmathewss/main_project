import { useState } from "react";
import ReportUploader from "../components/ReportUploader";
import LanguageSelector from "../components/LanguageSelector";
import SummaryGenerator from "../components/SummaryGenerator";

export default function ReportSummaryPage() {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState("en");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  // Function passed to SummaryGenerator to update summary
  const handleGenerate = () => {
    if (!file) return alert("Please upload a file first.");
    setLoading(true);

    // TODO: Replace with backend API call
    setTimeout(() => {
      setSummary(
        language === "ml"
          ? "ഇത് നിങ്ങളുടെ മെഡിക്കൽ റിപ്പോർട്ടിന്റെ ലളിതമായ വിശദീകരണമാണ്."
          : "This is a simplified explanation of your medical report."
      );
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50 px-6 py-12 flex justify-center">
      <div className="max-w-6xl w-full grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Left Side: Controls */}
        <div className="flex flex-col gap-6">
          <ReportUploader onFileSelect={setFile} />
          <LanguageSelector language={language} onLanguageChange={setLanguage} />
          <SummaryGenerator
            file={file}
            language={language}
            loading={loading}
            onGenerate={handleGenerate}
          />
        </div>

        {/* Right Side: Summary Display */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
          <h2 className="text-2xl font-bold mb-4">Report Summary</h2>
          {loading ? (
            <p className="text-gray-500">Analyzing report, please wait...</p>
          ) : (
            <textarea
              value={summary}
              readOnly
              rows={20}
              className="w-full h-full border rounded-lg px-4 py-3 text-gray-800 resize-none"
              placeholder="Your summary will appear here..."
            />
          )}
        </div>
      </div>
    </div>
  );
}
