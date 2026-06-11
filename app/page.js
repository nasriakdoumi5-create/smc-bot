import Link from 'next/link';
import { getFeaturedProducts } from '@/data/products';
import ProductCard from '@/components/ProductCard';
import NewsletterSection from '@/components/NewsletterSection';

export const metadata = {
  title: 'PawCase — Custom Pet Phone Cases for Dog & Cat Lovers',
  description: 'Premium phone cases with adorable dog and cat designs. Custom pet photo cases. Ships from EU in 3-5 days.',
};

export default function HomePage() {
  const featured = getFeaturedProducts().slice(0, 4);
  return (
    <>
      {/* Hero */}
      <section className="bg-primary text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="text-6xl mb-6">🐾</div>
          <h1 className="text-4xl md:text-6xl font-extrabold mb-6 leading-tight">
            Cases That Show Your<br />
            <span className="text-accent">Love for Your Pet</span>
          </h1>
          <p className="text-xl text-green-100 mb-10 max-w-2xl mx-auto">
            Premium custom phone cases for dog and cat lovers. Made with love, shipped from Europe in 3–5 days.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/products" className="bg-accent text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-orange-600 transition-colors shadow-lg">
              Shop Now
            </Link>
            <Link href="/product/custom-pet-phone-case" className="border-2 border-white text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-white hover:text-primary transition-colors">
              Custom Case →
            </Link>
          </div>
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

      {/* Testimonials */}
      <section className="max-w-5xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-2">What Pet Lovers Say</h2>
        <p className="text-center text-gray-500 mb-10">Over 5,000 happy customers across Europe</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { name: 'Sofia M.', location: 'Madrid, Spain', text: 'My golden retriever case gets compliments everywhere I go! The print quality is amazing and it arrived in just 4 days.', stars: 5 },
            { name: 'Lucas K.', location: 'Berlin, Germany', text: "Ordered a custom case with my cat's photo. The result was incredible — super sharp and detailed. Will order again!", stars: 5 },
            { name: 'Emma V.', location: 'Amsterdam, Netherlands', text: 'Adorable design, perfect protection. Already ordered a second one as a gift for my sister. She loved it!', stars: 5 },
          ].map(t => (
            <div key={t.name} className="card p-6">
              <div className="flex text-yellow-400 mb-3">{Array(t.stars).fill('⭐').join('')}</div>
              <p className="text-gray-700 text-sm mb-4 italic">"{t.text}"</p>
              <div>
                <p className="font-semibold text-dark text-sm">{t.name}</p>
                <p className="text-xs text-gray-400">{t.location}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <NewsletterSection />
    </>
  );
}
