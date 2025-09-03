import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { Star, Sparkles, Crown, Shirt, Palette } from 'lucide-react';
import ProductRecommendations from '../components/ProductRecommendations';
import FeedbackPopup from '../components/FeedbackPopup';
import { API_BASE_URL, API_ENDPOINTS, buildApiUrl } from '../config/api';
import { monkSkinTones } from '../lib/data/monkSkinTones';
import { getColorNameFromHex } from '../utils/colorUtils';

// Consolidated interfaces
interface Product {
  id?: number;
  brand: string;
  name: string;
  price: string;
  rating: number;
  image: string;
  image_url: string;
  mst: string;
  desc: string;
  product_type?: string;
} 

interface SkinAnalysisResult {
  label: string;
  confidences: null;
  monk_skin_tone?: string;
  seasonal_type?: string;
}

interface ApiProduct {
  product?: string;
  name?: string;
  brand?: string;
  Brand?: string;
  Product_Name?: string;
  "Product Name"?: string;
  Price?: string;
  Image_URL?: string;
  "Image URL"?: string;
  imgSrc?: string;
  image?: string;
  image_url?: string;
  product_name?: string;
  price?: string;
  rating?: number;
  mst: string;
  desc: string;
  imgAlt: string;
  gender: string;
  masterCategory: string;
  subCategory: string;
  baseColour: string;
  usage: string;
  season: string;
  product_type?: string;
}

interface ColorInfo {
  name: string;
  hex: string;
}

interface ColorRecommendations {
  colors_that_suit?: ColorInfo[]; // Make optional to handle API variations
  colors?: ColorInfo[]; // API might return 'colors' instead
  colors_to_avoid?: ColorInfo[];
  seasonal_type?: string;
  monk_skin_tone?: string;
  message?: string;
  description?: string;
  database_source?: boolean; // Flag to indicate if data came from database
}

interface DatabaseColor {
  hex_code: string;
  color_name: string | null;
  suitable_skin_tone?: string;
  seasonal_palette?: string;
  category?: string;
}

const DemoRecommendations = () => {
  const [showFeedbackPopup, setShowFeedbackPopup] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowFeedbackPopup(true);
    }, 4000); // Show popup after 4 seconds

    return () => clearTimeout(timer);
  }, []);

  const handleFeedbackClose = () => {
    setShowFeedbackPopup(false);
  };
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [skinAnalysis, setSkinAnalysis] = useState<SkinAnalysisResult | null>(null);
  const [skinHex, setSkinHex] = useState<string>('#d7bd96'); // Default skin hex
  const [monkSkinTone, setMonkSkinTone] = useState<string>('Monk05'); // Default Monk skin tone
  const [activeTab, setActiveTab] = useState<'makeup' | 'outfit' | 'colors'>('makeup');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [availableFilters, setAvailableFilters] = useState<{[key: string]: string[]}>({});
  const [selectedFilters, setSelectedFilters] = useState<{[key: string]: string}>({});
  const [colorRecommendations, setColorRecommendations] = useState<ColorRecommendations | null>(null);
  const itemsPerPage = 24;

  // Handle page changes
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // Handle filter changes
  const handleFilterChange = (filters: {[key: string]: string}) => {
    setSelectedFilters(filters);
    setCurrentPage(1);
  };

  // Display error message if needed
  const displayError = () => {
    if (error) {
      return (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      );
    }
    return null;
  };

  // Fetch ALL database colors for the user's skin tone
  useEffect(() => {
    const fetchColorRecommendations = async () => {
      if (activeTab === 'colors' && (skinHex || monkSkinTone)) {
        try {
          console.log('Fetching ALL database colors for skin tone:', { skinHex, monkSkinTone });
          
          // Determine the seasonal type from Monk skin tone
          const seasonalTypeMap: { [key: string]: string } = {
            'Monk01': 'Light Spring',
            'Monk02': 'Light Spring', 
            'Monk03': 'Clear Spring',
            'Monk04': 'Warm Spring',
            'Monk05': 'Soft Autumn',
            'Monk06': 'Warm Autumn',
            'Monk07': 'Deep Autumn',
            'Monk08': 'Deep Winter',
            'Monk09': 'Cool Winter',
            'Monk10': 'Clear Winter'
          };
          
          const seasonalType = seasonalTypeMap[monkSkinTone] || 'Universal';
          console.log('Seasonal type determined:', seasonalType);
          
          // Build query parameters to get ALL colors for this skin tone
          const queryParams = new URLSearchParams();
          queryParams.append('limit', '500'); // Get more colors
          queryParams.append('skin_tone', seasonalType); // Use seasonal type
          
          console.log('Fetching all colors with params:', Object.fromEntries(queryParams));
          
          // Fetch all colors from database that match the skin tone
          let response = await fetch(buildApiUrl(API_ENDPOINTS.COLOR_PALETTES_DB, Object.fromEntries(queryParams)));
          
          if (response.ok) {
            const responseData = await response.json();
            console.log('Raw API response:', responseData);
            
            // Handle the actual API response format from color-palettes-db endpoint
            if (responseData.colors_that_suit || responseData.colors) {
              // Direct API response format
              const transformedData = {
                colors_that_suit: responseData.colors_that_suit || responseData.colors || [],
                colors: responseData.colors_that_suit || responseData.colors || [],
                colors_to_avoid: responseData.colors_to_avoid || [],
                seasonal_type: responseData.seasonal_type || seasonalType,
                monk_skin_tone: responseData.monk_skin_tone || monkSkinTone,
                description: responseData.description || `Based on your ${seasonalType} seasonal type and ${monkSkinTone} skin tone, here are colors from our database that complement your complexion.`,
                message: responseData.message || `Found ${(responseData.colors_that_suit || responseData.colors || []).length} color recommendations`,
                database_source: true
              };
              
              setColorRecommendations(transformedData);
              setError(null);
            } else {
              // Fallback: check if it's an array of colors (old format)
              const databaseColors = Array.isArray(responseData) ? responseData : 
                                   (responseData && Array.isArray(responseData.data) ? responseData.data : []);
                                   
              console.log(`Processing ${databaseColors.length} colors from database for ${seasonalType}`);
              
              // Transform database colors to color recommendations format with safety checks
              const recommendedColors = databaseColors
                .filter((color: any) => color && typeof color === 'object' && color.category === 'recommended')
                .map((color: any) => ({
                  name: color.color_name || getColorNameFromHex(color.hex_code) || 'Unknown Color',
                  hex: color.hex_code || '#000000'
                }))
                .filter((color: any) => color.hex && color.hex !== '#000000'); // Filter out invalid colors
              
              const colorsToAvoid = databaseColors
                .filter((color: any) => color && typeof color === 'object' && color.category === 'avoid')
                .map((color: any) => ({
                  name: color.color_name || getColorNameFromHex(color.hex_code) || 'Unknown Color',
                  hex: color.hex_code || '#000000'
                }))
                .filter((color: any) => color.hex && color.hex !== '#000000'); // Filter out invalid colors
              
              // Create comprehensive color recommendations from database
              const transformedData = {
                colors_that_suit: recommendedColors,
                colors: recommendedColors,
                colors_to_avoid: colorsToAvoid,
                seasonal_type: seasonalType,
                monk_skin_tone: monkSkinTone,
                description: `Based on your ${seasonalType} seasonal type and ${monkSkinTone} skin tone, here are all the colors from our database that complement your complexion.`,
                message: `Showing ${recommendedColors.length} recommended colors and ${colorsToAvoid.length} colors to avoid from our comprehensive database.`,
                database_source: true // Flag to indicate this came from database
              };
              
              setColorRecommendations(transformedData);
              setError(null);
            }
          } else {
            console.error('Database color service unavailable:', response.status);
            
            // Try the color palettes as fallback
            try {
              const fallbackParams = new URLSearchParams();
              if (monkSkinTone) {
                fallbackParams.append('skin_tone', monkSkinTone);
              }
              
              const fallbackResponse = await fetch(buildApiUrl(API_ENDPOINTS.COLOR_PALETTES_DB, Object.fromEntries(fallbackParams)));
              if (fallbackResponse.ok) {
                const fallbackData = await fallbackResponse.json();
                console.log('Using color palettes fallback:', fallbackData);
                
                // Safely extract colors with validation
                const extractedColors = fallbackData.colors || fallbackData.colors_that_suit || [];
                const extractedColorsToAvoid = fallbackData.colors_to_avoid || [];
                
                // Ensure we have valid arrays
                const safeColors = Array.isArray(extractedColors) ? extractedColors.filter(color => 
                  color && typeof color === 'object' && color.hex && color.name
                ) : [];
                
                const safeColorsToAvoid = Array.isArray(extractedColorsToAvoid) ? extractedColorsToAvoid.filter(color => 
                  color && typeof color === 'object' && color.hex && color.name
                ) : [];
                
                const transformedFallback = {
                  colors_that_suit: safeColors,
                  colors: safeColors,
                  colors_to_avoid: safeColorsToAvoid,
                  seasonal_type: fallbackData.seasonal_type || seasonalType,
                  monk_skin_tone: monkSkinTone,
                  description: fallbackData.description || `Color recommendations for ${seasonalType}`,
                  message: fallbackData.message || fallbackData.description || `Found ${safeColors.length} color recommendations`
                };
                
                setColorRecommendations(transformedFallback);
                setError(null);
              } else {
                console.error('Color palettes service unavailable:', fallbackResponse.status);
            // Set empty recommendations when database is not available
                console.log('Database color service unavailable, setting empty recommendations');
                setColorRecommendations({
                  colors_that_suit: [],
                  colors: [],
                  colors_to_avoid: [],
                  seasonal_type: seasonalType,
                  monk_skin_tone: monkSkinTone,
                  message: 'Color recommendations are currently unavailable. Please try again later.',
                  database_source: false
                });
                setError(null);
              }
            } catch (fallbackError) {
              console.error('Fallback API error:', fallbackError);
              // Set empty recommendations when all services fail
              console.log('All color services failed, setting empty recommendations');
              setColorRecommendations({
                colors_that_suit: [],
                colors: [],
                colors_to_avoid: [],
                seasonal_type: seasonalType,
                monk_skin_tone: monkSkinTone,
                message: 'Color recommendations are currently unavailable. Please try again later.',
                database_source: false
              });
              setError(null);
            }
          }
        } catch (err) {
          console.error('Unable to fetch comprehensive color recommendations:', err);
          // Set empty recommendations when network fails
          const seasonalType = {
            'Monk01': 'Light Spring', 'Monk02': 'Light Spring', 'Monk03': 'Clear Spring',
            'Monk04': 'Warm Spring', 'Monk05': 'Soft Autumn', 'Monk06': 'Warm Autumn',
            'Monk07': 'Deep Autumn', 'Monk08': 'Deep Winter', 'Monk09': 'Cool Winter',
            'Monk10': 'Clear Winter'
          }[monkSkinTone] || 'Universal';
          
          console.log('Network error occurred, setting empty recommendations');
          setColorRecommendations({
            colors_that_suit: [],
            colors: [],
            colors_to_avoid: [],
            seasonal_type: seasonalType,
            monk_skin_tone: monkSkinTone,
            message: 'Unable to load color recommendations due to network error. Please check your connection and try again.',
            database_source: false
          });
          setError(null);
        }
      }
    };

    fetchColorRecommendations();
  }, [activeTab, skinHex, monkSkinTone]);

  // Fetch products based on active tab
  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      setError(null);
      
      try {
        let response;
        let transformedProducts: Product[] = [];
        
        if (activeTab === 'makeup') {
          // Build query parameters for makeup products
          const queryParams = new URLSearchParams();
          queryParams.append('page', currentPage.toString());
          queryParams.append('limit', itemsPerPage.toString());
          
          // Add Monk skin tone for better product matching
          if (monkSkinTone) {
            queryParams.append('mst', monkSkinTone);
          }
          
          // Add hex color for color matching
          if (skinHex) {
            queryParams.append('ogcolor', skinHex.replace('#', ''));
          }
          
          // Add selected filters if any
          if (selectedFilters.productType) {
            queryParams.append('product_type', selectedFilters.productType);
          }
          
          console.log(`Fetching makeup products with params: ${queryParams.toString()}`);
          // TODO: Temporarily commented out for future re-enable
          // response = await fetch(buildApiUrl(API_ENDPOINTS.MAKEUP_DATA, Object.fromEntries(queryParams)));
          // 
          // if (!response.ok) {
          //   throw new Error(`Unable to load makeup recommendations: ${response.status} ${response.statusText}`);
          // }

          // const data = await response.json();
          // Temporary placeholder data for makeup
          const data = { data: [], total_items: 0, total_pages: 0 };
          transformedProducts = data.data.map((item: ApiProduct) => ({
            id: Math.random(),
            name: item.product_name || item.Product_Name || item.name || '',
            brand: item.brand || item.Brand || 'Unknown',
            price: item.price || item.Price || '$29.99',
            rating: item.rating || 4.5,
            image: item.imgSrc || item.image_url || item.Image_URL || item.image || '',
            image_url: item.imgSrc || item.image_url || item.Image_URL || item.image || '',
            mst: item.mst || '',
            desc: item.imgAlt || item.desc || '',
            product_type: item.product_type || ''
          }));

          setTotalItems(data.total_items || transformedProducts.length);
          setTotalPages(data.total_pages || Math.ceil(transformedProducts.length / itemsPerPage));
          
          // Fetch available makeup types for filtering
          // TODO: Temporarily disabled for production deployment
          // if (Object.keys(availableFilters).length === 0) {
          //   try {
          //     const typesResponse = await fetch(`${API_BASE_URL}/makeup-types`);
          //     if (typesResponse.ok) {
          //       const typesData = await typesResponse.json();
          //       setAvailableFilters({
          //         productType: typesData.types || []
          //       });
          //     }
          //   } catch (err) {
          //     console.error('Unable to load makeup categories:', err);
          //   }
          // }
        } else if (activeTab === 'outfit') {
          // For outfit tab, use recommended colors if available
          const colorParams = new URLSearchParams();
          colorParams.append('page', currentPage.toString());
          colorParams.append('limit', itemsPerPage.toString());
          
          // Use color recommendations if available
          if (colorRecommendations && colorRecommendations.colors_that_suit && colorRecommendations.colors_that_suit.length > 0) {
            // Add up to 4 recommended colors if available
            const colorNames = colorRecommendations.colors_that_suit
              .slice(0, 4)
              .filter(color => color && color.name)
              .map(color => color.name);
              
            if (colorNames.length > 0) {
              colorNames.forEach(colorName => {
                colorParams.append('color', colorName);
              });
            } else {
              // Default colors if no valid names
              colorParams.append('color', 'Blue');
              colorParams.append('color', 'Black');
              colorParams.append('color', 'White');
              colorParams.append('color', 'Grey');
            }
          } else {
            // Default colors if no recommendations
            colorParams.append('color', 'Blue');
            colorParams.append('color', 'Black');
            colorParams.append('color', 'White');
            colorParams.append('color', 'Grey');
          }
          
          console.log(`Fetching outfits with params: ${colorParams.toString()}`);
          // TODO: Temporarily commented out for future re-enable
          // response = await fetch(`${API_BASE_URL}/apparel?${colorParams.toString()}`);
          // 
          // if (!response.ok) {
          //   throw new Error(`Unable to load outfit recommendations: ${response.status} ${response.statusText}`);
          // }

          // const data = await response.json();
          // Temporary placeholder data for outfits
          const data = { data: [], total_items: 0, total_pages: 0 };
          
          if (data.error) {
            throw new Error(data.error);
          }
          
          transformedProducts = data.data.map((item: {
            'Product Name'?: string;
            'Price'?: string;
            'Image URL'?: string;
            'Product Type'?: string;
          }) => ({
            id: Math.random(),
            name: item['Product Name'] || '',
            brand: 'Apparel',
            price: item['Price'] || '$0.00',
            rating: 4.5,
            image: item['Image URL'] || '',
            image_url: item['Image URL'] || '',
            mst: '',
            desc: item['Product Type'] || '',
            product_type: item['Product Type'] || ''
          }));
          
          setTotalItems(data.total_items || transformedProducts.length);
          setTotalPages(data.total_pages || Math.ceil(transformedProducts.length / itemsPerPage));
        }

        setProducts(transformedProducts);
        setLoading(false);
      } catch (err) {
        console.error('Error:', err);
        // TODO: Uncomment when proper data is available
        // setError(err instanceof Error ? err.message : 'An error occurred');
        setLoading(false);
        setProducts([]); // Clear products on error
      }
    };

    fetchProducts();
  }, [navigate, activeTab, currentPage, selectedFilters, skinHex, monkSkinTone, colorRecommendations]);

  // Initialize skin tone and hex from session storage or use defaults
  useEffect(() => {
    try {
      const storedAnalysis = sessionStorage.getItem('skinAnalysis');
      if (storedAnalysis) {
        const analysisData = JSON.parse(storedAnalysis);
        
        // Handle both old array format and new object format
        if (Array.isArray(analysisData) && analysisData.length >= 2) {
          // Old format: [analysis, hex]
          setSkinAnalysis(analysisData[0]);
          setSkinHex(analysisData[1]);
          
          // Determine Monk skin tone from hex color
          const hexColor = analysisData[1];
          const monkId = determineMonkSkinTone(hexColor);
          setMonkSkinTone(monkId);
        } else if (analysisData && typeof analysisData === 'object' && analysisData.monk_skin_tone) {
          // New format: direct SkinAnalysisResult object
          setSkinAnalysis(analysisData);
          
          // Use the derived_hex_code or monk_hex as the primary skin hex
          const hexColor = analysisData.derived_hex_code || analysisData.monk_hex;
          setSkinHex(hexColor);
          setMonkSkinTone(analysisData.monk_skin_tone);
          
          console.log('Skin analysis result:', analysisData);
        }
      }
    } catch (err) {
      console.error('Unable to load your color profile from session storage:', err);
      setError('Unable to load your color profile. Please try analyzing your photo again.');
    }
  }, []);
  
  // Enhanced function to determine the closest Monk skin tone with improved light skin detection
  const determineMonkSkinTone = (hexColor: string): string => {
    // Remove the # if present
    const hex = hexColor.startsWith('#') ? hexColor.substring(1) : hexColor;
    
    // Define the Monk skin tone hex values with enhanced calibration
    const monkHexValues = [
      { id: 'Monk01', hex: 'f6ede4', name: 'Monk 1' },
      { id: 'Monk02', hex: 'f3e7db', name: 'Monk 2' },
      { id: 'Monk03', hex: 'f7ead0', name: 'Monk 3' },
      { id: 'Monk04', hex: 'eadaba', name: 'Monk 4' },
      { id: 'Monk05', hex: 'd7bd96', name: 'Monk 5' },
      { id: 'Monk06', hex: 'a07e56', name: 'Monk 6' },
      { id: 'Monk07', hex: '825c43', name: 'Monk 7' },
      { id: 'Monk08', hex: '604134', name: 'Monk 8' },
      { id: 'Monk09', hex: '3a312a', name: 'Monk 9' },
      { id: 'Monk10', hex: '292420', name: 'Monk 10' }
    ];
    
    // Convert hex to RGB
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
    const inputColor = [r, g, b];
    
    console.log(`Enhanced Monk detection: Input color RGB(${r}, ${g}, ${b}) from hex ${hexColor}`);
    
    // Calculate brightness and color characteristics
    const avgBrightness = (r + g + b) / 3;
    const maxChannel = Math.max(r, g, b);
    const minChannel = Math.min(r, g, b);
    const colorRange = maxChannel - minChannel;
    
    console.log(`Brightness analysis: avg=${avgBrightness.toFixed(1)}, max=${maxChannel}, min=${minChannel}, range=${colorRange}`);
    
    // PRE-CLASSIFICATION: Use brightness to narrow down candidates (matching backend logic)
    let candidateMonks: typeof monkHexValues = [];
    
    if (avgBrightness >= 220) {  // Very light skin - Fair complexion
      candidateMonks = monkHexValues.filter(m => ['Monk01', 'Monk02'].includes(m.id));
      console.log(`Very light skin detected (brightness=${avgBrightness.toFixed(1)}), limiting to Monk 1-2`);
    } else if (avgBrightness >= 190) {  // Light skin
      candidateMonks = monkHexValues.filter(m => ['Monk01', 'Monk02', 'Monk03'].includes(m.id));
      console.log(`Light skin detected (brightness=${avgBrightness.toFixed(1)}), limiting to Monk 1-3`);
    } else if (avgBrightness >= 150) {  // Light-medium skin
      candidateMonks = monkHexValues.filter(m => ['Monk02', 'Monk03', 'Monk04', 'Monk05'].includes(m.id));
      console.log(`Light-medium skin detected (brightness=${avgBrightness.toFixed(1)}), limiting to Monk 2-5`);
    } else if (avgBrightness >= 120) {  // Medium skin
      candidateMonks = monkHexValues.filter(m => ['Monk04', 'Monk05', 'Monk06'].includes(m.id));
      console.log(`Medium skin detected (brightness=${avgBrightness.toFixed(1)}), limiting to Monk 4-6`);
    } else if (avgBrightness >= 90) {   // Medium-dark skin
      candidateMonks = monkHexValues.filter(m => ['Monk05', 'Monk06', 'Monk07', 'Monk08'].includes(m.id));
      console.log(`Medium-dark skin detected (brightness=${avgBrightness.toFixed(1)}), limiting to Monk 5-8`);
    } else if (avgBrightness >= 60) {   // Dark skin
      candidateMonks = monkHexValues.filter(m => ['Monk07', 'Monk08', 'Monk09'].includes(m.id));
      console.log(`Dark skin detected (brightness=${avgBrightness.toFixed(1)}), limiting to Monk 7-9`);
    } else {  // Very dark skin
      candidateMonks = monkHexValues.filter(m => ['Monk08', 'Monk09', 'Monk10'].includes(m.id));
      console.log(`Very dark skin detected (brightness=${avgBrightness.toFixed(1)}), limiting to Monk 8-10`);
    }
    
    // Find the closest match among candidates using enhanced algorithm
    let minDistance = Number.MAX_VALUE;
    let closestMatch = candidateMonks[0] || monkHexValues[4]; // Default to Monk05 if no candidates
    
    candidateMonks.forEach(monk => {
      const mr = parseInt(monk.hex.substring(0, 2), 16);
      const mg = parseInt(monk.hex.substring(2, 4), 16);
      const mb = parseInt(monk.hex.substring(4, 6), 16);
      const monkColor = [mr, mg, mb];
      
      // Multi-factor distance calculation (matching backend logic)
      // 1. Euclidean distance in RGB space
      const euclideanDistance = Math.sqrt(
        Math.pow(r - mr, 2) + 
        Math.pow(g - mg, 2) + 
        Math.pow(b - mb, 2)
      );
      
      // 2. Brightness difference
      const monkBrightness = (mr + mg + mb) / 3;
      const brightnessDiff = Math.abs(avgBrightness - monkBrightness);
      
      // 3. Color saturation difference
      const inputSaturation = maxChannel > 0 ? colorRange / maxChannel : 0;
      const monkMaxChannel = Math.max(mr, mg, mb);
      const monkMinChannel = Math.min(mr, mg, mb);
      const monkSaturation = monkMaxChannel > 0 ? (monkMaxChannel - monkMinChannel) / monkMaxChannel : 0;
      const saturationDiff = Math.abs(inputSaturation - monkSaturation);
      
      // 4. Weighted combination optimized for each brightness range
      let distance: number;
      if (avgBrightness >= 190) {  // Light skin - prioritize brightness matching
        distance = euclideanDistance * 0.4 + brightnessDiff * 3.0 + saturationDiff * 10;
      } else if (avgBrightness >= 120) {  // Medium skin - balanced approach
        distance = euclideanDistance * 0.6 + brightnessDiff * 1.5 + saturationDiff * 15;
      } else {  // Dark skin - prioritize overall color matching
        distance = euclideanDistance * 0.7 + brightnessDiff * 2.0 + saturationDiff * 20;
      }
      
      console.log(`${monk.name}: euclidean=${euclideanDistance.toFixed(2)}, brightness_diff=${brightnessDiff.toFixed(2)}, sat_diff=${saturationDiff.toFixed(3)}, total=${distance.toFixed(2)}`);
      
      if (distance < minDistance) {
        minDistance = distance;
        closestMatch = monk;
      }
    });
    
    // Safety fallback if no candidate was selected
    if (!closestMatch) {
      console.warn('No candidate selected, using brightness-based fallback');
      if (avgBrightness >= 190) {
        closestMatch = monkHexValues.find(m => m.id === 'Monk01') || monkHexValues[0];
      } else if (avgBrightness >= 150) {
        closestMatch = monkHexValues.find(m => m.id === 'Monk03') || monkHexValues[2];
      } else if (avgBrightness >= 120) {
        closestMatch = monkHexValues.find(m => m.id === 'Monk05') || monkHexValues[4];
      } else if (avgBrightness >= 90) {
        closestMatch = monkHexValues.find(m => m.id === 'Monk07') || monkHexValues[6];
      } else {
        closestMatch = monkHexValues.find(m => m.id === 'Monk09') || monkHexValues[8];
      }
    }
    
    console.log(`Final selection: ${closestMatch.id} (${closestMatch.name}) with distance ${minDistance.toFixed(2)}`);
    
    return closestMatch.id;
  };




  return (
    <Layout>
      <div className="min-h-screen bg-gray-50">
        {/* Feedback Popup */}
        <FeedbackPopup 
          isVisible={showFeedbackPopup}
          onClose={handleFeedbackClose}
          userContext={{
            monkSkinTone,
            activeTab,
            sessionId: Date.now().toString() // Simple session ID
          }}
        />
        {/* Hero Section - Enhanced Mobile Responsiveness */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 md:py-16 lg:py-20">
            <div className="text-center">
              {skinHex && (
                <div className="flex justify-center mb-4 sm:mb-6">
                  <div className="bg-white p-2 sm:p-3 rounded-lg shadow-lg">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-6 h-6 sm:w-8 sm:h-8 rounded-full border-2 border-white shadow-lg" 
                        style={{ backgroundColor: skinHex }}
                        title="Your Skin Tone"
                      />
                    </div>
                  </div>
                </div>
              )}
              <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-3 sm:mb-4 px-2">
                Your Perfect Style Match
              </h1>
              <p className="mt-2 sm:mt-4 text-base sm:text-lg md:text-xl text-white max-w-2xl mx-auto px-4 leading-relaxed">
                Discover colors and styles that enhance your natural beauty
              </p>
            </div>
          </div>
        </div>

        {/* Tab Navigation - Enhanced Responsive Design */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8 mt-8">
          <div className="flex flex-wrap justify-center gap-2 sm:gap-3 md:gap-4">
            <button
              onClick={() => setActiveTab('makeup')}
              className={`px-3 sm:px-4 md:px-6 py-2 sm:py-3 rounded-lg flex items-center space-x-2 transition-all text-sm sm:text-base font-medium min-w-0 flex-shrink-0 ${
                activeTab === 'makeup'
                  ? 'bg-purple-600 text-white shadow-lg transform scale-105'
                  : 'bg-white text-gray-600 hover:bg-purple-50 hover:shadow-md hover:scale-102'
              }`}
            >
              <Sparkles className="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0" />
              <span className="whitespace-nowrap">Makeup</span>
            </button>
            <button
              onClick={() => setActiveTab('outfit')}
              className={`px-3 sm:px-4 md:px-6 py-2 sm:py-3 rounded-lg flex items-center space-x-2 transition-all text-sm sm:text-base font-medium min-w-0 flex-shrink-0 ${
                activeTab === 'outfit'
                  ? 'bg-purple-600 text-white shadow-lg transform scale-105'
                  : 'bg-white text-gray-600 hover:bg-purple-50 hover:shadow-md hover:scale-102'
              }`}
            >
              <Shirt className="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0" />
              <span className="whitespace-nowrap">Outfits</span>
            </button>
            <button
              onClick={() => setActiveTab('colors')}
              className={`px-3 sm:px-4 md:px-6 py-2 sm:py-3 rounded-lg flex items-center space-x-2 transition-all text-sm sm:text-base font-medium min-w-0 flex-shrink-0 ${
                activeTab === 'colors'
                  ? 'bg-purple-600 text-white shadow-lg transform scale-105'
                  : 'bg-white text-gray-600 hover:bg-purple-50 hover:shadow-md hover:scale-102'
              }`}
            >
              <Palette className="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0" />
              <span className="whitespace-nowrap">Color Palettes</span>
            </button>
          </div>
        </div>

        {/* Display error message if any */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {displayError()}
        </div>

        {/* Products Grid */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
          {loading ? (
            <div className="col-span-full text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-purple-600 border-t-transparent" />
            </div>
          ) : (
            <>
              {activeTab === 'makeup' ? (
                // Coming Soon banner for makeup
                <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl p-8 text-white text-center shadow-xl">
                  <div className="max-w-2xl mx-auto">
                    <Sparkles className="h-16 w-16 mx-auto mb-4 opacity-90" />
                    <h2 className="text-3xl font-bold mb-4">Beauty Recommendations</h2>
                    <div className="bg-white bg-opacity-20 rounded-lg px-6 py-3 inline-block mb-4">
                      <span className="text-xl font-semibold">Coming Soon!</span>
                    </div>
                    <p className="text-lg mb-6">
                      We're working on bringing you personalized makeup recommendations based on your unique skin tone. 
                      Our beauty experts are curating the perfect products just for you!
                    </p>
                    <div className="flex justify-center items-center space-x-2 text-sm opacity-90">
                      <Crown className="h-4 w-4" />
                      <span>Premium makeup recommendations launching soon</span>
                    </div>
                  </div>
                </div>
              ) : activeTab === 'outfit' ? (
                // Coming Soon banner for outfits
                <div className="bg-gradient-to-r from-green-500 to-teal-500 rounded-xl p-8 text-white text-center shadow-xl">
                  <div className="max-w-2xl mx-auto">
                    <Shirt className="h-16 w-16 mx-auto mb-4 opacity-90" />
                    <h2 className="text-3xl font-bold mb-4">Outfit Recommendations</h2>
                    <div className="bg-white bg-opacity-20 rounded-lg px-6 py-3 inline-block mb-4">
                      <span className="text-xl font-semibold">Coming Soon!</span>
                    </div>
                    <p className="text-lg mb-6">
                      We're curating personalized outfit recommendations that perfectly match your skin tone analysis. 
                      Get ready for style suggestions that will make you look and feel amazing!
                    </p>
                    <div className="flex justify-center items-center space-x-2 text-sm opacity-90">
                      <Sparkles className="h-4 w-4" />
                      <span>Personalized outfit styling launching soon</span>
                    </div>
                  </div>
                </div>
              ) : (
                // Color Palettes Tab - Simplified to only show colors that suit
                <div className="space-y-8">
                  <div className="bg-white rounded-xl p-6 shadow-lg">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Color Recommendations</h2>
                    <p className="text-gray-600 mb-6">
                      Based on your skin tone ({monkSkinTone && monkSkinTones[monkSkinTone] ? monkSkinTones[monkSkinTone].userFriendlyName : monkSkinTone}), we've identified personalized color recommendations that will complement your natural complexion.
                    </p>
                    
                    <div className="flex flex-col md:flex-row md:items-center mb-6 gap-4">
                      <div 
                        className="w-16 h-16 rounded-full shadow-md"
                        style={{ backgroundColor: skinHex }}
                      />
                      <div>
                        <h3 className="text-lg font-semibold">Your Skin Tone</h3>
                        <p className="text-gray-500">{skinHex}</p>
                        {monkSkinTone && monkSkinTones[monkSkinTone] && (
                          <div className="text-gray-600 text-sm mb-2">
                            <p className="font-medium text-purple-700">{monkSkinTones[monkSkinTone].userFriendlyName}</p>
                            <p className="text-xs text-gray-500">{monkSkinTones[monkSkinTone].seasonalType}</p>
                          </div>
                        )}
                        {colorRecommendations?.seasonal_type && (
                          <p className="text-purple-600 font-medium">{colorRecommendations.seasonal_type} Color Type</p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Colors That Suit You */}
                  {colorRecommendations && (
                    <div className="bg-white rounded-xl p-6 shadow-lg">
                      <div className="flex items-center mb-6">
                        <Crown className="w-6 h-6 text-purple-600 mr-2" />
                        <h2 className="text-xl font-bold text-gray-900">Your Color Palette</h2>
                      </div>

                      <div className="space-y-8">
                        {/* All Colors That Suit Your Skin Tone */}
                        <div>
                          <h3 className="text-lg font-medium text-gray-800 mb-4 flex items-center">
                            <Star className="w-5 h-5 text-yellow-500 mr-2" />
                            All Colors That Suit Your Skin Tone
                            {colorRecommendations?.colors_that_suit && (
                              <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                                {colorRecommendations.colors_that_suit.length} colors
                              </span>
                            )}
                          </h3>
                          
                          
                          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 gap-3 sm:gap-4">
                            {(() => {
                              // Handle different API response formats
                              const colorsToDisplay = colorRecommendations.colors_that_suit || colorRecommendations.colors || [];
                              
                              if (colorsToDisplay && colorsToDisplay.length > 0) {
                                return colorsToDisplay.map((color, index) => (
                                  <div key={`${color.hex}-${color.name}-${index}`} className="bg-gray-50 p-2 sm:p-3 rounded-lg hover:shadow-md transition-shadow group">
                                    <div 
                                      className="w-full h-16 sm:h-18 md:h-20 lg:h-22 rounded-lg shadow-md mb-2 group-hover:scale-105 transition-transform"
                                      style={{ backgroundColor: color.hex }}
                                      title={`${color.name} - ${color.hex}`}
                                    />
                                    <span className="text-gray-700 text-xs sm:text-sm font-medium block truncate" title={color.name}>
                                      {color.name}
                                    </span>
                                    <span className="text-gray-500 text-xs hidden sm:block">{color.hex}</span>
                                  </div>
                                ));
                              } else {
                                return (
                                  <div className="col-span-full text-center py-8 text-gray-500">
                                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-purple-600 border-t-transparent mb-4"></div>
                                    <p>Loading your comprehensive color palette...</p>
                                  </div>
                                );
                              }
                            })()
                            }
                          </div>
                        </div>
                        
                        
                      </div>
                    </div>
                  )}

                </div>
              )}
            </>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default DemoRecommendations;