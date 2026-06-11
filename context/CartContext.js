'use client';
import { createContext, useContext, useState, useEffect } from 'react';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    try {
      const saved = localStorage.getItem('pawcase-cart');
      if (saved) setItems(JSON.parse(saved));
    } catch {}
  }, []);

  useEffect(() => {
    localStorage.setItem('pawcase-cart', JSON.stringify(items));
  }, [items]);

  const addToCart = (product, model, qty = 1) => {
    setItems(prev => {
      const key = `${product.id}-${model}`;
      const existing = prev.find(i => `${i.id}-${i.model}` === key);
      if (existing) {
        return prev.map(i => `${i.id}-${i.model}` === key ? { ...i, qty: i.qty + qty } : i);
      }
      return [...prev, { id: product.id, name: product.name, price: product.price, image: product.image, model, qty }];
    });
    setIsOpen(true);
  };

  const removeFromCart = (id, model) => {
    setItems(prev => prev.filter(i => !(i.id === id && i.model === model)));
  };

  const updateQty = (id, model, qty) => {
    if (qty < 1) { removeFromCart(id, model); return; }
    setItems(prev => prev.map(i => i.id === id && i.model === model ? { ...i, qty } : i));
  };

  const clearCart = () => setItems([]);
  const total = items.reduce((s, i) => s + i.price * i.qty, 0);
  const count = items.reduce((s, i) => s + i.qty, 0);

  return (
    <CartContext.Provider value={{ items, addToCart, removeFromCart, updateQty, clearCart, total, count, isOpen, openCart: () => setIsOpen(true), closeCart: () => setIsOpen(false) }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
