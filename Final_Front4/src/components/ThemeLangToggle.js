import React, { useEffect, useState } from 'react';
import './ThemeLangToggle.css';

const ThemeLangToggle = () => {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');
  const [lang, setLang] = useState(() => localStorage.getItem('lang') || 'ko');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
      document.body.classList.add('dark-mode');
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.body.classList.remove('dark-mode');
      document.documentElement.setAttribute('data-theme', 'light');
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('theme', theme);
    if (theme === 'dark') {
      document.body.classList.add('dark-mode');
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.body.classList.remove('dark-mode');
      document.documentElement.setAttribute('data-theme', 'light');
    }
    window.dispatchEvent(new CustomEvent('themeChange', { detail: { theme } }));
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('lang', lang);
    window.dispatchEvent(new CustomEvent('langChange', { detail: { lang } }));
  }, [lang]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const toggleLang = () => {
    setLang((prev) => (prev === 'ko' ? 'en' : 'ko'));
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
      <button
        className="toggle-btn lang-btn"
        onClick={toggleLang}
        aria-label={lang === 'ko' ? 'Switch to English' : '한국어로 전환'}
        title={lang === 'ko' ? 'English' : '한국어'}
      >
        <span className="lang-text">{lang === 'ko' ? 'KO' : 'EN'}</span>
      </button>
    </div>
  );
};

export default ThemeLangToggle;









