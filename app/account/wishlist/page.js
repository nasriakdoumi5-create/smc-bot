'use client';
import { useSession } from 'next-auth/react';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProductCard from '../../../components/ProductCard';
import Link from 'next/link';

export default function WishlistPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [products, setProducts] = useState([]);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    if (status === 'unauthenticated') router.push('/login');
  }, [status]);

  useEffect(() => {
    if (session) {
      fetch('/api/wishlist').then(r => r.json()).then(d => { setProducts(d); setLoading(false); });
    }
  }, [session]);

  if (status === 'loading' || loading) return <div className="flex justify-center py-20"><div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" /></div>;
  if (!session) return null;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center gap-3 mb-8">
        <Link href="/account" className="text-gray-400 hover:text-gray-600">← حسابي</Link>
        <h1 className="text-2xl font-bold text-gray-800">المفضلة ❤️</h1>
        {products.length > 0 && <span className="badge bg-red-100 text-red-600">{products.length} منتج</span>}
      </div>

      {products.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <div className="text-6xl mb-4">❤️</div>
          <p className="text-lg font-medium">قائمة المفضلة فارغة</p>
          <p className="text-sm mt-1">احفظ المنتجات التي تعجبك هنا</p>
          <Link href="/products" className="btn-primary mt-4 inline-block">تصفح المنتجات</Link>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {products.map(p => <ProductCard key={p.id} product={p} wishlistIds={products.map(x => x.id)} />)}
        </div>
      )}
    </div>
  );
}
