import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import ImageCapture from '../components/ImageCapture';
import { Camera, Shield, Image, RefreshCw, Sparkle } from 'lucide-react';
import { API_ENDPOINTS } from '../config/api';
// import { Client } from "@gradio/client"; // Use dynamic import instead

// Add interfaces at the top of the file
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
  dominant_rgb?: number[];
}

const DemoProcess = () => {
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [colorProfileResult, setColorProfileResult] = useState<ColorProfileResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
const [skinAnalysisResult, setSkinAnalysisResult] = useState<SkinAnalysisResult | null>(null);

  const analyzeSkinColor = async (imageBlob: Blob) => {
    try {
      console.log("Analyzing skin tone from image blob", {
        size: imageBlob.size,
        type: imageBlob.type,
        endpoint: API_ENDPOINTS.ANALYZE_SKIN_TONE
      });
      
      // Create form data for API call
      const formData = new FormData();
      formData.append('file', imageBlob, 'uploaded-image.jpg');
      
      console.log('Sending request to:', API_ENDPOINTS.ANALYZE_SKIN_TONE);
      console.log('FormData entries:', Array.from(formData.entries()));
      
      // Call the skin tone analysis API with proper headers
      const response = await fetch(API_ENDPOINTS.ANALYZE_SKIN_TONE, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type header - let browser set it with boundary
      });
      
      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error Response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
      
      const result = await response.json();
      console.log("Skin analysis result:", result);
      
      // Format the result to match the expected interface
      const formattedResult: SkinAnalysisResult = {
        monk_skin_tone: result.monk_skin_tone,
        monk_hex: result.monk_hex,
        derived_hex_code: result.derived_hex_code,
        dominant_rgb: result.dominant_rgb
      };
      
      setSkinAnalysisResult(formattedResult);
      
      // Store the result in sessionStorage for use in other components
      sessionStorage.setItem('skinAnalysis', JSON.stringify(formattedResult));
      
      // Continue with navigation after analysis
      navigate('/demo/try-on');
    } catch (error) {
      console.error("Skin analysis error:", error);
      
      // Fallback to a default result instead of always Monk03
      const fallbackResult: SkinAnalysisResult = {
        monk_skin_tone: "Monk05",
        monk_hex: "#d7bd96",
        derived_hex_code: "#d7bd96",
        dominant_rgb: [215, 189, 150]
      };
      
      setSkinAnalysisResult(fallbackResult);
      sessionStorage.setItem('skinAnalysis', JSON.stringify(fallbackResult));
      navigate('/demo/try-on');
    }
  };

  const handleImageCapture = async (image: string) => {
    setIsProcessing(true);
    setIsAnalyzing(true);

    try {
      // Store the captured image in sessionStorage
      sessionStorage.setItem('capturedImage', image);
      
      // Convert base64 image to blob with proper type
      const base64Data = image.split(',')[1]; // Remove data:image/jpeg;base64, prefix
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'image/jpeg' });
      
      console.log('Created blob:', blob.size, 'bytes, type:', blob.type);
      
      // Analyze skin color
      await analyzeSkinColor(blob);
    } catch (error) {
      console.error("Image processing error:", error);
      setCameraError("Unable to process your photo. Please try again with better lighting.");
    } finally {
      setIsProcessing(false);
      setIsAnalyzing(false);
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
        {/* Hero Section with Animation */}
        <div className="max-w-6xl mx-auto px-4 py-16">
          <div className="text-center mb-16 animate-fadeIn">
            <h1 className="text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Discover Your Perfect 
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-pink-600">
                {" "}Colors
              </span>
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Upload your photo and get personalized color recommendations that make you look amazing
            </p>
          </div>

          {/* Main Content Grid */}
          <div className="grid md:grid-cols-2 gap-12 items-start mb-20">
            {/* Left Column - Image Capture */}
            <div className="space-y-6">
              <div className="bg-white rounded-3xl shadow-xl p-8 transition-all duration-300 hover:shadow-2xl">
                <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                  Take or Upload Photo
                </h2>
                
                {cameraError && (
                  <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 flex items-center">
                    <Shield className="w-5 h-5 mr-2" />
                    <p>{cameraError}</p>
                  </div>
                )}

                {isProcessing ? (
                  <div className="text-center py-12">
                    <RefreshCw className="w-12 h-12 text-purple-500 animate-spin mx-auto mb-4" />
                    <p className="text-lg font-medium text-gray-700">Creating your color profile...</p>
                    <p className="text-gray-500">This will only take a moment</p>
                  </div>
                ) : (
                  <ImageCapture onImageCapture={handleImageCapture} />
                )}
              </div>

              {/* Quick Tips */}
              <div className="bg-gradient-to-br from-purple-100 to-pink-100 rounded-3xl p-8">
                <div className="flex items-center mb-4">
                  <Camera className="w-6 h-6 text-purple-600 mr-2" />
                  <h3 className="text-lg font-semibold text-gray-900">Quick Tips</h3>
                </div>
                <ul className="space-y-3 text-gray-700">
                  <li className="flex items-center">
                    <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mr-2" />
                    Use natural lighting
                  </li>
                  <li className="flex items-center">
                    <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mr-2" />
                    Face the camera directly
                  </li>
                  <li className="flex items-center">
                    <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mr-2" />
                    Remove glasses if wearing
                  </li>
                </ul>
              </div>
            </div>

            {/* Right Column - Process Steps */}
            <div className="space-y-6">
              <div className="bg-white rounded-3xl shadow-lg p-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                  How It Works
                </h2>
                <div className="space-y-8">
                  {[
                    {
                      icon: <Camera className="w-8 h-8 text-purple-500" />,
                      title: "Capture",
                      description: "Take a clear photo of your face in good lighting"
                    },
                    {
                      icon: <RefreshCw className="w-8 h-8 text-purple-500" />,
                      title: "Analysis",
                      description: "Our AI analyzes your unique skin tone"
                    },
                    {
                      icon: <Image className="w-8 h-8 text-purple-500" />,
                      title: "Results",
                      description: "Get your personalized color recommendations"
                    }
                  ].map((step, index) => (
                    <div key={index} className="flex items-start">
                      <div className="bg-purple-50 p-3 rounded-xl mr-4">
                        {step.icon}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 mb-1">
                          {step.title}
                        </h3>
                        <p className="text-gray-600">{step.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Loading Overlay */}
        {isAnalyzing && (
          <div className="fixed inset-0 bg-gradient-to-br from-purple-900/20 via-pink-900/20 to-black/30 backdrop-blur-md z-50 flex items-center justify-center">
            <div className="bg-gradient-to-br from-white/95 to-purple-50/95 backdrop-blur-sm rounded-3xl p-8 max-w-lg w-full mx-4 shadow-2xl border border-purple-100/50 relative overflow-hidden">
              {/* Background Animation */}
              <div className="absolute inset-0 bg-gradient-to-r from-purple-200/20 via-pink-200/20 to-purple-200/20 animate-pulse"></div>
              
              {/* Animated Color Swatches */}
              <div className="relative mb-8">
                <div className="flex justify-center items-center space-x-2 mb-4">
                  {/* Color Swatch 1 */}
                  <div className="relative">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 shadow-lg animate-bounce" style={{animationDelay: '0s'}}></div>
                    <div className="absolute inset-0 w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 animate-ping opacity-75"></div>
                  </div>
                  
                  {/* Color Swatch 2 */}
                  <div className="relative">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-400 to-pink-600 shadow-lg animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    <div className="absolute inset-0 w-10 h-10 rounded-full bg-gradient-to-br from-pink-400 to-pink-600 animate-ping opacity-75" style={{animationDelay: '0.2s'}}></div>
                  </div>
                  
                  {/* Color Swatch 3 */}
                  <div className="relative">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg animate-bounce" style={{animationDelay: '0.4s'}}></div>
                    <div className="absolute inset-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 animate-ping opacity-75" style={{animationDelay: '0.4s'}}></div>
                  </div>
                  
                  {/* Color Swatch 4 */}
                  <div className="relative">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-purple-500 shadow-lg animate-bounce" style={{animationDelay: '0.6s'}}></div>
                    <div className="absolute inset-0 w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-purple-500 animate-ping opacity-75" style={{animationDelay: '0.6s'}}></div>
                  </div>
                  
                  {/* Color Swatch 5 */}
                  <div className="relative">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-600 to-pink-400 shadow-lg animate-bounce" style={{animationDelay: '0.8s'}}></div>
                    <div className="absolute inset-0 w-12 h-12 rounded-full bg-gradient-to-br from-purple-600 to-pink-400 animate-ping opacity-75" style={{animationDelay: '0.8s'}}></div>
                  </div>
                </div>
                
                {/* Animated Progress Bar */}
                <div className="w-full bg-gradient-to-r from-purple-100 via-pink-100 to-purple-100 rounded-full h-1 overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full animate-pulse" style={{
                    width: '100%',
                    background: 'linear-gradient(90deg, #a855f7, #ec4899, #a855f7)',
                    backgroundSize: '200% 100%',
                    animation: 'gradientShift 2s ease-in-out infinite'
                  }}></div>
                </div>
              </div>
              
              {/* Content */}
              <div className="relative text-center">
                <div className="inline-flex items-center justify-center p-3 bg-gradient-to-r from-purple-100 to-pink-100 rounded-full mb-4">
                  <Sparkle className="h-6 w-6 text-purple-600 mr-2 animate-pulse" />
                  <span className="text-sm font-semibold text-purple-700 uppercase tracking-wide">AI Analysis</span>
                </div>
                
                <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mb-3">
                  Discovering Your Perfect Colors
                </h3>
                
                <p className="text-gray-600 mb-4 leading-relaxed">
                  Our AI is analyzing your unique skin tone to create your personalized color palette
                </p>
                
                {/* Animated Dots */}
                <div className="flex justify-center space-x-1">
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{animationDelay: '0s'}}></div>
                  <div className="w-2 h-2 bg-pink-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default DemoProcess;