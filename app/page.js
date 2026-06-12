'use client';
import Link from 'next/link';
import { getFeaturedProducts } from '@/data/products';
import ProductCard from '@/components/ProductCard';
import NewsletterSection from '@/components/NewsletterSection';

const featured = getFeaturedProducts().slice(0, 4);

export default function HomePage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-primary text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="text-6xl mb-4">🐾</div>
          <div className="inline-flex items-center gap-2 bg-white/20 rounded-full px-4 py-2 text-sm font-medium mb-6">
            <span className="text-yellow-300">⭐⭐⭐⭐⭐</span>
            <span>4.9/5 from 5,000+ happy pet lovers across Europe</span>
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
            { icon: '🔒', title: 'Secure Payment', sub: 'SSL encrypted checkout' },
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

      {/* Browse by category */}
      <section className="max-w-5xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-2">Shop by Category</h2>
        <p className="text-center text-gray-500 mb-10">Find the perfect case for your pet lover</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { slug: 'dogs', name: 'Dog Lovers', emoji: '🐕', desc: 'Golden Retrievers, Bulldogs & more', color: 'bg-amber-50 border-amber-200' },
            { slug: 'cats', name: 'Cat Lovers', emoji: '🐈', desc: 'Black cats, tabby cats & more', color: 'bg-purple-50 border-purple-200' },
            { slug: 'custom', name: 'Custom Cases', emoji: '✨', desc: 'Upload your own pet photo', color: 'bg-green-50 border-green-200' },
          ].map(c => (
            <Link key={c.slug} href={`/products?cat=${c.slug}`} className={`${c.color} border-2 rounded-2xl p-8 text-center hover:shadow-md transition-all hover:-translate-y-1`}>
              <div className="text-5xl mb-3">{c.emoji}</div>
              <h3 className="text-xl font-bold mb-1">{c.name}</h3>
              <p className="text-gray-500 text-sm">{c.desc}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured products */}
      <section className="bg-white py-16">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-2">Best Sellers</h2>
          <p className="text-center text-gray-500 mb-10">Our most loved designs by pet lovers across Europe</p>
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
            {[
              'https://picsum.photos/seed/pet1/300/300',
              'https://picsum.photos/seed/pet2/300/300',
              'https://picsum.photos/seed/pet3/300/300',
              'https://picsum.photos/seed/pet4/300/300',
            ].map((src, i) => (
              <div key={i} className="rounded-2xl overflow-hidden aspect-square">
                <img src={src} alt={`Custom pet case example ${i + 1}`} className="w-full h-full object-cover" />
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

      {/* Real PawCase Customers */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-2">See Real PawCase Customers</h2>
        <p className="text-center text-gray-500 mb-10">Thousands of pet lovers showing off their cases every day</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {[
            { seed: 'customer1', name: 'Sofia M.', caption: 'My golden boy on my phone 🐕' },
            { seed: 'customer2', name: 'Lucas K.', caption: 'Custom case came out perfect! ✨' },
            { seed: 'customer3', name: 'Emma V.', caption: 'The best gift for cat mums 🐈' },
            { seed: 'customer4', name: 'Marie D.', caption: 'Obsessed with my frenchie case 💕' },
            { seed: 'customer5', name: 'Anna S.', caption: 'My tabby is famous now 🐾' },
            { seed: 'customer6', name: 'James R.', caption: 'Quality is insane, worth every €' },
          ].map((c, i) => (
            <div key={i} className="card overflow-hidden group">
              <div className="relative overflow-hidden">
                <img
                  src={`https://picsum.photos/seed/${c.seed}/400/400`}
                  alt={c.caption}
                  className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-3">
                  <p className="text-white text-xs font-medium">{c.caption}</p>
                </div>
              </div>
              <div className="p-3">
                <p className="text-sm font-semibold text-dark">{c.name}</p>
                <p className="text-xs text-yellow-400">★★★★★</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <NewsletterSection />
    </>
  );
}
