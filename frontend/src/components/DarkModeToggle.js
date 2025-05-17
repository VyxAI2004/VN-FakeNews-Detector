import React from 'react';
import { useTheme } from '../context/ThemeContext';

/**
 * Dark mode toggle component
 * Matches the original implementation from chatbot.js
 */
const DarkModeToggle = () => {
  const { darkMode, toggleDarkMode } = useTheme();

  return (
    <div className="dark-mode-toggle">

    </div>
  );
};

export default DarkModeToggle; 