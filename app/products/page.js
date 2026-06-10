'use client';

import { useState, useMemo } from 'react';
import { PRODUCTS, CATEGORIES } from '../../data/products';
import ProductCard from '../../components/ProductCard';
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

function ProductsContent() {
  const searchParams = useSearchParams();
  const initialCategory = searchParams.get('category') || 'all';

  const [search, setSearch]       = useState('');
  const [category, setCategory]   = useState(initialCategory);
  const [sortBy, setSortBy]       = useState('default');

  const filtered = useMemo(() => {
    let list = PRODUCTS;

    if (category !== 'all') {
      list = list.filter(p => p.category === category);
    }

    if (search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q)
      );
    }

    switch (sortBy) {
      case 'price-asc':   return [...list].sort((a, b) => a.price - b.price);
      case 'price-desc':  return [...list].sort((a, b) => b.price - a.price);
      case 'rating':      return [...list].sort((a, b) => b.rating - a.rating);
      case 'discount': {
        const disc = p => Math.round(((p.originalPrice - p.price) / p.originalPrice) * 100);
        return [...list].sort((a, b) => disc(b) - disc(a));
      }
      default: return list;
    }
  }, [category, search, sortBy]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">جميع المنتجات</h1>

      {/* Filters Bar */}
      <div className="bg-white rounded-2xl p-4 shadow-sm mb-6 flex flex-col sm:flex-row gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <svg className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
            fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="ابحث عن منتج..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input-field pr-10"
          />
        </div>

        {/* Category */}
        <select
          value={category}
          onChange={e => setCategory(e.target.value)}
          className="input-field sm:w-44"
        >
          {CATEGORIES.map(c => (
            <option key={c.id} value={c.id}>{c.label}</option>
          ))}
        </select>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={e => setSortBy(e.target.value)}
          className="input-field sm:w-48"
        >
          <option value="default">الترتيب: افتراضي</option>
          <option value="price-asc">السعر: الأقل أولاً</option>
          <option value="price-desc">السعر: الأعلى أولاً</option>
          <option value="rating">الأعلى تقييماً</option>
          <option value="discount">أكبر خصم</option>
        </select>
      </div>

      {/* Category Chips */}
      <div className="flex gap-2 flex-wrap mb-6">
        {CATEGORIES.map(c => (
          <button
            key={c.id}
            onClick={() => setCategory(c.id)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
              category === c.id
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {/* Results Count */}
      <p className="text-sm text-gray-500 mb-4">
        {filtered.length} منتج{filtered.length !== 1 ? '' : ''}
      </p>

      {/* Grid */}
      {filtered.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {filtered.map(p => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20 text-gray-400">
          <div className="text-5xl mb-4">🔍</div>
          <p className="text-lg font-medium">لم يتم العثور على منتجات</p>
          <p className="text-sm mt-1">جرب كلمة بحث مختلفة أو فئة أخرى</p>
        </div>
      )}
    </div>
  );
}

export default function ProductsPage() {
  return (
    <Suspense fallback={<div className="text-center py-20 text-gray-400">جاري التحميل...</div>}>
      <ProductsContent />
    </Suspense>
  );
}
