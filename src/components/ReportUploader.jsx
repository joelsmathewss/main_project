import { useState } from "react";
import { Upload } from "lucide-react";

export default function ReportUploader({ onFileSelect }) {
  const [file, setFile] = useState(null);

  const handleChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    onFileSelect(selectedFile);
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
      <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Upload className="text-teal-500" /> Upload Medical Report
      </h3>
      <input
        type="file"
        accept=".pdf,.jpg,.jpeg,.png"
        onChange={handleChange}
        className="w-full border rounded-lg px-4 py-2"
      />
      {file && (
        <p className="mt-2 text-sm text-gray-600">Selected: {file.name}</p>
      )}
    </div>
  );
}
