'use client';
import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { products, categories } from '@/data/products';
import ProductCard from '@/components/ProductCard';

function ProductsContent() {
  const searchParams = useSearchParams();
  const [activeCategory, setActiveCategory] = useState('all');

  useEffect(() => {
    const cat = searchParams.get('cat');
    if (cat) setActiveCategory(cat);
  }, [searchParams]);

  const filtered = activeCategory === 'all' ? products : products.filter(p => p.category === activeCategory);

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold mb-3">Our Phone Cases</h1>
        <p className="text-gray-500">Premium custom cases for every pet lover</p>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-3 justify-center mb-10">
        {[{ id: 'all', name: 'All Cases', icon: '🐾' }, ...categories].map(cat => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`px-5 py-2.5 rounded-xl font-medium text-sm transition-all ${
              activeCategory === cat.id
                ? 'bg-primary text-white shadow-md'
                : 'bg-white text-dark hover:bg-secondary border border-gray-200'
            }`}
          >
            {cat.icon} {cat.name}
          </button>
        ))}
      </div>

      {/* Products grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-20 text-gray-400">No products found</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map(p => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </div>
  );
}

export default function ProductsPage() {
  return (
    <Suspense fallback={
      <div className="flex justify-center py-20">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    }>
      <ProductsContent />
    </Suspense>
  );
}
