import React, { useEffect } from 'react';
import { Star, ShoppingCart, Heart } from 'lucide-react';

interface ProductCardProps {
  id: number;
  name: string;
  brand: string;
  price: string;
  rating?: number;
  image: string;
  mst?: string;
  desc: string;
  onAddToCart?: () => void;
  onFavorite?: () => void;
}

// useEffect(()=>{

//   }
// },[])
// const storedAnalysis1 = sessionStorage.getItem('skinAnalysis');
// if (!storedAnalysis1) {
//   throw new Error('No skin analysis found. Please complete the skin analysis first.');}
// const analysisArray1 = JSON.parse(storedAnalysis1);

const ProductCard: React.FC<ProductCardProps> = ({
  name,
  brand,
  price,
  image,
  desc,
  onAddToCart,
  onFavorite,
}) => {
  const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(`"${brand}"`)}+${encodeURIComponent(`"${name}"`)}+${encodeURIComponent(`"${desc}"`)}`;
  // const shouldHideDescription = price.includes('$ ');
  return (
    <>
    <a href={googleSearchUrl}>
    <div  className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
      {/* Image Container */}
      <div className="relative aspect-square overflow-hidden bg-gray-100">
        <img
          src={image}
          alt={`Stunning ${name} by ${brand} - perfect for your unique style`}
          className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            // target.src = `https://placehold.co/600x400/${analysisArray1[1].substring(1)}/${analysisArray1[1].substring(1)}/png`;
            target.onerror = null;
          }}
        />
      </div>

      <div className="p-4">
        <div className="text-sm text-gray-500 mb-1">{brand}</div>
        {/* <h3 className="font-medium text-gray-900 mb-2 line-clamp-2">{name} {!shouldHideDescription && desc}</h3> */}
        <h3 className="font-medium text-gray-900 mb-2 line-clamp-2">{name} {desc}</h3>
        
        {/* Rating */}
        {/* {typeof rating === 'number' && (
          <div className="flex items-center mb-2">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`w-4 h-4 ${
                  i < Math.round(rating)
                    ? 'text-yellow-400 fill-current'
                    : 'text-gray-300'
                }`}
              />
            ))}
            <span className="ml-1 text-sm text-gray-600">
              {rating.toFixed(1)}
            </span>
          </div>
        )} */}

        {/* Price and Actions */}
        <div className="flex items-center justify-between mt-3">
          <span className="text-lg font-semibold text-gray-900">{price}</span>
          <div className="flex space-x-2">
            <button
              onClick={onFavorite}
              className="p-2 rounded-full hover:bg-gray-100 transition-colors"
              aria-label="Save to your favorites - you'll love this!"
              title="Add to wishlist ❤️"
            >
              <Heart className="w-5 h-5 text-gray-600" />
            </button>
            <button
              onClick={onAddToCart}
              className="p-2 rounded-full bg-purple-100 hover:bg-purple-200 transition-colors"
              aria-label="Get this amazing product - it's perfect for you!"
              title="Add to cart 🛍️"
            >
              <ShoppingCart className="w-5 h-5 text-purple-600" />
            </button>
          </div>
        </div>
      </div>
    </div>
    </a>
    </>
  );
};

export default ProductCard;