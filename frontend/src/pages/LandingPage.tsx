import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  Sparkle, 
  Camera, 
  ShoppingBag, 
  Instagram,
  Twitter,
  Linkedin,
  Facebook,
  Mail,
  Star,
  Palette,
  Zap
} from 'lucide-react';
import Navbar from '../components/Navbar';

const features = [
  {
    icon: Palette,
    title: "Color Theory Analysis",
    description: "Get personalized color suggestions based on advanced color theory and your unique skin tone."
  },
  {
    icon: ShoppingBag,
    title: "Smart Recommendations",
    description: "Receive tailored product suggestions that perfectly complement your natural coloring."
  },
  {
    icon: Camera,
    title: "Virtual Try-On",
    description: "Visualize how different colors look on you before making purchasing decisions."
  },
  {
    icon: Star,
    title: "Personalized Experience",
    description: "Enjoy a custom-tailored fashion journey designed specifically for your unique features."
  }
];

const testimonials = [
  {
    quote: "HueMatch completely transformed my shopping experience. I now know exactly which colors work best for me!",
    author: "Sarah J.",
    role: "Fashion Enthusiast"
  },
  {
    quote: "As a makeup artist, I recommend HueMatch to all my clients. The color recommendations are spot-on!",
    author: "Michael T.",
    role: "Professional Makeup Artist"
  },
  {
    quote: "I've saved so much money by avoiding colors that don't flatter me. This app is a game-changer!",
    author: "Emma R.",
    role: "Style Blogger"
  }
];

const galleryImages = [
  {
    url: "https://images.pexels.com/photos/2253832/pexels-photo-2253832.jpeg?auto=compress&cs=tinysrgb&w=600",
    alt: "Makeup Application"
  },
  {
    url: "https://images.pexels.com/photos/2113855/pexels-photo-2113855.jpeg?auto=compress&cs=tinysrgb&w=600",
    alt: "Foundation and Beauty Products"
  },
  {
    url: "https://images.pexels.com/photos/3373716/pexels-photo-3373716.jpeg?auto=compress&cs=tinysrgb&w=600",
    alt: "Colorful Makeup Palette"
  }
];

const LandingPage = () => {

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-purple-100 via-pink-50 to-white">
      <Navbar />
      
      {/* Hero Section */}
      <div className="relative pt-20 pb-32 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-16">
            <div className="lg:w-1/2 space-y-8 text-center lg:text-left">
              <h1 className="text-3xl sm:text-5xl lg:text-8xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 leading-tight">
                Discover Your Perfect Colors
              </h1>
              <p className="text-xl text-gray-600 max-w-xl mx-auto lg:mx-0">
                Unlock your personal color palette with AI-powered analysis that enhances your natural beauty
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Link
                  to="/demo"
                  className="group inline-flex items-center justify-center px-8 py-4 text-base font-medium rounded-full text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:opacity-90 transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  🎨 Find My Perfect Colors
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <button className="inline-flex items-center justify-center px-8 py-4 text-base font-medium rounded-full text-purple-600 bg-white/80 backdrop-blur hover:bg-white transition-all duration-300 shadow-md hover:shadow-lg border border-purple-100">
                  💖 See How It Works
                </button>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-500 justify-center lg:justify-start">
                <Zap className="h-4 w-4 text-pink-500" />
                <span>Join over 100,000 beauty lovers who've discovered their signature style</span>
              </div>
            </div>
            
            <div className="lg:w-1/2 relative flex justify-center">
              {/* Main container with pink background */}
              <div className="relative w-full max-w-lg h-80 sm:h-96 lg:h-[400px] bg-gradient-to-br from-pink-200 to-pink-300 rounded-[2rem] sm:rounded-[3rem] p-4 sm:p-6">
                {/* Main woman image */}
                <img
                  src="https://images.pexels.com/photos/2065195/pexels-photo-2065195.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
                  alt="Woman showcasing beautiful pink outfit with natural makeup look"
                  className="w-full h-full object-cover rounded-[1.5rem] sm:rounded-[2.5rem]"
                />
              </div>
              
              {/* Floating makeup palette - top left - hidden on mobile */}
              <div className="hidden sm:block absolute -top-8 -left-8 w-20 sm:w-28 h-20 sm:h-28 bg-white rounded-2xl shadow-xl p-2 sm:p-3 transform rotate-12 hover:rotate-6 transition-transform duration-300">
                <img 
                  src="https://images.pexels.com/photos/2533266/pexels-photo-2533266.jpeg?auto=compress&cs=tinysrgb&w=200" 
                  alt="Professional makeup palette with various lipstick shades" 
                  className="w-full h-full object-cover rounded-xl"
                />
              </div>
              
              {/* Floating makeup products - bottom left - hidden on mobile */}
              <div className="hidden sm:block absolute -bottom-6 -left-4 w-28 sm:w-36 h-28 sm:h-36 bg-white rounded-2xl shadow-xl p-2 sm:p-3 transform -rotate-6 hover:rotate-0 transition-transform duration-300">
                <img 
                  src="https://images.pexels.com/photos/2537930/pexels-photo-2537930.jpeg?auto=compress&cs=tinysrgb&w=200" 
                  alt="Collection of premium black makeup products and brushes" 
                  className="w-full h-full object-cover rounded-xl"
                />
              </div>
              
              {/* AI Badge - bottom right */}
              <div className="absolute -bottom-2 sm:-bottom-4 -right-2 sm:-right-4 bg-white rounded-xl sm:rounded-2xl shadow-xl px-3 sm:px-6 py-2 sm:py-4 flex items-center gap-2 sm:gap-3 border border-gray-100/50 min-h-[44px]">
                <div className="p-1 sm:p-2 bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg">
                  <Sparkle className="h-4 w-4 sm:h-5 sm:w-5 text-pink-600" />
                </div>
                <span className="text-xs sm:text-sm font-semibold text-gray-800 whitespace-nowrap">✨ Smart AI Insights</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <section className="py-12 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-8 text-center">
            <div className="p-3 sm:p-6">
              <p className="text-2xl sm:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">100K+</p>
              <p className="text-gray-600 mt-2 text-sm sm:text-base">Active Users</p>
            </div>
            <div className="p-3 sm:p-6">
              <p className="text-2xl sm:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">12</p>
              <p className="text-gray-600 mt-2 text-sm sm:text-base">Color Seasons</p>
            </div>
            <div className="p-3 sm:p-6">
              <p className="text-2xl sm:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">98%</p>
              <p className="text-gray-600 mt-2 text-sm sm:text-base">Satisfaction Rate</p>
            </div>
            <div className="p-3 sm:p-6">
              <p className="text-2xl sm:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">5M+</p>
              <p className="text-gray-600 mt-2 text-sm sm:text-base">Color Analyses</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
              Transform Your Style Journey
            </h2>
            <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
              Discover how our AI-powered color analysis can elevate your fashion and beauty choices
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div 
                key={feature.title} 
                className="group bg-white/80 backdrop-blur rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-purple-50 hover:border-pink-200"
                style={{ animationDelay: `${index * 150}ms` }}
              >
                <div className="p-3 bg-gradient-to-br from-purple-100 to-pink-100 rounded-xl w-fit mb-6 group-hover:scale-110 transition-transform">
                  <feature.icon className="h-8 w-8 text-pink-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Premium Features Preview Section */}
      <section className="py-24 bg-gradient-to-br from-purple-50 via-pink-50 to-white relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute top-0 left-0 w-72 h-72 bg-gradient-to-br from-purple-200 to-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
        <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-br from-pink-200 to-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-72 h-72 bg-gradient-to-br from-purple-200 to-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center mb-16">
            <div className="inline-flex items-center justify-center p-2 bg-gradient-to-r from-purple-100 to-pink-100 rounded-full mb-6">
              <Sparkle className="h-6 w-6 text-purple-600 mr-2" />
              <span className="text-sm font-semibold text-purple-700 uppercase tracking-wide">Premium Experience</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mb-6">
              Elevate Your Style Journey
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Start with our free color analysis, then unlock personalized recommendations, shopping guides, and advanced style matching.
            </p>
          </div>

          {/* Features Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8 mb-16">
            {/* Free Features */}
            <div className="bg-white/80 backdrop-blur rounded-3xl p-8 shadow-lg border border-purple-100 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-900">Free</h3>
                <div className="px-4 py-2 bg-green-100 text-green-700 rounded-full text-sm font-semibold">
                  Always Free
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-gray-600">Basic skin tone analysis</span>
                </div>
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-gray-600">Color palette generation</span>
                </div>
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-gray-600">Seasonal color matching</span>
                </div>
              </div>
            </div>

            {/* Premium Features */}
            <div className="bg-gradient-to-br from-white to-purple-50 rounded-3xl p-8 shadow-xl border-2 border-purple-200 hover:shadow-2xl transition-all duration-300 relative overflow-hidden transform scale-105">
              <div className="absolute top-0 right-0 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-bl-2xl text-sm font-bold">
                PREMIUM
              </div>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-900">Premium</h3>
                <div className="px-4 py-2 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 rounded-full text-sm font-semibold">
                  $9.99/month
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <Star className="w-3 h-3 text-white" />
                  </div>
                  <span className="text-gray-600">Personalized product recommendations</span>
                </div>
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <Star className="w-3 h-3 text-white" />
                  </div>
                  <span className="text-gray-600">Advanced makeup suggestions</span>
                </div>
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <Star className="w-3 h-3 text-white" />
                  </div>
                  <span className="text-gray-600">Style preference learning</span>
                </div>
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <Star className="w-3 h-3 text-white" />
                  </div>
                  <span className="text-gray-600">Shopping links & price comparisons</span>
                </div>
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <Star className="w-3 h-3 text-white" />
                  </div>
                  <span className="text-gray-600">Color history & favorites</span>
                </div>
              </div>
              <Link
                to="/demo"
                className="w-full mt-8 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-4 px-6 rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all duration-300 shadow-lg hover:shadow-xl inline-flex items-center justify-center"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </div>

            {/* Enterprise Features */}
            <div className="bg-white/80 backdrop-blur rounded-3xl p-8 shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-300">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-900">Enterprise</h3>
                <div className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full text-sm font-semibold">
                  Contact Us
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-gray-600 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-gray-600">Team collaboration tools</span>
                </div>
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-gray-600 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-gray-600">Brand customization</span>
                </div>
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-gray-600 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-gray-600">API access & integrations</span>
                </div>
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-gray-600 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-gray-600">Priority support</span>
                </div>
                <div className="flex items-center">
                  <div className="w-5 h-5 bg-gray-600 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-gray-600">Analytics & reporting</span>
                </div>
              </div>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="text-center">
            <div className="inline-flex items-center space-x-8 bg-white/80 backdrop-blur rounded-full px-8 py-4 shadow-lg">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">30-day money-back guarantee</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">Cancel anytime</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">Secure payments</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gradient-to-r from-purple-50 to-pink-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900">
              How It Works
            </h2>
            <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
              Get your personalized color palette in three simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl p-8 shadow-lg text-center relative overflow-hidden group hover:shadow-xl transition-all">
              <div className="absolute top-0 right-0 w-24 h-24 bg-purple-100 rounded-bl-full -mr-12 -mt-12 group-hover:bg-pink-100 transition-colors"></div>
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6 text-white">
                <span className="text-2xl font-bold">1</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Upload Your Photo
              </h3>
              <p className="text-gray-600">
                Take a selfie or upload a photo in natural lighting to analyze your unique skin tone
              </p>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-lg text-center relative overflow-hidden group hover:shadow-xl transition-all">
              <div className="absolute top-0 right-0 w-24 h-24 bg-purple-100 rounded-bl-full -mr-12 -mt-12 group-hover:bg-pink-100 transition-colors"></div>
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6 text-white">
                <span className="text-2xl font-bold">2</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                AI Analysis
              </h3>
              <p className="text-gray-600">
                Our advanced AI analyzes your skin tone, undertones, and features to determine your color season
              </p>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-lg text-center relative overflow-hidden group hover:shadow-xl transition-all">
              <div className="absolute top-0 right-0 w-24 h-24 bg-purple-100 rounded-bl-full -mr-12 -mt-12 group-hover:bg-pink-100 transition-colors"></div>
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6 text-white">
                <span className="text-2xl font-bold">3</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Get Your Color Palette
              </h3>
              <p className="text-gray-600">
                Receive a personalized color palette with flattering colors for clothing, makeup, and accessories
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900">
              What Our Users Say
            </h2>
            <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
              Join thousands of satisfied users who've transformed their style with HueMatch
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white rounded-xl p-8 shadow-lg relative">
                <div className="absolute top-0 right-0 transform -translate-y-1/3 translate-x-1/3">
                  <div className="text-pink-100 text-8xl">"</div>
                </div>
                <p className="text-gray-600 mb-6 relative z-10">{testimonial.quote}</p>
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold">
                    {testimonial.author.charAt(0)}
                  </div>
                  <div className="ml-4">
                    <p className="font-medium text-gray-900">{testimonial.author}</p>
                    <p className="text-sm text-gray-500">{testimonial.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Gallery Section */}
      <section className="py-20 bg-gradient-to-r from-purple-50 to-pink-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900">
              See It in Action
            </h2>
            <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
              Discover how HueMatch transforms the way you approach color
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {galleryImages.map((image, index) => (
              <div key={index} className="relative group overflow-hidden rounded-xl shadow-lg">
                <img
                  src={image.url}
                  alt={image.alt}
                  className="w-full h-80 object-cover transform group-hover:scale-110 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="absolute bottom-6 left-6 text-white">
                    <p className="font-medium text-lg">{image.alt}</p>
                    <div className="w-10 h-1 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mt-2"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl shadow-xl overflow-hidden">
            <div className="px-8 py-16 md:p-16 text-center text-white">
              <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to Discover Your Perfect Colors?</h2>
              <p className="text-xl text-purple-100 mb-8 max-w-2xl mx-auto">
                Join thousands of users who have transformed their style with personalized color analysis
              </p>
              <Link
                to="/demo"
                className="inline-flex items-center justify-center px-8 py-4 text-base font-medium rounded-full text-purple-600 bg-white hover:bg-purple-50 transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                Try Free Demo
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-6">
                <Sparkle className="h-6 w-6 text-pink-400" />
                <span className="text-xl font-bold">HueMatch</span>
              </div>
              <p className="text-gray-400">
                Transforming personal style with AI-powered color analysis technology
              </p>
            </div>

            <div>
              <h4 className="text-lg font-semibold mb-4">Company</h4>
              <ul className="space-y-2">
                <li><a href="#about" className="text-gray-400 hover:text-pink-400 transition-colors">About</a></li>
                <li><a href="#careers" className="text-gray-400 hover:text-pink-400 transition-colors">Careers</a></li>
                <li><a href="#press" className="text-gray-400 hover:text-pink-400 transition-colors">Press</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-lg font-semibold mb-4">Resources</h4>
              <ul className="space-y-2">
                <li><a href="#blog" className="text-gray-400 hover:text-pink-400 transition-colors">Blog</a></li>
                <li><a href="#documentation" className="text-gray-400 hover:text-pink-400 transition-colors">Documentation</a></li>
                <li><a href="#support" className="text-gray-400 hover:text-pink-400 transition-colors">Support</a></li>
              </ul>
            </div>

            <div>
              <h4 className="text-lg font-semibold mb-4">Connect</h4>
              <div className="flex space-x-4">
                <a href="#twitter" className="text-gray-400 hover:text-pink-400 transition-colors">
                  <Twitter className="h-6 w-6" />
                </a>
                <a href="#linkedin" className="text-gray-400 hover:text-pink-400 transition-colors">
                  <Linkedin className="h-6 w-6" />
                </a>
                <a href="#facebook" className="text-gray-400 hover:text-pink-400 transition-colors">
                  <Facebook className="h-6 w-6" />
                </a>
                <a href="#instagram" className="text-gray-400 hover:text-pink-400 transition-colors">
                  <Instagram className="h-6 w-6" />
                </a>
                <a href="#contact" className="text-gray-400 hover:text-pink-400 transition-colors">
                  <Mail className="h-6 w-6" />
                </a>
              </div>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
            <p>© 2023 HueMatch. All rights reserved.</p>
            <p className="text-xs mt-2 opacity-75">
              We use uploaded data to improve our AI recommendations. 
              <a href="#privacy" className="hover:text-pink-400 underline ml-1">Privacy Policy</a>
            </p>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default LandingPage;