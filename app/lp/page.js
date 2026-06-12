'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
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
    tag: 'Dogs',
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
    tag: 'Dogs',
  },
  {
    id: '2',
    name: 'Black Cat Case',
    price: 22,
    originalPrice: 32,
    image: 'https://picsum.photos/seed/blackcat1/600/600',
    badge: 'Top Rated',
    stars: 4.9,
    reviews: 287,
    href: '/product/black-cat-phone-case',
    tag: 'Cats',
  },
  {
    id: '5',
    name: 'Custom Pet Case',
    price: 35,
    originalPrice: 50,
    image: 'https://picsum.photos/seed/custompet1/600/600',
    badge: 'Your Photo',
    stars: 4.9,
    reviews: 270,
    href: '/product/custom-pet-phone-case',
    tag: 'Custom',
  },
];

const TRUST_BADGES = [
  { icon: '🚀', title: 'Fast EU Shipping', sub: 'Delivered in 3–5 days' },
  { icon: '↩️', title: '30-Day Returns', sub: 'Hassle-free guarantee' },
  { icon: '🖨️', title: 'Premium Print', sub: 'UV-resistant, lasting quality' },
  { icon: '💳', title: 'Secure Checkout', sub: 'Stripe-powered, always safe' },
];

const REVIEWS = [
  { name: 'Sofia M.', location: 'Madrid', text: 'I carry my golden retriever case everywhere. People constantly ask where I got it!', stars: 5 },
  { name: 'Camille D.', location: 'Paris', text: 'My cat Luna is officially on my phone now. Absolutely gorgeous print quality.', stars: 5 },
  { name: 'Marco F.', location: 'Milan', text: 'Ordered the custom case with my own photo — arrived in 4 days and looks incredible.', stars: 5 },
  { name: 'Lucas K.', location: 'Berlin', text: 'The case is slim, the protection is solid, and my dog Max is immortalised on my phone.', stars: 5 },
];

function Stars({ count = 5 }) {
  return (
    <span className="text-yellow-400 text-sm">
      {'★'.repeat(Math.floor(count))}{'☆'.repeat(5 - Math.floor(count))}
    </span>
  );
}

export default function GeneralLandingPage() {
  const [shoppers, setShoppers] = useState(41);

  useEffect(() => {
    trackViewContent({ name: 'Pet Cases Collection', id: 'lp-general', price: 22 });
    ttqViewContent({ name: 'Pet Cases Collection', id: 'lp-general', price: 22 });
  }, []);

  useEffect(() => {
    const base = Math.floor(Math.random() * 25) + 30;
    setShoppers(base);
    const interval = setInterval(() => {
      setShoppers(n => {
        const delta = Math.random() > 0.5 ? 1 : -1;
        return Math.min(70, Math.max(20, n + delta));
      });
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const CTA_HREF = '/products?coupon=PAWS10';

  return (
    <div className="min-h-screen bg-white font-sans">

      {/* Hero */}
      <section
        className="relative min-h-screen flex flex-col items-center justify-center text-center px-4 py-20 overflow-hidden"
        style={{ background: 'linear-gradient(160deg, #1B4332 0%, #2D6A4F 45%, #52B788 100%)' }}
      >
        {/* Decorative paw prints */}
        <div
          className="absolute inset-0 pointer-events-none select-none opacity-10 text-white text-6xl flex flex-wrap gap-16 p-10 overflow-hidden"
          aria-hidden="true"
        >
          {Array.from({ length: 12 }).map((_, i) => (
            <span key={i} style={{ transform: `rotate(${i * 30}deg)` }}>🐾</span>
          ))}
        </div>

        <div className="relative z-10 max-w-4xl mx-auto">
          {/* Urgency badge */}
          <div className="inline-flex items-center gap-2 bg-accent text-white text-sm font-bold px-5 py-2 rounded-full mb-8 shadow-lg animate-pulse">
            <span>⏰</span>
            <span>LIMITED: 30% OFF Today Only — Use Code PAWS10</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-extrabold text-white leading-tight mb-6 tracking-tight">
            Turn Your Pet Into Art{' '}
            <span className="text-yellow-300">That Goes Everywhere</span>{' '}
            You Do
          </h1>

          <p className="text-xl md:text-2xl text-green-100 mb-10 max-w-2xl mx-auto leading-relaxed">
            Your pet is your world. Now they can live on the one thing you never put down — your phone. Premium UV-printed cases, shipped across Europe in 3–5 days.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
            <Link
              href={CTA_HREF}
              className="inline-flex items-center justify-center gap-3 bg-accent hover:bg-orange-500 text-white text-xl font-extrabold px-10 py-5 rounded-2xl shadow-2xl transition-all hover:scale-105 hover:shadow-accent/40"
            >
              <span>Shop All Pet Cases</span>
              <span className="text-2xl">→</span>
            </Link>
            <Link
              href="/products?category=dogs&coupon=PAWS10"
              className="inline-flex items-center justify-center gap-2 bg-white/15 hover:bg-white/25 text-white text-lg font-bold px-8 py-5 rounded-2xl border border-white/30 transition-all hover:scale-105 backdrop-blur-sm"
            >
              <span>🐕</span> Dogs
            </Link>
            <Link
              href="/products?category=cats&coupon=PAWS10"
              className="inline-flex items-center justify-center gap-2 bg-white/15 hover:bg-white/25 text-white text-lg font-bold px-8 py-5 rounded-2xl border border-white/30 transition-all hover:scale-105 backdrop-blur-sm"
            >
              <span>🐈</span> Cats
            </Link>
          </div>

          <p className="text-green-200 text-sm">Free EU shipping on orders €40+ · No subscription · Ships in 3–5 days</p>
        </div>

        {/* Hero product preview */}
        <div className="relative z-10 mt-16 flex gap-4 justify-center flex-wrap">
          {PRODUCTS.map(p => (
            <div
              key={p.id}
              className="w-24 h-24 md:w-32 md:h-32 rounded-2xl overflow-hidden shadow-2xl border-2 border-white/30 hover:scale-105 transition-transform"
            >
              <img src={p.image} alt={p.name} className="w-full h-full object-cover" />
            </div>
          ))}
        </div>
      </section>

      {/* Social proof bar */}
      <div className="bg-yellow-400 text-yellow-900 py-3 px-4 text-center font-bold text-sm md:text-base">
        ⭐ 4.9/5 — Over 5,000 Happy Pet Owners Across Europe Love Their PawCase
      </div>

      {/* Urgency live counter */}
      <div className="bg-orange-50 border-b border-orange-100 py-3 px-4 text-center text-sm text-orange-700 font-medium">
        🔥 <strong>{shoppers} people</strong> are shopping right now — don't miss out on the 30% off deal
      </div>

      {/* As seen in / Brand trust (decorative) */}
      <div className="border-b border-gray-100 py-8 px-4">
        <p className="text-center text-xs text-gray-400 uppercase tracking-widest mb-5 font-semibold">Trusted by pet lovers across</p>
        <div className="flex flex-wrap justify-center gap-8 items-center opacity-50">
          {['🇫🇷 France', '🇩🇪 Germany', '🇪🇸 Spain', '🇳🇱 Netherlands', '🇮🇹 Italy', '🇸🇪 Sweden', '🇵🇹 Portugal'].map(country => (
            <span key={country} className="text-sm font-semibold text-gray-600">{country}</span>
          ))}
        </div>
      </div>

      {/* Featured Products */}
      <section className="max-w-6xl mx-auto px-4 py-20">
        <div className="text-center mb-14">
          <p className="text-accent font-bold text-sm uppercase tracking-widest mb-3">Featured Collection</p>
          <h2 className="text-4xl md:text-5xl font-extrabold text-dark mb-4">
            Your Pet. Your Phone. Your Story.
          </h2>
          <p className="text-gray-500 text-lg max-w-xl mx-auto">
            Choose from our bestsellers or upload your own photo for a fully custom case. Every order ships from the EU.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          {PRODUCTS.map(p => (
            <div
              key={p.id}
              className="group bg-white rounded-3xl shadow-lg hover:shadow-2xl transition-all overflow-hidden border border-gray-100"
            >
              <div className="relative aspect-square overflow-hidden bg-secondary">
                {p.badge && (
                  <span className="absolute top-3 left-3 z-10 bg-accent text-white text-xs font-bold px-3 py-1.5 rounded-full shadow">
                    {p.badge}
                  </span>
                )}
                <span className="absolute top-3 right-3 z-10 bg-white/80 text-gray-600 text-xs font-semibold px-2 py-1 rounded-full">
                  {p.tag}
                </span>
                <img
                  src={p.image}
                  alt={p.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
              </div>
              <div className="p-5">
                <h3 className="font-extrabold text-dark text-base mb-1">{p.name}</h3>
                <div className="flex items-center gap-1.5 mb-3">
                  <Stars count={p.stars} />
                  <span className="text-xs text-gray-400">({p.reviews})</span>
                </div>
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xl font-extrabold text-primary">€{p.price}</span>
                  <span className="text-gray-400 line-through text-sm">€{p.originalPrice}</span>
                  <span className="text-xs bg-green-100 text-green-700 font-bold px-2 py-0.5 rounded-full">
                    -{Math.round(100 - (p.price / p.originalPrice) * 100)}%
                  </span>
                </div>
                <Link
                  href={`${p.href}?coupon=PAWS10`}
                  className="block w-full text-center bg-primary hover:bg-primary-dark text-white font-bold py-3 rounded-2xl transition-all hover:scale-[1.02] shadow-md text-sm"
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
            View Full Collection <span>→</span>
          </Link>
        </div>
      </section>

      {/* How it works */}
      <section
        className="py-20 px-4"
        style={{ background: 'linear-gradient(135deg, #F5F0E8 0%, #E8F5EE 100%)' }}
      >
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-accent font-bold text-sm uppercase tracking-widest mb-3">Simple as 1-2-3</p>
            <h2 className="text-4xl md:text-5xl font-extrabold text-dark mb-4">
              How PawCase Works
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: '01', icon: '🛍️', title: 'Choose Your Case', desc: 'Pick from our curated dog and cat designs — or upload your own pet photo for a fully personalised case.' },
              { step: '02', icon: '🎨', title: 'We Print It for You', desc: 'Our UV-resistant printing process captures every detail. Each case is made to order, just for you.' },
              { step: '03', icon: '📦', title: 'Delivered to Your Door', desc: 'Fast EU shipping in 3–5 business days. Your pet in your hands in less than a week.' },
            ].map(item => (
              <div key={item.step} className="bg-white rounded-3xl p-8 shadow-md border border-gray-100 text-center">
                <div className="text-xs font-black text-accent tracking-widest mb-3 uppercase">Step {item.step}</div>
                <div className="text-5xl mb-4">{item.icon}</div>
                <h3 className="font-extrabold text-dark text-xl mb-3">{item.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Emotional mid-page CTA */}
      <section className="py-20 px-4 text-center bg-white">
        <div className="max-w-3xl mx-auto">
          <div className="text-6xl mb-6">🐾</div>
          <h2 className="text-4xl md:text-5xl font-extrabold text-dark mb-6 leading-tight">
            "The best gift I ever gave myself — and my pet."
          </h2>
          <p className="text-gray-600 text-xl mb-8 leading-relaxed">
            You check your phone over 80 times a day. Every single time, your pet is right there. That's not just a case — that's a daily reminder of unconditional love.
          </p>
          <Link
            href={CTA_HREF}
            className="inline-flex items-center gap-3 bg-accent hover:bg-orange-500 text-white text-xl font-extrabold px-10 py-5 rounded-2xl shadow-xl transition-all hover:scale-105"
          >
            Get Your Pet's Case — 30% Off <span>→</span>
          </Link>
        </div>
      </section>

      {/* Trust Badges */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
          {TRUST_BADGES.map(b => (
            <div
              key={b.title}
              className="flex flex-col items-center text-center bg-white rounded-2xl p-6 shadow-md border border-gray-100"
            >
              <span className="text-3xl mb-3">{b.icon}</span>
              <h3 className="font-extrabold text-dark text-sm mb-1">{b.title}</h3>
              <p className="text-gray-500 text-xs">{b.sub}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Reviews */}
      <section className="bg-secondary py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-10">
            <p className="text-accent font-bold text-sm uppercase tracking-widest mb-3">Real Reviews</p>
            <h2 className="text-3xl md:text-4xl font-extrabold text-dark">What Our Customers Say</h2>
            <p className="text-gray-500 mt-2">5,000+ happy pet owners across Europe</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-5">
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
            Join 5,000+ pet lovers across Europe. 30% off today only with code{' '}
            <strong className="text-yellow-300">PAWS10</strong>.
          </p>
          <Link
            href={CTA_HREF}
            className="inline-flex items-center gap-3 bg-accent hover:bg-orange-500 text-white text-xl font-extrabold px-10 py-5 rounded-2xl shadow-2xl transition-all hover:scale-105"
          >
            Shop All Pet Cases Now <span>→</span>
          </Link>
          <p className="mt-4 text-green-300 text-sm">Free EU shipping · 30-day returns · 5,000+ happy customers</p>
        </div>
      </section>

      {/* Minimal footer */}
      <footer className="bg-dark text-center py-6 px-4">
        <p className="text-gray-500 text-sm">© {new Date().getFullYear()} PawCase — All rights reserved</p>
        <p className="text-gray-600 text-xs mt-1">
          Questions?{' '}
          <a href="mailto:hello@pawcase.eu" className="text-gray-400 hover:text-white transition-colors">
            hello@pawcase.eu
          </a>
        </p>
      </footer>
    </div>
  );
}
