'use client';

import { PRODUCTS } from '../../../data/products';
import { useCart } from '../../../context/CartContext';
import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function ProductPage() {
  const { id } = useParams();
  const product = PRODUCTS.find(p => p.id === Number(id));
  const { dispatch } = useCart();
  const [qty, setQty]       = useState(1);
  const [added, setAdded]   = useState(false);
  const [tab, setTab]       = useState('desc');

  if (!product) {
    return (
      <div className="text-center py-20">
        <div className="text-5xl mb-4">😕</div>
        <p className="text-xl font-semibold text-gray-600">المنتج غير موجود</p>
        <Link href="/products" className="btn-primary mt-6 inline-block">العودة للمنتجات</Link>
      </div>
    );
  }

  const discount = Math.round(((product.originalPrice - product.price) / product.originalPrice) * 100);
  const related  = PRODUCTS.filter(p => p.category === product.category && p.id !== product.id).slice(0, 4);

  function handleAdd() {
    for (let i = 0; i < qty; i++) {
      dispatch({ type: 'ADD', product });
    }
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="text-sm text-gray-400 mb-6 flex items-center gap-2">
        <Link href="/" className="hover:text-primary-600">الرئيسية</Link>
        <span>/</span>
        <Link href="/products" className="hover:text-primary-600">المنتجات</Link>
        <span>/</span>
        <span className="text-gray-600">{product.name}</span>
      </nav>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* Image */}
        <div className="relative aspect-square rounded-2xl overflow-hidden bg-gray-100">
          <Image
            src={product.image}
            alt={product.name}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 50vw"
          />
          {discount > 0 && (
            <span className="absolute top-4 right-4 bg-red-500 text-white text-sm font-bold px-3 py-1 rounded-xl">
              خصم {discount}%
            </span>
          )}
        </div>

        {/* Details */}
        <div>
          {/* Tags */}
          <div className="flex gap-2 mb-3 flex-wrap">
            {product.tags.map(tag => (
              <span key={tag} className="badge bg-primary-100 text-primary-700">{tag}</span>
            ))}
          </div>

          <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mb-3">{product.name}</h1>

          {/* Rating */}
          <div className="flex items-center gap-2 mb-4">
            <div className="flex">
              {[1, 2, 3, 4, 5].map(s => (
                <span key={s} className={s <= Math.round(product.rating) ? 'text-yellow-400' : 'text-gray-200'}>★</span>
              ))}
            </div>
            <span className="font-semibold">{product.rating}</span>
            <span className="text-gray-400 text-sm">({product.reviews} تقييم)</span>
          </div>

          {/* Price */}
          <div className="flex items-baseline gap-3 mb-6">
            <span className="text-3xl font-bold text-primary-600">{product.price} ر.س</span>
            {product.originalPrice > product.price && (
              <span className="text-lg text-gray-400 line-through">{product.originalPrice} ر.س</span>
            )}
            {discount > 0 && (
              <span className="text-sm font-semibold text-red-500">وفّر {product.originalPrice - product.price} ر.س</span>
            )}
          </div>

          {/* Stock */}
          <div className="mb-6">
            {product.stock > 5
              ? <span className="badge bg-green-100 text-green-700">✓ متوفر في المخزن</span>
              : product.stock > 0
              ? <span className="badge bg-orange-100 text-orange-700">⚠ آخر {product.stock} قطع فقط</span>
              : <span className="badge bg-red-100 text-red-700">✗ غير متوفر</span>
            }
          </div>

          {/* Qty + Add to cart */}
          <div className="flex items-center gap-3 mb-4">
            <div className="flex items-center border border-gray-200 rounded-xl overflow-hidden">
              <button onClick={() => setQty(q => Math.max(1, q - 1))}
                className="px-4 py-3 text-lg hover:bg-gray-50 transition-colors font-bold text-gray-600">−</button>
              <span className="px-5 py-3 font-semibold text-gray-800 min-w-[3rem] text-center">{qty}</span>
              <button onClick={() => setQty(q => Math.min(product.stock, q + 1))}
                className="px-4 py-3 text-lg hover:bg-gray-50 transition-colors font-bold text-gray-600">+</button>
            </div>
            <button
              onClick={handleAdd}
              disabled={product.stock === 0}
              className={`flex-1 py-3 rounded-xl font-bold transition-all duration-200 active:scale-95 ${
                added
                  ? 'bg-green-100 text-green-700'
                  : product.stock === 0
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'btn-primary'
              }`}
            >
              {added ? '✓ تمت الإضافة للسلة' : '🛒 أضف للسلة'}
            </button>
          </div>

          <Link href="/checkout"
            className="block text-center btn-outline w-full mb-6">
            شراء الآن
          </Link>

          {/* Features */}
          <div className="grid grid-cols-3 gap-3 text-center text-xs text-gray-500 py-4 border-t border-gray-100">
            <div><div className="text-xl mb-1">🚚</div>توصيل مجاني</div>
            <div><div className="text-xl mb-1">🔄</div>إرجاع 14 يوم</div>
            <div><div className="text-xl mb-1">🔒</div>دفع آمن</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mt-12 bg-white rounded-2xl shadow-sm overflow-hidden">
        <div className="flex border-b border-gray-100">
          {[
            { id: 'desc', label: 'الوصف' },
            { id: 'specs', label: 'المواصفات' },
            { id: 'reviews', label: 'التقييمات' },
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-6 py-4 font-medium transition-colors ${
                tab === t.id
                  ? 'text-primary-600 border-b-2 border-primary-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className="p-6">
          {tab === 'desc' && (
            <p className="text-gray-600 leading-relaxed">{product.description}</p>
          )}
          {tab === 'specs' && (
            <table className="w-full text-sm">
              <tbody className="divide-y divide-gray-100">
                {[
                  ['الفئة', product.category === 'electronics' ? 'إلكترونيات' : product.category],
                  ['التقييم', `${product.rating}/5 (${product.reviews} تقييم)`],
                  ['المخزون', `${product.stock} قطعة`],
                  ['الضمان', '12 شهراً'],
                  ['رمز المنتج', `PRD-${product.id.toString().padStart(4, '0')}`],
                ].map(([k, v]) => (
                  <tr key={k}>
                    <td className="py-3 font-medium text-gray-600 w-1/3">{k}</td>
                    <td className="py-3 text-gray-800">{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {tab === 'reviews' && (
            <div className="space-y-4">
              {[
                { name: 'أحمد محمد', rating: 5, text: 'منتج رائع، جودة ممتازة وسعر مناسب. سأشتري مرة أخرى بالتأكيد.', date: 'منذ أسبوع' },
                { name: 'سارة أحمد', rating: 4, text: 'جيد جداً، التوصيل كان سريعاً والمنتج مطابق للوصف.', date: 'منذ أسبوعين' },
                { name: 'محمد علي', rating: 5, text: 'أنصح به بشدة! خدمة عملاء ممتازة وجودة عالية.', date: 'منذ شهر' },
              ].map((r, i) => (
                <div key={i} className="border border-gray-100 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center font-bold text-primary-700 text-sm">
                        {r.name[0]}
                      </div>
                      <span className="font-semibold text-gray-700">{r.name}</span>
                    </div>
                    <span className="text-xs text-gray-400">{r.date}</span>
                  </div>
                  <div className="text-yellow-400 text-sm mb-1">{'★'.repeat(r.rating)}{'☆'.repeat(5 - r.rating)}</div>
                  <p className="text-gray-600 text-sm">{r.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Related */}
      {related.length > 0 && (
        <section className="mt-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">منتجات مشابهة</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {related.map(p => {
              const disc = Math.round(((p.originalPrice - p.price) / p.originalPrice) * 100);
              return (
                <Link key={p.id} href={`/product/${p.id}`} className="card overflow-hidden group block">
                  <div className="relative aspect-square bg-gray-100">
                    <Image src={p.image} alt={p.name} fill className="object-cover group-hover:scale-105 transition-transform" sizes="25vw" />
                    {disc > 0 && <span className="absolute top-2 right-2 bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-lg font-bold">-{disc}%</span>}
                  </div>
                  <div className="p-3">
                    <p className="text-sm font-medium text-gray-700 line-clamp-1">{p.name}</p>
                    <p className="text-primary-600 font-bold mt-1">{p.price} ر.س</p>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}
