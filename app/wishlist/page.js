'use client';
import { useCart } from '@/context/CartContext';
import { getProductById } from '@/data/products';
import ProductCard from '@/components/ProductCard';
import Link from 'next/link';
import { Heart } from 'lucide-react';

export default function WishlistPage() {
  const { wishlist } = useCart();
  const wishlistProducts = wishlist.map(id => getProductById(id)).filter(Boolean);

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="flex items-center gap-3 mb-8">
        <Heart className="w-7 h-7 text-red-500 fill-current" />
        <h1 className="text-3xl font-bold text-dark">My Wishlist</h1>
        {wishlistProducts.length > 0 && (
          <span className="bg-red-100 text-red-600 text-sm font-semibold px-3 py-1 rounded-full">
            {wishlistProducts.length} {wishlistProducts.length === 1 ? 'item' : 'items'}
          </span>
        )}
      </div>

      {wishlistProducts.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">💝</div>
          <h2 className="text-2xl font-bold mb-2 text-dark">Your wishlist is empty</h2>
          <p className="text-gray-500 mb-6">Save your favourite designs and come back to them any time.</p>
          <Link href="/products" className="btn-primary">Discover Cases</Link>
        </div>
      ) : (
        <>
          <p className="text-gray-500 mb-8">Your saved favourites — ready to add to cart whenever you are.</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {wishlistProducts.map(p => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
          <div className="mt-10 text-center">
            <Link href="/products" className="btn-outline">Continue Shopping</Link>
          </div>
        </>
      )}
    </div>
  );
}
