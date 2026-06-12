'use client';
import { ShoppingCart, Zap } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function StickyATC({ product, selectedModel, onAddToCart, onBuyNow, added }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => setVisible(window.scrollY > 400);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-2xl">
      <div className="max-w-3xl mx-auto px-4 py-3">
        {/* Desktop: show product name + model */}
        <div className="hidden md:flex items-center justify-between gap-4 mb-2">
          <div className="flex items-center gap-3">
            {product?.image && (
              <img src={product.image} alt={product.name} className="w-10 h-10 rounded-lg object-cover" />
            )}
            <div>
              <p className="font-semibold text-dark text-sm">{product?.name}</p>
              <p className="text-xs text-gray-400">{selectedModel}</p>
            </div>
          </div>
          <p className="font-bold text-accent text-lg">€{product?.price}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={onAddToCart}
            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-sm transition-all ${
              added ? 'bg-green-600 text-white' : 'bg-primary text-white hover:bg-green-700'
            }`}
          >
            <ShoppingCart className="w-4 h-4" />
            {added ? '✓ Added to Cart!' : 'Add to Cart'}
          </button>
          <button
            onClick={onBuyNow}
            className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-sm bg-accent text-white hover:bg-orange-600 transition-colors"
          >
            <Zap className="w-4 h-4" />
            Buy Now
          </button>
        </div>
      </div>
    </div>
  );
}
