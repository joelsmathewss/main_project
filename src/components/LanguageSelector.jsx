export default function LanguageSelector({ language, onLanguageChange }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
      <h3 className="text-xl font-semibold mb-4">Choose Language</h3>
      <select
        value={language}
        onChange={(e) => onLanguageChange(e.target.value)}
        className="w-full border rounded-lg px-4 py-2"
      >
        <option value="en">English</option>
        <option value="ml">Malayalam</option>
      </select>
    </div>
  );
}
