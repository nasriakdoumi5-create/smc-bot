'use client';
import { Heart } from 'lucide-react';
import { useCart } from '@/context/CartContext';

export default function WishlistButton({ productId, className = '' }) {
  const { isWishlisted, addToWishlist, removeFromWishlist } = useCart();
  const active = isWishlisted(productId);

  return (
    <button
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        active ? removeFromWishlist(productId) : addToWishlist(productId);
      }}
      className={`p-2 rounded-full transition-all ${active ? 'text-red-500 bg-red-50' : 'text-gray-400 bg-white hover:text-red-400'} ${className}`}
      aria-label={active ? 'Remove from wishlist' : 'Add to wishlist'}
    >
      <Heart className={`w-4 h-4 ${active ? 'fill-current' : ''}`} />
    </button>
  );
}
