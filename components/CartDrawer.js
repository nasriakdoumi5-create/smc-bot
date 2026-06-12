'use client';
import { useCart } from '@/context/CartContext';
import { products } from '@/data/products';
import Link from 'next/link';
import { X, Plus, Minus, ShoppingBag, Shield, RotateCcw, Truck } from 'lucide-react';
import { useState } from 'react';
import FreeShippingBar from '@/components/FreeShippingBar';

export default function CartDrawer() {
  const { items, isOpen, closeCart, removeFromCart, updateQty, total, count, addToCart } = useCart();
  const [coupon, setCoupon] = useState('');
  const [couponApplied, setCouponApplied] = useState(false);
  const [couponError, setCouponError] = useState('');
  const shipping = total >= 40 ? 0 : 4.99;

  const cartIds = items.map(i => i.id);
  const upsell = products.find(p => !cartIds.includes(p.id) && !p.isCustom);

  const handleApplyCoupon = () => {
    if (coupon.toUpperCase() === 'PAWS10') {
      setCouponApplied(true);
      setCouponError('');
    } else {
      setCouponError('Invalid code. Try PAWS10 for 10% off!');
      setCouponApplied(false);
    }
  };

  const discount = couponApplied ? total * 0.1 : 0;
  const finalTotal = total - discount + shipping;

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black/50 z-50" onClick={closeCart} />
      <div className="fixed right-0 top-0 h-full w-full max-w-md bg-white z-50 flex flex-col shadow-2xl">
        <div className="flex items-center justify-between p-5 border-b">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <ShoppingBag className="w-5 h-5" /> Cart ({count})
          </h2>
          <button onClick={closeCart} className="p-2 hover:bg-secondary rounded-lg"><X className="w-5 h-5" /></button>
        </div>

        {items.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-400 gap-4 p-8 text-center">
            <ShoppingBag className="w-16 h-16 opacity-30" />
            <div>
              <p className="text-lg font-semibold text-dark">Your cart is empty</p>
              <p className="text-sm text-gray-400 mt-1">Your pet is waiting to be on your phone 🐾</p>
            </div>
            <Link href="/products" onClick={closeCart} className="btn-primary">Find Your Perfect Case</Link>
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              <FreeShippingBar total={total} />

              {items.map((item) => (
                <div key={`${item.id}-${item.model}`} className="flex gap-3 bg-secondary rounded-xl p-3">
                  <img src={item.image} alt={item.name} className="w-16 h-16 rounded-lg object-cover" />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm truncate">{item.name}</p>
                    <p className="text-xs text-gray-500">{item.model}</p>
                    <p className="text-accent font-bold">€{item.price.toFixed(2)}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <button onClick={() => updateQty(item.id, item.model, item.qty - 1)} className="w-6 h-6 rounded-full bg-white border flex items-center justify-center hover:bg-gray-50">
                        <Minus className="w-3 h-3" />
                      </button>
                      <span className="text-sm font-medium w-6 text-center">{item.qty}</span>
                      <button onClick={() => updateQty(item.id, item.model, item.qty + 1)} className="w-6 h-6 rounded-full bg-white border flex items-center justify-center hover:bg-gray-50">
                        <Plus className="w-3 h-3" />
                      </button>
                      <button onClick={() => removeFromCart(item.id, item.model)} className="ml-auto text-gray-400 hover:text-red-500">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}

              {upsell && (
                <div className="border-2 border-dashed border-primary/30 rounded-xl p-3 bg-primary/5">
                  <p className="text-xs font-bold text-primary mb-2">Customers also love...</p>
                  <div className="flex gap-3 items-center">
                    <img src={upsell.image} alt={upsell.name} className="w-12 h-12 rounded-lg object-cover" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-semibold text-dark truncate">{upsell.name}</p>
                      <p className="text-xs text-accent font-bold">€{upsell.price.toFixed(2)}</p>
                    </div>
                    <button
                      onClick={() => addToCart(upsell, upsell.models[0])}
                      className="text-xs bg-primary text-white px-3 py-1.5 rounded-lg font-semibold whitespace-nowrap"
                    >
                      + Add
                    </button>
                  </div>
                </div>
              )}

              <div>
                <p className="text-xs font-semibold text-dark mb-1.5">Promo Code</p>
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
            </div>

            <div className="p-5 border-t bg-white">
              <div className="flex justify-between text-sm mb-1">
                <span>Subtotal</span><span>€{total.toFixed(2)}</span>
              </div>
              {couponApplied && (
                <div className="flex justify-between text-sm mb-1 text-green-600">
                  <span>Discount (10%)</span><span>-€{discount.toFixed(2)}</span>
                </div>
              )}
              <div className="flex justify-between text-sm mb-3">
                <span>Shipping</span>
                <span>{shipping === 0 ? <span className="text-green-600 font-medium">Free!</span> : `€${shipping.toFixed(2)}`}</span>
              </div>
              <div className="flex justify-between font-bold text-lg mb-4">
                <span>Total</span><span>€{finalTotal.toFixed(2)}</span>
              </div>
              <Link href="/checkout" onClick={closeCart} className="btn-primary w-full text-center block mb-3">
                Checkout →
              </Link>
              <div className="flex justify-center gap-4 text-xs text-gray-400">
                <span className="flex items-center gap-1"><Shield className="w-3 h-3" /> SSL Secure</span>
                <span className="flex items-center gap-1"><RotateCcw className="w-3 h-3" /> 30-Day Returns</span>
                <span className="flex items-center gap-1"><Truck className="w-3 h-3" /> EU Shipping</span>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
