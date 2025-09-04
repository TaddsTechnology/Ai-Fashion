import React from 'react';
import { Check, X, Crown, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface ColorInfo {
  name: string;
  hex: string;
}

interface VisualColorPaletteProps {
  skinToneId: string;
  flatteringColors: ColorInfo[];
  colorsToAvoid: ColorInfo[];
  showViewAllLink?: boolean;
}

const VisualColorPalette: React.FC<VisualColorPaletteProps> = ({
  skinToneId,
  flatteringColors,
  colorsToAvoid,
  showViewAllLink = true
}) => {
  // Limit the number of colors shown in the simplified view
  const displayFlatteringColors = flatteringColors.slice(0, 4);
  const displayColorsToAvoid = colorsToAvoid.slice(0, 3);

  return (
    <div className="bg-white rounded-xl p-6 shadow-lg">
      <div className="flex items-center mb-6">
        <Crown className="w-6 h-6 text-purple-600 mr-2" />
        <h2 className="text-xl font-bold text-gray-900">Your Color Palette</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Colors That Flatter You */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Check className="w-5 h-5 text-green-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-800">Colors That Flatter You</h3>
            </div>
            {showViewAllLink && (
              <Link 
                to={`/monk-colors/${skinToneId}`}
                className="text-sm text-purple-600 hover:text-purple-800 flex items-center"
              >
                More <ChevronRight className="w-4 h-4 ml-1" />
              </Link>
            )}
          </div>
          
          <div className="space-y-4">
            {displayFlatteringColors.map((color) => (
              <div key={color.hex} className="flex items-center bg-gray-50 p-3 rounded-lg">
                <div 
                  className="w-14 h-14 rounded-lg shadow-md mr-4 flex-shrink-0"
                  style={{ backgroundColor: color.hex }}
                />
                <span className="text-gray-700 font-medium">{color.name}</span>
              </div>
            ))}
            {flatteringColors.length > displayFlatteringColors.length && (
              <div className="flex items-center text-gray-500 text-sm italic pl-3">
                +{flatteringColors.length - displayFlatteringColors.length} more colors
              </div>
            )}
          </div>
        </div>

        {/* Colors to Avoid */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <X className="w-5 h-5 text-red-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-800">Colors to Avoid</h3>
            </div>
            {showViewAllLink && (
              <Link 
                to={`/monk-colors/${skinToneId}`}
                className="text-sm text-purple-600 hover:text-purple-800 flex items-center"
              >
                More <ChevronRight className="w-4 h-4 ml-1" />
              </Link>
            )}
          </div>
          
          <div className="space-y-4">
            {displayColorsToAvoid.map((color) => (
              <div key={color.hex} className="flex items-center bg-gray-50 p-3 rounded-lg">
                <div 
                  className="w-14 h-14 rounded-lg shadow-md mr-4 flex-shrink-0 relative"
                  style={{ backgroundColor: color.hex }}
                >
                  <div className="absolute inset-0 flex items-center justify-center">
                    <X className="w-6 h-6 text-white opacity-70" />
                  </div>
                </div>
                <span className="text-gray-700 font-medium">{color.name}</span>
              </div>
            ))}
            {colorsToAvoid.length > displayColorsToAvoid.length && (
              <div className="flex items-center text-gray-500 text-sm italic pl-3">
                +{colorsToAvoid.length - displayColorsToAvoid.length} more colors
              </div>
            )}
          </div>
        </div>
      </div>

      {showViewAllLink && (
        <div className="mt-8 text-center">
          <Link 
            to={`/monk-colors/${skinToneId}`}
            className="inline-block px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            View complete color palette
          </Link>
        </div>
      )}
    </div>
  );
};

export default VisualColorPalette; 