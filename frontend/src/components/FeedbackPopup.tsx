import React, { useState, useEffect } from 'react';
import { X, ChevronRight, ChevronLeft, Sparkles, Heart, Star, Zap, MessageSquare, Send } from 'lucide-react';

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
  const [writtenFeedback, setWrittenFeedback] = useState('');
  const [rating, setRating] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastSessionId, setLastSessionId] = useState<string | undefined>(undefined);

  // Reset state when modal opens
  useEffect(() => {
    if (isVisible) {
      setCurrentSlide(0);
      setAnswers({});
      setShowThankYou(false);
      setWrittenFeedback('');
      setRating(0);
      setIsSubmitting(false);
    }
  }, [isVisible]);

  // Reset state when user context changes (new photo uploaded)
  useEffect(() => {
    if (userContext?.sessionId && userContext.sessionId !== lastSessionId) {
      // This is a new session - reset all feedback state
      console.log('New photo session detected, resetting feedback state');
      setLastSessionId(userContext.sessionId);
      setCurrentSlide(0);
      setAnswers({});
      setShowThankYou(false);
      setWrittenFeedback('');
      setRating(0);
      setIsSubmitting(false);
    }
  }, [userContext?.sessionId, lastSessionId]);

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

  // Add written feedback slide data
  const writtenFeedbackSlide = {
    id: slides.length,
    title: "Your Thoughts",
    subtitle: "Tell us more (optional)",
    question: "Any additional thoughts about these color recommendations?",
    icon: <MessageSquare className="w-6 h-6" />,
    gradient: "from-purple-500 via-indigo-500 to-blue-500",
    options: []
  };

  const totalSlides = slides.length + 1; // Include written feedback slide

  // Function to submit feedback to SheetDB
  const submitFeedback = async () => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      const sheetDbUrl = 'https://sheetdb.io/api/v1/atpn8mhf808aa';
      
      // Prepare feedback data for SheetDB (flatten the structure)
      const feedbackData = {
        timestamp: new Date().toISOString(),
        session_id: userContext?.sessionId || `session_${Date.now()}`,
        monk_skin_tone: userContext?.monkSkinTone || 'Unknown',
        active_tab: userContext?.activeTab || 'color-analysis',
        rating: rating || null,
        written_feedback: writtenFeedback.trim() || '',
        first_impression: answers[0] || '',
        confidence_boost: answers[1] || '',
        social_impact: answers[2] || '',
        purchase_intent: answers[3] || '',
        client_ip: 'N/A', // Client IP not available in browser context
        user_agent: navigator.userAgent
      };

      const response = await fetch(sheetDbUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedbackData),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Feedback submitted successfully to SheetDB:', result);
        
        // Show thank you message
        setShowThankYou(true);
        setTimeout(() => {
          onClose();
        }, 2500);
      } else {
        console.error('Failed to submit feedback to SheetDB:', response.statusText);
        // Still show thank you to avoid confusing the user
        setShowThankYou(true);
        setTimeout(() => {
          onClose();
        }, 2000);
      }
    } catch (error) {
      console.error('Error submitting feedback to SheetDB:', error);
      // Still show thank you to avoid confusing the user
      setShowThankYou(true);
      setTimeout(() => {
        onClose();
      }, 2000);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAnswerSelect = (slideId: number, answer: string) => {
    setAnswers(prev => ({ ...prev, [slideId]: answer }));
    
    // Add animation delay
    setIsAnimating(true);
    setTimeout(() => {
      if (slideId === slides.length - 1) {
        // Last quiz slide - move to written feedback slide
        setCurrentSlide(slides.length); // Go to written feedback slide
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

  const currentSlideData = currentSlide < slides.length ? slides[currentSlide] : writtenFeedbackSlide;
  const progress = ((currentSlide + 1) / totalSlides) * 100;
  const isWrittenFeedbackSlide = currentSlide === slides.length;

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
            <p className="text-xs sm:text-sm opacity-75">{currentSlide + 1} of {totalSlides}</p>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 sm:p-6">
          <h4 className="text-lg sm:text-xl font-semibold text-gray-800 mb-4 sm:mb-6 text-center leading-relaxed px-2">
            {currentSlideData.question}
          </h4>
          
          {isWrittenFeedbackSlide ? (
            // Written feedback slide content
            <div className="space-y-6">
              {/* Quick rating with improved design */}
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6 border border-purple-100">
                <div className="text-center">
                  <div className="mb-4">
                    <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                      <Star className="w-6 h-6 text-white" />
                    </div>
                    <h5 className="text-lg font-semibold text-gray-800 mb-2">Rate Your Experience</h5>
                    <p className="text-sm text-gray-600">How would you rate these recommendations overall?</p>
                  </div>
                  <div className="flex justify-center space-x-1 mb-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        onClick={() => setRating(star)}
                        className={`p-2 transition-all duration-200 hover:scale-110 transform rounded-lg ${
                          star <= rating 
                            ? 'text-yellow-500 bg-yellow-50 shadow-sm' 
                            : 'text-gray-300 hover:text-yellow-400 hover:bg-yellow-50'
                        }`}
                      >
                        <Star className="w-7 h-7 fill-current" />
                      </button>
                    ))}
                  </div>
                  {rating > 0 && (
                    <p className="text-xs text-purple-600 font-medium animate-fade-in">
                      {rating === 5 ? '🌟 Amazing!' : rating === 4 ? '✨ Great!' : rating === 3 ? '👍 Good!' : rating === 2 ? '👌 Okay' : '🤔 Needs work'}
                    </p>
                  )}
                </div>
              </div>

              {/* Text area with improved design */}
              <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-6 border border-indigo-100">
                <div className="mb-4">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center">
                      <MessageSquare className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h5 className="text-lg font-semibold text-gray-800">Share Your Thoughts</h5>
                      <p className="text-sm text-gray-600">Help us improve your experience</p>
                    </div>
                  </div>
                </div>
                <div className="relative">
                  <textarea
                    value={writtenFeedback}
                    onChange={(e) => setWrittenFeedback(e.target.value)}
                    placeholder="💭 What did you love about these colors? Any suggestions for improvement? Specific colors you'd like to see? Feel free to share anything that comes to mind!"
                    className="w-full p-4 border-2 border-white/60 rounded-xl focus:border-purple-300 focus:ring-4 focus:ring-purple-100 transition-all duration-300 resize-none h-36 text-gray-700 placeholder-gray-400 bg-white/70 backdrop-blur-sm shadow-sm hover:shadow-md"
                    maxLength={500}
                  />
                  <div className="absolute bottom-3 right-3 opacity-60">
                    <div className="text-xs text-gray-500 bg-white/80 px-2 py-1 rounded-full">
                      {writtenFeedback.length}/500
                    </div>
                  </div>
                </div>
                <div className="flex justify-between items-center mt-3">
                  <div className="flex items-center gap-2 text-xs text-indigo-600">
                    <Sparkles className="w-3 h-3" />
                    <span>Optional - but your insights are valuable!</span>
                  </div>
                  <div className="text-xs text-gray-400">
                    {writtenFeedback.length > 0 ? `${500 - writtenFeedback.length} characters left` : ''}
                  </div>
                </div>
              </div>

              {/* Action buttons with improved design */}
              <div className="space-y-3">
                <button
                  onClick={submitFeedback}
                  disabled={isSubmitting}
                  className={`w-full p-4 rounded-xl font-semibold text-white transition-all duration-300 transform hover:scale-[1.02] relative overflow-hidden ${
                    isSubmitting
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-purple-500 via-pink-500 to-indigo-500 hover:from-purple-600 hover:via-pink-600 hover:to-indigo-600 shadow-lg hover:shadow-xl active:scale-[0.98]'
                  }`}
                >
                  {/* Animated background effect */}
                  {!isSubmitting && (
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full hover:translate-x-full transition-transform duration-1000"></div>
                  )}
                  
                  {isSubmitting ? (
                    <div className="flex items-center justify-center gap-3">
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-base">Sending your feedback...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center gap-3 relative z-10">
                      <Send className="w-5 h-5" />
                      <span className="text-base font-semibold">Submit Feedback</span>
                      <div className="w-2 h-2 bg-white/60 rounded-full animate-pulse"></div>
                    </div>
                  )}
                </button>

                {/* Skip option with subtle design */}
                <button
                  onClick={() => submitFeedback()}
                  disabled={isSubmitting}
                  className="w-full p-3 text-sm text-gray-500 hover:text-gray-700 transition-all duration-200 rounded-lg hover:bg-gray-50 border border-transparent hover:border-gray-200 group"
                >
                  <div className="flex items-center justify-center gap-2">
                    <span>Skip and finish</span>
                    <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition-transform duration-200" />
                  </div>
                </button>
              </div>
            </div>
          ) : (
            // Regular quiz slide content
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
          )}

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
              {/* Add dot for written feedback slide */}
              <div 
                className={`w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full transition-all duration-300 ${
                  currentSlide === slides.length
                    ? 'bg-purple-500 w-4 sm:w-6' 
                    : currentSlide > slides.length 
                      ? 'bg-purple-300' 
                      : 'bg-gray-200'
                }`}
              ></div>
            </div>
            
            {/* Next button for quiz slides */}
            {!isWrittenFeedbackSlide && answers[currentSlide] ? (
              <button 
                onClick={() => {
                  if (currentSlide === slides.length - 1) {
                    // Last quiz slide - move to written feedback slide
                    setCurrentSlide(slides.length);
                  } else {
                    // Move to next quiz slide
                    setCurrentSlide(prev => prev + 1);
                  }
                }}
                disabled={isAnimating}
                className="flex items-center gap-1 sm:gap-2 px-3 sm:px-4 py-1.5 sm:py-2 rounded-full transition-all bg-purple-600 text-white hover:bg-purple-700 transform hover:scale-105"
              >
                <span className="text-xs sm:text-sm font-medium">Next</span>
                <ChevronRight className="w-3 h-3 sm:w-4 sm:h-4" />
              </button>
            ) : (
              <div className="w-8 sm:w-16" />
            )}
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
