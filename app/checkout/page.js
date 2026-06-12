'use client';
import { useCart } from '@/context/CartContext';
import Link from 'next/link';
import { Shield, Lock, RotateCcw, Truck, CheckCircle, ChevronRight } from 'lucide-react';
import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import FreeShippingBar from '@/components/FreeShippingBar';

const getDeliveryDate = () => {
  const d = new Date();
  d.setDate(d.getDate() + 5);
  const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  return `${days[d.getDay()]}, ${months[d.getMonth()]} ${d.getDate()}`;
};

function CheckoutContent() {
  const { items, total, clearCart } = useCart();
  const router = useRouter();
  const searchParams = useSearchParams();
  const shipping = total >= 40 ? 0 : 4.99;
  const [coupon, setCoupon] = useState('');
  const [couponApplied, setCouponApplied] = useState(false);
  const [couponError, setCouponError] = useState('');

  useEffect(() => {
    const urlCoupon = searchParams.get('coupon');
    if (urlCoupon && urlCoupon.toUpperCase() === 'PAWS10') {
      setCoupon('PAWS10');
      setCouponApplied(true);
    }
  }, [searchParams]);
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [payMethod, setPayMethod] = useState('card');
  const [form, setForm] = useState({
    firstName: '', lastName: '', email: '', address: '', city: '', country: 'Germany', zip: '',
    card: '', expiry: '', cvv: '', cardName: ''
  });
  const [errors, setErrors] = useState({});

  const discount = couponApplied ? total * 0.1 : 0;
  const finalTotal = total - discount + shipping;

  const handleApplyCoupon = () => {
    if (coupon.toUpperCase() === 'PAWS10') {
      setCouponApplied(true);
      setCouponError('');
    } else {
      setCouponError('Invalid code. Try PAWS10 for 10% off!');
      setCouponApplied(false);
    }
  };

  const validate1 = () => {
    const e = {};
    if (!form.firstName.trim()) e.firstName = 'Required';
    if (!form.lastName.trim()) e.lastName = 'Required';
    if (!form.email.includes('@')) e.email = 'Valid email required';
    if (!form.address.trim()) e.address = 'Required';
    if (!form.city.trim()) e.city = 'Required';
    if (!form.zip.trim()) e.zip = 'Required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const validate2 = () => {
    if (payMethod !== 'card') return true;
    const e = {};
    if (form.card.replace(/\s/g,'').length < 16) e.card = 'Valid 16-digit card number required';
    if (!form.expiry.includes('/')) e.expiry = 'Required (MM/YY)';
    if (form.cvv.length < 3) e.cvv = 'Required';
    if (!form.cardName.trim()) e.cardName = 'Name on card required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handlePlaceOrder = () => {
    if (!validate2()) return;
    setLoading(true);
    setTimeout(() => {
      clearCart();
      const orderNum = 'PW' + Date.now().toString().slice(-6);
      router.push(`/order-success?order=${orderNum}&email=${encodeURIComponent(form.email)}`);
    }, 1800);
  };

  const formatCard = v => v.replace(/\D/g,'').slice(0,16).replace(/(\d{4})(?=\d)/g,'$1 ').trim();
  const formatExpiry = v => {
    const d = v.replace(/\D/g,'').slice(0,4);
    return d.length > 2 ? d.slice(0,2) + '/' + d.slice(2) : d;
  };

  const Field = ({ label, name, type = 'text', placeholder = '' }) => (
    <div>
      <label className="block text-xs font-semibold text-gray-600 mb-1">{label}</label>
      <input
        type={type}
        value={form[name]}
        onChange={e => {
          let v = e.target.value;
          if (name === 'card') v = formatCard(v);
          if (name === 'expiry') v = formatExpiry(v);
          if (name === 'cvv') v = v.replace(/\D/g,'').slice(0,4);
          setForm(f => ({...f, [name]: v}));
          if (errors[name]) setErrors(er => ({...er, [name]: ''}));
        }}
        placeholder={placeholder}
        className={`w-full border-2 rounded-xl px-3 py-2.5 text-sm focus:outline-none transition-colors ${errors[name] ? 'border-red-400 bg-red-50' : 'border-gray-200 focus:border-primary'}`}
      />
      {errors[name] && <p className="text-xs text-red-500 mt-1">{errors[name]}</p>}
    </div>
  );

  if (items.length === 0 && !loading) {
    return (
      <div className="text-center py-20">
        <div className="text-6xl mb-4">🐾</div>
        <p className="text-gray-400 mb-6 text-lg">Your cart is empty</p>
        <Link href="/products" className="btn-primary">Start Shopping</Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <h1 className="text-2xl font-bold">Secure Checkout</h1>
        <div className="flex items-center gap-2 text-sm text-green-600 font-medium">
          <Lock className="w-4 h-4" />
          SSL Encrypted
        </div>
      </div>

      {/* Progress indicator */}
      <div className="flex items-center gap-2 mb-8 text-sm">
        {['Shipping', 'Payment', 'Confirm'].map((s, i) => (
          <div key={s} className="flex items-center gap-1.5">
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${step > i + 1 ? 'bg-green-500 text-white' : step === i + 1 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-400'}`}>
              {step > i + 1 ? '✓' : i + 1}
            </div>
            <span className={`hidden sm:inline ${step === i + 1 ? 'font-semibold text-dark' : 'text-gray-400'}`}>{s}</span>
            {i < 2 && <ChevronRight className="w-3 h-3 text-gray-300" />}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
        <div className="md:col-span-3 space-y-4">

          {/* STEP 1 — Shipping */}
          {step === 1 && (
            <div className="card p-6">
              <h2 className="font-bold text-lg mb-4">Shipping Information</h2>
              <div className="grid grid-cols-2 gap-3">
                <Field label="First Name" name="firstName" placeholder="Maria" />
                <Field label="Last Name" name="lastName" placeholder="García" />
              </div>
              <div className="mt-3">
                <Field label="Email Address" name="email" type="email" placeholder="you@example.com" />
              </div>
              <div className="mt-3">
                <Field label="Street Address" name="address" placeholder="Hauptstraße 42" />
              </div>
              <div className="grid grid-cols-2 gap-3 mt-3">
                <Field label="City" name="city" placeholder="Berlin" />
                <Field label="Postal Code" name="zip" placeholder="10115" />
              </div>
              <div className="mt-3">
                <label className="block text-xs font-semibold text-gray-600 mb-1">Country</label>
                <select value={form.country} onChange={e => setForm(f => ({...f, country: e.target.value}))}
                  className="w-full border-2 border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-primary bg-white">
                  {['Germany','France','Netherlands','Spain','Italy','Austria','Belgium','Sweden','Denmark','Poland','Portugal','Finland','Ireland','Czech Republic','Other EU'].map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-xl flex items-center gap-2 text-sm text-green-700">
                <Truck className="w-4 h-4 flex-shrink-0" />
                <span>Estimated delivery: <strong>{getDeliveryDate()}</strong></span>
              </div>
              <button onClick={() => { if (validate1()) setStep(2); }} className="btn-primary w-full mt-4">
                Continue to Payment →
              </button>
            </div>
          )}

          {/* STEP 2 — Payment */}
          {step === 2 && (
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-bold text-lg">Payment</h2>
                <button onClick={() => setStep(1)} className="text-xs text-primary hover:underline">← Edit shipping</button>
              </div>

              <div className="bg-secondary rounded-xl p-3 text-xs mb-4 text-gray-600">
                <strong>{form.firstName} {form.lastName}</strong> · {form.address}, {form.city} {form.zip}, {form.country}
                <span className="block mt-0.5">{form.email}</span>
              </div>

              {/* Method tabs */}
              <div className="flex gap-2 mb-5">
                {[{id:'card',label:'💳 Card'},{id:'paypal',label:'🅿️ PayPal'},{id:'applepay',label:' Apple Pay'}].map(m => (
                  <button key={m.id} onClick={() => setPayMethod(m.id)}
                    className={`flex-1 py-2 rounded-xl text-sm font-semibold border-2 transition-all ${payMethod === m.id ? 'border-primary bg-primary/5 text-primary' : 'border-gray-200 text-gray-500 hover:border-gray-300'}`}>
                    {m.label}
                  </button>
                ))}
              </div>

              {payMethod === 'card' && (
                <div className="space-y-3">
                  <Field label="Name on Card" name="cardName" placeholder="Maria García" />
                  <Field label="Card Number" name="card" placeholder="4242 4242 4242 4242" />
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Expiry (MM/YY)" name="expiry" placeholder="12/26" />
                    <Field label="CVV" name="cvv" placeholder="123" />
                  </div>
                  <div className="flex items-center gap-3 pt-1">
                    <span className="text-xs text-gray-400">Accepted:</span>
                    {['VISA','MC','AMEX'].map(c => (
                      <span key={c} className="text-xs font-bold border border-gray-200 rounded px-2 py-0.5 text-gray-500 bg-gray-50">{c}</span>
                    ))}
                    <span className="ml-auto flex items-center gap-1 text-xs text-green-600"><Lock className="w-3 h-3" />256-bit SSL</span>
                  </div>
                </div>
              )}

              {payMethod === 'paypal' && (
                <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-5 text-center">
                  <div className="text-3xl mb-2">🅿️</div>
                  <p className="font-semibold text-blue-800 mb-1">Pay with PayPal</p>
                  <p className="text-sm text-blue-600">You'll be redirected to PayPal to complete your purchase securely.</p>
                </div>
              )}

              {payMethod === 'applepay' && (
                <div className="bg-gray-50 border-2 border-gray-200 rounded-xl p-5 text-center">
                  <p className="font-semibold mb-1">Pay with Apple Pay</p>
                  <p className="text-sm text-gray-500">Complete your purchase using Face ID or Touch ID.</p>
                </div>
              )}

              <button onClick={handlePlaceOrder} disabled={loading}
                className="btn-primary w-full mt-5 flex items-center justify-center gap-2 disabled:opacity-70">
                {loading ? (
                  <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Processing…</>
                ) : (
                  <><Lock className="w-4 h-4" />Place Order — €{finalTotal.toFixed(2)}</>
                )}
              </button>
              <p className="text-xs text-gray-400 text-center mt-2">
                By placing your order you agree to our <a href="/faq" className="underline hover:text-primary">Returns Policy</a>
              </p>
            </div>
          )}

          {/* Protection box */}
          <div className="bg-green-50 border border-green-200 rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-4 h-4 text-green-600" />
              <p className="font-bold text-green-700 text-sm">Your order is protected</p>
            </div>
            <ul className="space-y-1 text-xs text-green-700">
              <li className="flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />30-day hassle-free returns</li>
              <li className="flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />Fully tracked &amp; insured delivery</li>
              <li className="flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />Print quality guaranteed</li>
            </ul>
          </div>
        </div>

        {/* Order summary */}
        <div className="md:col-span-2">
          <div className="card p-5 sticky top-24">
            <h2 className="font-bold text-base mb-3">Order Summary</h2>
            <FreeShippingBar total={total} />

            <div className="space-y-3 mt-3">
              {items.map(item => (
                <div key={`${item.id}-${item.model}`} className="flex gap-3 py-2 border-b last:border-0">
                  <div className="relative flex-shrink-0">
                    <img src={item.image} alt={item.name} className="w-12 h-12 rounded-lg object-cover" />
                    <span className="absolute -top-1.5 -right-1.5 bg-primary text-white text-xs rounded-full w-4 h-4 flex items-center justify-center leading-none">{item.qty}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-dark text-xs truncate">{item.name}</p>
                    <p className="text-xs text-gray-400">{item.model}</p>
                  </div>
                  <p className="font-bold text-accent text-sm whitespace-nowrap">€{(item.price * item.qty).toFixed(2)}</p>
                </div>
              ))}
            </div>

            <div className="mt-3 pt-3 border-t">
              <div className="flex gap-2">
                <input type="text" value={coupon} onChange={e => { setCoupon(e.target.value); setCouponError(''); }}
                  placeholder="Promo code"
                  className="flex-1 border-2 border-gray-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-primary" />
                <button onClick={handleApplyCoupon} className="bg-primary text-white px-3 py-2 rounded-xl text-xs font-semibold">Apply</button>
              </div>
              {couponApplied && <p className="text-xs text-green-600 font-medium mt-1">🎉 PAWS10 — 10% off applied!</p>}
              {couponError && <p className="text-xs text-red-500 mt-1">{couponError}</p>}
            </div>

            <div className="mt-3 space-y-1.5 text-sm">
              <div className="flex justify-between"><span className="text-gray-500">Subtotal</span><span>€{total.toFixed(2)}</span></div>
              {couponApplied && <div className="flex justify-between text-green-600"><span>Discount (PAWS10)</span><span>-€{discount.toFixed(2)}</span></div>}
              <div className="flex justify-between">
                <span className="text-gray-500">Shipping</span>
                <span>{shipping === 0 ? <span className="text-green-600 font-medium">Free</span> : `€${shipping.toFixed(2)}`}</span>
              </div>
              <div className="flex justify-between font-bold text-base border-t pt-2 mt-1">
                <span>Total</span><span className="text-accent">€{finalTotal.toFixed(2)}</span>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t grid grid-cols-3 gap-2 text-center">
              {[{icon:Lock,label:'SSL Secure'},{icon:RotateCcw,label:'30-Day Return'},{icon:Truck,label:'Fast Ship'}].map(t => (
                <div key={t.label} className="flex flex-col items-center gap-1">
                  <t.icon className="w-3.5 h-3.5 text-primary" />
                  <span className="text-xs text-gray-500">{t.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={<div className="flex justify-center py-20"><div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" /></div>}>
      <CheckoutContent />
    </Suspense>
  );
}
