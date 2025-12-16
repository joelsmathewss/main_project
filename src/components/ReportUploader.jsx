import { useState } from "react";
import { Upload } from "lucide-react";

export default function ReportUploader({ onFileSelect }) {
  const [file, setFile] = useState(null);

  const handleChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    setFile(selectedFile);
    onFileSelect(selectedFile);
  };

  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        <Upload size={16} className="text-teal-500" />
        Upload Medical Report
      </h3>

      <input
        type="file"
        accept=".pdf,.jpg,.jpeg,.png"
        onChange={handleChange}
        className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
      />

      {file && (
        <p className="mt-2 text-xs text-gray-500 truncate">
          Selected: {file.name}
        </p>
      )}
    </div>
  );
}
