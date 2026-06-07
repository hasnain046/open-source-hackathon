import React from 'react';

export const Button = ({ 
  children, 
  onClick, 
  variant = 'primary', // 'primary' | 'secondary' | 'glass' | 'danger'
  size = 'md', // 'sm' | 'md' | 'lg'
  className = '',
  disabled = false,
  type = 'button'
}) => {
  const baseStyle = "inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-300 active:scale-95 disabled:opacity-50 disabled:pointer-events-none";
  
  const variants = {
    primary: "bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/10 hover:shadow-cyan-400/25",
    secondary: "bg-slate-800 hover:bg-slate-700 text-white border border-slate-700",
    glass: "bg-slate-900/40 hover:bg-slate-900/80 text-cyan-400 border border-cyan-500/20 hover:border-cyan-500/40",
    danger: "bg-rose-600 hover:bg-rose-500 text-white shadow-md shadow-rose-600/10"
  };

  const sizes = {
    sm: "px-3.5 py-1.5 text-xs",
    md: "px-5 py-2.5 text-sm",
    lg: "px-7 py-3 text-base"
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyle} ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {children}
    </button>
  );
};
