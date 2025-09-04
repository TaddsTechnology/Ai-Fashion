interface ColorRecommendation {
  color: string;
  name: string;
}

interface ColorRecommendations {
  recommended: ColorRecommendation[];
  avoid: ColorRecommendation[];
}

interface OutfitRecommendations {
  recommended: ColorRecommendation[];
  avoid: ColorRecommendation[];
}

// Enhanced Monk Scale colors with more accurate hex codes
const monkScaleColors = {
  monk1: '#f6ede4', // Very Light
  monk2: '#f3e7db',
  monk3: '#f7ead0',
  monk4: '#eadaba', // Medium Light
  monk5: '#d7bd96',
  monk6: '#a07e56',
  monk7: '#825c43', // Medium Dark
  monk8: '#604134',
  monk9: '#3a312a',
  monk10: '#292420' // Very Dark
};

// Color palettes by season based on color theory
const seasonalColorPalettes = {
  // Spring palettes
  'Light Spring': {
    recommended: [
      { color: '#FFF9D7', name: 'Light Yellow' },
      { color: '#F1EB9C', name: 'Pale Yellow' },
      { color: '#F5E1A4', name: 'Cream Yellow' },
      { color: '#F8CFA9', name: 'Peach' },
      { color: '#FCC89B', name: 'Light Peach' },
      { color: '#D9EA9A', name: 'Light Green' },
      { color: '#A5DFD3', name: 'Mint' },
      { color: '#A4DBE8', name: 'Sky Blue' }
    ],
    avoid: [
      { color: '#000000', name: 'Black' },
      { color: '#5C068C', name: 'Deep Purple' },
      { color: '#341902', name: 'Dark Brown' },
      { color: '#890C58', name: 'Burgundy' }
    ]
  },
  'Warm Spring': {
    recommended: [
      { color: '#FCE300', name: 'Bright Yellow' },
      { color: '#FDD26E', name: 'Golden Yellow' },
      { color: '#FFCD00', name: 'Sunflower Yellow' },
      { color: '#FFB81C', name: 'Amber' },
      { color: '#F0B323', name: 'Honey' },
      { color: '#FF8200', name: 'Orange' },
      { color: '#DA291C', name: 'Warm Red' },
      { color: '#6CC24A', name: 'Fresh Green' }
    ],
    avoid: [
      { color: '#000000', name: 'Black' },
      { color: '#003DA5', name: 'Navy Blue' },
      { color: '#484A51', name: 'Charcoal' },
      { color: '#5C068C', name: 'Deep Purple' }
    ]
  },
  'Clear Spring': {
    recommended: [
      { color: '#FFF9D7', name: 'Light Yellow' },
      { color: '#FCE300', name: 'Bright Yellow' },
      { color: '#FDD26E', name: 'Golden Yellow' },
      { color: '#FFCD00', name: 'Sunflower Yellow' },
      { color: '#FFB81C', name: 'Amber' },
      { color: '#FF8200', name: 'Orange' },
      { color: '#DA291C', name: 'Warm Red' },
      { color: '#00A499', name: 'Turquoise' }
    ],
    avoid: [
      { color: '#000000', name: 'Black' },
      { color: '#5C462B', name: 'Dark Brown' },
      { color: '#453536', name: 'Charcoal' },
      { color: '#484A51', name: 'Dark Grey' }
    ]
  },
  
  // Summer palettes
  'Light Summer': {
    recommended: [
      { color: '#C6DAE7', name: 'Powder Blue' },
      { color: '#99D6EA', name: 'Light Blue' },
      { color: '#9BCBEB', name: 'Sky Blue' },
      { color: '#B8C9E1', name: 'Periwinkle' },
      { color: '#ECB3CB', name: 'Light Pink' },
      { color: '#DD9CDF', name: 'Lavender' },
      { color: '#F67599', name: 'Rose Pink' },
      { color: '#6DCDB8', name: 'Mint Green' }
    ],
    avoid: [
      { color: '#000000', name: 'Black' },
      { color: '#5C068C', name: 'Deep Purple' },
      { color: '#DA291C', name: 'Bright Red' },
      { color: '#FF8200', name: 'Orange' }
    ]
  },
  'Cool Summer': {
    recommended: [
      { color: '#F395C7', name: 'Pink' },
      { color: '#F57EB6', name: 'Rose' },
      { color: '#E277CD', name: 'Orchid' },
      { color: '#C964CF', name: 'Lilac' },
      { color: '#A277A6', name: 'Mauve' },
      { color: '#00A9E0', name: 'Azure' },
      { color: '#71C5E8', name: 'Sky Blue' },
      { color: '#00B0B9', name: 'Turquoise' }
    ],
    avoid: [
      { color: '#000000', name: 'Black' },
      { color: '#FF8200', name: 'Orange' },
      { color: '#DA291C', name: 'Bright Red' },
      { color: '#FFB81C', name: 'Amber' }
    ]
  },
  'Soft Summer': {
    recommended: [
      { color: '#F1BDC8', name: 'Soft Pink' },
      { color: '#FFA3B5', name: 'Coral Pink' },
      { color: '#9BCBEB', name: 'Soft Blue' },
      { color: '#6DCDB8', name: 'Seafoam Green' },
      { color: '#9CAF88', name: 'Sage Green' },
      { color: '#A39382', name: 'Taupe' },
      { color: '#C4A4A7', name: 'Mauve' },
      { color: '#D592AA', name: 'Dusty Rose' }
    ],
    avoid: [
      { color: '#000000', name: 'Black' },
      { color: '#FF8200', name: 'Orange' },
      { color: '#FCE300', name: 'Bright Yellow' },
      { color: '#DA291C', name: 'Bright Red' }
    ]
  },
  
  // Autumn palettes
  'Soft Autumn': {
    recommended: [
      { color: '#F5E1A4', name: 'Soft Yellow' },
      { color: '#FCD299', name: 'Peach' },
      { color: '#DFD1A7', name: 'Beige' },
      { color: '#BBC592', name: 'Sage' },
      { color: '#A3AA83', name: 'Olive' },
      { color: '#A09958', name: 'Moss Green' },
      { color: '#B58150', name: 'Camel' },
      { color: '#DB864E', name: 'Terracotta' }
    ],
    avoid: [
      { color: '#000000', name: 'Black' },
      { color: '#FF1493', name: 'Hot Pink' },
      { color: '#00A3E1', name: 'Bright Blue' },
      { color: '#FCE300', name: 'Bright Yellow' }
    ]
  },
  'Warm Autumn': {
    recommended: [
      { color: '#FFCD00', name: 'Golden Yellow' },
      { color: '#B4A91F', name: 'Mustard' },
      { color: '#A09958', name: 'Olive' },
      { color: '#A6631B', name: 'Rust' },
      { color: '#946037', name: 'Copper' },
      { color: '#9A3324', name: 'Brick Red' },
      { color: '#C4622D', name: 'Burnt Orange' },
      { color: '#EF7200', name: 'Pumpkin' }
    ],
    avoid: [
      { color: '#000000', name: 'Black' },
      { color: '#FF1493', name: 'Hot Pink' },
      { color: '#00A3E1', name: 'Bright Blue' },
      { color: '#F395C7', name: 'Pastel Pink' }
    ]
  },
  'Deep Autumn': {
    recommended: [
      { color: '#A6631B', name: 'Rust' },
      { color: '#946037', name: 'Copper' },
      { color: '#7C4D3A', name: 'Brown' },
      { color: '#9A3324', name: 'Brick Red' },
      { color: '#5C462B', name: 'Dark Brown' },
      { color: '#205C40', name: 'Forest Green' },
      { color: '#00778B', name: 'Teal' },
      { color: '#046A38', name: 'Emerald' }
    ],
    avoid: [
      { color: '#F395C7', name: 'Pastel Pink' },
      { color: '#99D6EA', name: 'Light Blue' },
      { color: '#FFF9D7', name: 'Pale Yellow' },
      { color: '#6DCDB8', name: 'Mint Green' }
    ]
  },
  
  // Winter palettes
  'Clear Winter': {
    recommended: [
      { color: '#FEFEFE', name: 'Pure White' },
      { color: '#00A3E1', name: 'Bright Blue' },
      { color: '#0077C8', name: 'Cobalt Blue' },
      { color: '#E40046', name: 'True Red' },
      { color: '#CE0037', name: 'Cherry Red' },
      { color: '#C724B1', name: 'Fuchsia' },
      { color: '#963CBD', name: 'Violet' },
      { color: '#009775', name: 'Emerald' }
    ],
    avoid: [
      { color: '#F5E1A4', name: 'Cream Yellow' },
      { color: '#A09958', name: 'Moss Green' },
      { color: '#B58150', name: 'Camel' },
      { color: '#DB864E', name: 'Terracotta' }
    ]
  },
  'Cool Winter': {
    recommended: [
      { color: '#FEFEFE', name: 'Pure White' },
      { color: '#0057B8', name: 'Royal Blue' },
      { color: '#004B87', name: 'Navy Blue' },
      { color: '#84329B', name: 'Purple' },
      { color: '#963CBD', name: 'Violet' },
      { color: '#C724B1', name: 'Magenta' },
      { color: '#E3006D', name: 'Hot Pink' },
      { color: '#CE0037', name: 'Cool Red' }
    ],
    avoid: [
      { color: '#F5E1A4', name: 'Cream Yellow' },
      { color: '#A09958', name: 'Moss Green' },
      { color: '#B58150', name: 'Camel' },
      { color: '#DB864E', name: 'Terracotta' }
    ]
  },
  'Deep Winter': {
    recommended: [
      { color: '#FEFEFE', name: 'Pure White' },
      { color: '#0057B8', name: 'Royal Blue' },
      { color: '#004B87', name: 'Navy Blue' },
      { color: '#002D72', name: 'Deep Blue' },
      { color: '#84329B', name: 'Purple' },
      { color: '#CE0037', name: 'Cool Red' },
      { color: '#009775', name: 'Emerald' },
      { color: '#00594C', name: 'Deep Green' }
    ],
    avoid: [
      { color: '#F5E1A4', name: 'Cream Yellow' },
      { color: '#FCC89B', name: 'Light Peach' },
      { color: '#D9EA9A', name: 'Light Green' },
      { color: '#A5DFD3', name: 'Mint' }
    ]
  }
};

// Map Monk skin tone to seasonal color type
function getSeasonalTypeFromMonkTone(monkTone: number): string {
  // Map according to the backend mapping for consistency
  const mapping: { [key: number]: string } = {
    1: 'Light Spring',
    2: 'Light Spring',
    3: 'Clear Spring',
    4: 'Warm Spring',
    5: 'Soft Autumn',
    6: 'Warm Autumn',
    7: 'Deep Autumn',
    8: 'Deep Winter',
    9: 'Cool Winter',
    10: 'Clear Winter'
  };
  
  return mapping[monkTone] || 'Clear Spring';
}

function findClosestMonkTone(hexColor: string): number {
  const r = parseInt(hexColor.slice(1, 3), 16);
  const g = parseInt(hexColor.slice(3, 5), 16);
  const b = parseInt(hexColor.slice(5, 7), 16);

  const differences = Object.entries(monkScaleColors).map(([monk, color]) => {
    const mr = parseInt(color.slice(1, 3), 16);
    const mg = parseInt(color.slice(3, 5), 16);
    const mb = parseInt(color.slice(5, 7), 16);

    const diff = Math.sqrt(
      Math.pow(r - mr, 2) + Math.pow(g - mg, 2) + Math.pow(b - mb, 2)
    );

    return { monk: parseInt(monk.replace('monk', '')), difference: diff };
  });

  return differences.reduce((prev, curr) => 
    curr.difference < prev.difference ? curr : prev
  ).monk;
}

export function getRecommendedColors(skinToneHex: string): ColorRecommendations {
  const monkTone = findClosestMonkTone(skinToneHex);
  const seasonalType = getSeasonalTypeFromMonkTone(monkTone);

  // Return the seasonal color palette based on the determined type
  return seasonalColorPalettes[seasonalType] || {
      recommended: [
        { color: '#FF6B6B', name: 'Coral Red' },
        { color: '#4ECDC4', name: 'Turquoise' },
        { color: '#45B7D1', name: 'Ocean Blue' },
        { color: '#96CEB4', name: 'Sage Green' },
        { color: '#FFAFCC', name: 'Soft Pink' },
        { color: '#9B5DE5', name: 'Royal Purple' }
      ],
      avoid: [
        { color: '#FFD700', name: 'Bright Yellow' },
        { color: '#FF4500', name: 'Orange Red' },
        { color: '#32CD32', name: 'Lime Green' },
        { color: '#FF1493', name: 'Deep Pink' }
      ]
    };
}

export function getOutfitRecommendations(skinToneHex: string): OutfitRecommendations {
  const monkTone = findClosestMonkTone(skinToneHex);
  const seasonalType = getSeasonalTypeFromMonkTone(monkTone);
  
  // Get the seasonal color palette
  const palette = seasonalColorPalettes[seasonalType] || {
    recommended: [],
    avoid: []
  };
  
  // Select a subset of colors specifically for outfits
    return {
      recommended: [
      ...palette.recommended.slice(0, 4),
        { color: '#000080', name: 'Navy Blue' },
      { color: '#FFFFFF', name: 'White' },
      { color: '#000000', name: 'Black' },
      { color: '#808080', name: 'Grey' }
    ],
    avoid: palette.avoid
  };
}

// Export the seasonal color palettes for use in other components
export const colorPalettes = seasonalColorPalettes;

// Export a function to get the seasonal type based on skin tone
export function getSeasonalType(skinToneHex: string): string {
  const monkTone = findClosestMonkTone(skinToneHex);
  return getSeasonalTypeFromMonkTone(monkTone);
}

// Import API configuration
import { API_ENDPOINTS, buildApiUrl } from '../config/api';

// Function to fetch color suggestions from the backend API
export const fetchColorSuggestions = async (skinTone: string): Promise<any> => {
  try {
    const response = await fetch(buildApiUrl(API_ENDPOINTS.COLOR_SUGGESTIONS, { skin_tone: skinTone }));
    if (!response.ok) {
      throw new Error('Failed to fetch color suggestions');
    }
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error('Error fetching color suggestions:', error);
    return [];
  }
};
