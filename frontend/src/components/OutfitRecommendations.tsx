import React from 'react';
import { getRecommendedColors } from '../utils/colorMatching';

interface OutfitRecommendationsProps {
  skinToneHex: string;
}

const OutfitRecommendations: React.FC<OutfitRecommendationsProps> = ({ skinToneHex }) => {
  const recommendations = getRecommendedColors(skinToneHex);

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Recommended Outfits</h3>
      <div className="grid grid-cols-2 gap-4">
        {recommendations.recommended.map((color, index) => (
          <div key={index} className="flex items-center gap-2">
            <div 
              className="w-8 h-8 rounded-full"
              style={{ backgroundColor: color.color }}
            />
            <span>{color.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OutfitRecommendations; 