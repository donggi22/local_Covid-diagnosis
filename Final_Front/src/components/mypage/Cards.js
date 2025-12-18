import React from 'react';

export const Card = ({ children, onClick, className }) => {
  return (
    <div
      className={`mp-card ${className || ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {children}
    </div>
  );
};

export const Stat = ({ label, value, helper }) => {
  return (
    <div className="mp-stat">
      <div className="mp-stat-value">{value}</div>
      <div className="mp-stat-label">{label}</div>
      {helper && <div className="mp-stat-helper">{helper}</div>}
    </div>
  );
};

export const Progress = ({ value = 0 }) => {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className="mp-progress">
      <div className="mp-progress-bar" style={{ width: `${clamped}%` }} />
    </div>
  );
};

export const Badge = ({ color = 'gray', children }) => {
  const colorMap = {
    red: '#EF4444',
    orange: '#F59E0B',
    green: '#10B981',
    gray: '#6B7280'
  };
  return (
    <span className="mp-badge" style={{ backgroundColor: `${colorMap[color]}22`, color: colorMap[color], borderColor: `${colorMap[color]}55` }}>
      {children}
    </span>
  );
};

export const Section = ({ title, action, children }) => (
  <section className="mp-section">
    <div className="mp-section-head">
      <h2>{title}</h2>
      {action}
    </div>
    {children}
  </section>
);




