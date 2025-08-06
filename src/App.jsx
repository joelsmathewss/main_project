import React from "react";
import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import WhyLucidCare from "./components/WhyLucidCare";

export default function App() {
  return (
    <div className="text-white font-sans">
      <Navbar />

      <section id="home" className="min-h-screen bg-gradient-to-br from-teal-700 via-emerald-600 to-cyan-700 flex items-center">
        <HeroSection />
      </section>

      <section id="why" className="bg-white text-black py-20">
        <WhyLucidCare />
      </section>
    </div>
  );
}
