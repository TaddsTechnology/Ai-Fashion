// import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { Camera, Upload, Sparkles, Star, Info } from 'lucide-react';

const Demo = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-white">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
        {/* Hero Section */}
        <div className="text-center relative">
          <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <Sparkles className="h-12 w-12 text-purple-500 animate-pulse" />
          </div>
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mb-6">
            Fashion AI Assistant
          </h1>
          <p className="mt-4 text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Transform your look instantly with our AI-powered beauty technology. 
            
          </p>
          
          {/* Floating badges */}
          <div className="flex justify-center gap-4 mt-8">
            <div className="bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm font-medium flex items-center">
              <Star className="w-4 h-4 mr-2" />
              AI-Powered
            </div>
            <div className="bg-pink-100 text-pink-700 px-4 py-2 rounded-full text-sm font-medium flex items-center">
              <Info className="w-4 h-4 mr-2" />
              Real-Time Results
            </div>
          </div>
        </div>

        {/* Main Options */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          <Link
            to="/demo/process"
            className="group relative overflow-hidden rounded-2xl bg-white p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1"
          >
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-purple-500 to-pink-500"></div>
            <div className="flex flex-col items-center">
              <div className="bg-purple-50 p-6 rounded-full mb-6 group-hover:scale-110 transition-transform duration-300">
                <Camera className="h-12 w-12 text-purple-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Live Camera</h2>
              <p className="text-gray-600 text-center leading-relaxed">
                Experience real-time makeup transformation using your device's camera. 
                Perfect for experimenting with different looks instantly.
              </p>
              <div className="mt-6 text-purple-600 font-medium flex items-center">
                Try Now
                <svg className="w-4 h-4 ml-2 group-hover:translate-x-2 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </Link>

          <Link
            to="/demo/process"
            className="group relative overflow-hidden rounded-2xl bg-white p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1"
          >
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-pink-500 to-purple-500"></div>
            <div className="flex flex-col items-center">
              <div className="bg-pink-50 p-6 rounded-full mb-6 group-hover:scale-110 transition-transform duration-300">
                <Upload className="h-12 w-12 text-pink-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Upload Photo</h2>
              <p className="text-gray-600 text-center leading-relaxed">
                Upload your favorite photo and see how different makeup styles 
                enhance your natural beauty.
              </p>
              <div className="mt-6 text-pink-600 font-medium flex items-center">
                Get Started
                <svg className="w-4 h-4 ml-2 group-hover:translate-x-2 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </Link>
        </div>

        {/* Tips Section */}
        <div className="mt-20 max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl p-8 shadow-lg relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full transform translate-x-1/2 -translate-y-1/2 opacity-50"></div>
            <h3 className="text-2xl font-bold text-gray-900 mb-6 relative">
              Tips for Perfect Results
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
              {[
                { tip: "Ensure your face is well-lit", icon: "💡" },
                { tip: "Remove glasses or accessories", icon: "👓" },
                { tip: "Face the camera directly", icon: "📸" },
                { tip: "Keep a neutral expression", icon: "😊" },
              ].map((item, index) => (
                <div key={index} className="flex items-center space-x-4 bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-xl">
                  <span className="text-2xl">{item.icon}</span>
                  <span className="text-gray-700">{item.tip}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Demo;