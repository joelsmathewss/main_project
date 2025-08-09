import React from "react";
import { FaUpload, FaShieldAlt, FaClock, FaCheckCircle } from "react-icons/fa";

const WhyLucidCare = () => {
  return (
    <div className="min-h-screen flex items-center px-4">
      <div className="max-w-7xl mx-auto w-full">
        <div className="rounded-3xl p-10 md:p-12">
          <div className="text-center mb-10">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-2">Why Choose LucidCare?</h2>
            <p className="text-lg md:text-xl text-gray-600">
              Making medical insights simple, so everyone can take charge of their health.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Easy Upload Card */}
            <div className="bg-white border border-gray-200 rounded-2xl shadow-lg p-6 flex flex-col items-center text-center">
              <div className="p-4 bg-green-100 rounded-full mb-4">
                <FaUpload className="text-green-600 text-3xl" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-2">Easy Upload</h4>
              <p className="text-gray-600">
                Drag and drop your medical reports in PDF, DOCX, or image formats
              </p>
            </div>

            {/* Secure & Private Card */}
            <div className="bg-white border border-gray-200 rounded-2xl shadow-lg p-6 flex flex-col items-center text-center">
              <div className="p-4 bg-green-100 rounded-full mb-4">
                <FaShieldAlt className="text-green-600 text-3xl" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-2">Secure & Private</h4>
              <p className="text-gray-600">
                Your medical data is encrypted and never shared with third parties
              </p>
            </div>

            {/* Instant Results Card */}
            <div className="bg-white border border-gray-200 rounded-2xl shadow-lg p-6 flex flex-col items-center text-center">
              <div className="p-4 bg-green-100 rounded-full mb-4">
                <FaClock className="text-green-600 text-3xl" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-2">Instant Results</h4>
              <p className="text-gray-600">
                Get simplified explanations of your reports in seconds
              </p>
            </div>

            {/* Medical Accuracy Card */}
            <div className="bg-white border border-gray-200 rounded-2xl shadow-lg p-6 flex flex-col items-center text-center">
              <div className="p-4 bg-green-100 rounded-full mb-4">
                <FaCheckCircle className="text-green-600 text-3xl" />
              </div>
              <h4 className="text-xl font-bold text-gray-900 mb-2">Medical Accuracy</h4>
              <p className="text-gray-600">
                AI-powered simplification maintains medical accuracy while improving readability
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WhyLucidCare;
