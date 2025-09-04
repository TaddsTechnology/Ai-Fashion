import React from 'react';
import { Link } from 'react-router-dom';
import { Check, X, Crown, ExternalLink } from 'lucide-react';

interface ColorInfo {
  name: string;
  hex: string;
}

interface SimplifiedColorPaletteProps {
  skinToneId: string;
  flatteringColors: ColorInfo[];
  colorsToAvoid: ColorInfo[];
  showAll?: boolean;
}

const SimplifiedColorPalette: React.FC<SimplifiedColorPaletteProps> = ({
  skinToneId,
  flatteringColors,
  colorsToAvoid,
  showAll = false
}) => {
  // Limit the number of colors shown in the simplified view
  const displayFlatteringColors = showAll ? flatteringColors : flatteringColors.slice(0, 3);
  const displayColorsToAvoid = showAll ? colorsToAvoid : colorsToAvoid.slice(0, 2);

  return (
    <div className="bg-white rounded-xl p-6 shadow-lg">
      <div className="flex items-center mb-6">
        <Crown className="w-6 h-6 text-purple-600 mr-2" />
        <h2 className="text-xl font-bold text-gray-900">Your Color Palette</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Colors That Flatter You */}
        <div>
          <div className="flex items-center mb-4">
            <Check className="w-5 h-5 text-green-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-800">Colors That Flatter You</h3>
          </div>
          
          <div className="space-y-3">
            {displayFlatteringColors.map((color) => (
              <div key={color.hex} className="flex items-center">
                <div 
                  className="w-12 h-12 rounded-lg shadow-md mr-3"
                  style={{ backgroundColor: color.hex }}
                />
                <span className="text-gray-700">{color.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Colors to Avoid */}
        <div>
          <div className="flex items-center mb-4">
            <X className="w-5 h-5 text-red-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-800">Colors to Avoid</h3>
          </div>
          
          <div className="space-y-3">
            {displayColorsToAvoid.map((color) => (
              <div key={color.hex} className="flex items-center">
                <div 
                  className="w-12 h-12 rounded-lg shadow-md mr-3"
                  style={{ backgroundColor: color.hex }}
                />
                <span className="text-gray-700">{color.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {!showAll && (
        <div className="mt-6 text-center">
          <Link 
            to={`/monk-colors/${skinToneId}`}
            className="inline-flex items-center text-purple-600 font-medium hover:text-purple-800 transition-colors"
          >
            View complete color palette
            <ExternalLink className="w-4 h-4 ml-2" />
          </Link>
        </div>
      )}
    </div>
  );
};

export default SimplifiedColorPalette; 