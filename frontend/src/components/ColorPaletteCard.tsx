import React from 'react';
import { Check, X, Crown, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface ColorInfo {
  name: string;
  hex: string;
}

interface ColorPaletteCardProps {
  skinToneId: string;
  flatteringColors: ColorInfo[];
  colorsToAvoid: ColorInfo[];
  showViewAllButton?: boolean;
}

const ColorPaletteCard: React.FC<ColorPaletteCardProps> = ({
  skinToneId,
  flatteringColors,
  colorsToAvoid,
  showViewAllButton = true
}) => {
  // Limit the number of colors shown
  const displayFlatteringColors = flatteringColors.slice(0, 4);
  const displayColorsToAvoid = colorsToAvoid.slice(0, 4);

  return (
    <div className="bg-white rounded-xl p-6 shadow-lg">
      <div className="flex items-center mb-6">
        <Crown className="w-6 h-6 text-purple-600 mr-2" />
        <h2 className="text-xl font-bold text-gray-900">Your Color Palette</h2>
      </div>

      <div className="space-y-8">
        {/* Colors That Flatter You */}
        <div>
          <div className="flex items-center mb-4">
            <Check className="w-5 h-5 text-green-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-800">Colors That Flatter You</h3>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            {displayFlatteringColors.map((color) => (
              <div key={color.hex} className="bg-gray-50 p-4 rounded-lg">
                <div 
                  className="w-full h-16 rounded-lg shadow-md mb-3"
                  style={{ backgroundColor: color.hex }}
                />
                <span className="text-gray-700 font-medium">{color.name}</span>
              </div>
            ))}
          </div>
          
          {showViewAllButton && flatteringColors.length > displayFlatteringColors.length && (
            <Link 
              to={`/monk-colors/${skinToneId}`}
              className="mt-3 inline-flex items-center text-sm text-purple-600 hover:text-purple-800"
            >
              View all flattering colors <ChevronRight className="w-4 h-4 ml-1" />
            </Link>
          )}
        </div>

        {/* Colors to Avoid */}
        <div>
          <div className="flex items-center mb-4">
            <X className="w-5 h-5 text-red-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-800">Colors to Avoid</h3>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            {displayColorsToAvoid.map((color) => (
              <div key={color.hex} className="bg-gray-50 p-4 rounded-lg">
                <div 
                  className="w-full h-16 rounded-lg shadow-md mb-3 relative"
                  style={{ backgroundColor: color.hex }}
                >
                  <div className="absolute inset-0 flex items-center justify-center">
                    <X className="w-6 h-6 text-white opacity-70" />
                  </div>
                </div>
                <span className="text-gray-700 font-medium">{color.name}</span>
              </div>
            ))}
          </div>
          
          {showViewAllButton && colorsToAvoid.length > displayColorsToAvoid.length && (
            <Link 
              to={`/monk-colors/${skinToneId}`}
              className="mt-3 inline-flex items-center text-sm text-purple-600 hover:text-purple-800"
            >
              View all colors to avoid <ChevronRight className="w-4 h-4 ml-1" />
            </Link>
          )}
        </div>
      </div>

      {showViewAllButton && (
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

export default ColorPaletteCard; 