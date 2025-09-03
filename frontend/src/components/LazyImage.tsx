import React, { useState, useRef, useEffect } from 'react';
import { Eye } from 'lucide-react';

interface LazyImageProps {
  src: string;
  alt: string;
  className?: string;
  placeholder?: string;
  blurDataURL?: string;
  quality?: number;
  priority?: boolean;
  sizes?: string;
  onLoad?: () => void;
  onError?: () => void;
}

const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  className = '',
  placeholder,
  blurDataURL,
  quality = 85,
  priority = false,
  sizes = '100vw',
  onLoad,
  onError
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(priority); // Load immediately if priority
  const [hasError, setHasError] = useState(false);
  const [optimizedSrc, setOptimizedSrc] = useState('');
  const imgRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Optimize image URL based on device capabilities
  const optimizeImageUrl = (originalSrc: string) => {
    try {
      const url = new URL(originalSrc);
      
      // Check if it's a supported image service
      if (url.hostname.includes('pexels.com') || url.hostname.includes('unsplash.com')) {
        // Add WebP format support
        if (supportsWebP()) {
          url.searchParams.set('fm', 'webp');
        }
        
        // Add responsive sizing
        const screenWidth = window.innerWidth;
        const dpr = window.devicePixelRatio || 1;
        const targetWidth = Math.min(screenWidth * dpr, 2048);
        
        url.searchParams.set('w', targetWidth.toString());
        url.searchParams.set('q', quality.toString());
        
        // Enable compression
        url.searchParams.set('auto', 'compress');
      }
      
      return url.toString();
    } catch {
      return originalSrc;
    }
  };

  // Check WebP support
  const supportsWebP = () => {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  };

  // Generate blur placeholder
  const generateBlurDataURL = () => {
    const canvas = document.createElement('canvas');
    canvas.width = 10;
    canvas.height = 10;
    const ctx = canvas.getContext('2d');
    
    if (ctx) {
      // Create a simple gradient as blur placeholder
      const gradient = ctx.createLinearGradient(0, 0, 10, 10);
      gradient.addColorStop(0, '#f3f4f6');
      gradient.addColorStop(1, '#e5e7eb');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 10, 10);
    }
    
    return canvas.toDataURL('image/jpeg', 0.1);
  };

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (priority) return; // Skip observer if priority loading

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        rootMargin: '50px', // Load 50px before entering viewport
        threshold: 0.1
      }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, [priority]);

  // Optimize image URL when component mounts or src changes
  useEffect(() => {
    setOptimizedSrc(optimizeImageUrl(src));
  }, [src, quality]);

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    console.warn(`Failed to load image: ${src}`);
    setHasError(true);
    onError?.();
  };

  // Generate a colored placeholder based on alt text for better UX
  const getColorFromAlt = (altText: string) => {
    let hash = 0;
    for (let i = 0; i < altText.length; i++) {
      hash = altText.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = hash % 360;
    return `hsl(${hue}, 70%, 85%)`;
  };

  const placeholderSrc = blurDataURL || placeholder || generateBlurDataURL();

  return (
    <div ref={containerRef} className={`relative overflow-hidden ${className}`}>
      {/* Blur placeholder */}
      <img
        src={placeholderSrc}
        alt=""
        className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-300 ${
          isLoaded ? 'opacity-0' : 'opacity-100'
        }`}
        style={{ filter: 'blur(5px)' }}
        aria-hidden="true"
      />

      {/* Main image */}
      {isInView && !hasError && (
        <img
          ref={imgRef}
          src={optimizedSrc}
          alt={alt}
          sizes={sizes}
          className={`w-full h-full object-cover transition-opacity duration-300 ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          }`}
          onLoad={handleLoad}
          onError={handleError}
          loading={priority ? 'eager' : 'lazy'}
          decoding="async"
        />
      )}

      {/* Error state */}
      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-200">
          <div className="text-center text-gray-500">
            <Eye className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">Image unavailable</p>
          </div>
        </div>
      )}

      {/* Loading state */}
      {isInView && !isLoaded && !hasError && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}
    </div>
  );
};

export default LazyImage;
