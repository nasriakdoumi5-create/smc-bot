'use client';
import Link from 'next/link';
import { useCart } from '@/context/CartContext';
import { ShoppingCart } from 'lucide-react';

export default function ProductCard({ product }) {
  const { addToCart } = useCart();
  const discount = Math.round((1 - product.price / product.originalPrice) * 100);

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
        {product.isCustom && (
          <span className="absolute top-3 right-3 bg-primary text-white text-xs font-bold px-2 py-1 rounded-lg">
            Custom
          </span>
        )}
      </Link>
      <div className="p-4">
        <Link href={`/product/${product.slug}`}>
          <h3 className="font-semibold text-dark hover:text-primary transition-colors line-clamp-2 mb-1">{product.name}</h3>
        </Link>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xl font-bold text-accent">€{product.price}</span>
          {product.originalPrice && (
            <span className="text-sm text-gray-400 line-through">€{product.originalPrice}</span>
          )}
        </div>
        <button
          onClick={() => addToCart(product, product.models[0])}
          className="w-full bg-primary text-white py-2 rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors flex items-center justify-center gap-2"
        >
          <ShoppingCart className="w-4 h-4" />
          Add to Cart
        </button>
      </div>
    </div>
  );
}
