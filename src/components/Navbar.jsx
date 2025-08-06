import React, { useEffect, useState } from "react";

const Navbar = () => {
  const [progress, setProgress] = useState(0); // scroll progress from 0 → 1

  useEffect(() => {
    const handleScroll = () => {
      const maxScroll = 300; // adjust if needed
      const scrollY = window.scrollY;
      const ratio = Math.min(scrollY / maxScroll, 1);
      setProgress(ratio);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Linear interpolation between transparent and gradient
  const background = progress === 0
    ? "rgba(255, 255, 255, 0.1)" // start (glass)
    : `linear-gradient(to bottom right,
        rgba(13, 148, 136, ${progress}),
        rgba(5, 150, 105, ${progress}),
        rgba(6, 182, 212, ${progress}))`; // gradient match with opacity

  return (
    <header className="fixed top-4 left-4 right-4 z-50 transition-all duration-300">
      <div
        style={{
          backgroundImage: background,
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
          border: "1px solid rgba(255,255,255,0.2)",
          transition: "background-image 0.3s ease-out",
        }}
        className="rounded-2xl shadow-lg"
      >
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between h-[72px]">
          <div className="flex items-center">
            <img src="/Frame 3.svg" alt="LucidCare Logo" className="h-16 w-auto" />
          </div>
          <nav className="hidden md:flex space-x-8 text-lg font-medium">
            <a href="#home" className="hover:text-lime-300 transition-colors">Home</a>
            <a href="#why" className="hover:text-lime-300 transition-colors">About</a>
            <a href="#" className="hover:text-lime-300 transition-colors">Profile</a>
            <a href="#" className="hover:text-lime-300 transition-colors">Help</a>
          </nav>
          <div className="hidden sm:flex items-center space-x-2">
            <a href="#" className="px-4 py-1.5 text-sm rounded-full border border-white/30 bg-white/10 text-white backdrop-blur-md hover:bg-white hover:text-black transition-all">Login</a>
            <a href="#" className="px-4 py-1.5 text-sm rounded-full border border-white/10 bg-white/10 text-white backdrop-blur-md hover:bg-white hover:text-black transition-all">Signup</a>
          </div>
          <div className="sm:hidden">
            <button className="text-white p-2">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
