'use client';
import Link from 'next/link';
import { useCart } from '@/context/CartContext';
import { ShoppingBag } from 'lucide-react';
import { useState } from 'react';

export default function Navbar() {
  const { count, openCart } = useCart();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="bg-white shadow-sm sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-primary flex items-center gap-2">
          🐾 PawCase
        </Link>

        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-dark">
          <Link href="/products" className="hover:text-primary transition-colors">Shop</Link>
          <Link href="/products?cat=dogs" className="hover:text-primary transition-colors">Dogs</Link>
          <Link href="/products?cat=cats" className="hover:text-primary transition-colors">Cats</Link>
          <Link href="/products?cat=custom" className="hover:text-primary transition-colors">Custom</Link>
          <Link href="/about" className="hover:text-primary transition-colors">About</Link>
        </div>

        <div className="flex items-center gap-3">
          <button onClick={openCart} className="relative p-2 hover:bg-secondary rounded-lg transition-colors">
            <ShoppingBag className="w-5 h-5 text-dark" />
            {count > 0 && (
              <span className="absolute -top-1 -right-1 bg-accent text-white text-xs w-5 h-5 rounded-full flex items-center justify-center font-bold">
                {count}
              </span>
            )}
          </button>
          <button className="md:hidden p-2" onClick={() => setMobileOpen(!mobileOpen)}>
            <div className="w-5 h-0.5 bg-dark mb-1"></div>
            <div className="w-5 h-0.5 bg-dark mb-1"></div>
            <div className="w-5 h-0.5 bg-dark"></div>
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="md:hidden bg-white border-t px-4 py-4 flex flex-col gap-4 text-sm font-medium">
          <Link href="/products" onClick={() => setMobileOpen(false)}>Shop All</Link>
          <Link href="/products?cat=dogs" onClick={() => setMobileOpen(false)}>Dogs 🐕</Link>
          <Link href="/products?cat=cats" onClick={() => setMobileOpen(false)}>Cats 🐈</Link>
          <Link href="/products?cat=custom" onClick={() => setMobileOpen(false)}>Custom ✨</Link>
          <Link href="/about" onClick={() => setMobileOpen(false)}>About</Link>
          <Link href="/faq" onClick={() => setMobileOpen(false)}>FAQ</Link>
          <Link href="/contact" onClick={() => setMobileOpen(false)}>Contact</Link>
        </div>
      )}
    </nav>
  );
}
