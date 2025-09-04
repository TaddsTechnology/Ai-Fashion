import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { colorPalettes } from '../lib/data/colorPalettes';
import { ArrowLeft, Check, X } from 'lucide-react';

const ColorPalettePage = () => {
  const { skinTone } = useParams<{ skinTone: string }>();
  const navigate = useNavigate();
  const [palette, setPalette] = useState(skinTone && colorPalettes[skinTone] ? colorPalettes[skinTone] : null);

  useEffect(() => {
    // If no skin tone is provided or it's invalid, redirect to demo page
    if (!skinTone || !colorPalettes[skinTone]) {
      navigate('/demo/recommendations');
    } else {
      setPalette(colorPalettes[skinTone]);
    }
  }, [skinTone, navigate]);

  if (!palette) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <p className="text-gray-500">Loading color palette...</p>
        </div>
      </Layout>
    );
  }

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

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-10">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {palette.skinTone} Color Palette
          </h1>
          <p className="text-gray-600 mb-8 max-w-3xl">
            {palette.description}
          </p>

          {/* Flattering Colors Section */}
          <div className="mb-12">
            <div className="flex items-center mb-6">
              <Check className="w-6 h-6 text-green-500 mr-3" />
              <h2 className="text-2xl font-semibold text-gray-900">Colors That Flatter You</h2>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
              {palette.flatteringColors.map((color) => (
                <div key={color.hex} className="flex flex-col items-center">
                  <div 
                    className="w-20 h-20 rounded-full shadow-md mb-3"
                    style={{ backgroundColor: color.hex }}
                  />
                  <span className="text-sm font-medium text-gray-700">{color.name}</span>
                  <span className="text-xs text-gray-500">{color.hex}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Colors to Avoid Section */}
          <div>
            <div className="flex items-center mb-6">
              <X className="w-6 h-6 text-red-500 mr-3" />
              <h2 className="text-2xl font-semibold text-gray-900">Colors to Avoid</h2>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {palette.colorsToAvoid.map((color) => (
                <div key={color.hex} className="flex flex-col items-center">
                  <div 
                    className="w-16 h-16 rounded-full shadow-md mb-3 relative"
                    style={{ backgroundColor: color.hex }}
                  >
                    <div className="absolute inset-0 flex items-center justify-center">
                      <X className="w-8 h-8 text-white opacity-70" />
                    </div>
                  </div>
                  <span className="text-sm font-medium text-gray-700">{color.name}</span>
                  <span className="text-xs text-gray-500">{color.hex}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Extended Color Palette */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-10">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Extended Color Palette
          </h2>
          
          <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-8 xl:grid-cols-12 gap-4">
            {/* Generate extended colors from the color 2.txt file */}
            {skinTone && colorPalettes[skinTone]?.flatteringColors.concat(
              Object.values(colorPalettes)
                .filter(p => p.skinTone === skinTone)
                .flatMap(p => p.flatteringColors)
            ).map((color: { hex: string; name: string }, index: number) => (
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
                  <span>Tops in {palette.flatteringColors[0].name.toLowerCase()}, {palette.flatteringColors[1].name.toLowerCase()}, or {palette.flatteringColors[2].name.toLowerCase()}</span>
                </li>
                <li className="flex items-start">
                  <div className="w-3 h-3 rounded-full bg-purple-500 mt-1.5 mr-3"></div>
                  <span>Neutral bottoms that complement your color palette</span>
                </li>
                <li className="flex items-start">
                  <div className="w-3 h-3 rounded-full bg-purple-500 mt-1.5 mr-3"></div>
                  <span>Accessories in {palette.flatteringColors[3].name.toLowerCase()} or {palette.flatteringColors[4].name.toLowerCase()} to add pops of color</span>
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
      </div>
    </Layout>
  );
};

export default ColorPalettePage; 