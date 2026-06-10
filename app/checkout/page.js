'use client';

import { useCart } from '../../context/CartContext';
import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';

const STEPS = ['بيانات الشحن', 'طريقة الدفع', 'تأكيد الطلب'];

export default function CheckoutPage() {
  const { items, total, dispatch } = useCart();
  const [step, setStep] = useState(0);
  const [done, setDone] = useState(false);
  const [form, setForm] = useState({
    name: '', email: '', phone: '', city: '', address: '', notes: '',
    payMethod: 'card',
    cardNumber: '', cardExp: '', cardCvv: '',
  });

  const shipping = total >= 500 ? 0 : 30;
  const grandTotal = total + shipping;

  function update(field, val) {
    setForm(f => ({ ...f, [field]: val }));
  }

  function handleNext() {
    if (step < STEPS.length - 1) setStep(s => s + 1);
  }

  function handleBack() {
    if (step > 0) setStep(s => s - 1);
  }

  function handleSubmit() {
    setDone(true);
    dispatch({ type: 'CLEAR' });
  }

  if (items.length === 0 && !done) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <div className="text-6xl mb-4">🛒</div>
        <h2 className="text-2xl font-bold text-gray-700 mb-4">السلة فارغة</h2>
        <Link href="/products" className="btn-primary inline-block">تصفح المنتجات</Link>
      </div>
    );
  }

  if (done) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center">
        <div className="text-7xl mb-6 animate-bounce">🎉</div>
        <h2 className="text-3xl font-bold text-gray-800 mb-3">تم تأكيد طلبك!</h2>
        <p className="text-gray-500 mb-2">رقم الطلب: <strong className="text-primary-600">#ORD-{Date.now().toString().slice(-6)}</strong></p>
        <p className="text-gray-500 mb-8">
          سيتم التواصل معك على <strong>{form.phone || 'رقمك'}</strong> لتأكيد التفاصيل
        </p>
        <div className="bg-primary-50 rounded-2xl p-6 mb-8 text-right">
          <h3 className="font-bold text-gray-700 mb-3">تفاصيل الطلب:</h3>
          <div className="text-sm text-gray-600 space-y-1">
            <p>المجموع: <strong>{grandTotal} ر.س</strong></p>
            <p>الشحن: <strong>{shipping === 0 ? 'مجاني' : `${shipping} ر.س`}</strong></p>
            <p>التوصيل خلال: <strong>2-4 أيام عمل</strong></p>
          </div>
        </div>
        <div className="flex gap-3 justify-center">
          <Link href="/products" className="btn-primary px-8">مواصلة التسوق</Link>
          <Link href="/" className="btn-outline px-8">الرئيسية</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">إتمام الشراء</h1>

      {/* Step Indicator */}
      <div className="flex items-center justify-center mb-10 gap-0">
        {STEPS.map((s, i) => (
          <div key={i} className="flex items-center">
            <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ${
              i === step ? 'bg-primary-600 text-white shadow-md' :
              i < step  ? 'bg-primary-100 text-primary-700' :
                          'bg-gray-100 text-gray-400'
            }`}>
              <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                i < step ? 'bg-primary-600 text-white' : i === step ? 'bg-white text-primary-600' : 'bg-gray-300 text-gray-500'
              }`}>
                {i < step ? '✓' : i + 1}
              </span>
              {s}
            </div>
            {i < STEPS.length - 1 && (
              <div className={`h-0.5 w-8 ${i < step ? 'bg-primary-400' : 'bg-gray-200'}`} />
            )}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form */}
        <div className="lg:col-span-2 card p-6">
          {/* Step 0: Shipping */}
          {step === 0 && (
            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-5">بيانات الشحن</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الاسم الكامل *</label>
                  <input value={form.name} onChange={e => update('name', e.target.value)}
                    className="input-field" placeholder="أحمد محمد" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">رقم الجوال *</label>
                  <input value={form.phone} onChange={e => update('phone', e.target.value)}
                    className="input-field" placeholder="05xxxxxxxx" type="tel" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">البريد الإلكتروني</label>
                  <input value={form.email} onChange={e => update('email', e.target.value)}
                    className="input-field" placeholder="example@email.com" type="email" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">المدينة *</label>
                  <select value={form.city} onChange={e => update('city', e.target.value)} className="input-field">
                    <option value="">اختر المدينة</option>
                    {['الرياض', 'جدة', 'مكة', 'المدينة', 'الدمام', 'الخبر', 'القصيم', 'أبها'].map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">العنوان التفصيلي *</label>
                  <input value={form.address} onChange={e => update('address', e.target.value)}
                    className="input-field" placeholder="الحي، الشارع، رقم المنزل" />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات إضافية</label>
                  <textarea value={form.notes} onChange={e => update('notes', e.target.value)}
                    className="input-field resize-none" rows={3} placeholder="أي تعليمات خاصة للتوصيل..." />
                </div>
              </div>
            </div>
          )}

          {/* Step 1: Payment */}
          {step === 1 && (
            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-5">طريقة الدفع</h2>
              <div className="space-y-3 mb-6">
                {[
                  { id: 'card', label: 'بطاقة بنكية', icon: '💳', desc: 'Visa / Mastercard / Mada' },
                  { id: 'stc',  label: 'STC Pay',      icon: '📱', desc: 'ادفع عبر محفظة STC Pay' },
                  { id: 'cod',  label: 'الدفع عند الاستلام', icon: '💵', desc: 'ادفع نقداً عند التوصيل' },
                ].map(m => (
                  <label key={m.id}
                    className={`flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all ${
                      form.payMethod === m.id ? 'border-primary-400 bg-primary-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input type="radio" name="payMethod" value={m.id}
                      checked={form.payMethod === m.id}
                      onChange={e => update('payMethod', e.target.value)}
                      className="text-primary-600"
                    />
                    <span className="text-2xl">{m.icon}</span>
                    <div>
                      <div className="font-semibold text-gray-800">{m.label}</div>
                      <div className="text-sm text-gray-400">{m.desc}</div>
                    </div>
                  </label>
                ))}
              </div>

              {form.payMethod === 'card' && (
                <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">رقم البطاقة</label>
                    <input value={form.cardNumber} onChange={e => update('cardNumber', e.target.value)}
                      className="input-field" placeholder="1234 5678 9012 3456" maxLength={19} />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ الانتهاء</label>
                      <input value={form.cardExp} onChange={e => update('cardExp', e.target.value)}
                        className="input-field" placeholder="MM/YY" maxLength={5} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">CVV</label>
                      <input value={form.cardCvv} onChange={e => update('cardCvv', e.target.value)}
                        className="input-field" placeholder="123" maxLength={4} type="password" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 2: Confirm */}
          {step === 2 && (
            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-5">مراجعة الطلب</h2>
              <div className="space-y-3 mb-6">
                <div className="bg-gray-50 rounded-xl p-4">
                  <h3 className="font-semibold text-gray-700 mb-2 text-sm">📦 بيانات الشحن</h3>
                  <p className="text-sm text-gray-600">{form.name} — {form.phone}</p>
                  <p className="text-sm text-gray-600">{form.city}، {form.address}</p>
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <h3 className="font-semibold text-gray-700 mb-2 text-sm">💳 طريقة الدفع</h3>
                  <p className="text-sm text-gray-600">
                    {form.payMethod === 'card' ? 'بطاقة بنكية' : form.payMethod === 'stc' ? 'STC Pay' : 'الدفع عند الاستلام'}
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                {items.map(item => (
                  <div key={item.id} className="flex gap-3 items-center">
                    <div className="relative w-16 h-16 rounded-xl overflow-hidden bg-gray-100 flex-shrink-0">
                      <Image src={item.image} alt={item.name} fill className="object-cover" sizes="64px" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-700 line-clamp-1">{item.name}</p>
                      <p className="text-xs text-gray-400">الكمية: {item.qty}</p>
                    </div>
                    <p className="font-bold text-primary-600 text-sm">{item.price * item.qty} ر.س</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-100">
            {step > 0
              ? <button onClick={handleBack} className="btn-outline">← رجوع</button>
              : <Link href="/cart" className="btn-outline">← السلة</Link>
            }
            {step < STEPS.length - 1
              ? <button onClick={handleNext} className="btn-primary" disabled={
                  step === 0 && (!form.name || !form.phone || !form.city || !form.address)
                }>
                  التالي →
                </button>
              : <button onClick={handleSubmit} className="btn-primary px-8">
                  ✓ تأكيد الطلب — {grandTotal} ر.س
                </button>
            }
          </div>
        </div>

        {/* Order Summary Sidebar */}
        <div className="lg:col-span-1">
          <div className="card p-5 sticky top-20">
            <h3 className="font-bold text-gray-800 mb-4">ملخص الطلب</h3>
            <div className="space-y-3 max-h-60 overflow-y-auto">
              {items.map(item => (
                <div key={item.id} className="flex items-center gap-3">
                  <div className="relative w-12 h-12 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
                    <Image src={item.image} alt={item.name} fill className="object-cover" sizes="48px" />
                    <span className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center font-bold">
                      {item.qty}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-gray-600 line-clamp-1">{item.name}</p>
                  </div>
                  <p className="text-sm font-bold text-gray-700">{item.price * item.qty} ر.س</p>
                </div>
              ))}
            </div>
            <div className="border-t border-gray-100 mt-4 pt-4 space-y-2 text-sm">
              <div className="flex justify-between text-gray-500">
                <span>المجموع</span><span>{total} ر.س</span>
              </div>
              <div className="flex justify-between text-gray-500">
                <span>الشحن</span>
                <span className={shipping === 0 ? 'text-green-600 font-semibold' : ''}>
                  {shipping === 0 ? 'مجاني' : `${shipping} ر.س`}
                </span>
              </div>
              <div className="flex justify-between font-bold text-base border-t border-gray-100 pt-2">
                <span>الإجمالي</span>
                <span className="text-primary-600 text-lg">{grandTotal} ر.س</span>
              </div>
            </div>
            <div className="flex flex-col gap-1 mt-4 text-xs text-gray-400 text-center">
              <span>🔒 جميع المعاملات مشفرة وآمنة</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
