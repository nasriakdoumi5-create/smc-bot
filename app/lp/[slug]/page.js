'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { getProductBySlug } from '@/data/products';
import { trackViewContent } from '@/components/MetaPixel';
import { ttqViewContent } from '@/components/TikTokPixel';
import { Shield, Truck, RotateCcw, Star, ChevronDown } from 'lucide-react';

const PHONE_MODELS = ['iPhone 15 Pro', 'iPhone 14 Pro', 'iPhone 13 Pro', 'Samsung S24', 'Samsung S23', 'Other'];

function Stars({ rating = 5, size = 'sm' }) {
  const full = Math.floor(rating);
  return (
    <span className={`text-yellow-400 ${size === 'lg' ? 'text-lg' : 'text-sm'}`}>
      {'★'.repeat(full)}{'☆'.repeat(5 - full)}
    </span>
  );
}

export default function SingleProductLP() {
  const { slug } = useParams();
  const product = getProductBySlug(slug);

  const [model, setModel] = useState(PHONE_MODELS[0]);
  const [modelOpen, setModelOpen] = useState(false);
  const [viewers, setViewers] = useState(0);

  useEffect(() => {
    if (!product) return;
    trackViewContent(product);
    ttqViewContent(product);
    setViewers(product.viewerCount || Math.floor(Math.random() * 15) + 8);
  }, [product?.id]);

  if (!product) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-center px-4">
        <div className="text-6xl mb-4">🐾</div>
        <h1 className="text-2xl font-bold mb-4">Product not found</h1>
        <Link href="/products" className="inline-block bg-primary text-white font-bold px-8 py-4 rounded-2xl">
          Browse All Cases
        </Link>
      </div>
    );
  }

  const savings = product.originalPrice - product.price;
  const savePct = Math.round((savings / product.originalPrice) * 100);
  const ctaHref = `/product/${product.slug}?coupon=PAWS10&model=${encodeURIComponent(model)}`;

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: 'Arial, sans-serif' }}>

      {/* Trust bar */}
      <div className="bg-primary text-white text-center py-2 px-4 text-xs font-semibold tracking-wide">
        🚚 Free EU Shipping · 30-Day Money-Back Guarantee · 5,000+ Happy Customers
      </div>

      {/* Hero — above the fold on all devices */}
      <section className="max-w-5xl mx-auto px-4 py-8 md:py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">

          {/* Product image */}
          <div className="relative">
            {product.badge && (
              <div className="absolute top-4 left-4 z-10 bg-accent text-white text-xs font-bold px-3 py-1.5 rounded-full shadow-lg">
                {product.badge}
              </div>
            )}
            <div className="absolute top-4 right-4 z-10 bg-green-500 text-white text-xs font-bold px-3 py-1.5 rounded-full">
              Save {savePct}%
            </div>
            <img
              src={product.images?.[0] || product.image}
              alt={product.name}
              className="w-full aspect-square object-cover rounded-3xl shadow-2xl"
            />
            {/* Social proof overlay */}
            <div className="absolute bottom-4 left-4 right-4 bg-white/90 backdrop-blur-sm rounded-2xl px-4 py-2.5 flex items-center justify-between shadow-lg">
              <div className="flex items-center gap-1.5">
                <Stars rating={product.rating} />
                <span className="text-xs font-bold text-dark">{product.rating}</span>
                <span className="text-xs text-gray-400">({product.reviewCount} reviews)</span>
              </div>
              <span className="text-xs text-orange-600 font-semibold">🔥 {viewers} viewing now</span>
            </div>
          </div>

          {/* Copy + CTA */}
          <div>
            {/* Emotional hook */}
            <p className="text-accent font-bold text-sm uppercase tracking-widest mb-2">
              {product.category === 'dogs' ? '🐕 For Dog Lovers' : product.category === 'cats' ? '🐈 For Cat Lovers' : '✨ Custom Order'}
            </p>
            <h1 className="text-3xl md:text-4xl font-extrabold text-dark leading-tight mb-3">
              {product.emotionalHook || product.name}
            </h1>
            <p className="text-gray-500 text-base leading-relaxed mb-5">
              {product.emotionalSub || product.description?.slice(0, 120) + '…'}
            </p>

            {/* Price block */}
            <div className="flex items-center gap-3 mb-5">
              <span className="text-4xl font-extrabold text-primary">€{product.price}</span>
              <span className="text-gray-400 line-through text-xl">€{product.originalPrice}</span>
              <span className="bg-red-100 text-red-600 font-bold text-sm px-3 py-1 rounded-full">
                Save €{savings}
              </span>
            </div>

            {/* Coupon callout */}
            <div className="bg-orange-50 border border-orange-200 rounded-xl px-4 py-2.5 mb-5 flex items-center gap-2 text-sm">
              <span className="text-orange-500 font-bold">PAWS10</span>
              <span className="text-orange-700">— extra 10% off applied at checkout</span>
            </div>

            {/* Stock urgency */}
            {product.stock <= 10 && (
              <div className="flex items-center gap-2 mb-4 text-red-600 text-sm font-semibold">
                <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                Only {product.stock} left in stock — order soon!
              </div>
            )}

            {/* Model selector */}
            <div className="mb-4">
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">Select your phone model</label>
              <div className="relative">
                <button
                  onClick={() => setModelOpen(o => !o)}
                  className="w-full flex items-center justify-between border-2 border-gray-200 rounded-xl px-4 py-3 text-sm font-medium bg-white hover:border-primary transition-colors"
                >
                  <span>{model}</span>
                  <ChevronDown className={`w-4 h-4 transition-transform ${modelOpen ? 'rotate-180' : ''}`} />
                </button>
                {modelOpen && (
                  <div className="absolute z-20 top-full left-0 right-0 mt-1 bg-white border-2 border-gray-200 rounded-xl overflow-hidden shadow-xl">
                    {(product.models || PHONE_MODELS).map(m => (
                      <button
                        key={m}
                        onClick={() => { setModel(m); setModelOpen(false); }}
                        className={`w-full text-left px-4 py-2.5 text-sm hover:bg-primary/5 transition-colors ${model === m ? 'bg-primary/10 font-semibold text-primary' : ''}`}
                      >
                        {m}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Main CTA */}
            <Link
              href={ctaHref}
              className="block w-full text-center bg-accent hover:bg-orange-500 text-white text-lg font-extrabold py-4 rounded-2xl shadow-lg hover:shadow-accent/30 transition-all hover:scale-[1.02] mb-3"
            >
              Get Mine Now — €{product.price} 🐾
            </Link>
            <Link
              href={`/products?coupon=PAWS10`}
              className="block w-full text-center border-2 border-gray-200 text-gray-500 text-sm font-semibold py-3 rounded-2xl hover:border-primary hover:text-primary transition-all"
            >
              Browse All Cases
            </Link>

            {/* Trust micro-badges */}
            <div className="grid grid-cols-3 gap-2 mt-4">
              {[
                { icon: Shield, label: '30-Day Returns' },
                { icon: Truck, label: 'Ships in 3–5 Days' },
                { icon: RotateCcw, label: 'Free Exchange' },
              ].map(t => (
                <div key={t.label} className="flex flex-col items-center gap-1 text-center py-2">
                  <t.icon className="w-4 h-4 text-primary" />
                  <span className="text-xs text-gray-500">{t.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Emotional section */}
      <section className="bg-secondary py-12 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-gray-500 text-sm font-semibold uppercase tracking-widest mb-3">Why pet owners love it</p>
          <h2 className="text-2xl md:text-3xl font-extrabold text-dark mb-8">
            {product.description?.split('.')[0]}.
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
            {(product.features || []).slice(0, 4).map((f, i) => (
              <div key={i} className="flex items-start gap-3 bg-white rounded-2xl p-4 shadow-sm">
                <span className="text-green-500 font-bold text-lg flex-shrink-0">✓</span>
                <span className="text-sm text-gray-700">{f}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Reviews */}
      <section className="max-w-5xl mx-auto px-4 py-12">
        <h2 className="text-2xl font-extrabold text-dark text-center mb-8">
          What customers are saying
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {(product.reviews || []).slice(0, 3).map((r, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                  {r.name[0]}
                </div>
                <div>
                  <p className="font-bold text-dark text-sm">{r.name}</p>
                  <p className="text-xs text-gray-400">{r.location}</p>
                </div>
              </div>
              <Stars rating={r.rating} />
              <p className="text-sm text-gray-600 mt-2 leading-relaxed italic">"{r.text}"</p>
              {r.verified && <p className="text-xs text-green-600 font-semibold mt-2">✓ Verified Purchase</p>}
            </div>
          ))}
        </div>
      </section>

      {/* Final CTA sticky bar */}
      <div className="sticky bottom-0 left-0 right-0 z-50 bg-white border-t-2 border-gray-100 shadow-2xl px-4 py-3">
        <div className="max-w-lg mx-auto flex items-center gap-3">
          <div className="flex-1">
            <p className="font-extrabold text-dark text-sm">{product.name}</p>
            <div className="flex items-center gap-2">
              <span className="text-accent font-bold">€{product.price}</span>
              <span className="text-gray-400 line-through text-xs">€{product.originalPrice}</span>
              <Stars rating={product.rating} />
            </div>
          </div>
          <Link
            href={ctaHref}
            className="bg-accent hover:bg-orange-500 text-white font-extrabold px-5 py-3 rounded-2xl text-sm transition-all whitespace-nowrap"
          >
            Get Mine →
          </Link>
        </div>
      </div>

      {/* Footer */}
      <div className="pb-20 bg-white" />
      <footer className="bg-dark py-5 text-center px-4">
        <p className="text-gray-500 text-xs">© {new Date().getFullYear()} PawCase · <a href="mailto:hello@pawcase.eu" className="text-gray-400 hover:text-white transition-colors">hello@pawcase.eu</a></p>
      </footer>
    </div>
  );
}
