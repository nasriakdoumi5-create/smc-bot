import Link from 'next/link';
import { PRODUCTS, CATEGORIES } from '../data/products';
import ProductCard from '../components/ProductCard';

export default function HomePage() {
  const featured = PRODUCTS.filter(p => p.featured);
  const categories = CATEGORIES.filter(c => c.id !== 'all');

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-700 to-primary-900 text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
            🛍️ تسوق بذكاء، وفّر أكثر
          </h1>
          <p className="text-primary-100 text-lg mb-8 max-w-2xl mx-auto">
            آلاف المنتجات بأسعار منافسة، توصيل سريع، وضمان استرجاع خلال 14 يوم
          </p>
          <Link href="/products" className="inline-block bg-white text-primary-700 font-bold px-8 py-3.5 rounded-2xl hover:bg-primary-50 transition-colors text-lg shadow-lg">
            تصفح المنتجات →
          </Link>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-white py-8 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          {[
            { icon: '📦', value: '+500', label: 'منتج متاح' },
            { icon: '🚀', value: '24h', label: 'توصيل سريع' },
            { icon: '⭐', value: '4.8', label: 'تقييم العملاء' },
            { icon: '🔄', value: '14 يوم', label: 'ضمان الاسترجاع' },
          ].map(s => (
            <div key={s.label} className="py-2">
              <div className="text-2xl mb-1">{s.icon}</div>
              <div className="text-xl font-bold text-primary-600">{s.value}</div>
              <div className="text-sm text-gray-500">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Categories */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">تسوق حسب الفئة</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
            {categories.map(cat => {
              const icons = { electronics: '💻', clothing: '👕', home: '🏠', sports: '⚽', books: '📚' };
              return (
                <Link
                  key={cat.id}
                  href={`/products?category=${cat.id}`}
                  className="card p-5 text-center hover:border-primary-200 border border-transparent transition-all group"
                >
                  <div className="text-3xl mb-2">{icons[cat.id]}</div>
                  <div className="font-semibold text-gray-700 group-hover:text-primary-600 transition-colors">
                    {cat.label}
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        {/* Featured Products */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">منتجات مميزة</h2>
            <Link href="/products" className="text-primary-600 hover:text-primary-700 font-medium text-sm">
              عرض الكل ←
            </Link>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {featured.map(p => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>

        {/* Banner */}
        <section className="mt-12 bg-gradient-to-r from-amber-400 to-orange-500 rounded-3xl p-8 md:p-12 text-white">
          <div className="max-w-lg">
            <h3 className="text-2xl md:text-3xl font-bold mb-3">خصم 25% على أول طلب</h3>
            <p className="mb-6 text-amber-50">استخدم الكود <strong>FIRST25</strong> عند الدفع وتمتع بخصم رائع</p>
            <Link href="/products"
              className="inline-block bg-white text-orange-600 font-bold px-6 py-3 rounded-xl hover:bg-orange-50 transition-colors">
              تسوق الآن
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
