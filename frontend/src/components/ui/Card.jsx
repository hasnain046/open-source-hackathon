import React from 'react';

export const Card = ({ children, className = '', hover = false, glow = false }) => {
  return (
    <div className={`
      rounded-2xl p-6 transition-all duration-300
      glass-panel dark:glass-panel
      ${hover ? 'hover:-translate-y-1 hover:border-cyan-500/30' : ''}
      ${glow ? 'glow-cyan' : ''}
      ${className}
    `}>
      {children}
    </div>
  );
};
