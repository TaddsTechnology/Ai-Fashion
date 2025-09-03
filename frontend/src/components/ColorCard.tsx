import React from 'react';

interface ColorCardProps {
  color: string;
  name: string;
  size?: 'sm' | 'md' | 'lg';
  showHex?: boolean;
}

const ColorCard: React.FC<ColorCardProps> = ({
  color,
  name,
  size = 'md',
  showHex = false
}) => {
  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-16 h-16',
    lg: 'w-20 h-20'
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 flex flex-col">
      <div 
        className={`${sizeClasses[size]} rounded-lg mb-3`}
        style={{ backgroundColor: color }}
      />
      <span className="text-gray-700 font-medium">{name}</span>
      {showHex && <span className="text-xs text-gray-500 mt-1">{color}</span>}
    </div>
  );
};

export default ColorCard; 