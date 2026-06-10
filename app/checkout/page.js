'use client';
import { useState } from 'react';
import { useCart } from '../../context/CartContext';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import Image from 'next/image';
import Link from 'next/link';

export default function CheckoutPage() {
  const { items, total, dispatch } = useCart();
  const { data: session } = useSession();
  const router = useRouter();
  const shipping = total >= 500 ? 0 : 30;
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    name: session?.user?.name || '',
    phone: '',
    city: '',
    address: '',
    payMethod: 'cod',
    notes: '',
  });

  function handleChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (items.length === 0) { toast.error('السلة فارغة'); return; }
    setSubmitting(true);
    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, items, total: total + shipping }),
      });
      const order = await res.json();
      if (!res.ok) throw new Error(order.error || 'حدث خطأ');
      dispatch({ type: 'CLEAR' });
      toast.success('تم تأكيد طلبك بنجاح! 🎉');
      router.push(`/order-success?id=${order.id}`);
    } catch (e) {
      toast.error(e.message);
    }
    setSubmitting(false);
  }

  if (items.length === 0) return (
    <div className="max-w-lg mx-auto px-4 py-20 text-center">
      <div className="text-6xl mb-4">🛒</div>
      <h2 className="text-xl font-bold text-gray-700 mb-2">السلة فارغة</h2>
      <p className="text-gray-500 mb-6">أضف منتجات للسلة أولاً</p>
      <Link href="/products" className="btn-primary">تسوق الآن</Link>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-8">إتمام الشراء</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form */}
        <form onSubmit={handleSubmit} className="lg:col-span-2 space-y-6">
          <div className="card p-6">
            <h2 className="font-bold text-gray-700 mb-4 text-lg">بيانات التوصيل</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">الاسم الكامل *</label>
                <input name="name" value={form.name} onChange={handleChange} required className="input-field" placeholder="أحمد محمد" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">رقم الجوال *</label>
                <input name="phone" value={form.phone} onChange={handleChange} required className="input-field" placeholder="05xxxxxxxx" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">المدينة *</label>
                <select name="city" value={form.city} onChange={handleChange} required className="input-field">
                  <option value="">اختر المدينة</option>
                  {['الرياض','جدة','مكة المكرمة','المدينة المنورة','الدمام','الخبر','الطائف','تبوك','أبها','نجران'].map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1.5">العنوان التفصيلي *</label>
                <textarea name="address" value={form.address} onChange={handleChange} required className="input-field h-20 resize-none" placeholder="الحي، الشارع، رقم المبنى..." />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1.5">ملاحظات (اختياري)</label>
                <textarea name="notes" value={form.notes} onChange={handleChange} className="input-field h-16 resize-none" placeholder="أي تعليمات خاصة للتوصيل..." />
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h2 className="font-bold text-gray-700 mb-4 text-lg">طريقة الدفع</h2>
            <div className="space-y-3">
              {[
                {value:'cod', label:'الدفع عند الاستلام', icon:'💵', desc:'ادفع نقداً عند وصول الطلب'},
                {value:'card', label:'بطاقة ائتمانية', icon:'💳', desc:'Visa / Mastercard / مدى'},
                {value:'stcpay', label:'STC Pay', icon:'📱', desc:'الدفع عبر STC Pay'},
              ].map(m => (
                <label key={m.value} className={`flex items-center gap-4 p-4 border-2 rounded-xl cursor-pointer transition-colors ${form.payMethod === m.value ? 'border-primary-500 bg-primary-50' : 'border-gray-200 hover:border-gray-300'}`}>
                  <input type="radio" name="payMethod" value={m.value} checked={form.payMethod === m.value} onChange={handleChange} className="hidden" />
                  <span className="text-2xl">{m.icon}</span>
                  <div>
                    <p className="font-semibold text-gray-700">{m.label}</p>
                    <p className="text-xs text-gray-500">{m.desc}</p>
                  </div>
                  {form.payMethod === m.value && <span className="mr-auto text-primary-600">✓</span>}
                </label>
              ))}
            </div>
          </div>

          <button type="submit" disabled={submitting} className="w-full btn-primary py-4 text-lg">
            {submitting ? '⏳ جاري معالجة الطلب...' : `✓ تأكيد الطلب — ${total + shipping} ر.س`}
          </button>
        </form>

        {/* Order summary */}
        <div className="card p-5 h-fit sticky top-24">
          <h2 className="font-bold text-gray-700 mb-4">ملخص الطلب</h2>
          <div className="space-y-3 mb-4 max-h-72 overflow-y-auto">
            {items.map(item => (
              <div key={item.id} className="flex gap-3 items-center">
                <div className="relative w-12 h-12 rounded-xl overflow-hidden bg-gray-100 flex-shrink-0">
                  <Image src={item.images?.[0] || `https://picsum.photos/seed/${item.id}/100/100`} alt={item.name} fill className="object-cover" sizes="48px" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-gray-700 line-clamp-1">{item.name}</p>
                  <p className="text-xs text-gray-500">× {item.qty}</p>
                </div>
                <span className="text-sm font-bold text-gray-700">{(item.price * item.qty).toFixed(0)} ر.س</span>
              </div>
            ))}
          </div>
          <div className="border-t pt-3 space-y-2 text-sm">
            <div className="flex justify-between text-gray-500"><span>المجموع</span><span>{total} ر.س</span></div>
            <div className="flex justify-between text-gray-500">
              <span>الشحن</span>
              <span className={shipping === 0 ? 'text-green-600 font-semibold' : ''}>{shipping === 0 ? 'مجاني' : `${shipping} ر.س`}</span>
            </div>
            {shipping > 0 && <p className="text-xs text-primary-600">أضف {500 - total} ر.س للشحن المجاني</p>}
            <div className="flex justify-between font-bold text-base border-t pt-2">
              <span>الإجمالي</span>
              <span className="text-primary-600 text-xl">{total + shipping} ر.س</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
