import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import Button from '../components/Button';
import ColorPicker from '../components/ColorPicker';
import { AlertCircle, Palette, Wand, Camera, Sparkles, Heart, Check, X, Crown, RefreshCcw, ShoppingBag } from 'lucide-react';
import { getRecommendedColors } from '../utils/colorMatching';

// Define interfaces for type safety
interface ColorRecommendation {
  color: string;
  name: string;
}

interface ColorRecommendations {
  recommended: ColorRecommendation[];
  avoid: ColorRecommendation[];
}

interface CategoryType {
  id: string;
  name: string;
  colors: string[];
  icon: React.ReactNode;
  description: string;
}

interface ColorProfileResult {
  skin_tone_type: string;
  profile_color: string;
  matched_color: string;
  color_values: number[];
}

interface SkinAnalysisResult {
  monk_skin_tone: string;
  monk_hex: string;
  derived_hex_code: string;
}

const DemoTryOn = () => {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState<string>('lipstick');
  const [selectedColor, setSelectedColor] = useState<string>();
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [colorProfile, setColorProfile] = useState<ColorProfileResult | null>(null);
  const [colorRecommendations, setColorRecommendations] = useState<ColorRecommendations | null>(null);
  const [skinAnalysis, setSkinAnalysis] = useState<SkinAnalysisResult | null>(null);
  
  useEffect(() => {
    const image = sessionStorage.getItem('capturedImage');
    if (!image) {
      navigate('/demo/process');
    } else {
      setCapturedImage(image);
    }

    const analysisData = sessionStorage.getItem('skinAnalysis');
    if (analysisData) {
      const parsedData = JSON.parse(analysisData) as SkinAnalysisResult;
      setSkinAnalysis(parsedData);
      
      if (parsedData?.monk_hex) {
        const recommendations = getRecommendedColors(parsedData.monk_hex);
        setColorRecommendations(recommendations);
      }
    }
  }, [navigate]);

  // Helper function to get makeup colors based on Monk skin tone
  const getMakeupColors = (monkScale: string) => {
    // Base colors for different Monk scales
    const makeupPalettes = {
      // Light skin tones (Monk 1-3)
      light: {
        foundation: ['#FFE0BD', '#FFD1A1', '#FFC183', '#FFDEB3', '#FFE4C4'],
        blush: ['#FFB6C1', '#FF69B4', '#DB7093', '#FFC0CB', '#FFE4E1'],
        lipstick: ['#FF1493', '#FF69B4', '#DC143C', '#FF4500', '#FF6B6B'],
        eyeshadow: ['#DDA0DD', '#DA70D6', '#BA55D3', '#9370DB', '#8B008B'],
        eyeliner: ['#2F4F4F', '#4B0082', '#800000', '#8B4513', '#000000']
      },
      // Medium skin tones (Monk 4-7)
      medium: {
        foundation: ['#DEB887', '#D2B48C', '#CD853F', '#BC8F8F', '#F4A460'],
        blush: ['#E9967A', '#FF7F50', '#FF6347', '#CD5C5C', '#DC143C'],
        lipstick: ['#8B0000', '#800000', '#B22222', '#DC143C', '#FF4500'],
        eyeshadow: ['#8B4513', '#A0522D', '#6B4423', '#8B008B', '#4B0082'],
        eyeliner: ['#2F4F4F', '#000000', '#8B4513', '#4A0404', '#1A1A1A']
      },
      // Deep skin tones (Monk 8-10)
      deep: {
        foundation: ['#8B4513', '#A0522D', '#8B5742', '#996515', '#8B4513'],
        blush: ['#CD5C5C', '#DC143C', '#8B0000', '#800000', '#B22222'],
        lipstick: ['#8B0000', '#800000', '#4A0404', '#DC143C', '#CC0033'],
        eyeshadow: ['#8B4513', '#800000', '#4B0082', '#000080', '#2F4F4F'],
        eyeliner: ['#000000', '#1A1A1A', '#4A0404', '#2F4F4F', '#4B0082']
      }
    };

    // Determine skin tone category based on Monk scale
    const skinToneCategory = 
      parseInt(monkScale) <= 3 ? 'light' :
      parseInt(monkScale) <= 7 ? 'medium' : 'deep';

    return makeupPalettes[skinToneCategory];
  };

  // Get makeup colors based on skin analysis
  const makeupColors = skinAnalysis ? getMakeupColors(skinAnalysis.monk_skin_tone.replace('Monk', '').replace('monk', '')) : null;

  const categories: CategoryType[] = makeupColors ? [
    {
      id: 'foundation',
      name: 'Foundation',
      icon: <Crown className="w-5 h-5" />,
      colors: makeupColors.foundation,
      description: 'Find your perfect match'
    },
    {
      id: 'blush',
      name: 'Blush',
      icon: <Heart className="w-5 h-5" />,
      colors: makeupColors.blush,
      description: 'Add a natural flush'
    },
    {
      id: 'lipstick',
      name: 'Lipstick',
      icon: <Sparkles className="w-5 h-5" />,
      colors: makeupColors.lipstick,
      description: 'Perfect your pout'
    },
    {
      id: 'eyeshadow',
      name: 'Eyeshadow',
      icon: <Palette className="w-5 h-5" />,
      colors: makeupColors.eyeshadow,
      description: 'Define your eyes'
    },
    {
      id: 'eyeliner',
      name: 'Eyeliner',
      icon: <Wand className="w-5 h-5" />,
      colors: makeupColors.eyeliner,
      description: 'Frame your gaze'
    }
  ] : [];

  const currentCategory = categories.find(cat => cat.id === selectedCategory);

  if (!capturedImage) {
    return (
      <Layout>
        <div className="min-h-[60vh] flex items-center justify-center bg-gradient-to-br from-purple-50 via-pink-50 to-white">
          <div className="text-center bg-white p-8 rounded-3xl shadow-2xl max-w-md mx-auto border border-purple-100">
            <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4 animate-bounce" />
            <p className="text-gray-600 text-lg mb-4">We need your photo to create your personalized color palette. Let's get started!</p>
            <Button variant="primary" icon={Camera} onClick={() => navigate('/demo/process')}>
              Upload Your Photo
            </Button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-white">
        {/* Header Section */}
        <div className="bg-white border-b border-purple-100">
          <div className="max-w-7xl mx-auto py-6 px-4">
            <div className="text-center mb-4">
              <span className="inline-flex items-center gap-2 bg-purple-50 px-4 py-2 rounded-full text-purple-700 font-medium text-sm mb-2">
                <Crown className="w-4 h-4" />
                Color Analysis Complete
              </span>
              <h1 className="text-3xl font-bold text-gray-900">Your Perfect Color Palette</h1>
              <p className="text-gray-600 mt-2">Colors that make you look and feel amazing</p>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column: Skin Analysis & Photo */}
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-200 to-pink-200 transform -skew-y-3"></div>
                  <img 
                    src={capturedImage || ''} 
                    alt="Your photo" 
                    className="relative w-full h-64 object-cover"
                  />
                </div>
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Skin Analysis</h3>
                  {skinAnalysis && (
                    <div className="space-y-4">
                      <div className="bg-purple-50 p-4 rounded-xl">
                        <p className="text-sm text-gray-600">Detected Skin Tone</p>
                        <p className="font-medium text-gray-900">
                          {(() => {
                            const monkScale = parseInt(skinAnalysis.monk_skin_tone.replace('Monk', '').replace('monk', ''));
                            if (monkScale <= 3) return 'Light Skin Tone';
                            if (monkScale <= 7) return 'Medium Skin Tone';
                            return 'Deep Skin Tone';
                          })()
                          }
                        </p>
                      </div>
                      <div className="flex gap-4">
                        {[skinAnalysis.monk_hex, skinAnalysis.derived_hex_code].map((color, idx) => (
                          <div key={idx} className="flex-1 bg-gray-50 p-3 rounded-xl">
                            <div 
                              className="w-full h-12 rounded-lg mb-2"
                              style={{ backgroundColor: color }}
                            />
                            <p className="text-xs text-center text-gray-600">{color}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Single New Photo Button */}
              <div className="flex gap-3">
                <Button
                  variant="secondary"
                  icon={RefreshCcw}
                  onClick={() => navigate('/demo/process')}
                  className="flex-1"
                >
                  New Photo
                </Button>
              </div>
            </div>

            {/* Middle Column: Color Recommendations */}
            <div className="lg:col-span-2 space-y-6">
              {/* Outfit Color Analysis */}
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                  <Crown className="w-5 h-5 text-purple-500" />
                  Your Color Palette
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Recommended Colors */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <Check className="w-5 h-5 text-green-500" />
                      <h4 className="font-medium text-gray-900">Colors That Flatter You</h4>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      {colorRecommendations?.recommended.map((rec: ColorRecommendation, idx: number) => (
                        <div key={idx} className="flex items-center gap-2 bg-gray-50 p-3 rounded-xl">
                          <div 
                            className="w-10 h-10 rounded-lg shadow-inner"
                            style={{ backgroundColor: rec.color }}
                          />
                          <span className="text-sm text-gray-700">{rec.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Colors to Avoid */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <X className="w-5 h-5 text-red-500" />
                      <h4 className="font-medium text-gray-900">Colors to Avoid</h4>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      {colorRecommendations?.avoid.map((rec: ColorRecommendation, idx: number) => (
                        <div key={idx} className="flex items-center gap-2 bg-gray-50 p-3 rounded-xl">
                          <div 
                            className="w-10 h-10 rounded-lg shadow-inner"
                            style={{ backgroundColor: rec.color }}
                          />
                          <span className="text-sm text-gray-700">{rec.name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Recommended Color Palettes Section */}
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-500" />
                  Recommended Color Palettes
                </h3>
                <div className="space-y-6">
                  {/* Category Selection */}
                  <div className="flex overflow-x-auto gap-3 pb-2 scrollbar-hide">
                    {categories.map((category) => (
                      <button
                        key={category.id}
                        onClick={() => setSelectedCategory(category.id)}
                        className={`flex-shrink-0 flex items-center gap-2 px-4 py-3 rounded-xl transition-all duration-300 ${
                          selectedCategory === category.id
                            ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                            : 'hover:bg-purple-50 text-gray-700 border border-gray-100'
                        }`}
                      >
                        <span className={selectedCategory === category.id ? 'text-white' : 'text-purple-500'}>
                          {category.icon}
                        </span>
                        <span className="font-medium whitespace-nowrap">{category.name}</span>
                      </button>
                    ))}
                  </div>

                  {/* Color Selection */}
                  {currentCategory && (
                    <div className="bg-gray-50 rounded-xl p-4">
                      <p className="text-sm text-gray-600 mb-4">{currentCategory.description}</p>
                      <ColorPicker
                        colors={currentCategory.colors}
                        selectedColor={selectedColor}
                        onChange={setSelectedColor}
                      />
                    </div>
                  )}
                </div>

                {/* Single View Products Button */}
                <div className="mt-6 pt-6 border-t border-gray-100">
                  <Button
                    variant="primary"
                    icon={ShoppingBag}
                    onClick={() => navigate('/demo/recommendations')}
                    className="w-full sm:w-auto"
                  >
                    <span className="flex items-center gap-2">
                      View Recommended Products
                      <ShoppingBag className="w-4 h-4" />
                    </span>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default DemoTryOn;