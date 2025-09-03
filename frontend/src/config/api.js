// AI Fashion Frontend API Configuration
// Handles connection to deployed backend service

const API_CONFIG = {
  // Get base URL from environment variable or default to local
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:10000',
  
  // API endpoints
  ENDPOINTS: {
    HEALTH: '/health',
    ANALYZE_SKIN_TONE: '/analyze-skin-tone',
    COLOR_RECOMMENDATIONS: '/api/color-recommendations',
    COLOR_PALETTES: '/api/color-palettes-db',
    
    // Enhanced MST endpoints
    ENHANCED_RECOMMENDATIONS: '/api/v2/color-recommendations/enhanced',
    SEASONAL_ANALYSIS: '/api/v2/seasonal-analysis',
    STYLING_GUIDE: '/api/v2/styling-guide',
    QUICK_PALETTE: '/api/v2/quick-palette',
    MST_INFO: '/api/v2/mst-info',
    OCCASION_COLORS: '/api/v2/occasion-colors',
  },
  
  // Request timeout in milliseconds
  TIMEOUT: 30000,
  
  // Enable debug logging in development
  DEBUG: import.meta.env.VITE_DEBUG_API === 'true' || import.meta.env.DEV,
};

// Helper function to build full URL
export const buildApiUrl = (endpoint, params = {}) => {
  const url = new URL(endpoint, API_CONFIG.BASE_URL);
  
  // Add query parameters
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.append(key, value);
    }
  });
  
  if (API_CONFIG.DEBUG) {
    console.log('API URL:', url.toString());
  }
  
  return url.toString();
};

// API request headers
export const getApiHeaders = () => ({
  'Content-Type': 'application/json',
  'Accept': 'application/json',
});

// API request headers for file upload
export const getFileUploadHeaders = () => ({
  // Don't set Content-Type for multipart/form-data, let the browser set it
  'Accept': 'application/json',
});

// Named export for endpoints (for backward compatibility)
export const API_ENDPOINTS = API_CONFIG.ENDPOINTS;

export default API_CONFIG;
