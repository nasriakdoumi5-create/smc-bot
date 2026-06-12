'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { trackViewContent } from '@/components/MetaPixel';
import { ttqViewContent } from '@/components/TikTokPixel';

const PRODUCTS = [
  {
    id: '1',
    name: 'Golden Retriever Case',
    price: 22,
    originalPrice: 32,
    image: 'https://picsum.photos/seed/golden1/600/600',
    badge: 'Best Seller',
    stars: 4.9,
    reviews: 312,
    href: '/product/golden-retriever-phone-case',
  },
  {
    id: '3',
    name: 'French Bulldog Case',
    price: 24,
    originalPrice: 34,
    image: 'https://picsum.photos/seed/frenchbull1/600/600',
    badge: 'Popular',
    stars: 4.8,
    reviews: 203,
    href: '/product/french-bulldog-phone-case',
  },
  {
    id: '5',
    name: 'Custom Dog Case',
    price: 35,
    originalPrice: 50,
    image: 'https://picsum.photos/seed/custompet1/600/600',
    badge: 'Your Photo',
    stars: 4.9,
    reviews: 127,
    href: '/product/custom-pet-phone-case',
  },
];

const TRUST_BADGES = [
  { icon: '🚀', title: 'Fast EU Shipping', sub: 'Delivered in 3–5 days' },
  { icon: '↩️', title: '30-Day Returns', sub: 'Hassle-free guarantee' },
  { icon: '🖨️', title: 'Premium Print', sub: 'UV-resistant, lasting quality' },
];

const REVIEWS = [
  { name: 'Sofia M.', location: 'Madrid', text: 'My golden retriever case gets compliments everywhere I go! The quality is incredible.', stars: 5 },
  { name: 'Lucas K.', location: 'Berlin', text: 'Perfect quality. The image is super sharp and the case feels really sturdy. My dog Max approves!', stars: 5 },
  { name: 'Emma V.', location: 'Amsterdam', text: 'Bought as a gift for my sister. She absolutely loved it! Great protection too.', stars: 5 },
];

function Stars({ count = 5 }) {
  return (
    <span className="text-yellow-400 text-sm">
      {'★'.repeat(Math.floor(count))}{'☆'.repeat(5 - Math.floor(count))}
    </span>
  );
}

export default function DogsLandingPage() {
  const [shoppers, setShoppers] = useState(34);

  useEffect(() => {
    trackViewContent({ name: 'Dog Cases Collection', id: 'lp-dogs', price: 22 });
    ttqViewContent({ name: 'Dog Cases Collection', id: 'lp-dogs', price: 22 });
  }, []);

  useEffect(() => {
    const base = Math.floor(Math.random() * 20) + 25;
    setShoppers(base);
    const interval = setInterval(() => {
      setShoppers(n => {
        const delta = Math.random() > 0.5 ? 1 : -1;
        return Math.min(60, Math.max(18, n + delta));
      });
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const CTA_HREF = '/products?category=dogs&coupon=PAWS10';

  return (
    <div className="min-h-screen bg-white font-sans">

      {/* Hero */}
      <section
        className="relative min-h-screen flex flex-col items-center justify-center text-center px-4 py-20 overflow-hidden"
        style={{ background: 'linear-gradient(160deg, #1B4332 0%, #2D6A4F 50%, #52B788 100%)' }}
      >
        {/* Decorative paw prints */}
        <div className="absolute inset-0 pointer-events-none select-none opacity-10 text-white text-6xl flex flex-wrap gap-16 p-10 overflow-hidden" aria-hidden="true">
          {Array.from({ length: 12 }).map((_, i) => (
            <span key={i} style={{ transform: `rotate(${i * 30}deg)` }}>🐾</span>
          ))}
        </div>

        <div className="relative z-10 max-w-3xl mx-auto">
          {/* Urgency badge */}
          <div className="inline-flex items-center gap-2 bg-accent text-white text-sm font-bold px-5 py-2 rounded-full mb-8 shadow-lg animate-pulse">
            <span>⏰</span>
            <span>LIMITED: 30% OFF Today Only — Use Code PAWS10</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-extrabold text-white leading-tight mb-6 tracking-tight">
            Your Dog Deserves to Be on{' '}
            <span className="text-yellow-300">Your Phone</span>{' '}
            Forever
          </h1>

          <p className="text-xl md:text-2xl text-green-100 mb-10 max-w-2xl mx-auto leading-relaxed">
            You reach for your phone 80 times a day. Make every single one of those moments a little brighter — with your dog's face right there with you.
          </p>

          <Link
            href={CTA_HREF}
            className="inline-flex items-center gap-3 bg-accent hover:bg-orange-500 text-white text-xl font-extrabold px-10 py-5 rounded-2xl shadow-2xl transition-all hover:scale-105 hover:shadow-accent/40"
          >
            <span>Get Your Dog's Case</span>
            <span className="text-2xl">→</span>
          </Link>

          <p className="mt-5 text-green-200 text-sm">Free EU shipping on orders €40+ · No subscription · Ships in 3–5 days</p>
        </div>

        {/* Hero product preview */}
        <div className="relative z-10 mt-16 flex gap-4 justify-center flex-wrap">
          {PRODUCTS.map(p => (
            <div key={p.id} className="w-28 h-28 md:w-36 md:h-36 rounded-2xl overflow-hidden shadow-2xl border-2 border-white/30 hover:scale-105 transition-transform">
              <img src={p.image} alt={p.name} className="w-full h-full object-cover" />
            </div>
          ))}
        </div>
      </section>

      {/* Social proof bar */}
      <div className="bg-yellow-400 text-yellow-900 py-3 px-4 text-center font-bold text-sm md:text-base">
        ⭐ 4.9/5 — Over 5,000 Happy Dog Owners Across Europe Love Their PawCase
      </div>

      {/* Urgency live counter */}
      <div className="bg-orange-50 border-b border-orange-100 py-3 px-4 text-center text-sm text-orange-700 font-medium">
        🔥 <strong>{shoppers} people</strong> are shopping right now — don't miss out on the 30% off deal
      </div>

      {/* Product Grid */}
      <section className="max-w-6xl mx-auto px-4 py-20">
        <div className="text-center mb-14">
          <p className="text-accent font-bold text-sm uppercase tracking-widest mb-3">Our Dog Collection</p>
          <h2 className="text-4xl md:text-5xl font-extrabold text-dark mb-4">
            Made for Dog Lovers. Made to Last.
          </h2>
          <p className="text-gray-500 text-lg max-w-xl mx-auto">
            Premium UV-printed phone cases with vivid detail. Slim, protective, and unmistakably you.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {PRODUCTS.map(p => (
            <div key={p.id} className="group bg-white rounded-3xl shadow-lg hover:shadow-2xl transition-all overflow-hidden border border-gray-100">
              <div className="relative aspect-square overflow-hidden bg-secondary">
                {p.badge && (
                  <span className="absolute top-3 left-3 z-10 bg-accent text-white text-xs font-bold px-3 py-1.5 rounded-full shadow">
                    {p.badge}
                  </span>
                )}
                <img
                  src={p.image}
                  alt={p.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
              </div>
              <div className="p-6">
                <h3 className="font-extrabold text-dark text-lg mb-1">{p.name}</h3>
                <div className="flex items-center gap-2 mb-3">
                  <Stars count={p.stars} />
                  <span className="text-xs text-gray-400">({p.reviews})</span>
                </div>
                <div className="flex items-center gap-3 mb-5">
                  <span className="text-2xl font-extrabold text-primary">€{p.price}</span>
                  <span className="text-gray-400 line-through text-base">€{p.originalPrice}</span>
                  <span className="text-xs bg-green-100 text-green-700 font-bold px-2 py-0.5 rounded-full">
                    -{Math.round(100 - (p.price / p.originalPrice) * 100)}%
                  </span>
                </div>
                <Link
                  href={`${p.href}?coupon=PAWS10`}
                  className="block w-full text-center bg-primary hover:bg-primary-dark text-white font-bold py-3.5 rounded-2xl transition-all hover:scale-[1.02] shadow-md"
                >
                  Shop Now
                </Link>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center mt-12">
          <Link
            href={CTA_HREF}
            className="inline-flex items-center gap-2 text-primary font-bold text-lg border-2 border-primary rounded-2xl px-8 py-4 hover:bg-primary hover:text-white transition-all"
          >
            View All Dog Cases <span>→</span>
          </Link>
        </div>
      </section>

      {/* Emotional section */}
      <section
        className="py-20 px-4 text-center"
        style={{ background: 'linear-gradient(135deg, #F5F0E8 0%, #E8F5EE 100%)' }}
      >
        <div className="max-w-3xl mx-auto">
          <div className="text-6xl mb-6">🐕</div>
          <h2 className="text-4xl md:text-5xl font-extrabold text-dark mb-6 leading-tight">
            "Every time I reach for my phone, I see my dog's face."
          </h2>
          <p className="text-gray-600 text-xl mb-8 leading-relaxed">
            That's what thousands of dog owners across Europe say every single day. Your dog is your best friend. They deserve to be with you — everywhere you go.
          </p>
          <Link
            href={CTA_HREF}
            className="inline-flex items-center gap-3 bg-accent hover:bg-orange-500 text-white text-xl font-extrabold px-10 py-5 rounded-2xl shadow-xl transition-all hover:scale-105"
          >
            Get Your Dog's Case — 30% Off Today <span>→</span>
          </Link>
        </div>
      </section>

      {/* Trust Badges */}
      <section className="max-w-5xl mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {TRUST_BADGES.map(b => (
            <div key={b.title} className="flex flex-col items-center text-center bg-white rounded-2xl p-8 shadow-md border border-gray-100">
              <span className="text-4xl mb-4">{b.icon}</span>
              <h3 className="font-extrabold text-dark text-lg mb-1">{b.title}</h3>
              <p className="text-gray-500 text-sm">{b.sub}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Reviews */}
      <section className="bg-secondary py-16 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-3xl md:text-4xl font-extrabold text-dark">What Dog Owners Are Saying</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {REVIEWS.map((r, i) => (
              <div key={i} className="bg-white rounded-2xl p-6 shadow-md">
                <Stars count={r.stars} />
                <p className="text-dark text-sm mt-3 mb-4 leading-relaxed italic">"{r.text}"</p>
                <div className="text-xs text-gray-500 font-medium">— {r.name}, {r.location}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section
        className="py-20 px-4 text-center"
        style={{ background: 'linear-gradient(160deg, #1B4332 0%, #2D6A4F 100%)' }}
      >
        <div className="max-w-2xl mx-auto">
          <div className="text-5xl mb-4">🐾</div>
          <h2 className="text-4xl md:text-5xl font-extrabold text-white mb-5 leading-tight">
            Don't Wait — This Deal Ends Tonight
          </h2>
          <p className="text-green-200 text-lg mb-8">
            Join 5,000+ dog lovers across Europe. 30% off today only with code <strong className="text-yellow-300">PAWS10</strong>.
          </p>
          <Link
            href={CTA_HREF}
            className="inline-flex items-center gap-3 bg-accent hover:bg-orange-500 text-white text-xl font-extrabold px-10 py-5 rounded-2xl shadow-2xl transition-all hover:scale-105"
          >
            Get Your Dog's Case Now <span>→</span>
          </Link>
          <p className="mt-4 text-green-300 text-sm">Free EU shipping · 30-day returns · 5,000+ happy customers</p>
        </div>
      </section>

      {/* Minimal footer */}
      <footer className="bg-dark text-center py-6 px-4">
        <p className="text-gray-500 text-sm">© {new Date().getFullYear()} PawCase — All rights reserved</p>
        <p className="text-gray-600 text-xs mt-1">
          Questions? <a href="mailto:hello@pawcase.eu" className="text-gray-400 hover:text-white transition-colors">hello@pawcase.eu</a>
        </p>
      </footer>
    </div>
  );
}
