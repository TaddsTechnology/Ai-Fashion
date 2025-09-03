// AI Fashion API Service
// Handles all API calls to the deployed backend

import API_CONFIG, { buildApiUrl, getApiHeaders, getFileUploadHeaders } from '../config/api.js';

class ApiService {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = buildApiUrl(endpoint, options.params);
    
    const config = {
      method: options.method || 'GET',
      headers: options.headers || getApiHeaders(),
      ...options.fetchOptions,
    };

    if (options.body) {
      config.body = typeof options.body === 'string' 
        ? options.body 
        : JSON.stringify(options.body);
    }

    if (API_CONFIG.DEBUG) {
      console.log('API Request:', { url, config });
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (API_CONFIG.DEBUG) {
        console.log('API Response:', data);
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Health check
  async checkHealth() {
    return this.request(API_CONFIG.ENDPOINTS.HEALTH);
  }

  // Analyze skin tone from uploaded image
  async analyzeSkinTone(imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);

    const url = buildApiUrl(API_CONFIG.ENDPOINTS.ANALYZE_SKIN_TONE);
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: getFileUploadHeaders(),
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Skin tone analysis error:', error);
      throw error;
    }
  }

  // Get color recommendations
  async getColorRecommendations(skinTone, options = {}) {
    return this.request(API_CONFIG.ENDPOINTS.COLOR_RECOMMENDATIONS, {
      params: {
        skin_tone: skinTone,
        limit: options.limit || 50,
        occasion: options.occasion || 'casual',
        use_mst: options.useMst !== false, // Default to true
        ...options
      }
    });
  }

  // Get color palettes
  async getColorPalettes(skinTone, hexColor = null) {
    return this.request(API_CONFIG.ENDPOINTS.COLOR_PALETTES, {
      params: {
        skin_tone: skinTone,
        hex_color: hexColor,
      }
    });
  }

  // Enhanced MST recommendations
  async getEnhancedRecommendations(monkTone, options = {}) {
    return this.request(API_CONFIG.ENDPOINTS.ENHANCED_RECOMMENDATIONS, {
      params: {
        monk_tone: monkTone,
        occasion: options.occasion || 'casual',
        limit: options.limit || 20,
        use_database: options.useDatabase !== false, // Default to true
      }
    });
  }

  // Get seasonal analysis
  async getSeasonalAnalysis(monkTone) {
    return this.request(API_CONFIG.ENDPOINTS.SEASONAL_ANALYSIS, {
      params: { monk_tone: monkTone }
    });
  }

  // Get styling guide
  async getStylingGuide(monkTone) {
    return this.request(API_CONFIG.ENDPOINTS.STYLING_GUIDE, {
      params: { monk_tone: monkTone }
    });
  }

  // Get quick palette
  async getQuickPalette(monkTone, count = 8) {
    return this.request(API_CONFIG.ENDPOINTS.QUICK_PALETTE, {
      params: { 
        monk_tone: monkTone,
        count 
      }
    });
  }

  // Get MST information
  async getMstInfo() {
    return this.request(API_CONFIG.ENDPOINTS.MST_INFO);
  }

  // Get occasion-specific colors
  async getOccasionColors(monkTone, occasions = 'work,casual,party,formal') {
    return this.request(API_CONFIG.ENDPOINTS.OCCASION_COLORS, {
      params: {
        monk_tone: monkTone,
        occasions
      }
    });
  }

  // Utility method to test backend connectivity
  async testConnection() {
    try {
      const health = await this.checkHealth();
      const mstInfo = await this.getMstInfo();
      
      return {
        connected: true,
        backend_url: this.baseURL,
        health_status: health.status,
        available_colors: mstInfo.data?.total_tones || 0,
        features: mstInfo.data?.features || [],
      };
    } catch (error) {
      return {
        connected: false,
        backend_url: this.baseURL,
        error: error.message,
      };
    }
  }
}

// Export singleton instance
export default new ApiService();
