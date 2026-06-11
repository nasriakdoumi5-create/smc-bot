'use client';
import { useCart } from '@/context/CartContext';
import Link from 'next/link';
import { X, Plus, Minus, ShoppingBag } from 'lucide-react';

export default function CartDrawer() {
  const { items, isOpen, closeCart, removeFromCart, updateQty, total, count } = useCart();
  const shipping = total >= 40 ? 0 : 4.99;

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
          <div className="flex-1 flex flex-col items-center justify-center text-gray-400 gap-4 p-8">
            <ShoppingBag className="w-16 h-16 opacity-30" />
            <p className="text-lg">Your cart is empty</p>
            <Link href="/products" onClick={closeCart} className="btn-primary">Shop Now</Link>
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              {items.map((item) => (
                <div key={`${item.id}-${item.model}`} className="flex gap-3 bg-secondary rounded-xl p-3">
                  <img src={item.image} alt={item.name} className="w-16 h-16 rounded-lg object-cover" />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm truncate">{item.name}</p>
                    <p className="text-xs text-gray-500">{item.model}</p>
                    <p className="text-accent font-bold">€{item.price}</p>
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
            </div>

            <div className="p-5 border-t bg-white">
              <div className="flex justify-between text-sm mb-1">
                <span>Subtotal</span><span>€{total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm mb-3">
                <span>Shipping</span>
                <span>{shipping === 0 ? <span className="text-green-600 font-medium">Free!</span> : `€${shipping.toFixed(2)}`}</span>
              </div>
              {total < 40 && <p className="text-xs text-gray-500 mb-3">Add €{(40 - total).toFixed(2)} more for free shipping</p>}
              <div className="flex justify-between font-bold text-lg mb-4">
                <span>Total</span><span>€{(total + shipping).toFixed(2)}</span>
              </div>
              <Link href="/checkout" onClick={closeCart} className="btn-primary w-full text-center block">
                Checkout
              </Link>
            </div>
          </>
        )}
      </div>
    </>
  );
}
