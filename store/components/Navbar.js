'use client';

import Link from 'next/link';
import { useCart } from '../context/CartContext';
import { useState } from 'react';

export default function Navbar() {
  const { count } = useCart();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">🛍️</span>
            <span className="text-xl font-bold text-primary-600">متجري</span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-6">
            <Link href="/" className="text-gray-600 hover:text-primary-600 font-medium transition-colors">
              الرئيسية
            </Link>
            <Link href="/products" className="text-gray-600 hover:text-primary-600 font-medium transition-colors">
              المنتجات
            </Link>
            <Link href="/admin" className="text-gray-600 hover:text-primary-600 font-medium transition-colors">
              لوحة التحكم
            </Link>
          </div>

          {/* Cart */}
          <div className="flex items-center gap-3">
            <Link href="/cart" className="relative p-2 rounded-xl hover:bg-gray-100 transition-colors">
              <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              {count > 0 && (
                <span className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center font-bold">
                  {count}
                </span>
              )}
            </Link>

            {/* Mobile menu button */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden p-2 rounded-xl hover:bg-gray-100 transition-colors"
            >
              <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {menuOpen
                  ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                }
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden pb-4 flex flex-col gap-2">
            <Link href="/" onClick={() => setMenuOpen(false)}
              className="px-4 py-2 text-gray-700 hover:bg-gray-50 rounded-xl font-medium">
              الرئيسية
            </Link>
            <Link href="/products" onClick={() => setMenuOpen(false)}
              className="px-4 py-2 text-gray-700 hover:bg-gray-50 rounded-xl font-medium">
              المنتجات
            </Link>
            <Link href="/admin" onClick={() => setMenuOpen(false)}
              className="px-4 py-2 text-gray-700 hover:bg-gray-50 rounded-xl font-medium">
              لوحة التحكم
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
