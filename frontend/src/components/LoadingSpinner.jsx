import React from 'react';
import { Loader } from 'lucide-react';

export default function LoadingSpinner({ size = 'md', text = 'Loading...' }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6', 
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  return (
    <div className="loading-spinner">
      <Loader className={`animate-spin ${sizeClasses[size]}`} />
      {text && <span className="loading-text">{text}</span>}
    </div>
  );
}
