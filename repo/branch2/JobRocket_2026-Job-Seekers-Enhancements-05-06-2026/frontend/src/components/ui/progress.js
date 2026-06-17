import React from "react";

const Progress = ({ value, className = "", ...props }) => {
  const percentage = Math.min(100, Math.max(0, value || 0));
  
  return (
    <div
      className={`relative h-2 w-full overflow-hidden rounded-full bg-slate-200 ${className}`}
      {...props}
    >
      <div
        className="h-full w-full flex-1 bg-gradient-to-r from-blue-600 to-blue-500 transition-all duration-500 ease-out"
        style={{
          transform: `translateX(-${100 - percentage}%)`
        }}
      />
    </div>
  );
};

export { Progress };