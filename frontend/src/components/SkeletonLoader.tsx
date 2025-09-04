import React from 'react';

interface SkeletonLoaderProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'rectangular' | 'circular';
  animation?: boolean;
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  className = '',
  width = '100%',
  height = '1rem',
  variant = 'rectangular',
  animation = true,
}) => {
  const baseClasses = 'bg-gray-200';
  const animationClasses = animation ? 'shimmer-bg' : '';
  
  const variantClasses = {
    text: 'rounded',
    rectangular: 'rounded-md',
    circular: 'rounded-full',
  };

  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  return (
    <div
      className={`
        ${baseClasses} 
        ${variantClasses[variant]} 
        ${animationClasses} 
        ${className}
      `}
      style={style}
      role="presentation"
      aria-label="Loading content"
    />
  );
};

// Pre-built skeleton components for common use cases
export const ProductCardSkeleton: React.FC = () => (
  <div className="p-4 border border-gray-200 rounded-lg space-y-4">
    <SkeletonLoader variant="rectangular" height="200px" />
    <SkeletonLoader variant="text" height="1.5rem" />
    <SkeletonLoader variant="text" height="1rem" width="60%" />
    <SkeletonLoader variant="text" height="1.25rem" width="40%" />
  </div>
);

export const ColorPaletteSkeleton: React.FC = () => (
  <div className="space-y-4">
    <SkeletonLoader variant="text" height="2rem" width="70%" />
    <div className="flex space-x-2">
      {Array.from({ length: 6 }).map((_, i) => (
        <SkeletonLoader
          key={i}
          variant="circular"
          width="3rem"
          height="3rem"
        />
      ))}
    </div>
    <SkeletonLoader variant="text" height="1rem" />
    <SkeletonLoader variant="text" height="1rem" width="80%" />
  </div>
);

export default SkeletonLoader;
