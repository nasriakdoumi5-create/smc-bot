'use client';
import Link from 'next/link';
import { useCart } from '../context/CartContext';
import { useSession, signOut } from 'next-auth/react';
import { useState } from 'react';

const CATEGORIES = [
  {slug:'electronics',name:'إلكترونيات',icon:'💻'},
  {slug:'clothing',name:'ملابس',icon:'👕'},
  {slug:'home',name:'المنزل',icon:'🏠'},
  {slug:'sports',name:'رياضة',icon:'⚽'},
  {slug:'books',name:'كتب',icon:'📚'},
];

export default function Navbar() {
  const { count, setOpen } = useCart();
  const { data: session }  = useSession();
  const [search, setSearch]   = useState('');
  const [userMenu, setUserMenu] = useState(false);

  function handleSearch(e) {
    e.preventDefault();
    if (search.trim()) window.location.href = `/products?search=${encodeURIComponent(search.trim())}`;
  }

  return (
    <header className="sticky top-0 z-30 bg-slate-800 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center gap-4">
        <Link href="/" className="flex-shrink-0 flex items-center gap-2">
          <span className="text-2xl">🛍️</span>
          <span className="text-white font-extrabold text-xl tracking-tight hidden sm:block">متجري</span>
        </Link>

        <form onSubmit={handleSearch} className="flex-1 flex">
          <div className="flex w-full rounded-xl overflow-hidden border-2 border-transparent focus-within:border-primary-400 transition-colors">
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="ابحث عن منتج..."
              className="flex-1 px-4 py-2 text-sm bg-white text-gray-800 focus:outline-none"
            />
            <button type="submit" className="px-4 bg-primary-600 hover:bg-primary-700 transition-colors text-white font-bold text-sm">بحث</button>
          </div>
        </form>

        <div className="flex items-center gap-1 flex-shrink-0">
          <button onClick={() => setOpen(true)} className="relative p-2.5 text-white hover:bg-slate-700 rounded-xl transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            {count > 0 && <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center font-bold">{count > 9 ? '9+' : count}</span>}
          </button>

          <Link href="/account/wishlist" className="p-2.5 text-white hover:bg-slate-700 rounded-xl transition-colors hidden sm:flex">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </Link>

          <div className="relative">
            <button onClick={() => setUserMenu(!userMenu)} className="p-2.5 text-white hover:bg-slate-700 rounded-xl transition-colors flex items-center gap-1">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              {session && <span className="text-xs text-gray-300 hidden md:block max-w-[80px] truncate">{session.user.name}</span>}
            </button>
            {userMenu && (
              <div className="absolute left-0 top-full mt-1 w-48 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50">
                {session ? (
                  <>
                    <Link href="/account" onClick={() => setUserMenu(false)} className="flex items-center gap-2 px-4 py-3 text-sm text-gray-700 hover:bg-gray-50">👤 حسابي</Link>
                    <Link href="/account/orders" onClick={() => setUserMenu(false)} className="flex items-center gap-2 px-4 py-3 text-sm text-gray-700 hover:bg-gray-50">📦 طلباتي</Link>
                    <Link href="/account/wishlist" onClick={() => setUserMenu(false)} className="flex items-center gap-2 px-4 py-3 text-sm text-gray-700 hover:bg-gray-50">❤️ المفضلة</Link>
                    {session.user.role === 'ADMIN' && <Link href="/admin" onClick={() => setUserMenu(false)} className="flex items-center gap-2 px-4 py-3 text-sm text-primary-600 hover:bg-primary-50 font-semibold">⚙️ لوحة التحكم</Link>}
                    <button onClick={() => { signOut(); setUserMenu(false); }} className="w-full text-right flex items-center gap-2 px-4 py-3 text-sm text-red-500 hover:bg-red-50">🚪 تسجيل الخروج</button>
                  </>
                ) : (
                  <>
                    <Link href="/login" onClick={() => setUserMenu(false)} className="flex items-center gap-2 px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 font-semibold">تسجيل الدخول</Link>
                    <Link href="/register" onClick={() => setUserMenu(false)} className="flex items-center gap-2 px-4 py-3 text-sm text-primary-600 hover:bg-primary-50 font-semibold">إنشاء حساب</Link>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="bg-slate-700 border-t border-slate-600">
        <div className="max-w-7xl mx-auto px-4 flex gap-1 overflow-x-auto py-1.5">
          <Link href="/products" className="flex-shrink-0 px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-slate-600 rounded-lg transition-colors font-medium">الكل</Link>
          {CATEGORIES.map(c => (
            <Link key={c.slug} href={`/products?category=${c.slug}`}
              className="flex-shrink-0 flex items-center gap-1.5 px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-slate-600 rounded-lg transition-colors font-medium whitespace-nowrap">
              <span>{c.icon}</span>{c.name}
            </Link>
          ))}
        </div>
      </div>
    </header>
  );
}
