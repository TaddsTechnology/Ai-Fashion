import React from 'react';

interface ColorSwatchProps {
  color: string;
  name?: string;
  size?: 'sm' | 'md' | 'lg';
  showHex?: boolean;
}

const ColorSwatch: React.FC<ColorSwatchProps> = ({ 
  color, 
  name, 
  size = 'md',
  showHex = false
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };

  return (
    <div className="flex flex-col items-center">
      <div 
        className={`${sizeClasses[size]} rounded-full shadow-md mb-2`}
        style={{ backgroundColor: color }}
      />
      {name && <span className="text-sm font-medium text-gray-700">{name}</span>}
      {showHex && <span className="text-xs text-gray-500">{color}</span>}
    </div>
  );
};

export default ColorSwatch; 