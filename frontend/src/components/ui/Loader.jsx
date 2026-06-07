import React from 'react';

export const Loader = ({ size = 'md', className = '' }) => {
  const sizes = {
    sm: 'w-5 h-5 border-2',
    md: 'w-10 h-10 border-3',
    lg: 'w-16 h-16 border-4'
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div className={`
        ${sizes[size]}
        rounded-full 
        border-t-cyan-500 
        border-r-transparent 
        border-b-cyan-500/30 
        border-l-transparent 
        animate-spin
      `} />
    </div>
  );
};
