'use client';
import Link from 'next/link';
import { useCart } from '@/context/CartContext';
import { ShoppingCart, ChevronDown } from 'lucide-react';
import StarRating from '@/components/StarRating';
import WishlistButton from '@/components/WishlistButton';
import { useState } from 'react';

export default function ProductCard({ product }) {
  const { addToCart } = useCart();
  const [selectedModel, setSelectedModel] = useState(product.models?.[0] || '');
  const [showModelPicker, setShowModelPicker] = useState(false);
  const [added, setAdded] = useState(false);
  const discount = product.originalPrice ? Math.round((1 - product.price / product.originalPrice) * 100) : 0;

  const handleAddToCart = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!selectedModel) {
      setShowModelPicker(true);
      return;
    }
    addToCart(product, selectedModel);
    setAdded(true);
    setTimeout(() => setAdded(false), 1500);
  };

  return (
    <div className="card group relative">
      <Link href={`/product/${product.slug}`} className="block relative overflow-hidden">
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-56 object-cover group-hover:scale-105 transition-transform duration-300"
        />
        {discount > 0 && (
          <span className="absolute top-3 left-3 bg-accent text-white text-xs font-bold px-2 py-1 rounded-lg">
            -{discount}%
          </span>
        )}
        {product.badge && (
          <span className={`absolute top-3 ${discount > 0 ? 'left-16' : 'left-3'} text-white text-xs font-bold px-2 py-1 rounded-lg ${
            product.badge === 'Best Seller' ? 'bg-yellow-500' :
            product.badge === 'New' ? 'bg-primary' : 'bg-purple-500'
          }`}>
            {product.badge}
          </span>
        )}
        <div className="absolute top-3 right-3">
          <WishlistButton productId={product.id} />
        </div>
        {product.stock && product.stock <= 5 && (
          <div className="absolute bottom-0 left-0 right-0 bg-red-500/90 text-white text-xs font-bold text-center py-1">
            Only {product.stock} left!
          </div>
        )}
      </Link>

      <div className="p-4">
        <Link href={`/product/${product.slug}`}>
          <h3 className="font-semibold text-dark hover:text-primary transition-colors line-clamp-2 mb-1">{product.name}</h3>
        </Link>

        {product.rating && (
          <div className="mb-1">
            <StarRating rating={product.rating} count={product.reviewCount} />
          </div>
        )}

        <div className="flex items-center gap-2 mb-3">
          <span className="text-xl font-bold text-accent">€{product.price}</span>
          {product.originalPrice && (
            <span className="text-sm text-gray-400 line-through">€{product.originalPrice}</span>
          )}
          {discount > 0 && (
            <span className="text-xs text-green-600 font-medium">Save €{product.originalPrice - product.price}</span>
          )}
        </div>

        {/* Model selector */}
        {product.models && product.models.length > 0 && (
          <div className="mb-3 relative">
            <button
              onClick={e => { e.preventDefault(); setShowModelPicker(!showModelPicker); }}
              className="w-full flex items-center justify-between border-2 border-gray-200 rounded-xl px-3 py-2 text-xs font-medium hover:border-primary transition-colors bg-white"
            >
              <span className="text-gray-600">{selectedModel || 'Select model'}</span>
              <ChevronDown className={`w-3.5 h-3.5 text-gray-400 transition-transform ${showModelPicker ? 'rotate-180' : ''}`} />
            </button>
            {showModelPicker && (
              <div className="absolute top-full left-0 right-0 z-20 bg-white border border-gray-200 rounded-xl shadow-lg mt-1 overflow-hidden">
                <div className="max-h-40 overflow-y-auto">
                  {product.models.map(m => (
                    <button
                      key={m}
                      onClick={e => { e.preventDefault(); setSelectedModel(m); setShowModelPicker(false); }}
                      className={`w-full text-left px-3 py-2 text-xs hover:bg-secondary transition-colors ${selectedModel === m ? 'bg-primary/5 text-primary font-semibold' : 'text-gray-700'}`}
                    >
                      {m}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <button
          onClick={handleAddToCart}
          className={`w-full py-2.5 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-all ${
            added
              ? 'bg-green-600 text-white'
              : 'bg-primary text-white hover:bg-green-700'
          }`}
        >
          <ShoppingCart className="w-4 h-4" />
          {added ? '✓ Added!' : 'Add to Cart'}
        </button>
      </div>
    </div>
  );
}
