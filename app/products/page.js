'use client';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import ProductCard from '../../components/ProductCard';
import { Suspense } from 'react';

const CATEGORIES = [
  {slug:'all',name:'الكل'},
  {slug:'electronics',name:'إلكترونيات'},
  {slug:'clothing',name:'ملابس'},
  {slug:'home',name:'المنزل'},
  {slug:'sports',name:'رياضة'},
  {slug:'books',name:'كتب'},
];

function ProductsContent() {
  const searchParams = useSearchParams();
  const [products, setProducts] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [category, setCategory] = useState(searchParams.get('category') || 'all');
  const [search, setSearch]     = useState(searchParams.get('search') || '');
  const [sort, setSort]         = useState('createdAt');
  const [searchInput, setSearchInput] = useState(searchParams.get('search') || '');

  useEffect(() => {
    fetchProducts();
  }, [category, search, sort]);

  async function fetchProducts() {
    setLoading(true);
    const params = new URLSearchParams();
    if (category !== 'all') params.set('category', category);
    if (search) params.set('search', search);
    params.set('sort', sort);
    const res = await fetch(`/api/products?${params}`);
    const data = await res.json();
    setProducts(data);
    setLoading(false);
  }

  function handleSearch(e) {
    e.preventDefault();
    setSearch(searchInput);
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">جميع المنتجات</h1>
          {!loading && <p className="text-gray-500 text-sm mt-1">{products.length} منتج</p>}
        </div>
        <select value={sort} onChange={e => setSort(e.target.value)} className="input-field w-auto text-sm">
          <option value="createdAt">الأحدث</option>
          <option value="price-asc">السعر: من الأقل</option>
          <option value="price-desc">السعر: من الأعلى</option>
        </select>
      </div>

      {/* Search bar */}
      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <input
          value={searchInput}
          onChange={e => setSearchInput(e.target.value)}
          placeholder="ابحث عن منتج..."
          className="input-field flex-1"
        />
        <button type="submit" className="btn-primary px-6">بحث</button>
        {search && <button type="button" onClick={() => { setSearch(''); setSearchInput(''); }} className="btn-outline px-4">✕</button>}
      </form>

      {/* Category chips */}
      <div className="flex gap-2 flex-wrap mb-6">
        {CATEGORIES.map(c => (
          <button key={c.slug} onClick={() => setCategory(c.slug)}
            className={`px-4 py-2 rounded-full text-sm font-semibold transition-all ${category === c.slug ? 'bg-primary-600 text-white shadow-md' : 'bg-white text-gray-600 hover:bg-primary-50 hover:text-primary-600 border border-gray-200'}`}>
            {c.name}
          </button>
        ))}
      </div>

      {/* Products grid */}
      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="aspect-square bg-gray-200 rounded-t-2xl" />
              <div className="p-3 space-y-2">
                <div className="h-3 bg-gray-200 rounded w-1/2" />
                <div className="h-4 bg-gray-200 rounded" />
                <div className="h-4 bg-gray-200 rounded w-3/4" />
                <div className="h-8 bg-gray-200 rounded-xl" />
              </div>
            </div>
          ))}
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <div className="text-6xl mb-4">🔍</div>
          <p className="text-lg font-medium">لا توجد منتجات</p>
          <p className="text-sm mt-1">جرب البحث بكلمات مختلفة</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {products.map(p => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </div>
  );
}

export default function ProductsPage() {
  return (
    <Suspense fallback={<div className="flex justify-center py-20"><div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" /></div>}>
      <ProductsContent />
    </Suspense>
  );
}
