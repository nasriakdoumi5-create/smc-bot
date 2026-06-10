'use client';
import { createContext, useContext, useReducer, useEffect, useState } from 'react';

const CartContext = createContext(null);

function reducer(state, action) {
  switch (action.type) {
    case 'ADD': {
      const ex = state.items.find(i => i.id === action.item.id);
      if (ex) return { ...state, items: state.items.map(i => i.id === action.item.id ? {...i, qty: i.qty+1} : i) };
      return { ...state, items: [...state.items, { ...action.item, qty: 1 }] };
    }
    case 'REMOVE': return { ...state, items: state.items.filter(i => i.id !== action.id) };
    case 'UPDATE': {
      if (action.qty <= 0) return { ...state, items: state.items.filter(i => i.id !== action.id) };
      return { ...state, items: state.items.map(i => i.id === action.id ? {...i, qty: action.qty} : i) };
    }
    case 'CLEAR': return { ...state, items: [] };
    case 'LOAD':  return { ...state, items: action.items };
    default: return state;
  }
}

export function CartProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, { items: [] });
  const [open, setOpen]   = useState(false);

  useEffect(() => {
    try { const s = localStorage.getItem('cart'); if (s) dispatch({ type:'LOAD', items: JSON.parse(s) }); } catch {}
  }, []);
  useEffect(() => { localStorage.setItem('cart', JSON.stringify(state.items)); }, [state.items]);

  const total = state.items.reduce((s, i) => s + i.price * i.qty, 0);
  const count = state.items.reduce((s, i) => s + i.qty, 0);

  function addToCart(item) { dispatch({ type:'ADD', item }); setOpen(true); }

  return (
    <CartContext.Provider value={{ items: state.items, total, count, dispatch, open, setOpen, addToCart }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() { return useContext(CartContext); }
