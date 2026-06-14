'use client';
import Link from 'next/link';
import { getFeaturedProducts, products } from '@/data/products';
import ProductCard from '@/components/ProductCard';
import NewsletterSection from '@/components/NewsletterSection';
import ProcessShowcase from '@/components/ProcessShowcase';
import { useState, useEffect } from 'react';

const featured = getFeaturedProducts().slice(0, 4);

function RecentlyViewed() {
  const [viewed, setViewed] = useState([]);
  useEffect(() => {
    try {
      const ids = JSON.parse(localStorage.getItem('pawcase-recent') || '[]');
      const viewedProducts = ids.map(id => products.find(p => p.id === id)).filter(Boolean).slice(0, 4);
      setViewed(viewedProducts);
    } catch {}
  }, []);
  if (viewed.length < 2) return null;
  return (
    <section className="max-w-6xl mx-auto px-4 py-12">
      <h2 className="text-2xl font-bold mb-6">Recently Viewed</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {viewed.map(p => <ProductCard key={p.id} product={p} />)}
      </div>
    </section>
  );
}

export default function HomePage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-primary text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="text-6xl mb-4">🐾</div>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-6">
            <div className="inline-flex items-center gap-2 bg-white/20 rounded-full px-4 py-2 text-sm font-medium">
              <span className="text-yellow-300">⭐⭐⭐⭐⭐</span>
              <span>4.9/5 from 5,000+ pet lovers</span>
            </div>
            <div className="inline-flex items-center gap-2 bg-white/15 rounded-full px-4 py-1.5 text-sm">
              <span className="text-green-300">✓</span>
              <span>Digital preview within 24h · Free EU shipping on €40+</span>
            </div>
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold mb-6 leading-tight">
            Carry Your Best Friend<br />
            <span className="text-accent">Everywhere You Go</span>
          </h1>
          <p className="text-xl text-green-100 mb-10 max-w-2xl mx-auto">
            Turn your pet's love into wearable art. Premium cases that protect your phone and show the world who you love most.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/products" className="bg-accent text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-orange-600 transition-colors shadow-lg">
              Shop Now →
            </Link>
            <Link href="/product/custom-pet-phone-case" className="border-2 border-white text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-white hover:text-primary transition-colors">
              Custom Case ✨
            </Link>
          </div>
          <p className="text-green-200 text-sm mt-5">🚚 Free shipping on orders over €40 · 30-day returns</p>
        </div>
      </section>

      {/* Stats bar */}
      <section className="bg-dark text-white py-6">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {[
            { value: '5,000+', label: 'Orders Shipped' },
            { value: '4.9★', label: 'Average Rating' },
            { value: '30-Day', label: 'Returns Policy' },
            { value: 'EU Shipped', label: '3–5 Business Days' },
          ].map(s => (
            <div key={s.label}>
              <p className="text-2xl font-extrabold text-accent">{s.value}</p>
              <p className="text-gray-400 text-xs mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Trust badges */}
      <section className="bg-white py-8 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {[
            { icon: '🚚', title: 'Free Shipping', sub: 'On orders over €40' },
            { icon: '🔄', title: '30-Day Returns', sub: 'Hassle-free returns' },
            { icon: '🔒', title: 'Secure Payment', sub: 'Visa, MC, PayPal, Apple Pay' },
            { icon: '🇪🇺', title: 'Ships from EU', sub: '3-5 business days' },
          ].map(b => (
            <div key={b.title} className="flex flex-col items-center gap-1">
              <span className="text-2xl">{b.icon}</span>
              <p className="font-semibold text-dark text-sm">{b.title}</p>
              <p className="text-xs text-gray-500">{b.sub}</p>
            </div>
          ))}
        </div>
      </section>

      <ProcessShowcase />

      {/* As Seen In */}
      <section className="bg-secondary py-8">
        <div className="max-w-5xl mx-auto px-4 text-center">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-5">As featured in</p>
          <div className="flex flex-wrap items-center justify-center gap-8 opacity-60">
            {['PetWorld Magazine', 'DogLovers EU', 'The Pet Blog', 'CatFancy', 'PetStyle Weekly'].map(m => (
              <span key={m} className="text-sm font-bold text-gray-500 italic">{m}</span>
            ))}
          </div>
        </div>
      </section>

      {/* Browse by category */}
      <section className="max-w-5xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-2">Shop by Category</h2>
        <p className="text-center text-gray-500 mb-10">Find the perfect case for your pet lover</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { slug: 'dogs', name: 'Dog Lovers', emoji: '🐕', desc: 'Golden Retrievers, Bulldogs & more', color: 'bg-amber-50 border-amber-200', count: products.filter(p=>p.category==='dogs').length },
            { slug: 'cats', name: 'Cat Lovers', emoji: '🐈', desc: 'Black cats, tabby cats & more', color: 'bg-purple-50 border-purple-200', count: products.filter(p=>p.category==='cats').length },
            { slug: 'custom', name: 'Custom Cases', emoji: '✨', desc: 'Upload your own pet photo', color: 'bg-green-50 border-green-200', count: 'Unlimited' },
          ].map(c => (
            <Link key={c.slug} href={`/products?cat=${c.slug}`} className={`${c.color} border-2 rounded-2xl p-8 text-center hover:shadow-md transition-all hover:-translate-y-1`}>
              <div className="text-5xl mb-3">{c.emoji}</div>
              <h3 className="text-xl font-bold mb-1">{c.name}</h3>
              <p className="text-gray-500 text-sm mb-2">{c.desc}</p>
              <span className="text-xs font-semibold text-primary">{c.count} designs →</span>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured products */}
      <section className="bg-white py-16">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-3xl font-bold">Best Sellers</h2>
            <div className="hidden sm:flex items-center gap-2 text-sm text-orange-500 font-medium bg-orange-50 px-3 py-1.5 rounded-full">
              🔥 Selling fast today
            </div>
          </div>
          <p className="text-gray-500 mb-10">Our most loved designs by pet lovers across Europe</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featured.map(p => <ProductCard key={p.id} product={p} />)}
          </div>
          <div className="text-center mt-10">
            <Link href="/products" className="btn-outline">View All Products</Link>
          </div>
        </div>
      </section>

      {/* Turn Your Pet Into Art */}
      <section className="max-w-5xl mx-auto px-4 py-16">
        <div className="bg-primary rounded-3xl p-10 text-white grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
          <div>
            <div className="text-5xl mb-4">🐾✨</div>
            <h2 className="text-3xl font-extrabold mb-4">Turn Your Pet Into Art</h2>
            <p className="text-green-100 mb-6">Every pet has a face that deserves to be celebrated. Upload your favourite photo and we'll transform it into a stunning, one-of-a-kind phone case that's completely yours.</p>
            <ul className="space-y-2 text-green-100 text-sm mb-8">
              <li className="flex items-center gap-2">✓ Digital mockup within 24 hours</li>
              <li className="flex items-center gap-2">✓ Printed in vivid, UV-resistant detail</li>
              <li className="flex items-center gap-2">✓ Ships in 3–5 business days</li>
              <li className="flex items-center gap-2">✓ The perfect personalised gift</li>
            </ul>
            <Link href="/product/custom-pet-phone-case" className="bg-accent text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-orange-600 transition-colors inline-block">
              Create My Custom Case
            </Link>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {['pet1','pet2','pet3','pet4'].map((seed, i) => (
              <div key={i} className="rounded-2xl overflow-hidden aspect-square">
                <img src={`https://picsum.photos/seed/${seed}/300/300`} alt={`Custom pet case example ${i + 1}`} className="w-full h-full object-cover" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="bg-white py-16">
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-2">What Pet Lovers Say</h2>
          <p className="text-center text-gray-500 mb-10">Over 5,000 happy customers across Europe</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { name: 'Sofia M.', location: 'Madrid, Spain', text: 'My golden retriever case gets compliments everywhere I go! The print quality is amazing and it arrived in just 4 days.', stars: 5 },
              { name: 'Lucas K.', location: 'Berlin, Germany', text: "Ordered a custom case with my cat's photo. The result was incredible — super sharp and detailed. Will order again!", stars: 5 },
              { name: 'Emma V.', location: 'Amsterdam, Netherlands', text: 'Adorable design, perfect protection. Already ordered a second one as a gift for my sister. She loved it!', stars: 5 },
            ].map(t => (
              <div key={t.name} className="card p-6">
                <div className="flex text-yellow-400 mb-3 text-lg">{'★'.repeat(t.stars)}</div>
                <p className="text-gray-700 text-sm mb-4 italic">"{t.text}"</p>
                <div>
                  <p className="font-semibold text-dark text-sm">{t.name}</p>
                  <p className="text-xs text-gray-400">{t.location}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Real PawCase Customers — UGC Gallery */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center mb-10">
          <span className="inline-block bg-accent/10 text-accent text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-widest mb-3">
            Real Customers
          </span>
          <h2 className="text-3xl font-bold">Shared With Love on Instagram</h2>
          <p className="text-center text-gray-500 mt-2">Join thousands of pet lovers showing off their PawCase every day</p>
        </div>
        <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
          {[
            { seed: 'customer1', handle: '@sofiapets', caption: 'My golden boy on my phone 🐕', stars: 5 },
            { seed: 'customer2', handle: '@lucas.k', caption: 'Custom case came out perfect! ✨', stars: 5 },
            { seed: 'customer3', handle: '@emmav_nl', caption: 'The best gift for cat mums 🐈', stars: 5 },
            { seed: 'customer4', handle: '@mariedparis', caption: 'Obsessed with my frenchie case 💕', stars: 5 },
            { seed: 'customer5', handle: '@annasthlm', caption: 'My tabby is famous now 🐾', stars: 5 },
            { seed: 'customer6', handle: '@jamesr_uk', caption: 'Quality is insane, worth every €', stars: 5 },
            { seed: 'ugc1', handle: '@petlover_de', caption: 'Second case for my sister 🎁', stars: 5 },
            { seed: 'ugc2', handle: '@catlady_be', caption: 'Everyone asks where I got this 😍', stars: 5 },
            { seed: 'ugc3', handle: '@dogdad_es', caption: 'Ships so fast, I was shocked', stars: 5 },
            { seed: 'ugc4', handle: '@pawmom_fr', caption: 'The colours are unreal 🎨', stars: 5 },
            { seed: 'ugc5', handle: '@petcase_it', caption: 'Already ordering a third one', stars: 5 },
            { seed: 'ugc6', handle: '@goldenlife', caption: 'Best purchase of 2025 🏆', stars: 5 },
          ].map((c, i) => (
            <div key={i} className="rounded-xl overflow-hidden relative group cursor-pointer aspect-square">
              <img
                src={`https://picsum.photos/seed/${c.seed}/400/400`}
                alt={c.caption}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-2.5">
                <p className="text-white text-xs font-bold">{c.handle}</p>
                <p className="text-white/80 text-xs leading-tight">{c.caption}</p>
                <p className="text-yellow-400 text-xs mt-0.5">{'★'.repeat(c.stars)}</p>
              </div>
              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="bg-white/90 rounded-full p-1">
                  <svg className="w-3 h-3 text-pink-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="text-center mt-8">
          <p className="text-gray-500 text-sm">Tag us <span className="font-semibold text-primary">@pawcase.eu</span> for a chance to be featured</p>
        </div>
      </section>

      {/* Recently Viewed */}
      <RecentlyViewed />

      <NewsletterSection />
    </>
  );
}
