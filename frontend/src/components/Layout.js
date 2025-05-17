import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import DarkModeToggle from './DarkModeToggle';

const Layout = () => {
  return (
    <>
      <Navbar />
      <main>
        <Outlet />
      </main>
      <footer className="footer mt-auto py-3 bg-light">
        <div className="container text-center">
          <span className="text-muted">© 2025 - NLP Tool</span>
        </div>
      </footer>
      
      {/* Dark Mode Toggle */}
      <DarkModeToggle />
    </>
  );
};

export default Layout; 