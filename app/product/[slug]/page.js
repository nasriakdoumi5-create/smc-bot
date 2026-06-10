'use client';
import { useState, useEffect } from 'react';
import Image from 'next/image';
import { useCart } from '../../../context/CartContext';
import { useSession } from 'next-auth/react';
import { toast } from 'sonner';
import Link from 'next/link';

export default function ProductPage({ params }) {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selImg, setSelImg]   = useState(0);
  const [qty, setQty]         = useState(1);
  const [rating, setRating]   = useState(5);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { addToCart } = useCart();
  const { data: session } = useSession();

  useEffect(() => {
    fetch(`/api/products/${params.slug}`)
      .then(r => r.json())
      .then(d => { setProduct(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [params.slug]);

  function handleAdd() {
    if (!product) return;
    for (let i = 0; i < qty; i++) addToCart(product);
    toast.success(`تمت إضافة ${qty} قطعة للسلة 🛒`);
  }

  async function submitReview(e) {
    e.preventDefault();
    if (!session) { toast.error('يجب تسجيل الدخول أولاً'); return; }
    setSubmitting(true);
    const res = await fetch('/api/reviews', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productId: product.id, rating, comment }),
    });
    if (res.ok) {
      toast.success('تم إضافة تقييمك ✓');
      setComment('');
      const updated = await fetch(`/api/products/${params.slug}`).then(r => r.json());
      setProduct(updated);
    } else {
      toast.error('حدث خطأ، حاول مرة أخرى');
    }
    setSubmitting(false);
  }

  if (loading) return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="animate-pulse grid grid-cols-1 md:grid-cols-2 gap-10">
        <div className="aspect-square bg-gray-200 rounded-2xl" />
        <div className="space-y-4">
          <div className="h-6 bg-gray-200 rounded w-3/4" />
          <div className="h-10 bg-gray-200 rounded w-1/2" />
          <div className="h-4 bg-gray-200 rounded" />
          <div className="h-4 bg-gray-200 rounded w-4/5" />
          <div className="h-12 bg-gray-200 rounded-xl" />
        </div>
      </div>
    </div>
  );

  if (!product || product.error) return (
    <div className="text-center py-20">
      <p className="text-gray-500 text-lg">المنتج غير موجود</p>
      <Link href="/products" className="btn-primary mt-4 inline-block">العودة للمنتجات</Link>
    </div>
  );

  const discount = product.originalPrice ? Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100) : 0;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="flex gap-2 text-sm text-gray-400 mb-6">
        <Link href="/" className="hover:text-primary-600">الرئيسية</Link>
        <span>/</span>
        <Link href="/products" className="hover:text-primary-600">المنتجات</Link>
        <span>/</span>
        <Link href={`/products?category=${product.category?.slug}`} className="hover:text-primary-600">{product.category?.name}</Link>
        <span>/</span>
        <span className="text-gray-600">{product.name}</span>
      </nav>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10 mb-12">
        {/* Images */}
        <div>
          <div className="relative aspect-square rounded-2xl overflow-hidden bg-gray-100 mb-3">
            <Image src={product.images[selImg] || `https://picsum.photos/seed/${product.id}/600/600`} alt={product.name} fill className="object-cover" sizes="(max-width:768px) 100vw, 50vw" priority />
            {discount > 0 && <span className="absolute top-3 right-3 badge bg-red-500 text-white text-sm">-{discount}%</span>}
          </div>
          {product.images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto">
              {product.images.map((img, i) => (
                <button key={i} onClick={() => setSelImg(i)}
                  className={`relative w-16 h-16 rounded-xl overflow-hidden flex-shrink-0 border-2 transition-colors ${selImg === i ? 'border-primary-500' : 'border-transparent'}`}>
                  <Image src={img} alt="" fill className="object-cover" sizes="64px" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Details */}
        <div>
          <p className="text-sm text-primary-600 font-medium mb-1">{product.category?.name}</p>
          <h1 className="text-2xl font-bold text-gray-800 mb-3">{product.name}</h1>

          {Number(product.avgRating) > 0 && (
            <div className="flex items-center gap-2 mb-3">
              <span className="text-yellow-400">{'★'.repeat(Math.round(product.avgRating))}{'☆'.repeat(5 - Math.round(product.avgRating))}</span>
              <span className="text-sm text-gray-500">{product.avgRating} ({product.reviews?.length} تقييم)</span>
            </div>
          )}

          <div className="flex items-baseline gap-3 mb-4">
            <span className="text-3xl font-extrabold text-primary-600">{product.price} ر.س</span>
            {product.originalPrice > product.price && (
              <>
                <span className="text-gray-400 line-through text-lg">{product.originalPrice} ر.س</span>
                <span className="badge bg-red-100 text-red-600">وفّر {product.originalPrice - product.price} ر.س</span>
              </>
            )}
          </div>

          <p className="text-gray-600 leading-relaxed mb-6">{product.description}</p>

          <div className="flex items-center gap-3 mb-4">
            <span className={`badge ${product.stock > 5 ? 'bg-green-100 text-green-700' : product.stock > 0 ? 'bg-orange-100 text-orange-700' : 'bg-red-100 text-red-700'}`}>
              {product.stock > 5 ? '✓ متوفر' : product.stock > 0 ? `آخر ${product.stock} قطع!` : 'نفذ المخزون'}
            </span>
          </div>

          {product.stock > 0 && (
            <div className="flex items-center gap-3 mb-6">
              <span className="text-sm font-medium text-gray-700">الكمية:</span>
              <div className="flex items-center border border-gray-200 rounded-xl overflow-hidden">
                <button onClick={() => setQty(Math.max(1, qty-1))} className="px-4 py-2 hover:bg-gray-100 font-bold text-gray-600">−</button>
                <span className="px-4 py-2 font-semibold w-12 text-center">{qty}</span>
                <button onClick={() => setQty(Math.min(product.stock, qty+1))} className="px-4 py-2 hover:bg-gray-100 font-bold text-gray-600">+</button>
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={handleAdd} disabled={product.stock === 0}
              className="flex-1 btn-primary py-4 text-base disabled:opacity-50 disabled:cursor-not-allowed">
              {product.stock === 0 ? 'نفذ المخزون' : '🛒 أضف للسلة'}
            </button>
            <button onClick={async () => { handleAdd(); window.location.href='/checkout'; }}
              disabled={product.stock === 0}
              className="flex-1 btn-dark py-4 text-base disabled:opacity-50 disabled:cursor-not-allowed">
              اشتر الآن ←
            </button>
          </div>

          <div className="mt-6 grid grid-cols-3 gap-3 text-center text-xs text-gray-500">
            <div className="bg-gray-50 rounded-xl p-3"><div className="text-lg mb-1">🚚</div>توصيل سريع</div>
            <div className="bg-gray-50 rounded-xl p-3"><div className="text-lg mb-1">🔒</div>دفع آمن</div>
            <div className="bg-gray-50 rounded-xl p-3"><div className="text-lg mb-1">↩️</div>إرجاع 14 يوم</div>
          </div>
        </div>
      </div>

      {/* Reviews */}
      <div className="card p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-6">التقييمات والمراجعات</h2>

        {/* Add review form */}
        {session ? (
          <form onSubmit={submitReview} className="bg-gray-50 rounded-2xl p-5 mb-6">
            <h3 className="font-semibold text-gray-700 mb-4">أضف تقييمك</h3>
            <div className="flex gap-2 mb-3">
              {[1,2,3,4,5].map(s => (
                <button type="button" key={s} onClick={() => setRating(s)}
                  className={`text-2xl transition-transform hover:scale-110 ${s <= rating ? 'text-yellow-400' : 'text-gray-300'}`}>★</button>
              ))}
            </div>
            <textarea value={comment} onChange={e => setComment(e.target.value)} required
              placeholder="شاركنا تجربتك مع هذا المنتج..."
              className="input-field h-24 resize-none mb-3" />
            <button type="submit" disabled={submitting} className="btn-primary">{submitting ? 'جاري الإرسال...' : 'نشر التقييم'}</button>
          </form>
        ) : (
          <div className="bg-primary-50 rounded-2xl p-4 mb-6 text-center">
            <p className="text-gray-600 mb-2">سجّل دخولك لإضافة تقييم</p>
            <Link href="/login" className="btn-primary text-sm">تسجيل الدخول</Link>
          </div>
        )}

        {/* Reviews list */}
        {product.reviews?.length === 0 ? (
          <p className="text-gray-400 text-center py-8">لا توجد تقييمات بعد. كن أول من يقيّم!</p>
        ) : (
          <div className="space-y-4">
            {product.reviews?.map(r => (
              <div key={r.id} className="border-b border-gray-100 pb-4 last:border-0">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold text-gray-700 text-sm">{r.user.name}</p>
                    <span className="text-yellow-400 text-sm">{'★'.repeat(r.rating)}{'☆'.repeat(5-r.rating)}</span>
                  </div>
                  <span className="text-xs text-gray-400">{new Date(r.createdAt).toLocaleDateString('ar-SA')}</span>
                </div>
                <p className="text-gray-600 text-sm leading-relaxed">{r.comment}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
