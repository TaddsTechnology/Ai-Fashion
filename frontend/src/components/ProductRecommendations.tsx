import React, { useState, Suspense, lazy } from 'react';
// import ProductCard from './ProductCard';
import { Product } from '../types/Product';
import { ChevronLeft, ChevronRight, Filter } from 'lucide-react';

interface ProductRecommendationsProps {
  skinTone: string;
  products: Product[];
  type: 'makeup' | 'outfit';
  totalItems?: number;
  totalPages?: number;
  currentPage?: number;
  onPageChange?: (page: number) => void;
  onFilterChange?: (filters: { [key: string]: string }) => void;
  availableFilters?: { [key: string]: string[] };
}

// Rename to LazyProductCard
const LazyProductCard = lazy(() => import('./ProductCard'));

// Loading skeleton component
const ProductCardSkeleton = () => (
  <div className="animate-pulse">
    <div className="bg-gray-200 h-48 rounded-lg mb-4"></div>
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
  </div>
);

const ProductRecommendations: React.FC<ProductRecommendationsProps> = ({
  skinTone,
  products,
  type,
  totalItems = 0,
  totalPages = 1,
  currentPage = 1,
  onPageChange = () => {},
  onFilterChange = () => {},
  availableFilters = {}
}) => {
  const [showFilters, setShowFilters] = useState(false);
  const [selectedFilters, setSelectedFilters] = useState<{ [key: string]: string }>({});

  const handleFilterChange = (filterType: string, value: string) => {
    const newFilters = { ...selectedFilters, [filterType]: value };
    setSelectedFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearFilters = () => {
    setSelectedFilters({});
    onFilterChange({});
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {type === 'makeup' ? 'Makeup Recommendations' : 'Outfit Recommendations'}
          </h2>
          <p className="text-gray-600">
            {type === 'makeup'
              ? `Personalized makeup products for ${skinTone} skin tone`
              : `Outfit recommendations that complement your ${skinTone} skin tone`}
          </p>
        </div>
        
        {Object.keys(availableFilters).length > 0 && (
          <button 
            onClick={() => setShowFilters(!showFilters)}
            className="mt-4 md:mt-0 flex items-center px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
          >
            <Filter className="w-4 h-4 mr-2" />
            {showFilters ? 'Hide Filters' : 'Show Filters'}
          </button>
        )}
      </div>

      {/* Filters */}
      {showFilters && Object.keys(availableFilters).length > 0 && (
        <div className="bg-gray-50 p-4 rounded-lg mb-6">
          <div className="flex flex-wrap gap-4">
            {Object.entries(availableFilters).map(([filterType, options]) => (
              <div key={filterType} className="flex-1 min-w-[200px]">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
                </label>
                <select
                  value={selectedFilters[filterType] || ''}
                  onChange={(e) => handleFilterChange(filterType, e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="">All {filterType}s</option>
                  {options.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
            ))}
            <div className="flex items-end">
              <button
                onClick={clearFilters}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Products Grid */}
      {products.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {products.map((product, index) => (
            <Suspense key={product.id || index} fallback={<ProductCardSkeleton />}>
              <LazyProductCard
                key={product.id || index}
                id={product.id || index}
                name={product.product_name || product.name}
                brand={product.brand}
                desc={product.desc}
                price={product.price}
                rating={product.rating || 4.5}
                image={product.image_url || product.image}
                mst={product.mst}
                onAddToCart={() => {
                  console.log('Add to cart:', product.name);
                }}
                onFavorite={() => {
                  console.log('Add to favorites:', product.name);
                }}
              />
            </Suspense>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No products found matching your criteria.</p>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center mt-8">
          <nav className="flex items-center space-x-2">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="p-2 rounded-md border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              aria-label="Previous page"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>
            
            <div className="flex space-x-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(page => 
                  page === 1 || 
                  page === totalPages || 
                  (page >= currentPage - 1 && page <= currentPage + 1)
                )
                .map((page, index, array) => (
                  <React.Fragment key={page}>
                    {index > 0 && array[index - 1] !== page - 1 && (
                      <span className="px-4 py-2 text-gray-500">...</span>
                    )}
                    <button
                      onClick={() => onPageChange(page)}
                      className={`px-4 py-2 rounded-md ${
                        currentPage === page
                          ? 'bg-purple-600 text-white'
                          : 'border border-gray-300 hover:bg-gray-50'
                      }`}
                      aria-label={`Page ${page}`}
                      aria-current={currentPage === page ? 'page' : undefined}
                    >
                      {page}
                    </button>
                  </React.Fragment>
                ))
              }
            </div>
            
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="p-2 rounded-md border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              aria-label="Next page"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </nav>
        </div>
      )}

      {/* Results Summary */}
      {totalItems > 0 && (
        <div className="text-center text-sm text-gray-500 mt-4">
          Showing {Math.min((currentPage - 1) * (products.length) + 1, totalItems)} to {Math.min(currentPage * products.length, totalItems)} of {totalItems} products
        </div>
      )}
    </div>
  );
};

export default ProductRecommendations; 