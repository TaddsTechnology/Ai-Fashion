import React from 'react';
import { Star, ShoppingBag, Eye, ExternalLink } from 'lucide-react';

interface Product {
  id?: number;
  name?: string;
  product_name?: string;
  'Product Name'?: string;
  brand?: string;
  price?: string;
  Price?: string;
  rating?: number;
  image?: string;
  image_url?: string;
  'Image URL'?: string;
  mst?: string;
  desc?: string;
  description?: string;
  product_type?: string;
  'Product Type'?: string;
  category?: string;
  color?: string;
  baseColour?: string;
  hex_color?: string;
  undertone?: string;
  shade_name?: string;
  gender?: string;
  occasion?: string;
  season?: string;
  product_url?: string;
}

interface ColorInfo {
  name: string;
  hex: string;
}

interface ColorRecommendations {
  colors_that_suit?: ColorInfo[];
  colors?: ColorInfo[];
  colors_to_avoid?: ColorInfo[];
  seasonal_type?: string;
  monk_skin_tone?: string;
  message?: string;
  description?: string;
  database_source?: boolean;
}

interface EnhancedProductRecommendationsProps {
  products: Product[];
  loading: boolean;
  error: string | null;
  activeTab: 'makeup' | 'outfit' | 'colors';
  skinTone?: string;
  monkTone?: string;
  colorRecommendations?: ColorRecommendations | null;
  totalItems: number;
  totalPages: number;
  currentPage: number;
  itemsPerPage: number;
  onPageChange: (page: number) => void;
  availableFilters: {[key: string]: string[]};
  selectedFilters: {[key: string]: string};
  onFilterChange: (filters: {[key: string]: string}) => void;
  className?: string;
}

const EnhancedProductRecommendations: React.FC<EnhancedProductRecommendationsProps> = ({
  products,
  loading,
  error,
  activeTab,
  skinTone,
  monkTone,
  colorRecommendations,
  totalItems,
  totalPages,
  currentPage,
  itemsPerPage,
  onPageChange,
  availableFilters,
  selectedFilters,
  onFilterChange,
  className = ""
}) => {
  // Helper functions to get product data
  const getProductName = (product: Product): string => {
    return product.name || product.product_name || product['Product Name'] || 'Unknown Product';
  };

  const getProductPrice = (product: Product): string => {
    return product.price || product.Price || 'N/A';
  };

  const getProductImage = (product: Product): string => {
    const imageUrl = product.image || product.image_url || product['Image URL'];
    return imageUrl || `https://via.placeholder.com/200x200/f3f4f6/9ca3af?text=${activeTab === 'makeup' ? 'Makeup' : 'Outfit'}`;
  };

  const getProductDescription = (product: Product): string => {
    return product.desc || product.description || `${getProductName(product)} from ${product.brand || 'premium brand'}`;
  };

  const getProductType = (product: Product): string => {
    return product.product_type || product['Product Type'] || product.category || '';
  };

  // Handle filter changes
  const handleFilterChange = (filterKey: string, value: string) => {
    const newFilters = { ...selectedFilters, [filterKey]: value };
    onFilterChange(newFilters);
  };

  // Render filters
  const renderFilters = () => {
    if (Object.keys(availableFilters).length === 0) return null;

    return (
      <div className="mb-6 p-4 bg-gray-50 rounded-lg border">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Filter Products</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(availableFilters).map(([filterKey, options]) => (
            <div key={filterKey}>
              <label className="block text-xs text-gray-600 mb-1 capitalize">
                {filterKey.replace(/([A-Z])/g, ' $1').toLowerCase()}
              </label>
              <select
                value={selectedFilters[filterKey] || ''}
                onChange={(e) => handleFilterChange(filterKey, e.target.value)}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All {filterKey}</option>
                {options.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Render pagination
  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const pageNumbers = [];
    const maxVisiblePages = 5;
    const startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    for (let i = startPage; i <= endPage; i++) {
      pageNumbers.push(i);
    }

    return (
      <div className="mt-8 flex flex-col sm:flex-row items-center justify-between">
        <div className="text-sm text-gray-700 mb-4 sm:mb-0">
          Showing {Math.min((currentPage - 1) * itemsPerPage + 1, totalItems)} to{' '}
          {Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems} results
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-3 py-2 text-sm border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
          >
            Previous
          </button>
          
          {pageNumbers.map((page) => (
            <button
              key={page}
              onClick={() => onPageChange(page)}
              className={`px-3 py-2 text-sm border rounded-md transition-colors ${
                currentPage === page
                  ? 'bg-purple-600 text-white border-purple-600'
                  : 'border-gray-300 hover:bg-gray-50'
              }`}
            >
              {page}
            </button>
          ))}
          
          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="px-3 py-2 text-sm border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
          >
            Next
          </button>
        </div>
      </div>
    );
  };

  // Render product card
  const renderProductCard = (product: Product, index: number) => {
    const productName = getProductName(product);
    const productPrice = getProductPrice(product);
    const productImage = getProductImage(product);
    const productDescription = getProductDescription(product);
    const productType = getProductType(product);

    return (
      <div
        key={product.id || index}
        className="bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-300 overflow-hidden border border-gray-200 group"
      >
        <div className="relative aspect-w-1 aspect-h-1 bg-gray-100">
          <img
            src={productImage}
            alt={productName}
            className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.src = `https://via.placeholder.com/200x200/f3f4f6/9ca3af?text=${activeTab === 'makeup' ? 'Makeup' : 'Outfit'}`;
            }}
          />
          {product.rating && (
            <div className="absolute top-2 right-2 bg-white bg-opacity-90 px-2 py-1 rounded-full flex items-center">
              <Star className="w-3 h-3 text-yellow-400 fill-current mr-1" />
              <span className="text-xs font-medium">{product.rating}</span>
            </div>
          )}
        </div>
        
        <div className="p-4">
          <div className="mb-2">
            <h3 className="font-semibold text-gray-800 text-sm mb-1 line-clamp-2 group-hover:text-purple-700 transition-colors">
              {productName}
            </h3>
            <p className="text-xs text-gray-500 mb-1">
              {product.brand || 'Unknown Brand'}
            </p>
            {productType && (
              <p className="text-xs text-purple-600 font-medium">
                {productType}
              </p>
            )}
          </div>
          
          <div className="mb-3">
            <span className="font-bold text-purple-600 text-lg">
              {productPrice}
            </span>
            {monkTone && (
              <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full ml-2">
                {monkTone}
              </span>
            )}
          </div>

          {/* Product-specific details */}
          <div className="space-y-1 mb-3">
            {activeTab === 'makeup' && (
              <>
                {product.undertone && (
                  <p className="text-xs text-gray-500">Undertone: {product.undertone}</p>
                )}
                {product.shade_name && (
                  <p className="text-xs text-gray-500">Shade: {product.shade_name}</p>
                )}
                {product.color && (
                  <p className="text-xs text-gray-500">Color: {product.color}</p>
                )}
              </>
            )}

            {activeTab === 'outfit' && (
              <>
                {product.gender && (
                  <p className="text-xs text-gray-500">Gender: {product.gender}</p>
                )}
                {product.occasion && (
                  <p className="text-xs text-gray-500">Occasion: {product.occasion}</p>
                )}
                {product.baseColour && (
                  <p className="text-xs text-gray-500">Color: {product.baseColour}</p>
                )}
                {product.season && (
                  <p className="text-xs text-gray-500">Season: {product.season}</p>
                )}
              </>
            )}
          </div>

          <p className="text-xs text-gray-600 mb-3 line-clamp-2">
            {productDescription}
          </p>

          {/* Action buttons */}
          <div className="flex space-x-2">
            <button className="flex-1 bg-purple-100 text-purple-700 py-2 px-3 rounded text-xs font-medium hover:bg-purple-200 transition-colors flex items-center justify-center">
              <Eye className="w-3 h-3 mr-1" />
              Details
            </button>
            {product.product_url ? (
              <a
                href={product.product_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 bg-purple-600 text-white py-2 px-3 rounded text-xs font-medium hover:bg-purple-700 transition-colors flex items-center justify-center"
              >
                <ExternalLink className="w-3 h-3 mr-1" />
                Buy Now
              </a>
            ) : (
              <button className="flex-1 bg-purple-600 text-white py-2 px-3 rounded text-xs font-medium hover:bg-purple-700 transition-colors flex items-center justify-center">
                <ShoppingBag className="w-3 h-3 mr-1" />
                Add to Cart
              </button>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={`enhanced-product-recommendations ${className}`}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-800 capitalize">
            {activeTab === 'makeup' ? '💄' : '👗'} {activeTab} Recommendations
          </h2>
          {skinTone && (
            <div className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
              For {skinTone} skin tone
            </div>
          )}
        </div>
        
        {colorRecommendations && colorRecommendations.description && (
          <p className="text-sm text-gray-600 mb-4">
            {colorRecommendations.description}
          </p>
        )}
      </div>

      {/* Filters */}
      {renderFilters()}

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600 text-sm">⚠️ {error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          <span className="ml-3 text-gray-600">Loading {activeTab} products...</span>
        </div>
      )}

      {/* Products Grid */}
      {!loading && (
        <>
          {products.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {products.map((product, index) => renderProductCard(product, index))}
            </div>
          ) : (
            /* Empty State */
            <div className="text-center py-12">
              <div className="text-gray-400 text-6xl mb-4">
                {activeTab === 'makeup' ? '💄' : '👗'}
              </div>
              <h3 className="text-lg font-medium text-gray-600 mb-2">
                No {activeTab} products found
              </h3>
              <p className="text-gray-500 mb-4">
                We're working on bringing you personalized {activeTab} recommendations based on your skin tone analysis.
              </p>
              {colorRecommendations && (
                <div className="max-w-md mx-auto">
                  <p className="text-sm text-purple-600 bg-purple-50 p-3 rounded-lg">
                    💡 Try adjusting your filters or check back soon for new products matching your {colorRecommendations.seasonal_type} color palette!
                  </p>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Pagination */}
      {!loading && products.length > 0 && renderPagination()}
    </div>
  );
};

export default EnhancedProductRecommendations;
