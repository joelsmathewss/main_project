export default function SummaryGenerator({ file, language, onGenerate, loading }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
      <button
        onClick={onGenerate}
        disabled={loading}
        className="w-full bg-gradient-to-r from-blue-500 to-teal-500 text-white py-2 rounded-lg font-semibold hover:opacity-90 transition"
      >
        {loading ? "Generating..." : "Generate Summary"}
      </button>
    </div>
  );
}
