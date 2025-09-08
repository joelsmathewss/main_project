export default function Signup() {
  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-500 to-teal-400 flex items-center justify-center pt-24 pb-12 px-4">
      <div className="bg-white rounded-2xl shadow-lg w-full max-w-md p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Create Your Account
        </h2>

        <form className="space-y-4">
          {/* Full Name */}
          <div>
            <label className="block text-gray-700 font-medium mb-1">
              Full Name
            </label>
            <input
              type="text"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:outline-none"
              placeholder="Enter your full name"
            />
          </div>

          {/* Age */}
          <div>
            <label className="block text-gray-700 font-medium mb-1">Age</label>
            <input
              type="number"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:outline-none"
              placeholder="Enter your age"
            />
          </div>

          {/* Sex */}
          <div>
            <label className="block text-gray-700 font-medium mb-1">Sex</label>
            <select className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:outline-none">
              <option>Select</option>
              <option>Male</option>
              <option>Female</option>
              <option>Other</option>
            </select>
          </div>

          {/* Email */}
          <div>
            <label className="block text-gray-700 font-medium mb-1">Email</label>
            <input
              type="email"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:outline-none"
              placeholder="Enter your email"
            />
          </div>

          {/* AI Mode
          <div>
            <label className="block text-gray-700 font-medium mb-1">
              Select AI Mode
            </label>
            <div className="flex items-center space-x-6">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="aiMode"
                  value="professional"
                  defaultChecked
                  className="text-teal-500 focus:ring-teal-500"
                />
                <span className="ml-2">Professional</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="aiMode"
                  value="coach"
                  className="text-teal-500 focus:ring-teal-500"
                />
                <span className="ml-2">Coach</span>
              </label>
            </div>
          </div> */}

          {/* Password */}
          <div>
            <label className="block text-gray-700 font-medium mb-1">
              Password
            </label>
            <input
              type="password"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:outline-none"
              placeholder="Enter your password"
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="w-full bg-gradient-to-r from-blue-500 to-teal-500 text-white py-2 rounded-lg font-semibold hover:opacity-90 transition"
          >
            Sign Up
          </button>
        </form>

        <p className="mt-6 text-center text-gray-600 text-sm">
          Already have an account?{" "}
          <a href="/login" className="text-teal-600 font-medium hover:underline">
            Log In
          </a>
        </p>
      </div>
    </div>
  );
}
