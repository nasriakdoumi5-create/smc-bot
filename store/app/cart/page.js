'use client';

import { useCart } from '../../context/CartContext';
import Image from 'next/image';
import Link from 'next/link';

export default function CartPage() {
  const { items, total, dispatch } = useCart();

  if (items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <div className="text-7xl mb-6">🛒</div>
        <h2 className="text-2xl font-bold text-gray-700 mb-3">السلة فارغة</h2>
        <p className="text-gray-400 mb-8">لم تضف أي منتجات بعد. تصفح منتجاتنا وابدأ التسوق!</p>
        <Link href="/products" className="btn-primary inline-block text-lg px-8 py-3">
          تصفح المنتجات
        </Link>
      </div>
    );
  }

  const shipping = total >= 500 ? 0 : 30;
  const grandTotal = total + shipping;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">
        🛒 سلة التسوق <span className="text-lg text-gray-400 font-normal">({items.length} منتج)</span>
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Items */}
        <div className="lg:col-span-2 space-y-4">
          {items.map(item => {
            const subtotal = item.price * item.qty;
            return (
              <div key={item.id} className="card p-4 flex gap-4">
                <Link href={`/product/${item.id}`} className="relative w-24 h-24 rounded-xl overflow-hidden bg-gray-100 flex-shrink-0">
                  <Image src={item.image} alt={item.name} fill className="object-cover" sizes="96px" />
                </Link>

                <div className="flex-1 min-w-0">
                  <Link href={`/product/${item.id}`}>
                    <h3 className="font-semibold text-gray-800 hover:text-primary-600 transition-colors line-clamp-2 text-sm md:text-base">
                      {item.name}
                    </h3>
                  </Link>
                  <p className="text-primary-600 font-bold mt-1">{item.price} ر.س</p>

                  <div className="flex items-center justify-between mt-3">
                    {/* Qty */}
                    <div className="flex items-center border border-gray-200 rounded-xl overflow-hidden">
                      <button
                        onClick={() => dispatch({ type: 'UPDATE_QTY', id: item.id, qty: item.qty - 1 })}
                        className="px-3 py-1.5 hover:bg-gray-50 font-bold text-gray-600">−</button>
                      <span className="px-3 py-1.5 font-semibold text-sm min-w-[2rem] text-center">{item.qty}</span>
                      <button
                        onClick={() => dispatch({ type: 'UPDATE_QTY', id: item.id, qty: item.qty + 1 })}
                        className="px-3 py-1.5 hover:bg-gray-50 font-bold text-gray-600">+</button>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="font-bold text-gray-700">{subtotal} ر.س</span>
                      <button
                        onClick={() => dispatch({ type: 'REMOVE', id: item.id })}
                        className="text-red-400 hover:text-red-600 p-1 rounded-lg hover:bg-red-50 transition-colors"
                        title="حذف"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}

          <button
            onClick={() => dispatch({ type: 'CLEAR' })}
            className="text-red-500 hover:text-red-600 text-sm font-medium flex items-center gap-1 mt-2"
          >
            🗑 إفراغ السلة
          </button>
        </div>

        {/* Summary */}
        <div className="lg:col-span-1">
          <div className="card p-6 sticky top-20">
            <h2 className="text-xl font-bold text-gray-800 mb-5">ملخص الطلب</h2>

            <div className="space-y-3 text-sm mb-5">
              <div className="flex justify-between text-gray-600">
                <span>المجموع الفرعي</span>
                <span className="font-medium">{total} ر.س</span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>الشحن</span>
                <span className={shipping === 0 ? 'text-green-600 font-semibold' : 'font-medium'}>
                  {shipping === 0 ? 'مجاني 🎉' : `${shipping} ر.س`}
                </span>
              </div>
              {shipping > 0 && (
                <p className="text-xs text-gray-400">الشحن مجاني للطلبات فوق 500 ر.س</p>
              )}
              <div className="border-t border-gray-100 pt-3 flex justify-between">
                <span className="font-bold text-gray-800 text-base">الإجمالي</span>
                <span className="font-bold text-primary-600 text-xl">{grandTotal} ر.س</span>
              </div>
            </div>

            {/* Coupon */}
            <div className="flex gap-2 mb-5">
              <input
                type="text"
                placeholder="كوبون الخصم"
                className="input-field text-sm py-2"
              />
              <button className="btn-outline text-sm py-2 px-4 whitespace-nowrap">تطبيق</button>
            </div>

            <Link href="/checkout" className="btn-primary w-full text-center block text-lg py-3.5">
              إتمام الشراء →
            </Link>

            <Link href="/products" className="block text-center text-sm text-gray-400 hover:text-primary-600 mt-3 transition-colors">
              ← متابعة التسوق
            </Link>

            {/* Trust badges */}
            <div className="flex justify-around mt-5 pt-4 border-t border-gray-100 text-xs text-gray-400">
              <span>🔒 دفع آمن</span>
              <span>🚚 توصيل سريع</span>
              <span>🔄 إرجاع مجاني</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
