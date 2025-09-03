/**
 * Color utility functions for the AI Fashion app
 */

/**
 * Interface for a color with name and hex
 */
interface Color {
  name: string;
  hex: string;
}

/**
 * Get a color name from a hex code
 * Generates a descriptive name based on RGB values since database provides the actual color names
 */
export const getColorNameFromHex = (hex: string): string => {
  if (!hex) return 'Unknown Color';
  
  // Clean the hex string
  const cleanHex = hex.startsWith('#') ? hex : `#${hex}`;
  
  // Generate a descriptive name based on RGB values
  return generateColorNameFromHex(cleanHex);
};

/**
 * Generate a descriptive color name from hex code based on RGB analysis
 */
const generateColorNameFromHex = (hex: string): string => {
  // Remove # if present
  const cleanHex = hex.replace('#', '');
  
  // Convert to RGB
  const r = parseInt(cleanHex.substring(0, 2), 16);
  const g = parseInt(cleanHex.substring(2, 4), 16);
  const b = parseInt(cleanHex.substring(4, 6), 16);
  
  // Calculate brightness and saturation
  const brightness = (r + g + b) / 3;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const saturation = max > 0 ? (max - min) / max : 0;
  
  // Determine base color
  let baseColor = '';
  let intensity = '';
  
  // Determine intensity based on brightness and saturation
  if (brightness > 220) {
    intensity = 'Light ';
  } else if (brightness > 180) {
    intensity = 'Soft ';
  } else if (brightness < 60) {
    intensity = 'Deep ';
  } else if (brightness < 100) {
    intensity = 'Dark ';
  }
  
  // Add saturation modifiers
  if (saturation < 0.1) {
    if (brightness > 200) {
      baseColor = 'White';
    } else if (brightness > 150) {
      baseColor = 'Light Gray';
    } else if (brightness > 100) {
      baseColor = 'Gray';
    } else if (brightness > 50) {
      baseColor = 'Dark Gray';
    } else {
      baseColor = 'Black';
    }
    return baseColor;
  }
  
  // Determine dominant color channel
  if (r >= g && r >= b) {
    // Red dominant
    if (g > b + 30) {
      baseColor = 'Orange';
    } else if (b > g + 20) {
      baseColor = 'Pink';
    } else {
      baseColor = 'Red';
    }
  } else if (g >= r && g >= b) {
    // Green dominant
    if (r > b + 20) {
      baseColor = 'Yellow Green';
    } else if (b > r + 20) {
      baseColor = 'Teal';
    } else {
      baseColor = 'Green';
    }
  } else {
    // Blue dominant
    if (r > g + 20) {
      baseColor = 'Purple';
    } else if (g > r + 20) {
      baseColor = 'Cyan';
    } else {
      baseColor = 'Blue';
    }
  }
  
  // Special cases for common colors
  if (r > 200 && g < 100 && b < 100) {
    baseColor = 'Red';
  } else if (g > 200 && r < 100 && b < 100) {
    baseColor = 'Green';
  } else if (b > 200 && r < 100 && g < 100) {
    baseColor = 'Blue';
  } else if (r > 180 && g > 180 && b < 100) {
    baseColor = 'Yellow';
  } else if (r > 180 && b > 180 && g < 100) {
    baseColor = 'Magenta';
  } else if (g > 180 && b > 180 && r < 100) {
    baseColor = 'Cyan';
  }
  
  return `${intensity}${baseColor}`.trim();
};

/**
 * Find the closest matching color from a predefined set
 */
export const findClosestColor = (targetHex: string, colorSet: Color[]): Color | null => {
  if (!targetHex || !colorSet || colorSet.length === 0) return null;
  
  const targetRgb = hexToRgb(targetHex);
  if (!targetRgb) return null;
  
  let closestColor: Color | null = null;
  let minDistance = Infinity;
  
  for (const color of colorSet) {
    const colorRgb = hexToRgb(color.hex);
    if (!colorRgb) continue;
    
    const distance = Math.sqrt(
      Math.pow(targetRgb.r - colorRgb.r, 2) +
      Math.pow(targetRgb.g - colorRgb.g, 2) +
      Math.pow(targetRgb.b - colorRgb.b, 2)
    );
    
    if (distance < minDistance) {
      minDistance = distance;
      closestColor = color;
    }
  }
  
  return closestColor;
};

/**
 * Convert hex color to RGB
 */
export const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
  const cleanHex = hex.replace('#', '');
  
  if (cleanHex.length !== 6) return null;
  
  const r = parseInt(cleanHex.substring(0, 2), 16);
  const g = parseInt(cleanHex.substring(2, 4), 16);
  const b = parseInt(cleanHex.substring(4, 6), 16);
  
  if (isNaN(r) || isNaN(g) || isNaN(b)) return null;
  
  return { r, g, b };
};

/**
 * Convert RGB to hex
 */
export const rgbToHex = (r: number, g: number, b: number): string => {
  const toHex = (n: number) => {
    const hex = Math.round(Math.max(0, Math.min(255, n))).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };
  
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`.toUpperCase();
};

/**
 * Calculate color brightness (0-255)
 */
export const getColorBrightness = (hex: string): number => {
  const rgb = hexToRgb(hex);
  if (!rgb) return 0;
  
  // Use standard brightness formula
  return Math.round(0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b);
};

/**
 * Determine if a color is light or dark
 */
export const isLightColor = (hex: string): boolean => {
  return getColorBrightness(hex) > 128;
};
