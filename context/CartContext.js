'use client';
import { createContext, useContext, useState, useEffect } from 'react';
import { trackAddToCart } from '@/components/MetaPixel';
import { ttqAddToCart } from '@/components/TikTokPixel';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [wishlist, setWishlist] = useState([]);
  const [recentlyViewed, setRecentlyViewed] = useState([]);

  useEffect(() => {
    try {
      const saved = localStorage.getItem('pawcase-cart');
      if (saved) setItems(JSON.parse(saved));
    } catch {}
    try {
      const savedWishlist = localStorage.getItem('pawcase-wishlist');
      if (savedWishlist) setWishlist(JSON.parse(savedWishlist));
    } catch {}
    try {
      const savedRecent = localStorage.getItem('pawcase-recent');
      if (savedRecent) setRecentlyViewed(JSON.parse(savedRecent));
    } catch {}
  }, []);

  useEffect(() => {
    localStorage.setItem('pawcase-cart', JSON.stringify(items));
  }, [items]);

  useEffect(() => {
    localStorage.setItem('pawcase-wishlist', JSON.stringify(wishlist));
  }, [wishlist]);

  useEffect(() => {
    localStorage.setItem('pawcase-recent', JSON.stringify(recentlyViewed));
  }, [recentlyViewed]);

  const addToCart = (product, model, qty = 1) => {
    trackAddToCart(product);
    ttqAddToCart(product);
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

  const addToWishlist = (id) => {
    setWishlist(prev => prev.includes(id) ? prev : [...prev, id]);
  };

  const removeFromWishlist = (id) => {
    setWishlist(prev => prev.filter(w => w !== id));
  };

  const isWishlisted = (id) => wishlist.includes(id);

  const addToRecentlyViewed = (id) => {
    setRecentlyViewed(prev => {
      const filtered = prev.filter(r => r !== id);
      return [id, ...filtered].slice(0, 6);
    });
  };

  return (
    <CartContext.Provider value={{
      items, addToCart, removeFromCart, updateQty, clearCart, total, count,
      isOpen, openCart: () => setIsOpen(true), closeCart: () => setIsOpen(false),
      wishlist, addToWishlist, removeFromWishlist, isWishlisted,
      recentlyViewed, addToRecentlyViewed,
    }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
