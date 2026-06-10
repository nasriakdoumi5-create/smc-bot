'use client';

import { createContext, useContext, useReducer, useEffect } from 'react';

const CartContext = createContext(null);

function cartReducer(state, action) {
  switch (action.type) {
    case 'ADD': {
      const existing = state.items.find(i => i.id === action.product.id);
      if (existing) {
        return {
          ...state,
          items: state.items.map(i =>
            i.id === action.product.id
              ? { ...i, qty: i.qty + 1 }
              : i
          ),
        };
      }
      return { ...state, items: [...state.items, { ...action.product, qty: 1 }] };
    }
    case 'REMOVE':
      return { ...state, items: state.items.filter(i => i.id !== action.id) };
    case 'UPDATE_QTY':
      if (action.qty <= 0) {
        return { ...state, items: state.items.filter(i => i.id !== action.id) };
      }
      return {
        ...state,
        items: state.items.map(i =>
          i.id === action.id ? { ...i, qty: action.qty } : i
        ),
      };
    case 'CLEAR':
      return { ...state, items: [] };
    case 'LOAD':
      return { ...state, items: action.items };
    default:
      return state;
  }
}

export function CartProvider({ children }) {
  const [state, dispatch] = useReducer(cartReducer, { items: [] });

  useEffect(() => {
    try {
      const saved = localStorage.getItem('cart');
      if (saved) dispatch({ type: 'LOAD', items: JSON.parse(saved) });
    } catch {}
  }, []);

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(state.items));
  }, [state.items]);

  const total = state.items.reduce((sum, i) => sum + i.price * i.qty, 0);
  const count = state.items.reduce((sum, i) => sum + i.qty, 0);

  return (
    <CartContext.Provider value={{ items: state.items, total, count, dispatch }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used within CartProvider');
  return ctx;
}
