import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { monkSkinTones } from '../lib/data/monkSkinTones';
import { ArrowLeft, X, Info } from 'lucide-react';
import ColorCard from '../components/ColorCard';
import ColorPaletteCard from '../components/ColorPaletteCard';
import SeasonalColorType from '../components/SeasonalColorType';
import { getSeasonalType, colorPalettes, fetchColorSuggestions } from '../utils/colorMatching';

interface ColorSuggestion {
  skin_tone: string;
  suitable_colors: string;
}

// Define the type for the seasonal color palettes
interface SeasonalColorPalette {
  recommended: Array<{ color: string; name: string }>;
  avoid: Array<{ color: string; name: string }>;
}

const MonkColorPalettePage = () => {
  const { monkId } = useParams<{ monkId: string }>();
  const navigate = useNavigate();
  const [skinTone, setSkinTone] = useState(monkId ? monkSkinTones[monkId] : null);
  const [colorSuggestions, setColorSuggestions] = useState<ColorSuggestion[]>([]);

  useEffect(() => {
    // If no skin tone is provided or it's invalid, redirect to demo page
    if (!monkId || !monkSkinTones[monkId]) {
      navigate('/demo/recommendations');
    } else {
      setSkinTone(monkSkinTones[monkId]);
      
      // Fetch color suggestions for the seasonal type
      if (monkSkinTones[monkId]) {
        const seasonalType = getSeasonalType(monkSkinTones[monkId].hexCode);
        fetchColorSuggestionsData(seasonalType);
      }
    }
  }, [monkId, navigate]);
  
  // Function to fetch color suggestions from the backend
  const fetchColorSuggestionsData = async (seasonalType: string) => {
    try {
      const suggestions = await fetchColorSuggestions(seasonalType);
      setColorSuggestions(suggestions);
    } catch (error) {
      console.error('Error fetching color suggestions:', error);
    }
  };

  if (!skinTone) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <p className="text-gray-500">Loading color palette...</p>
        </div>
      </Layout>
    );
  }

  // Find adjacent skin tones for comparison
  const monkIds = Object.keys(monkSkinTones);
  const currentIndex = monkIds.indexOf(monkId || '');
  const prevMonkId = currentIndex > 0 ? monkIds[currentIndex - 1] : null;
  const nextMonkId = currentIndex < monkIds.length - 1 ? monkIds[currentIndex + 1] : null;

  // Generate additional colors based on the skin tone
  const additionalColors = [
    { name: "Light Shade", hex: lightenColor(skinTone.hexCode, 30) },
    { name: "Medium Shade", hex: lightenColor(skinTone.hexCode, 15) },
    { name: "Dark Shade", hex: darkenColor(skinTone.hexCode, 15) },
    { name: "Deeper Shade", hex: darkenColor(skinTone.hexCode, 30) },
  ];
  
  // Get the seasonal type for this skin tone
  const seasonalType = getSeasonalType(skinTone.hexCode);

  // Get the seasonal color palette, with type checking
  const seasonalPalette = colorPalettes[seasonalType as keyof typeof colorPalettes] as unknown as SeasonalColorPalette;

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <button 
          onClick={() => navigate(-1)}
          className="flex items-center text-purple-600 mb-6 hover:text-purple-800 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Recommendations
        </button>

        {/* Monk Skin Tone Scale */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-10">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Monk Skin Tone Scale</h2>
          <div className="flex overflow-x-auto pb-4 space-x-4">
            {Object.values(monkSkinTones).map((tone) => (
              <button
                key={tone.id}
                onClick={() => navigate(`/monk-colors/${tone.id}`)}
                className={`flex-shrink-0 flex flex-col items-center ${
                  tone.id === monkId ? 'ring-4 ring-purple-500 ring-offset-2' : ''
                }`}
              >
                <div 
                  className="w-16 h-16 rounded-full shadow-md mb-2"
                  style={{ backgroundColor: tone.hexCode }}
                />
                <span className="text-xs font-medium text-gray-700">{tone.userFriendlyName}</span>
                <span className="text-xs text-gray-500">{tone.seasonalType}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Main Color Palette */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-10">
          <div className="flex items-center mb-4">
            <div 
              className="w-12 h-12 rounded-full shadow-md mr-4"
              style={{ backgroundColor: skinTone.hexCode }}
            />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {skinTone.userFriendlyName} Color Palette
              </h1>
              <p className="text-sm text-purple-600 font-medium">
                {skinTone.seasonalType}
              </p>
              <p className="text-gray-600">
                {skinTone.hexCode}
              </p>
              <div className="mt-2">
                <SeasonalColorType skinToneHex={skinTone.hexCode} />
              </div>
            </div>
          </div>
          
          <p className="text-gray-600 mb-4 max-w-3xl">
            {skinTone.description}
          </p>
          
          {/* Seasonal Color Information */}
          <div className="mb-8 p-4 bg-gray-50 rounded-lg flex items-start">
            <Info className="w-5 h-5 text-purple-500 mt-1 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">
                {seasonalType} Color Characteristics
              </h3>
              <p className="text-gray-600">
                {seasonalType.includes('Spring') && 
                  "Spring color palettes feature warm, clear, and bright colors that reflect the freshness of spring. These colors are typically warm-toned with yellow undertones."}
                {seasonalType.includes('Summer') && 
                  "Summer color palettes consist of cool, soft, and muted colors with blue undertones. These colors have a gentle, delicate quality reminiscent of summer haze."}
                {seasonalType.includes('Autumn') && 
                  "Autumn color palettes include warm, muted, and rich colors with golden undertones. These colors reflect the earthy, warm tones of fall foliage."}
                {seasonalType.includes('Winter') && 
                  "Winter color palettes feature cool, clear, and intense colors with blue undertones. These colors are typically high-contrast and dramatic."}
              </p>
            </div>
          </div>

          {/* Color Palette Card */}
          <ColorPaletteCard 
            skinToneId={monkId || ''}
            flatteringColors={skinTone.flatteringColors}
            colorsToAvoid={skinTone.colorsToAvoid}
            showViewAllButton={false}
          />
        </div>

        {/* Color Suggestions from API */}
        {colorSuggestions.length > 0 && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-10">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">
              Suggested Colors for {seasonalType}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {colorSuggestions.map((suggestion, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-medium text-gray-800 mb-2">
                    {suggestion.skin_tone}
                  </h3>
                  <p className="text-gray-600">
                    {suggestion.suitable_colors}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Seasonal Color Palette */}
        {seasonalPalette && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-10">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">
              {seasonalType} Seasonal Palette
            </h2>
            <p className="text-gray-600 mb-6">
              These colors are specifically selected for your seasonal color type and will complement your natural coloring.
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {seasonalPalette.recommended.map((color: { color: string; name: string }, index: number) => (
                <div key={`seasonal-${index}`} className="flex flex-col items-center">
                  <div 
                    className="w-16 h-16 rounded-full shadow-md mb-2"
                    style={{ backgroundColor: color.color }}
                  />
                  <span className="text-sm text-gray-700 text-center">{color.name}</span>
                </div>
              ))}
            </div>
            
            <h3 className="text-xl font-semibold text-gray-900 mt-8 mb-4">Colors to Avoid</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              {seasonalPalette.avoid.map((color: { color: string; name: string }, index: number) => (
                <div key={`avoid-${index}`} className="flex flex-col items-center">
                  <div 
                    className="w-12 h-12 rounded-full shadow-md mb-2 relative"
                    style={{ backgroundColor: color.color }}
                  >
                    <div className="absolute inset-0 flex items-center justify-center">
                      <X className="w-6 h-6 text-white opacity-70" />
                    </div>
                  </div>
                  <span className="text-sm text-gray-700 text-center">{color.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Extended Color Palette */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-10">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Extended Color Palette
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-4">Complementary Colors</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {skinTone.flatteringColors.slice(0, 3).map((color) => (
                  <ColorCard 
                    key={color.hex}
                    color={color.hex}
                    name={color.name}
                    showHex={true}
                  />
                ))}
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-4">Accent Colors</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {skinTone.flatteringColors.slice(3).map((color) => (
                  <ColorCard 
                    key={color.hex}
                    color={color.hex}
                    name={color.name}
                    showHex={true}
                  />
                ))}
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-4">Neutral Tones</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {additionalColors.slice(0, 2).map((color) => (
                  <ColorCard 
                    key={color.hex}
                    color={color.hex}
                    name={color.name}
                    showHex={true}
                  />
                ))}
                <ColorCard 
                  color="#FFFFFF"
                  name="White"
                  showHex={true}
                />
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-4">Shades</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {additionalColors.slice(2).map((color) => (
                  <ColorCard 
                    key={color.hex}
                    color={color.hex}
                    name={color.name}
                    showHex={true}
                  />
                ))}
                <ColorCard 
                  color="#000000"
                  name="Black"
                  showHex={true}
                />
              </div>
            </div>
          </div>
          
          <div className="mt-8">
            <h3 className="text-lg font-medium text-gray-800 mb-4">All Colors</h3>
            <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-8 xl:grid-cols-12 gap-4">
              {[...skinTone.flatteringColors, ...additionalColors].map((color, index) => (
                <div key={`${color.hex}-${index}`} className="flex flex-col items-center">
                  <div 
                    className="w-12 h-12 rounded-full shadow-md mb-2"
                    style={{ backgroundColor: color.hex }}
                  />
                  <span className="text-xs text-gray-500">{color.hex}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Outfit Recommendations */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Outfit Recommendations
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-4">Clothing Items</h3>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <div className="w-3 h-3 rounded-full bg-purple-500 mt-1.5 mr-3"></div>
                  <span>Tops in {skinTone.flatteringColors[0].name.toLowerCase()}, {skinTone.flatteringColors[1].name.toLowerCase()}, or {skinTone.flatteringColors[2].name.toLowerCase()}</span>
                </li>
                <li className="flex items-start">
                  <div className="w-3 h-3 rounded-full bg-purple-500 mt-1.5 mr-3"></div>
                  <span>Neutral bottoms that complement your color palette</span>
                </li>
                <li className="flex items-start">
                  <div className="w-3 h-3 rounded-full bg-purple-500 mt-1.5 mr-3"></div>
                  <span>Accessories in {skinTone.flatteringColors[3].name.toLowerCase()} or {skinTone.flatteringColors[4].name.toLowerCase()} to add pops of color</span>
                </li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-4">Styling Tips</h3>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <div className="w-3 h-3 rounded-full bg-purple-500 mt-1.5 mr-3"></div>
                  <span>Wear your best colors near your face for the most flattering effect</span>
                </li>
                <li className="flex items-start">
                  <div className="w-3 h-3 rounded-full bg-purple-500 mt-1.5 mr-3"></div>
                  <span>Mix and match within your palette for harmonious outfits</span>
                </li>
                <li className="flex items-start">
                  <div className="w-3 h-3 rounded-full bg-purple-500 mt-1.5 mr-3"></div>
                  <span>If you want to wear colors to avoid, keep them away from your face</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Navigation between skin tones */}
        <div className="flex justify-between mt-8">
          {prevMonkId ? (
            <button
              onClick={() => navigate(`/monk-colors/${prevMonkId}`)}
              className="flex items-center text-purple-600 hover:text-purple-800 transition-colors"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Previous: {monkSkinTones[prevMonkId].userFriendlyName}
            </button>
          ) : (
            <div></div>
          )}
          
          {nextMonkId && (
            <button
              onClick={() => navigate(`/monk-colors/${nextMonkId}`)}
              className="flex items-center text-purple-600 hover:text-purple-800 transition-colors"
            >
              Next: {monkSkinTones[nextMonkId].userFriendlyName}
              <ArrowLeft className="w-5 h-5 ml-2 transform rotate-180" />
            </button>
          )}
        </div>
      </div>
    </Layout>
  );
};

// Helper functions for color manipulation
function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : { r: 0, g: 0, b: 0 };
}

function rgbToHex(r: number, g: number, b: number): string {
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}

function lightenColor(hex: string, amount: number): string {
  const { r, g, b } = hexToRgb(hex);
  const newR = Math.min(255, r + amount);
  const newG = Math.min(255, g + amount);
  const newB = Math.min(255, b + amount);
  return rgbToHex(Math.round(newR), Math.round(newG), Math.round(newB));
}

function darkenColor(hex: string, amount: number): string {
  const { r, g, b } = hexToRgb(hex);
  const newR = Math.max(0, r - amount);
  const newG = Math.max(0, g - amount);
  const newB = Math.max(0, b - amount);
  return rgbToHex(Math.round(newR), Math.round(newG), Math.round(newB));
}

export default MonkColorPalettePage; 