import React from "react";

const WhyLucidCare = () => {
  return (
    <div className="min-h-screen flex items-center px-4">
      <div className="max-w-7xl mx-auto w-full">
        <div className="bg-white rounded-3xl shadow-2xl p-10 md:p-12">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-10">
            Why LucidCare?
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-8">
            <div className="bg-gray-200 h-40 rounded-xl"></div>
            <div className="bg-gray-200 h-40 rounded-xl"></div>
            <div className="bg-gray-200 h-40 rounded-xl"></div>
            <div className="bg-gray-200 h-40 rounded-xl"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WhyLucidCare;
