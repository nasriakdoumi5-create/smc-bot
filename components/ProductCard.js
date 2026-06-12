'use client';
import Link from 'next/link';
import { useCart } from '@/context/CartContext';
import { ShoppingCart } from 'lucide-react';
import StarRating from '@/components/StarRating';
import WishlistButton from '@/components/WishlistButton';

export default function ProductCard({ product }) {
  const { addToCart } = useCart();
  const discount = product.originalPrice ? Math.round((1 - product.price / product.originalPrice) * 100) : 0;

  return (
    <div className="card group">
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
            product.badge === 'New' ? 'bg-primary' :
            'bg-purple-500'
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
        {product.viewerCount && product.stock > 5 && (
          <p className="text-xs text-orange-500 font-medium mb-2">🔥 {product.viewerCount} people viewing</p>
        )}
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xl font-bold text-accent">€{product.price}</span>
          {product.originalPrice && (
            <span className="text-sm text-gray-400 line-through">€{product.originalPrice}</span>
          )}
        </div>
        <button
          onClick={() => addToCart(product, product.models[0])}
          className="w-full bg-primary text-white py-2 rounded-xl text-sm font-medium hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
        >
          <ShoppingCart className="w-4 h-4" />
          Add to Cart
        </button>
      </div>
    </div>
  );
}
