'use client';
import { useCart } from '@/context/CartContext';
import Link from 'next/link';

export default function CheckoutPage() {
  const { items, total, clearCart } = useCart();
  const shipping = total >= 40 ? 0 : 4.99;

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-8">Order Summary</h1>
      {items.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-gray-400 mb-4">Your cart is empty</p>
          <Link href="/products" className="btn-primary">Start Shopping</Link>
        </div>
      ) : (
        <div className="card p-6">
          {items.map(item => (
            <div key={`${item.id}-${item.model}`} className="flex justify-between py-3 border-b last:border-0">
              <div>
                <p className="font-medium">{item.name}</p>
                <p className="text-sm text-gray-500">{item.model} × {item.qty}</p>
              </div>
              <p className="font-bold text-accent">€{(item.price * item.qty).toFixed(2)}</p>
            </div>
          ))}
          <div className="mt-4 space-y-2">
            <div className="flex justify-between text-sm"><span>Subtotal</span><span>€{total.toFixed(2)}</span></div>
            <div className="flex justify-between text-sm"><span>Shipping</span><span>{shipping === 0 ? 'Free' : `€${shipping.toFixed(2)}`}</span></div>
            <div className="flex justify-between font-bold text-lg border-t pt-3"><span>Total</span><span>€{(total + shipping).toFixed(2)}</span></div>
          </div>
          <div className="mt-6 bg-secondary rounded-xl p-4 text-center">
            <p className="text-gray-600 text-sm">💳 <strong>Payment integration coming soon</strong></p>
            <p className="text-gray-500 text-xs mt-1">We accept Visa, Mastercard, PayPal & Apple Pay</p>
          </div>
        </div>
      )}
    </div>
  );
}
