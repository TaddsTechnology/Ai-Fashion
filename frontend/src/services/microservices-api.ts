// Microservices API Integration
import { API_BASE_URL } from '../config/api';

export interface SkinAnalysisRequest {
  file: File;
}

export interface SkinAnalysisResponse {
  monk_code: string;
  confidence: number;
  season: string;
  undertone: string;
  contrast: string;
  monk_hex: string;
  derived_hex: string;
  success: boolean;
}

export interface ColorPaletteResponse {
  season: string;
  contrast: string;
  occasion?: string;
  colors: Array<{
    hex: string;
    name: string;
    type: 'base' | 'accent' | 'neutral' | 'occasion';
  }>;
  total_colors: number;
  source: string;
}

export interface Product {
  id: number;
  name: string;
  brand: string;
  category: string;
  subcategory?: string;
  color: string;
  hex_color?: string;
  price: number;
  currency?: string;
  description?: string;
  image_url?: string;
  product_url?: string;
  color_score?: number;
  total_score?: number;
  matched_color?: string;
  explanation?: string;
}

export interface RecommendationsRequest {
  season: string;
  undertone: string;
  contrast: string;
  occasion?: string;
  gender?: string;
  budget_min?: number;
  budget_max?: number;
  outfit_categories?: string;
  makeup_categories?: string;
}

export interface RecommendationsResponse {
  season: string;
  undertone: string;
  contrast: string;
  occasion: string;
  palette: Array<{
    hex: string;
    name: string;
    type: string;
  }>;
  recommended_outfits: Product[];
  recommended_makeup: Product[];
  algorithm: {
    outfit_weights: Record<string, number>;
    makeup_weights: Record<string, number>;
  };
  total_candidates: {
    outfits: number;
    makeup: number;
  };
}

export interface GatewayHealthResponse {
  gateway_status: string;
  overall_status: string;
  services: Record<string, {
    status: string;
    url: string;
    error?: string;
  }>;
}

class MicroservicesAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Health check for gateway and all services
  async checkHealth(): Promise<GatewayHealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    return response.json();
  }

  // Detection Service: Analyze skin tone from photo
  async analyzeSkinTone(file: File): Promise<SkinAnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/analyze-skin-tone`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Analysis failed: ${response.status}`);
    }

    return response.json();
  }

  // Palette Service: Get color palette by season
  async getColorPalette(
    season: string,
    contrast: string = 'medium',
    occasion?: string
  ): Promise<ColorPaletteResponse> {
    const params = new URLSearchParams({
      season,
      contrast,
    });

    if (occasion) {
      params.append('occasion', occasion);
    }

    const response = await fetch(`${this.baseUrl}/api/color-palettes?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to get color palette: ${response.status}`);
    }

    return response.json();
  }

  // Palette Service: Get contrast-specific colors
  async getContrastColors(
    season: string,
    contrastLevel: string = 'medium'
  ): Promise<ColorPaletteResponse> {
    const params = new URLSearchParams({
      season,
      contrast_level: contrastLevel,
    });

    const response = await fetch(`${this.baseUrl}/api/contrast-colors?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to get contrast colors: ${response.status}`);
    }

    return response.json();
  }

  // Recommendation Service: Get personalized product recommendations
  async getRecommendations(
    request: RecommendationsRequest
  ): Promise<RecommendationsResponse> {
    const params = new URLSearchParams({
      season: request.season,
      undertone: request.undertone,
      contrast: request.contrast,
      occasion: request.occasion || 'casual',
      gender: request.gender || 'Unisex',
      budget_min: (request.budget_min || 0).toString(),
      budget_max: (request.budget_max || 1000).toString(),
      outfit_categories: request.outfit_categories || 'tops,bottoms,dresses',
      makeup_categories: request.makeup_categories || 'foundation,lipstick,eyeshadow',
    });

    const response = await fetch(`${this.baseUrl}/api/recommendations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params,
    });

    if (!response.ok) {
      throw new Error(`Failed to get recommendations: ${response.status}`);
    }

    return response.json();
  }

  // Recommendation Service: Get color alternatives
  async getColorAlternatives(
    originalColor: string,
    season: string,
    limit: number = 5
  ): Promise<{ alternatives: Array<{ hex: string; name: string; similarity: number }> }> {
    const params = new URLSearchParams({
      original_color: originalColor,
      season,
      limit: limit.toString(),
    });

    const response = await fetch(`${this.baseUrl}/api/color-alternatives?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to get color alternatives: ${response.status}`);
    }

    return response.json();
  }

  // Legacy endpoints for backward compatibility
  async getLegacyColorRecommendations(skinTone: string): Promise<any> {
    const params = new URLSearchParams({ skin_tone: skinTone });
    const response = await fetch(`${this.baseUrl}/api/color-recommendations?${params}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get color recommendations: ${response.status}`);
    }

    return response.json();
  }

  // Complete workflow: Analyze skin tone and get full recommendations
  async getCompleteAnalysis(
    file: File,
    options: {
      occasion?: string;
      gender?: string;
      budget_min?: number;
      budget_max?: number;
      outfit_categories?: string;
      makeup_categories?: string;
    } = {}
  ): Promise<{
    analysis: SkinAnalysisResponse;
    palette: ColorPaletteResponse;
    recommendations: RecommendationsResponse;
  }> {
    // Step 1: Analyze skin tone
    const analysis = await this.analyzeSkinTone(file);

    if (!analysis.success) {
      throw new Error('Skin tone analysis failed');
    }

    // Step 2: Get color palette
    const palette = await this.getColorPalette(
      analysis.season,
      analysis.contrast,
      options.occasion
    );

    // Step 3: Get product recommendations
    const recommendations = await this.getRecommendations({
      season: analysis.season,
      undertone: analysis.undertone,
      contrast: analysis.contrast,
      occasion: options.occasion || 'casual',
      gender: options.gender || 'Unisex',
      budget_min: options.budget_min || 0,
      budget_max: options.budget_max || 1000,
      outfit_categories: options.outfit_categories || 'tops,bottoms,dresses',
      makeup_categories: options.makeup_categories || 'foundation,lipstick,eyeshadow',
    });

    return {
      analysis,
      palette,
      recommendations,
    };
  }
}

// Export singleton instance
export const microservicesAPI = new MicroservicesAPI();
export default microservicesAPI;
