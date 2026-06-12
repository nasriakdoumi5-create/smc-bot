'use client';
import { useCart } from '@/context/CartContext';
import Link from 'next/link';
import { Shield, Lock, RotateCcw, Truck, CheckCircle } from 'lucide-react';
import { useState } from 'react';
import FreeShippingBar from '@/components/FreeShippingBar';

export default function CheckoutPage() {
  const { items, total, clearCart } = useCart();
  const shipping = total >= 40 ? 0 : 4.99;
  const [coupon, setCoupon] = useState('');
  const [couponApplied, setCouponApplied] = useState(false);
  const [couponError, setCouponError] = useState('');

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

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="flex items-center justify-between mb-8 flex-wrap gap-3">
        <h1 className="text-3xl font-bold">Checkout</h1>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Lock className="w-4 h-4 text-green-600" />
          <span className="text-green-600 font-medium">SSL Secured Checkout</span>
        </div>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">🐾</div>
          <p className="text-gray-400 mb-2 text-lg">Your cart is empty</p>
          <p className="text-gray-400 text-sm mb-6">Add some adorable pet cases to get started!</p>
          <Link href="/products" className="btn-primary">Start Shopping</Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
          <div className="md:col-span-3">
            <div className="card p-6 mb-4">
              <h2 className="font-bold text-lg mb-4">Order Summary</h2>

              <FreeShippingBar total={total} />

              <div className="space-y-4">
                {items.map(item => (
                  <div key={`${item.id}-${item.model}`} className="flex gap-4 py-3 border-b last:border-0">
                    <img src={item.image} alt={item.name} className="w-16 h-16 rounded-xl object-cover flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-dark text-sm truncate">{item.name}</p>
                      <p className="text-xs text-gray-500">{item.model}</p>
                      <p className="text-xs text-gray-500">Qty: {item.qty}</p>
                    </div>
                    <p className="font-bold text-accent whitespace-nowrap">€{(item.price * item.qty).toFixed(2)}</p>
                  </div>
                ))}
              </div>

              <div className="mt-4 pt-4 border-t">
                <p className="text-sm font-semibold mb-2">Promo Code</p>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={coupon}
                    onChange={e => { setCoupon(e.target.value); setCouponError(''); }}
                    placeholder="Enter code (e.g. PAWS10)"
                    className="flex-1 border-2 border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-primary"
                  />
                  <button
                    onClick={handleApplyCoupon}
                    className="bg-primary text-white px-4 py-2 rounded-xl text-sm font-semibold"
                  >
                    Apply
                  </button>
                </div>
                {couponApplied && <p className="text-xs text-green-600 font-medium mt-1">🎉 10% discount applied!</p>}
                {couponError && <p className="text-xs text-red-500 mt-1">{couponError}</p>}
              </div>

              <div className="mt-4 space-y-2">
                <div className="flex justify-between text-sm"><span className="text-gray-600">Subtotal</span><span>€{total.toFixed(2)}</span></div>
                {couponApplied && (
                  <div className="flex justify-between text-sm text-green-600">
                    <span>Discount (10%)</span><span>-€{discount.toFixed(2)}</span>
                  </div>
                )}
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Shipping</span>
                  <span>{shipping === 0 ? <span className="text-green-600 font-medium">Free</span> : `€${shipping.toFixed(2)}`}</span>
                </div>
                <div className="flex justify-between font-bold text-xl border-t pt-3">
                  <span>Total</span>
                  <span className="text-accent">€{finalTotal.toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-2xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <Shield className="w-5 h-5 text-green-600" />
                <p className="font-bold text-green-700">Your order is protected</p>
              </div>
              <ul className="space-y-1.5 text-sm text-green-700">
                <li className="flex items-center gap-2"><CheckCircle className="w-3.5 h-3.5 flex-shrink-0" /> 30-day hassle-free returns</li>
                <li className="flex items-center gap-2"><CheckCircle className="w-3.5 h-3.5 flex-shrink-0" /> Fully tracked &amp; insured delivery</li>
                <li className="flex items-center gap-2"><CheckCircle className="w-3.5 h-3.5 flex-shrink-0" /> Print quality guaranteed</li>
              </ul>
            </div>
          </div>

          <div className="md:col-span-2">
            <div className="card p-6 mb-4">
              <div className="flex items-center gap-2 mb-4">
                <Lock className="w-4 h-4 text-green-600" />
                <h3 className="font-bold text-dark">Payment</h3>
              </div>
              <div className="bg-secondary rounded-xl p-5 text-center mb-4">
                <p className="text-gray-600 text-sm">💳 <strong>Payment integration coming soon</strong></p>
                <p className="text-gray-500 text-xs mt-2">We accept Visa, Mastercard, PayPal &amp; Apple Pay</p>
              </div>
              <button className="btn-primary w-full text-center">
                Complete Order →
              </button>
            </div>

            <div className="space-y-3">
              {[
                { icon: Lock, label: 'SSL Encrypted', sub: '256-bit encryption' },
                { icon: RotateCcw, label: '30-Day Returns', sub: 'No questions asked' },
                { icon: Truck, label: 'Fast EU Shipping', sub: '3–5 business days' },
              ].map(t => (
                <div key={t.label} className="flex items-center gap-3 bg-white rounded-xl px-4 py-3">
                  <t.icon className="w-4 h-4 text-primary flex-shrink-0" />
                  <div>
                    <p className="text-xs font-semibold text-dark">{t.label}</p>
                    <p className="text-xs text-gray-400">{t.sub}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
