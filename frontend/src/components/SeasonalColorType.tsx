import React from 'react';
import { getSeasonalType } from '../utils/colorMatching';

interface SeasonalColorTypeProps {
  skinToneHex: string;
  className?: string;
}

const SeasonalColorType: React.FC<SeasonalColorTypeProps> = ({ skinToneHex, className = '' }) => {
  const seasonalType = getSeasonalType(skinToneHex);
  
  // Define background colors for each seasonal type
  const seasonalBackgrounds = {
    'Light Spring': 'bg-yellow-50',
    'Warm Spring': 'bg-amber-50',
    'Clear Spring': 'bg-orange-50',
    'Light Summer': 'bg-blue-50',
    'Cool Summer': 'bg-indigo-50',
    'Soft Summer': 'bg-purple-50',
    'Soft Autumn': 'bg-orange-50',
    'Warm Autumn': 'bg-amber-100',
    'Deep Autumn': 'bg-orange-100',
    'Clear Winter': 'bg-blue-100',
    'Cool Winter': 'bg-indigo-100',
    'Deep Winter': 'bg-purple-100'
  };
  
  // Define text colors for each seasonal type
  const seasonalTextColors = {
    'Light Spring': 'text-yellow-800',
    'Warm Spring': 'text-amber-800',
    'Clear Spring': 'text-orange-800',
    'Light Summer': 'text-blue-800',
    'Cool Summer': 'text-indigo-800',
    'Soft Summer': 'text-purple-800',
    'Soft Autumn': 'text-orange-800',
    'Warm Autumn': 'text-amber-800',
    'Deep Autumn': 'text-orange-900',
    'Clear Winter': 'text-blue-900',
    'Cool Winter': 'text-indigo-900',
    'Deep Winter': 'text-purple-900'
  };
  
  // Get the background and text color for the current seasonal type
  const bgColor = seasonalBackgrounds[seasonalType] || 'bg-gray-100';
  const textColor = seasonalTextColors[seasonalType] || 'text-gray-800';
  
  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full ${bgColor} ${textColor} ${className}`}>
      <span className="text-sm font-medium">{seasonalType}</span>
    </div>
  );
};

export default SeasonalColorType; 