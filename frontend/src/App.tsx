import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { HomePage } from './pages/HomePage';
import { ContactPage } from './pages/ContactPage';
import { LoginPage } from './pages/LoginPage';
import { AgentPage } from './pages/AgentPage';
import { UserDashboard } from './pages/UserDashboard';
import { OperatorDashboard } from './pages/OperatorDashboard';
// Scroll to top upon route change
const ScrollToTop = () => {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Navbar />
      <div className="app-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/contact-us" element={<ContactPage />} />
          <Route path="/services" element={<HomePage />} />
          <Route path="/about" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/agent" element={<AgentPage />} />
          <Route path="/user-dashboard" element={<UserDashboard />} />
          <Route path="/operator-dashboard" element={<OperatorDashboard />} />
        </Routes>
      </div>
      <Footer />
    </BrowserRouter>
  );
};

export default App;
