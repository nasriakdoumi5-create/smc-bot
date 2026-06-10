'use client';
import Link from 'next/link';
import Image from 'next/image';
import { useCart } from '../context/CartContext';
import { useSession } from 'next-auth/react';
import { useState } from 'react';
import { toast } from 'sonner';

export default function ProductCard({ product, wishlistIds = [] }) {
  const { addToCart } = useCart();
  const { data: session } = useSession();
  const [wished, setWished]  = useState(wishlistIds.includes(product.id));
  const [adding, setAdding]  = useState(false);

  const discount = product.originalPrice ? Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100) : 0;
  const img      = product.images?.[0] || `https://picsum.photos/seed/${product.id}/400/400`;

  async function toggleWish(e) {
    e.preventDefault();
    if (!session) { toast.error('يجب تسجيل الدخول أولاً'); return; }
    const prev = wished;
    setWished(!wished);
    const res = await fetch('/api/wishlist', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ productId: product.id }) });
    if (!res.ok) setWished(prev);
    else toast.success(wished ? 'تمت الإزالة من المفضلة' : 'تمت الإضافة للمفضلة ❤️');
  }

  async function handleAdd(e) {
    e.preventDefault();
    setAdding(true);
    addToCart(product);
    toast.success('تمت الإضافة للسلة 🛒');
    setTimeout(() => setAdding(false), 1200);
  }

  return (
    <Link href={`/product/${product.slug}`} className="card group overflow-hidden block hover:shadow-lg transition-shadow duration-200">
      <div className="relative aspect-square overflow-hidden bg-gray-100">
        <Image src={img} alt={product.name} fill className="object-cover group-hover:scale-105 transition-transform duration-300" sizes="(max-width:640px) 50vw, (max-width:1024px) 33vw, 25vw" />
        {discount > 0 && <span className="absolute top-2 right-2 badge bg-red-500 text-white">-{discount}%</span>}
        {product.stock <= 3 && product.stock > 0 && <span className="absolute bottom-2 right-2 badge bg-orange-500 text-white">آخر {product.stock}</span>}
        {product.stock === 0 && <div className="absolute inset-0 bg-black/40 flex items-center justify-center"><span className="badge bg-black/70 text-white text-sm">نفذت الكمية</span></div>}
        <button onClick={toggleWish} className={`absolute top-2 left-2 w-8 h-8 rounded-full flex items-center justify-center transition-all ${wished ? 'bg-red-500 text-white' : 'bg-white/90 text-gray-400 hover:text-red-400 opacity-0 group-hover:opacity-100'}`}>
          {wished ? '❤️' : '🤍'}
        </button>
      </div>
      <div className="p-3">
        <p className="text-xs text-gray-400 mb-1">{product.category?.name}</p>
        <h3 className="font-semibold text-gray-800 text-sm line-clamp-2 leading-snug mb-2">{product.name}</h3>
        {Number(product.avgRating) > 0 && (
          <div className="flex items-center gap-1 mb-2">
            <span className="text-yellow-400 text-xs">{'★'.repeat(Math.round(product.avgRating))}{'☆'.repeat(5 - Math.round(product.avgRating))}</span>
            <span className="text-xs text-gray-400">({product.reviewCount || 0})</span>
          </div>
        )}
        <div className="flex items-baseline gap-1.5 mb-3">
          <span className="font-bold text-primary-600 text-base">{product.price} ر.س</span>
          {product.originalPrice > product.price && <span className="text-xs text-gray-400 line-through">{product.originalPrice} ر.س</span>}
        </div>
        <button onClick={handleAdd} disabled={product.stock === 0 || adding}
          className={`w-full py-2 rounded-xl text-xs font-bold transition-all duration-200 active:scale-95 ${product.stock === 0 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : adding ? 'bg-green-100 text-green-700' : 'bg-primary-50 hover:bg-primary-600 text-primary-700 hover:text-white'}`}>
          {adding ? '✓ تمت الإضافة' : product.stock === 0 ? 'نفذ' : '+ أضف للسلة'}
        </button>
      </div>
    </Link>
  );
}
