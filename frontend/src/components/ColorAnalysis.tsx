import React from 'react';
import { Link } from 'react-router-dom';
import { Seasons } from '../lib/types/seasons';
import type { SeasonInfo } from '../lib/types/seasons';
import { seasonsData } from '../lib/data/seasons';
import { colorPalettes } from '../lib/data/colorPalettes';
import { ExternalLink } from 'lucide-react';

interface ColorAnalysisProps {
  season?: Seasons;
}

const ColorAnalysis: React.FC<ColorAnalysisProps> = ({ season }) => {
  if (!season) return null;

  const seasonInfo: SeasonInfo = seasonsData[season];
  const palette = colorPalettes[season];

  return (
    <div className="bg-white rounded-xl p-6 shadow-lg">
      <h3 className={`text-2xl font-bold mb-4 ${seasonInfo.textColor}`}>
        {season}
      </h3>
      <p className="text-gray-600 mb-6">{seasonInfo.description}</p>
      
      {/* Initial color palette */}
      <div className="mb-6">
        <h4 className="text-lg font-medium text-gray-800 mb-3">Your Color Palette</h4>
        <div className="grid grid-cols-6 gap-2 mb-4">
          {palette?.flatteringColors.slice(0, 6).map((color, index) => (
            <div
              key={index}
              className="w-10 h-10 rounded-full shadow-md relative group"
              style={{ backgroundColor: color.hex }}
            >
              <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 bg-black bg-opacity-50 flex items-center justify-center transition-opacity">
                <span className="text-white text-xs">{color.name}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Colors to avoid */}
      <div className="mb-6">
        <h4 className="text-lg font-medium text-gray-800 mb-3">Colors to Avoid</h4>
        <div className="grid grid-cols-4 gap-2">
          {palette?.colorsToAvoid.slice(0, 4).map((color, index) => (
            <div
              key={index}
              className="w-8 h-8 rounded-full shadow-md relative group"
              style={{ backgroundColor: color.hex }}
            >
              <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 bg-black bg-opacity-50 flex items-center justify-center transition-opacity">
                <span className="text-white text-xs">{color.name}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Link to detailed color palette page */}
      <Link 
        to={`/colors/${season}`}
        className="inline-flex items-center text-purple-600 font-medium hover:text-purple-800 transition-colors"
      >
        View detailed color palette
        <ExternalLink className="w-4 h-4 ml-2" />
      </Link>
    </div>
  );
};

export default ColorAnalysis; 