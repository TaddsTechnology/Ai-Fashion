import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Sparkles, Camera, BookOpen, Users, MessageSquare, Zap } from 'lucide-react';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // Handle body scroll lock when mobile menu is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const navItems = [
    { name: 'Resources', path: '/resources', icon: <BookOpen className="w-4 h-4 mr-1" /> },
    { name: 'Blog', path: '/blog', icon: <BookOpen className="w-4 h-4 mr-1" /> },
    { name: 'About', path: '/about', icon: <Users className="w-4 h-4 mr-1" /> },
    { name: 'Find Your Colors', path: '/demo', icon: <Camera className="w-4 h-4 mr-1" /> },
    { name: 'Contact', path: '/contact', icon: <MessageSquare className="w-4 h-4 mr-1" /> },
  ];

  return (
    <nav 
      className={`fixed w-full z-50 transition-all duration-300 ${
        scrolled 
          ? 'bg-white/95 backdrop-blur-md shadow-md' 
          : 'bg-gradient-to-r from-white/80 to-purple-50/80 backdrop-blur-sm'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2 group">
              <div className="relative">
                <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-500 rounded-full blur-md opacity-70 group-hover:opacity-100 transition duration-300"></div>
                <div className="relative bg-white rounded-full p-1.5">
                  <Sparkles className="h-7 w-7 text-pink-600 transition-transform group-hover:scale-110" />
                </div>
              </div>
              <span className="text-lg sm:text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-500 bg-clip-text text-transparent pl-1">
                HueMatch
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.path}
                className={`relative flex items-center px-4 py-2 text-sm font-medium rounded-full transition-all duration-200
                  hover:bg-purple-50 hover:text-pink-600 group ${
                    location.pathname === item.path || location.pathname.startsWith(item.path + '/')
                      ? 'text-pink-600 bg-purple-50/80'
                      : 'text-gray-700'
                  }`}
              >
                {item.icon}
                {item.name}
                {(location.pathname === item.path || location.pathname.startsWith(item.path + '/')) && (
                  <span className="absolute inset-x-0 -bottom-px h-0.5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></span>
                )}
              </Link>
            ))}
            <Link
              to="/demo"
              className="ml-3 flex items-center px-5 py-2 text-sm font-medium rounded-full bg-gradient-to-r from-purple-600 to-pink-500 text-white shadow-md hover:shadow-lg transition-all duration-200 hover:scale-105"
            >
              <Zap className="w-4 h-4 mr-1.5" />
              Try Now
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-3 rounded-full bg-purple-50 text-gray-600 hover:text-pink-600 transition-colors focus:outline-none min-w-[44px] min-h-[44px] flex items-center justify-center"
            >
              {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div
        className={`md:hidden fixed inset-y-0 right-0 transform w-full max-w-xs sm:w-72 bg-white shadow-xl transition-transform duration-300 ease-in-out z-60 ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="pt-16 px-4 sm:px-6 space-y-3 h-full overflow-y-auto pb-20">
          <div className="flex justify-end absolute top-3 right-3 sm:top-5 sm:right-5">
            <button
              onClick={() => setIsOpen(false)}
              className="p-3 rounded-full bg-purple-50 text-gray-600 hover:text-pink-600 transition-colors focus:outline-none min-w-[44px] min-h-[44px] flex items-center justify-center"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          <div className="border-b border-gray-100 pb-5 mb-5">
            <Link to="/" className="flex items-center space-x-2 mb-6" onClick={() => setIsOpen(false)}>
              <div className="bg-gradient-to-r from-purple-600 to-pink-500 rounded-full p-2">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-500 bg-clip-text text-transparent">
                HueMatch
              </span>
            </Link>
          </div>
          
          {navItems.map((item) => (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center px-4 py-3 text-base font-medium rounded-xl transition-colors
                hover:bg-purple-50 ${
                  location.pathname === item.path || location.pathname.startsWith(item.path + '/')
                    ? 'text-pink-600 bg-purple-50'
                    : 'text-gray-700'
                }`}
              onClick={() => setIsOpen(false)}
            >
              <div className="bg-white shadow-sm rounded-lg p-2 mr-3">
                {React.cloneElement(item.icon, { className: "w-5 h-5 text-pink-600" })}
              </div>
              {item.name}
            </Link>
          ))}
          
          <div className="mt-8 pt-6 border-t border-gray-100">
            <Link
              to="/demo"
              className="flex items-center justify-center px-5 py-3 text-base font-medium rounded-xl bg-gradient-to-r from-purple-600 to-pink-500 text-white shadow-md hover:shadow-lg transition-all duration-200"
              onClick={() => setIsOpen(false)}
            >
              <Zap className="w-5 h-5 mr-2" />
              Try HueMatch Now
            </Link>
          </div>
        </div>
      </div>
      
      {/* Overlay for mobile menu */}
      {isOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
          onClick={() => setIsOpen(false)}
        ></div>
      )}
    </nav>
  );
};

export default Navbar;