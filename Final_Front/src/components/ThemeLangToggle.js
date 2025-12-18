import React, { useEffect, useState } from 'react';
import './ThemeLangToggle.css';

const ThemeLangToggle = () => {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    window.dispatchEvent(new CustomEvent('themeChange', { detail: { theme } }));
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <div className="theme-lang-toggle">
      <button
        className="toggle-btn theme-btn"
        onClick={toggleTheme}
        aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        title={theme === 'dark' ? '라이트 모드' : '다크 모드'}
      >
        {theme === 'dark' ? <span className="icon moon">🌙</span> : <span className="icon sun">☀️</span>}
      </button>
    </div>
  );
};

export default ThemeLangToggle;









