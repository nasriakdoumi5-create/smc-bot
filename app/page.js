import Link from 'next/link';
import Image from 'next/image';
import { db } from '../lib/db';
import ProductCard from '../components/ProductCard';

const CATEGORIES = [
  {slug:'electronics',name:'إلكترونيات',icon:'💻',color:'bg-blue-50 text-blue-600'},
  {slug:'clothing',name:'ملابس',icon:'👕',color:'bg-pink-50 text-pink-600'},
  {slug:'home',name:'المنزل',icon:'🏠',color:'bg-amber-50 text-amber-600'},
  {slug:'sports',name:'رياضة',icon:'⚽',color:'bg-green-50 text-green-600'},
  {slug:'books',name:'كتب',icon:'📚',color:'bg-purple-50 text-purple-600'},
];

export default async function HomePage() {
  const featuredProducts = await db.product.findMany({
    where: { featured: true },
    include: {
      category: true,
      reviews: { select: { rating: true } },
      _count: { select: { reviews: true } },
    },
    take: 8,
  });

  const products = featuredProducts.map(p => ({
    ...p,
    images: JSON.parse(p.images),
    avgRating: p.reviews.length ? (p.reviews.reduce((s, r) => s + r.rating, 0) / p.reviews.length).toFixed(1) : 0,
    reviewCount: p._count.reviews,
  }));

  return (
    <div>
      {/* Hero Banner */}
      <section className="bg-gradient-to-l from-slate-800 to-slate-900 text-white py-16 px-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center gap-8">
          <div className="flex-1 text-center md:text-right">
            <span className="badge bg-primary-600 text-white mb-4 text-sm px-3 py-1">🎉 عروض حصرية</span>
            <h1 className="text-4xl md:text-5xl font-extrabold mb-4 leading-tight">
              تسوق بذكاء<br />
              <span className="text-primary-400">وفّر أكثر</span>
            </h1>
            <p className="text-gray-300 text-lg mb-8">آلاف المنتجات بأفضل الأسعار مع توصيل سريع لباب منزلك</p>
            <div className="flex gap-3 justify-center md:justify-start flex-wrap">
              <Link href="/products" className="btn-primary text-base px-8 py-3">تسوق الآن</Link>
              <Link href="/products?featured=true" className="btn-outline border-white text-white hover:bg-white/10 text-base px-8 py-3">العروض المميزة</Link>
            </div>
          </div>
          <div className="flex-1 flex justify-center">
            <div className="relative w-72 h-72 md:w-96 md:h-96">
              <div className="absolute inset-0 bg-primary-600/20 rounded-full blur-3xl" />
              <div className="relative grid grid-cols-2 gap-4 p-4">
                {products.slice(0,4).map((p, i) => (
                  <div key={p.id} className={`relative rounded-2xl overflow-hidden bg-white/10 backdrop-blur aspect-square ${i === 0 ? 'col-span-2 row-span-1' : ''}`}>
                    <Image src={p.images[0]} alt={p.name} fill className="object-cover opacity-80" sizes="200px" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="bg-primary-600 text-white py-4">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          {[
            {icon:'🚚', text:'شحن مجاني فوق 500 ر.س'},
            {icon:'🔒', text:'دفع آمن 100%'},
            {icon:'↩️', text:'إرجاع خلال 14 يوم'},
            {icon:'🎧', text:'دعم 24/7'},
          ].map(s => (
            <div key={s.text} className="flex items-center justify-center gap-2 text-sm font-medium">
              <span className="text-xl">{s.icon}</span>{s.text}
            </div>
          ))}
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 py-10">
        {/* Categories */}
        <div className="mb-10">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">تسوق حسب الفئة</h2>
          <div className="grid grid-cols-3 md:grid-cols-5 gap-3">
            {CATEGORIES.map(c => (
              <Link key={c.slug} href={`/products?category=${c.slug}`}
                className={`${c.color} rounded-2xl p-4 text-center hover:shadow-md transition-all duration-200 hover:-translate-y-0.5 group`}>
                <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">{c.icon}</div>
                <p className="font-semibold text-sm">{c.name}</p>
              </Link>
            ))}
          </div>
        </div>

        {/* Featured Products */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">منتجات مميزة ⭐</h2>
            <Link href="/products" className="text-primary-600 font-semibold hover:text-primary-700 text-sm">عرض الكل ←</Link>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {products.map(p => <ProductCard key={p.id} product={p} />)}
          </div>
        </div>

        {/* Promo Banners */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-10">
          <Link href="/products?category=electronics" className="bg-gradient-to-l from-blue-600 to-blue-800 rounded-2xl p-8 text-white hover:shadow-xl transition-shadow block">
            <p className="text-sm font-medium opacity-80 mb-1">تخفيضات الموسم</p>
            <h3 className="text-2xl font-bold mb-2">إلكترونيات بأسعار لا تُصدق 💻</h3>
            <p className="text-sm opacity-80">خصم حتى 30% على المنتجات المختارة</p>
            <div className="mt-4 inline-block bg-white text-blue-700 font-bold text-sm px-4 py-2 rounded-xl">تسوق الآن</div>
          </Link>
          <Link href="/products?category=clothing" className="bg-gradient-to-l from-pink-500 to-rose-600 rounded-2xl p-8 text-white hover:shadow-xl transition-shadow block">
            <p className="text-sm font-medium opacity-80 mb-1">كولكشن جديد</p>
            <h3 className="text-2xl font-bold mb-2">أحدث صيحات الموضة 👗</h3>
            <p className="text-sm opacity-80">أناقة لكل المناسبات بأسعار رائعة</p>
            <div className="mt-4 inline-block bg-white text-pink-600 font-bold text-sm px-4 py-2 rounded-xl">اكتشف الآن</div>
          </Link>
        </div>
      </div>
    </div>
  );
}
