import React, { useState, useEffect } from 'react';
import { X, ChevronRight, ChevronLeft, Sparkles, Heart, Star, Zap } from 'lucide-react';

interface FeedbackPopupProps {
  isVisible: boolean;
  onClose: () => void;
  userContext?: {
    monkSkinTone?: string;
    activeTab?: string;
    sessionId?: string;
  };
}

interface SlideData {
  id: number;
  title: string;
  subtitle: string;
  question: string;
  icon: React.ReactElement;
  gradient: string;
  options: {
    value: string;
    emoji: string;
    text: string;
    description?: string;
  }[];
}

const FeedbackPopup: React.FC<FeedbackPopupProps> = ({ isVisible, onClose, userContext }) => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [answers, setAnswers] = useState<{ [key: number]: string }>({});
  const [isAnimating, setIsAnimating] = useState(false);
  const [showThankYou, setShowThankYou] = useState(false);

  // Reset state when modal opens
  useEffect(() => {
    if (isVisible) {
      setCurrentSlide(0);
      setAnswers({});
      setShowThankYou(false);
    }
  }, [isVisible]);

  if (!isVisible) return null;

  const slides: SlideData[] = [
    {
      id: 0,
      title: "First Impression",
      subtitle: "Trust your gut feeling",
      question: "What's your instant reaction to these color recommendations?",
      icon: <Zap className="w-6 h-6" />,
      gradient: "from-purple-400 via-pink-400 to-purple-500",
      options: [
        { value: 'wow', emoji: '🤩', text: 'WOW! Love at first sight', description: 'These colors speak to my soul!' },
        { value: 'intrigued', emoji: '😍', text: 'Intrigued and excited', description: 'I want to try these immediately' },
        { value: 'curious', emoji: '🤔', text: 'Curious but hesitant', description: 'Interesting... tell me more' },
        { value: 'unsure', emoji: '😕', text: 'Not feeling it', description: 'These don\'t seem like "me"' }
      ]
    },
    {
      id: 1,
      title: "Confidence Boost",
      subtitle: "Imagine yourself wearing these",
      question: "How confident would you feel wearing these colors?",
      icon: <Star className="w-6 h-6" />,
      gradient: "from-pink-400 via-purple-400 to-indigo-500",
      options: [
        { value: 'superhero', emoji: '💫', text: 'Like a superhero!', description: 'Ready to conquer the world' },
        { value: 'confident', emoji: '✨', text: 'Very confident', description: 'I\'d feel amazing and stylish' },
        { value: 'comfortable', emoji: '😊', text: 'Comfortable', description: 'Nice but nothing special' },
        { value: 'awkward', emoji: '😬', text: 'A bit awkward', description: 'Not sure if it suits me' }
      ]
    },
    {
      id: 2,
      title: "Social Impact",
      subtitle: "What would others think?",
      question: "How do you think people would react to you in these colors?",
      icon: <Heart className="w-6 h-6" />,
      gradient: "from-indigo-400 via-purple-400 to-pink-500",
      options: [
        { value: 'compliments', emoji: '🌟', text: 'Shower me with compliments', description: 'Everyone would notice how great I look' },
        { value: 'positive', emoji: '👏', text: 'Positive reactions', description: 'People would appreciate my style' },
        { value: 'neutral', emoji: '😐', text: 'No strong reactions', description: 'It\'s fine, nothing remarkable' },
        { value: 'concerned', emoji: '🤨', text: 'Might raise eyebrows', description: 'Not sure if it\'s the right choice' }
      ]
    },
    {
      id: 3,
      title: "Purchase Intent",
      subtitle: "The moment of truth",
      question: "If you could buy clothes in these colors right now, would you?",
      icon: <Sparkles className="w-6 h-6" />,
      gradient: "from-pink-400 via-purple-400 to-purple-600",
      options: [
        { value: 'immediately', emoji: '🛍️', text: 'Take my money now!', description: 'I need these colors in my wardrobe' },
        { value: 'probably', emoji: '💳', text: 'Probably yes', description: 'I\'d seriously consider buying' },
        { value: 'maybe', emoji: '🤷', text: 'Maybe later', description: 'I\'d think about it for a while' },
        { value: 'no', emoji: '❌', text: 'Not really', description: 'I\'d keep looking for other options' }
      ]
    }
  ];

  const handleAnswerSelect = (slideId: number, answer: string) => {
    setAnswers(prev => ({ ...prev, [slideId]: answer }));
    
    // Add animation delay
    setIsAnimating(true);
    setTimeout(() => {
      if (slideId === slides.length - 1) {
        // Last slide - show thank you
        setShowThankYou(true);
        setTimeout(() => {
          onClose();
        }, 2000);
      } else {
        // Move to next slide
        setCurrentSlide(prev => prev + 1);
      }
      setIsAnimating(false);
    }, 600);
  };

  const goToPreviousSlide = () => {
    if (currentSlide > 0) {
      setCurrentSlide(prev => prev - 1);
    }
  };

  const currentSlideData = slides[currentSlide];
  const progress = ((currentSlide + 1) / slides.length) * 100;

  if (showThankYou) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-2 sm:p-4">
        <div className="bg-white rounded-2xl sm:rounded-3xl shadow-2xl max-w-sm sm:max-w-md lg:max-w-lg xl:max-w-xl w-full p-4 sm:p-8 text-center transform animate-pulse">
          <div className="mb-6">
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-r from-purple-400 to-pink-400 flex items-center justify-center">
              <Heart className="w-10 h-10 text-white animate-bounce" />
            </div>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
              Thank You! 💖
            </h2>
            <p className="text-gray-600">
              Your feedback helps us create better recommendations just for you!
            </p>
          </div>
          <div className="flex justify-center space-x-1">
            {[...Array(3)].map((_, i) => (
              <div key={i} className={`w-2 h-2 rounded-full bg-purple-400 animate-bounce`} style={{ animationDelay: `${i * 0.2}s` }}></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-2 sm:p-4 transition-all duration-300 ${isVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
      <div className={`bg-white rounded-2xl sm:rounded-3xl shadow-2xl w-full max-w-sm sm:max-w-md lg:max-w-lg xl:max-w-xl transform transition-all duration-500 ${isVisible ? 'scale-100 opacity-100' : 'scale-95 opacity-0'}`}>
        
        {/* Header with Gradient */}
        <div className={`p-4 sm:p-6 bg-gradient-to-r ${currentSlideData.gradient} rounded-t-2xl sm:rounded-t-3xl text-white relative overflow-hidden`}>
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-2 right-2 w-12 h-12 sm:w-20 sm:h-20 rounded-full border-2 border-white/20"></div>
            <div className="absolute bottom-2 left-2 w-10 h-10 sm:w-16 sm:h-16 rounded-full border-2 border-white/20"></div>
            <div className="absolute top-1/2 left-1/4 w-6 h-6 sm:w-8 sm:h-8 rounded-full bg-white/10"></div>
          </div>
          
          <div className="relative z-10">
            <div className="flex justify-between items-center mb-3 sm:mb-4">
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="p-1.5 sm:p-2 bg-white/20 rounded-full">
                  <div className="w-5 h-5 sm:w-6 sm:h-6">{currentSlideData.icon}</div>
                </div>
                <div>
                  <h3 className="text-base sm:text-lg font-bold">{currentSlideData.title}</h3>
                  <p className="text-xs sm:text-sm opacity-90">{currentSlideData.subtitle}</p>
                </div>
              </div>
              <button onClick={onClose} className="p-1.5 sm:p-2 hover:bg-white/20 rounded-full transition-colors">
                <X className="w-4 h-4 sm:w-5 sm:h-5" />
              </button>
            </div>
            
            {/* Progress Bar */}
            <div className="w-full bg-white/20 rounded-full h-2 mb-2">
              <div 
                className="bg-white rounded-full h-2 transition-all duration-500 ease-out" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-xs sm:text-sm opacity-75">{currentSlide + 1} of {slides.length}</p>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 sm:p-6">
          <h4 className="text-lg sm:text-xl font-semibold text-gray-800 mb-4 sm:mb-6 text-center leading-relaxed px-2">
            {currentSlideData.question}
          </h4>
          
          <div className="space-y-2 sm:space-y-3">
            {currentSlideData.options.map((option, index) => {
              const isSelected = answers[currentSlide] === option.value;
              return (
                <button 
                  key={option.value} 
                  onClick={() => handleAnswerSelect(currentSlide, option.value)}
                  disabled={isAnimating}
                  className={`w-full text-left p-3 sm:p-4 rounded-xl sm:rounded-2xl transition-all duration-300 transform hover:scale-[1.01] sm:hover:scale-[1.02] border-2 group ${
                    isSelected 
                      ? `bg-gradient-to-r ${currentSlideData.gradient} text-white border-transparent shadow-lg scale-[1.01] sm:scale-[1.02]` 
                      : 'bg-gray-50 hover:bg-gray-100 border-gray-200 hover:border-gray-300'
                  } ${isAnimating ? 'pointer-events-none' : ''}`}
                  style={{ 
                    animationDelay: `${index * 0.1}s`,
                    animation: isVisible ? 'slideInUp 0.6s ease-out' : 'none'
                  }}
                >
                  <div className="flex items-start gap-3 sm:gap-4">
                    <span className="text-2xl sm:text-3xl flex-shrink-0 transform transition-transform group-hover:scale-110">
                      {option.emoji}
                    </span>
                    <div className="flex-1 min-w-0">
                      <span className={`font-semibold text-base sm:text-lg block mb-1 leading-tight ${
                        isSelected ? 'text-white' : 'text-gray-800'
                      }`}>
                        {option.text}
                      </span>
                      {option.description && (
                        <span className={`text-xs sm:text-sm leading-tight ${
                          isSelected ? 'text-white/90' : 'text-gray-500'
                        }`}>
                          {option.description}
                        </span>
                      )}
                    </div>
                    {isSelected && (
                      <ChevronRight className="w-4 h-4 sm:w-5 sm:h-5 text-white animate-pulse flex-shrink-0" />
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Navigation */}
          <div className="flex justify-between items-center mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-gray-100">
            <button 
              onClick={goToPreviousSlide}
              disabled={currentSlide === 0 || isAnimating}
              className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-1.5 sm:py-2 rounded-full transition-all ${
                currentSlide === 0 
                  ? 'text-gray-400 cursor-not-allowed' 
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
              }`}
            >
              <ChevronLeft className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="text-xs sm:text-sm font-medium hidden sm:inline">Back</span>
            </button>
            
            <div className="flex space-x-1.5 sm:space-x-2">
              {slides.map((_, index) => (
                <div 
                  key={index}
                  className={`w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full transition-all duration-300 ${
                    index === currentSlide 
                      ? 'bg-purple-500 w-4 sm:w-6' 
                      : index < currentSlide 
                        ? 'bg-purple-300' 
                        : 'bg-gray-200'
                  }`}
                ></div>
              ))}
            </div>
            
            <div className="w-8 sm:w-16"></div> {/* Spacer for alignment */}
          </div>
        </div>
      </div>
      
      {/* Custom animations */}
      <style>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default FeedbackPopup;
