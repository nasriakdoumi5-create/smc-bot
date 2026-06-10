'use client';
import { useCart } from '../context/CartContext';
import Image from 'next/image';
import Link from 'next/link';

export default function CartDrawer() {
  const { items, total, count, dispatch, open, setOpen } = useCart();
  const shipping = total >= 500 ? 0 : 30;

  return (
    <>
      {open && <div className="fixed inset-0 bg-black/40 z-40" onClick={() => setOpen(false)} />}

      <div className={`fixed top-0 left-0 h-full w-full max-w-sm bg-white z-50 shadow-2xl transition-transform duration-300 flex flex-col ${open ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-bold text-gray-800">سلة التسوق {count > 0 && <span className="badge bg-primary-100 text-primary-700 mr-1">{count}</span>}</h2>
          <button onClick={() => setOpen(false)} className="p-2 hover:bg-gray-100 rounded-xl transition-colors text-gray-500 hover:text-gray-700">✕</button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {items.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <div className="text-5xl mb-3">🛒</div>
              <p className="font-medium">السلة فارغة</p>
              <button onClick={() => setOpen(false)} className="mt-4 btn-primary text-sm">تصفح المنتجات</button>
            </div>
          ) : items.map(item => (
            <div key={item.id} className="flex gap-3 items-center bg-gray-50 rounded-xl p-3">
              <div className="relative w-16 h-16 rounded-xl overflow-hidden bg-white flex-shrink-0">
                <Image src={item.images?.[0] || `https://picsum.photos/seed/${item.id}/200/200`} alt={item.name} fill className="object-cover" sizes="64px" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-700 line-clamp-2 leading-snug">{item.name}</p>
                <p className="text-primary-600 font-bold text-sm mt-1">{item.price} ر.س</p>
                <div className="flex items-center gap-2 mt-2">
                  <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-white">
                    <button onClick={() => dispatch({type:'UPDATE', id:item.id, qty:item.qty-1})} className="px-2.5 py-1 text-gray-500 hover:bg-gray-100 font-bold text-sm">−</button>
                    <span className="px-2.5 py-1 text-sm font-semibold">{item.qty}</span>
                    <button onClick={() => dispatch({type:'UPDATE', id:item.id, qty:item.qty+1})} className="px-2.5 py-1 text-gray-500 hover:bg-gray-100 font-bold text-sm">+</button>
                  </div>
                  <button onClick={() => dispatch({type:'REMOVE', id:item.id})} className="text-red-400 hover:text-red-600 p-1 rounded-lg hover:bg-red-50 transition-colors text-xs">🗑</button>
                </div>
              </div>
              <div className="text-sm font-bold text-gray-700 self-start pt-1">{(item.price * item.qty).toFixed(0)} ر.س</div>
            </div>
          ))}
        </div>

        {items.length > 0 && (
          <div className="p-4 border-t bg-white">
            <div className="flex justify-between text-sm text-gray-500 mb-1">
              <span>المجموع</span><span>{total} ر.س</span>
            </div>
            <div className="flex justify-between text-sm text-gray-500 mb-3">
              <span>الشحن</span>
              <span className={shipping===0?'text-green-600 font-semibold':''}>{shipping===0?'مجاني 🎉':`${shipping} ر.س`}</span>
            </div>
            <div className="flex justify-between font-bold text-base border-t pt-3 mb-4">
              <span>الإجمالي</span>
              <span className="text-primary-600 text-xl">{total + shipping} ر.س</span>
            </div>
            <Link href="/checkout" onClick={() => setOpen(false)} className="btn-primary w-full block text-center py-3.5 text-base">إتمام الشراء ←</Link>
            <button onClick={() => setOpen(false)} className="w-full text-center text-sm text-gray-400 hover:text-primary-600 mt-2 transition-colors">← مواصلة التسوق</button>
          </div>
        )}
      </div>
    </>
  );
}
