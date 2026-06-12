'use client';
import { ShoppingCart, Zap } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function StickyATC({ product, selectedModel, onAddToCart, onBuyNow, added }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setVisible(window.scrollY > 400);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 p-3 md:hidden shadow-2xl">
      <div className="flex gap-2 max-w-lg mx-auto">
        <button
          onClick={onAddToCart}
          className={`flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl font-bold text-sm transition-all ${added ? 'bg-green-600 text-white' : 'bg-primary text-white'}`}
        >
          <ShoppingCart className="w-4 h-4" />
          {added ? '✓ Added!' : 'Add to Cart'}
        </button>
        <button
          onClick={onBuyNow}
          className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl font-bold text-sm bg-accent text-white"
        >
          <Zap className="w-4 h-4" />
          Buy Now
        </button>
      </div>
    </div>
  );
}
