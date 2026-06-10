'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useCart } from '../context/CartContext';
import { useState } from 'react';

export default function ProductCard({ product }) {
  const { dispatch } = useCart();
  const [added, setAdded] = useState(false);

  const discount = Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100);

  function handleAdd(e) {
    e.preventDefault();
    dispatch({ type: 'ADD', product });
    setAdded(true);
    setTimeout(() => setAdded(false), 1500);
  }

  return (
    <Link href={`/product/${product.id}`} className="card group block overflow-hidden">
      {/* Image */}
      <div className="relative overflow-hidden bg-gray-100 aspect-square">
        <Image
          src={product.image}
          alt={product.name}
          fill
          className="object-cover group-hover:scale-105 transition-transform duration-300"
          sizes="(max-width: 768px) 50vw, 25vw"
        />
        {discount > 0 && (
          <span className="absolute top-2 right-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-lg">
            -{discount}%
          </span>
        )}
        {product.tags.map(tag => (
          <span key={tag} className="absolute top-2 left-2 bg-primary-600 text-white text-xs font-bold px-2 py-1 rounded-lg">
            {tag}
          </span>
        ))}
        {product.stock <= 5 && product.stock > 0 && (
          <span className="absolute bottom-2 right-2 bg-orange-500 text-white text-xs font-bold px-2 py-1 rounded-lg">
            آخر {product.stock} قطع
          </span>
        )}
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-800 text-sm mb-1 line-clamp-2 leading-snug">
          {product.name}
        </h3>

        {/* Rating */}
        <div className="flex items-center gap-1 mb-2">
          <span className="text-yellow-400 text-sm">★</span>
          <span className="text-sm font-medium text-gray-700">{product.rating}</span>
          <span className="text-xs text-gray-400">({product.reviews})</span>
        </div>

        {/* Price */}
        <div className="flex items-center gap-2 mb-3">
          <span className="text-lg font-bold text-primary-600">{product.price} ر.س</span>
          {product.originalPrice > product.price && (
            <span className="text-sm text-gray-400 line-through">{product.originalPrice} ر.س</span>
          )}
        </div>

        <button
          onClick={handleAdd}
          className={`w-full py-2 rounded-xl text-sm font-semibold transition-all duration-200 active:scale-95 ${
            added
              ? 'bg-green-100 text-green-700'
              : 'bg-primary-50 hover:bg-primary-600 text-primary-600 hover:text-white'
          }`}
        >
          {added ? '✓ تمت الإضافة' : '+ أضف للسلة'}
        </button>
      </div>
    </Link>
  );
}
