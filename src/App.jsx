// src/App.jsx
import { BrowserRouter as Router, Routes, Route, Outlet } from "react-router-dom"; // Import Outlet
import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import FeaturesSection from "./components/FeaturesSection";
import HowItWorksSection from "./components/HowItWorksSection";
import CTASection from "./components/CTASection";
import Footer from "./components/Footer";
import Signup from "./components/Signup";
import Login from "./components/Login";
import ContactUs from "./components/ContactUs";

// Update Home to include <Outlet />
// This allows nested pages (Login/Signup) to render on top of it
function Home() {
  return (
    <div className="relative"> {/* Make relative for positioning context if needed */}
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <CTASection />
      <Footer />
      
      {/* The Outlet renders the child route (Login/Signup) if one is active */}
      <Outlet /> 
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <div className="bg-white text-gray-800 font-inter">
        <Navbar />
        <main>
          <Routes>
            {/* Nest login and signup under the "/" route */}
            <Route path="/" element={<Home />}>
              <Route path="login" element={<Login />} />
              <Route path="signup" element={<Signup />} />
            </Route>
            
            {/* Contact remains a separate page */}
            <Route path="/contact" element={<ContactUs />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}