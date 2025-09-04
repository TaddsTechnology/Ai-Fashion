// API Configuration - Updated for HuggingFace backend
export const VITE_API_URL = import.meta.env.VITE_API_URL || 'https://taddsteam-ai-fashion.hf.space';

// Keep API_BASE_URL for backward compatibility
export const API_BASE_URL = VITE_API_URL;

console.log('VITE_API_URL:', VITE_API_URL);
console.log('API_BASE_URL:', API_BASE_URL);

// API endpoints using VITE_API_URL
export const API_ENDPOINTS = {
  ANALYZE_SKIN_TONE: `${VITE_API_URL}/analyze-skin-tone`,
  COLOR_SUGGESTIONS: `${VITE_API_URL}/color-suggestions`,
  COLOR_RECOMMENDATIONS: `${VITE_API_URL}/api/color-recommendations`,
  COLOR_PALETTES_DB: `${VITE_API_URL}/api/color-palettes-db`,
  ALL_COLORS: `${VITE_API_URL}/api/colors/all`,
  MAKEUP_DATA: `${VITE_API_URL}/data/`,
  APPAREL: `${VITE_API_URL}/apparel`,
  HEALTH: `${VITE_API_URL}/health`,
};

// Helper function to build API URLs
export const buildApiUrl = (endpoint: string, params?: Record<string, any>): string => {
  const url = new URL(endpoint);
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  
  return url.toString();
};
