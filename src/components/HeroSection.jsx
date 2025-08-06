import React from "react";

// Upload icon
const Upload = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242" />
    <path d="M12 12v9" />
    <path d="m16 16-4-4-4 4" />
  </svg>
);

const HeroSection = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16 w-full">
      <div className="max-w-3xl">
        <h1 className="text-5xl md:text-6xl font-bold tracking-tight">
          Understand Your <br />
          Medical Reports Instantly
        </h1>
        <p className="mt-6 text-lg text-slate-200">
          Transform complex medical documents into clear, easy-to-understand explanations. Get the insights you need about your health in one click.
        </p>
        <div className="mt-10 flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <button className="bg-lime-400 hover:bg-lime-500 text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2 shadow-lg transform hover:scale-105 transition-transform">
            <Upload size={20} />
            Upload Your Report
          </button>
          <button className="bg-white hover:bg-gray-200 text-black font-semibold px-6 py-3 rounded-full shadow-md transform hover:scale-105 transition-transform">
            View Sample Report
          </button>
        </div>
      </div>
    </div>
  );
};

export default HeroSection;
