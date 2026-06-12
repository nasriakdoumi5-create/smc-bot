'use client';
import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { products, categories } from '@/data/products';
import ProductCard from '@/components/ProductCard';
import { SlidersHorizontal } from 'lucide-react';

const SORT_OPTIONS = [
  { value: 'featured', label: 'Featured' },
  { value: 'price-asc', label: 'Price: Low to High' },
  { value: 'price-desc', label: 'Price: High to Low' },
  { value: 'rating', label: 'Best Rated' },
  { value: 'reviews', label: 'Most Reviews' },
];

function sortProducts(list, sort) {
  const arr = [...list];
  switch (sort) {
    case 'price-asc': return arr.sort((a, b) => a.price - b.price);
    case 'price-desc': return arr.sort((a, b) => b.price - a.price);
    case 'rating': return arr.sort((a, b) => (b.rating || 0) - (a.rating || 0));
    case 'reviews': return arr.sort((a, b) => (b.reviewCount || 0) - (a.reviewCount || 0));
    default: return arr.sort((a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0));
  }
}

function ProductsContent() {
  const searchParams = useSearchParams();
  const [activeCategory, setActiveCategory] = useState('all');
  const [sort, setSort] = useState('featured');
  const [showSortMenu, setShowSortMenu] = useState(false);

  useEffect(() => {
    const cat = searchParams.get('cat');
    if (cat) setActiveCategory(cat);
  }, [searchParams]);

  const filtered = activeCategory === 'all' ? products : products.filter(p => p.category === activeCategory);
  const sorted = sortProducts(filtered, sort);
  const sortLabel = SORT_OPTIONS.find(o => o.value === sort)?.label;

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold mb-3">Our Phone Cases</h1>
        <p className="text-gray-500">Premium custom cases for every pet lover</p>
      </div>

      {/* Filters row */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        {/* Category tabs */}
        <div className="flex flex-wrap gap-2">
          {[{ id: 'all', name: 'All Cases', icon: '🐾' }, ...categories].map(cat => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`px-4 py-2 rounded-xl font-medium text-sm transition-all ${
                activeCategory === cat.id
                  ? 'bg-primary text-white shadow-md'
                  : 'bg-white text-dark hover:bg-secondary border border-gray-200'
              }`}
            >
              {cat.icon} {cat.name}
            </button>
          ))}
        </div>

        {/* Sort + count */}
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">{sorted.length} product{sorted.length !== 1 ? 's' : ''}</span>
          <div className="relative">
            <button
              onClick={() => setShowSortMenu(v => !v)}
              className="flex items-center gap-2 border border-gray-200 rounded-xl px-3 py-2 text-sm font-medium hover:border-primary transition-colors bg-white"
            >
              <SlidersHorizontal className="w-4 h-4 text-gray-400" />
              {sortLabel}
            </button>
            {showSortMenu && (
              <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg z-10 min-w-[180px] overflow-hidden">
                {SORT_OPTIONS.map(o => (
                  <button
                    key={o.value}
                    onClick={() => { setSort(o.value); setShowSortMenu(false); }}
                    className={`w-full text-left px-4 py-2.5 text-sm hover:bg-secondary transition-colors ${sort === o.value ? 'text-primary font-semibold bg-primary/5' : 'text-gray-700'}`}
                  >
                    {o.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Products grid */}
      {sorted.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">🐾</div>
          <p className="text-gray-400 text-lg">No products found in this category</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {sorted.map(p => <ProductCard key={p.id} product={p} />)}
        </div>
      )}

      {/* Custom case CTA */}
      <div className="mt-16 bg-primary rounded-3xl p-8 text-white text-center">
        <div className="text-4xl mb-3">✨</div>
        <h2 className="text-2xl font-bold mb-2">Don't see your pet breed?</h2>
        <p className="text-green-100 mb-6">Create a fully custom case with your own pet's photo — delivered in 3–5 days.</p>
        <a href="/product/custom-pet-phone-case" className="bg-accent text-white px-8 py-3 rounded-xl font-bold hover:bg-orange-600 transition-colors inline-block">
          Create Custom Case →
        </a>
      </div>
    </div>
  );
}

export default function ProductsPage() {
  return (
    <Suspense fallback={
      <div className="flex justify-center items-center py-20 flex-col gap-4">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-400 text-sm">Loading cases…</p>
      </div>
    }>
      <ProductsContent />
    </Suspense>
  );
}
