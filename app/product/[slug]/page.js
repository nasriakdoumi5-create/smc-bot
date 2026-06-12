'use client';
import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getProductBySlug, products } from '@/data/products';
import { useCart } from '@/context/CartContext';
import ProductCard from '@/components/ProductCard';
import StarRating from '@/components/StarRating';
import TrustBadges from '@/components/TrustBadges';
import BundleOffer from '@/components/BundleOffer';
import StickyATC from '@/components/StickyATC';
import RecentPurchaseNotification from '@/components/RecentPurchaseNotification';
import WishlistButton from '@/components/WishlistButton';
import { ShoppingCart, Zap, CheckCircle, Upload, Users, Shield, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react';
import Link from 'next/link';

const faqs = [
  { q: 'How long does delivery take?', a: '3–5 business days EU-wide via Printful. Express options available at checkout.' },
  { q: 'Will the print fade?', a: 'No — we use UV-resistant inks and a premium coating process. Your print will stay vibrant for years of daily use.' },
  { q: "What if it doesn't fit my phone?", a: "Select your exact model from the dropdown before ordering. If there's any issue, our 30-day hassle-free return policy has you covered." },
  { q: 'Can I see a preview of my custom case?', a: "We'll send you a digital mockup within 24 hours of receiving your photo. We won't print until you approve it." },
  { q: 'Is it compatible with wireless charging?', a: 'Yes — all our cases are Qi wireless charging compatible. No need to remove the case to charge.' },
];

export default function ProductPage() {
  const { slug } = useParams();
  const router = useRouter();
  const product = getProductBySlug(slug);

  const [selectedModel, setSelectedModel] = useState(product ? product.models[0] : '');
  const [selectedImg, setSelectedImg] = useState(0);
  const [photoFile, setPhotoFile] = useState(null);
  const [added, setAdded] = useState(false);
  const [openFaq, setOpenFaq] = useState(null);
  const { addToCart, addToRecentlyViewed } = useCart();

  useEffect(() => {
    if (product) {
      addToRecentlyViewed(product.id);
    }
  }, [product ? product.id : null]);

  if (!product) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <div className="text-6xl mb-4">🐾</div>
        <h1 className="text-2xl font-bold mb-4">Product not found</h1>
        <Link href="/products" className="btn-primary">Browse Products</Link>
      </div>
    );
  }

  const discount = Math.round((1 - product.price / product.originalPrice) * 100);
  const related = products.filter(p => p.category === product.category && p.id !== product.id).slice(0, 3);

  const handleAddToCart = () => {
    addToCart(product, selectedModel);
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  };

  const handleBuyNow = () => {
    addToCart(product, selectedModel);
    router.push('/checkout');
  };

  return (
    <>
      <div className="max-w-6xl mx-auto px-4 py-8 pb-24 md:pb-8">
        {/* Breadcrumb */}
        <nav className="text-sm text-gray-500 mb-6 flex items-center gap-2 flex-wrap">
          <Link href="/" className="hover:text-primary">Home</Link>
          <span>/</span>
          <Link href="/products" className="hover:text-primary">Products</Link>
          <span>/</span>
          <Link href={`/products?cat=${product.category}`} className="hover:text-primary capitalize">{product.category}</Link>
          <span>/</span>
          <span className="text-dark font-medium">{product.name}</span>
        </nav>

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          {/* Image gallery */}
          <div>
            <div className="rounded-2xl overflow-hidden mb-4 bg-white shadow-sm relative">
              <img src={product.images[selectedImg]} alt={product.name} className="w-full h-96 object-cover" />
              {discount > 0 && (
                <span className="absolute top-4 left-4 bg-accent text-white text-sm font-bold px-3 py-1.5 rounded-xl">
                  -{discount}% OFF
                </span>
              )}
              <div className="absolute top-4 right-4">
                <WishlistButton productId={product.id} className="shadow-md" />
              </div>
            </div>
            {product.images.length > 1 && (
              <div className="flex gap-3">
                {product.images.map((img, i) => (
                  <button key={i} onClick={() => setSelectedImg(i)} className={`rounded-xl overflow-hidden border-2 transition-colors ${selectedImg === i ? 'border-primary' : 'border-transparent hover:border-gray-300'}`}>
                    <img src={img} alt="" className="w-16 h-16 object-cover" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Product info */}
          <div>
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <span className="bg-primary/10 text-primary text-xs font-semibold px-3 py-1 rounded-full capitalize">{product.category}</span>
              {product.badge && (
                <span className={`text-white text-xs font-bold px-3 py-1 rounded-full ${
                  product.badge === 'Best Seller' ? 'bg-yellow-500' :
                  product.badge === 'New' ? 'bg-primary' : 'bg-purple-500'
                }`}>{product.badge}</span>
              )}
            </div>

            <h1 className="text-3xl font-extrabold text-dark mb-1">Carry Your Best Friend Everywhere</h1>
            <p className="text-lg font-semibold text-gray-700 mb-2">{product.name}</p>
            <p className="text-gray-500 text-sm mb-4">Turn your pet's love into wearable art. Premium cases that protect your phone and show the world who you love most.</p>

            <div className="flex items-center gap-4 mb-4 flex-wrap">
              <StarRating rating={product.rating} count={product.reviewCount} size="md" />
              {product.viewerCount && (
                <span className="text-xs text-orange-500 font-semibold bg-orange-50 px-2 py-1 rounded-full flex items-center gap-1">
                  <Users className="w-3 h-3" />
                  {product.viewerCount} people viewing now
                </span>
              )}
            </div>

            {product.stock <= 5 && (
              <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-2 mb-4 flex items-center gap-2">
                <span className="text-red-500 text-sm font-bold">Only {product.stock} left in stock — order soon!</span>
              </div>
            )}

            <div className="flex items-center gap-3 mb-6 flex-wrap">
              <span className="text-4xl font-extrabold text-accent">€{product.price.toFixed(2)}</span>
              {product.originalPrice && (
                <>
                  <span className="text-xl text-gray-400 line-through">€{product.originalPrice.toFixed(2)}</span>
                  <span className="bg-green-100 text-green-700 text-sm font-bold px-2 py-1 rounded-lg">Save €{(product.originalPrice - product.price).toFixed(2)}</span>
                </>
              )}
            </div>

            <div className="mb-5">
              <BundleOffer product={product} selectedModel={selectedModel} />
            </div>

            <div className="mb-5">
              <label className="block font-semibold mb-2 text-sm text-dark">Select Phone Model <span className="text-red-500">*</span></label>
              <select
                value={selectedModel}
                onChange={e => setSelectedModel(e.target.value)}
                className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-primary text-dark bg-white"
              >
                {product.models.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>

            {product.isCustom && (
              <div className="mb-5 bg-secondary rounded-xl p-4">
                <label className="block font-semibold mb-2 text-sm text-dark">Upload Your Pet's Photo <span className="text-red-500">*</span></label>
                <div className="border-2 border-dashed border-primary/40 rounded-xl p-4 text-center">
                  <Upload className="w-8 h-8 text-primary mx-auto mb-2" />
                  <p className="text-sm text-gray-600 mb-2">Drag &amp; drop or click to upload</p>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={e => setPhotoFile(e.target.files[0])}
                    className="w-full text-sm text-gray-600 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:font-medium file:bg-primary file:text-white hover:file:bg-green-700 cursor-pointer"
                  />
                </div>
                {photoFile && <p className="text-xs text-green-600 mt-2 font-medium">✓ {photoFile.name} ready to upload</p>}
                <p className="text-xs text-gray-500 mt-2">JPG, PNG or HEIC. Max 10MB. High resolution recommended for best results.</p>
              </div>
            )}

            <div className="flex gap-3 mb-5">
              <button
                onClick={handleAddToCart}
                className={`flex-1 flex items-center justify-center gap-2 py-4 rounded-xl font-bold text-base transition-all ${
                  added ? 'bg-green-600 text-white' : 'bg-primary text-white hover:bg-green-700'
                }`}
              >
                <ShoppingCart className="w-5 h-5" />
                {added ? '✓ Added to Cart!' : 'Add to Cart'}
              </button>
              <button
                onClick={handleBuyNow}
                className="flex-1 flex items-center justify-center gap-2 py-4 rounded-xl font-bold text-base bg-accent text-white hover:bg-orange-600 transition-all"
              >
                <Zap className="w-5 h-5" />
                Buy Now
              </button>
            </div>

            <TrustBadges variant="compact" />

            <div className="mt-4 flex items-center gap-2 text-sm bg-green-50 rounded-xl px-4 py-3">
              <span className="text-lg">🚚</span>
              <span className="text-gray-700">
                {product.price >= 40
                  ? <span className="text-green-700 font-semibold">This order qualifies for free shipping!</span>
                  : <span>Add <span className="font-bold text-primary">€{(40 - product.price).toFixed(2)}</span> more for free shipping</span>
                }
              </span>
            </div>
          </div>
        </div>

        {/* How It Works */}
        <section className="bg-white rounded-3xl p-8 mb-12">
          <h2 className="text-2xl font-extrabold text-center mb-8">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                step: '1', icon: '🎨',
                title: product.isCustom ? 'Upload Your Photo' : 'Choose Your Design',
                desc: product.isCustom
                  ? "Send us your favourite pet photo — we'll create a stunning digital mockup within 24 hours."
                  : "Browse our collection and pick the design that best captures your pet's personality."
              },
              { step: '2', icon: '📱', title: 'Select Your Phone Model', desc: 'Choose from a wide range of iPhone and Samsung models. Perfect fit guaranteed or your money back.' },
              { step: '3', icon: '📦', title: 'Receive in 3–5 Days', desc: 'Your case is printed and shipped from within the EU. Fast, tracked delivery right to your door.' },
            ].map(s => (
              <div key={s.step} className="text-center">
                <div className="w-12 h-12 bg-primary text-white rounded-full flex items-center justify-center font-extrabold text-lg mx-auto mb-3">{s.step}</div>
                <div className="text-3xl mb-2">{s.icon}</div>
                <h3 className="font-bold text-dark mb-2">{s.title}</h3>
                <p className="text-sm text-gray-500">{s.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Features */}
        <section className="mb-12">
          <h2 className="text-2xl font-extrabold mb-6">What's Included</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {product.features.map((f, i) => (
              <div key={i} className="flex items-start gap-3 bg-white rounded-xl p-4">
                <CheckCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                <span className="text-sm text-gray-700 font-medium">{f}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Why Pet Owners Love PawCase */}
        <section className="bg-primary text-white rounded-3xl p-8 mb-12">
          <h2 className="text-2xl font-extrabold text-center mb-8">Why Pet Owners Love PawCase</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: '🖼️', title: 'Print That Pops', desc: 'Pro-grade UV printing delivers museum-quality clarity that lasts for years.' },
              { icon: '🛡️', title: 'Slim Yet Tough', desc: 'Drop-tested protection in a slim profile. Your phone is safe without the bulk.' },
              { icon: '🌱', title: 'Eco Conscious', desc: 'Printed on demand — no waste, no overproduction. Better for the planet.' },
              { icon: '💝', title: 'Gift-Ready', desc: 'Arrives in beautiful packaging — the perfect gift for any pet lover.' },
            ].map(b => (
              <div key={b.title} className="text-center">
                <div className="text-4xl mb-3">{b.icon}</div>
                <h3 className="font-bold mb-1">{b.title}</h3>
                <p className="text-green-100 text-sm">{b.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Customer Reviews */}
        <section className="mb-12">
          <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
            <div>
              <h2 className="text-2xl font-extrabold">Customer Reviews</h2>
              <div className="flex items-center gap-3 mt-2">
                <div className="flex text-yellow-400 text-2xl">{'★'.repeat(5)}</div>
                <span className="text-3xl font-extrabold text-dark">{product.rating}</span>
                <span className="text-gray-500 text-sm">out of 5 ({product.reviewCount.toLocaleString()} reviews)</span>
              </div>
            </div>
          </div>
          <div className="space-y-4">
            {product.reviews.map((r, i) => (
              <div key={i} className="bg-white rounded-2xl p-5">
                <div className="flex items-start justify-between mb-2 flex-wrap gap-2">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-bold text-dark">{r.name}</span>
                      {r.verified && (
                        <span className="text-xs bg-green-100 text-green-700 font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
                          <CheckCircle className="w-3 h-3" /> Verified
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-400">{r.location} · {r.date}</p>
                  </div>
                  <StarRating rating={r.rating} size="sm" />
                </div>
                <p className="text-gray-700 text-sm leading-relaxed">"{r.text}"</p>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ */}
        <section className="mb-12">
          <h2 className="text-2xl font-extrabold mb-6">Frequently Asked Questions</h2>
          <div className="space-y-2">
            {faqs.map((faq, i) => (
              <div key={i} className="bg-white rounded-2xl overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex items-center justify-between p-5 text-left font-semibold text-dark hover:bg-secondary/50 transition-colors"
                >
                  <span>{faq.q}</span>
                  {openFaq === i ? <ChevronUp className="w-5 h-5 text-primary flex-shrink-0" /> : <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />}
                </button>
                {openFaq === i && (
                  <div className="px-5 pb-5 text-sm text-gray-600 leading-relaxed">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Shipping & Returns */}
        <section className="mb-12 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl p-6">
            <h3 className="font-extrabold text-lg mb-4 flex items-center gap-2">
              <span className="text-2xl">🚚</span> Shipping
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary flex-shrink-0" /> Standard EU shipping: 3–5 business days</li>
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary flex-shrink-0" /> Free shipping on orders over €40</li>
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary flex-shrink-0" /> Fully tracked &amp; insured delivery</li>
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary flex-shrink-0" /> Ships from within the EU — no customs fees</li>
            </ul>
          </div>
          <div className="bg-white rounded-2xl p-6">
            <h3 className="font-extrabold text-lg mb-4 flex items-center gap-2">
              <span className="text-2xl">🔄</span> Returns &amp; Guarantee
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary flex-shrink-0" /> 30-day hassle-free returns</li>
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary flex-shrink-0" /> Full refund or free replacement</li>
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary flex-shrink-0" /> Print quality guaranteed for life</li>
              <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary flex-shrink-0" /> Contact us within 30 days of delivery</li>
            </ul>
          </div>
        </section>

        {/* Satisfaction Guarantee */}
        <section className="bg-secondary rounded-3xl p-8 mb-12 text-center">
          <div className="text-5xl mb-4">🏆</div>
          <h2 className="text-2xl font-extrabold mb-2">100% Satisfaction Guarantee</h2>
          <p className="text-gray-600 max-w-xl mx-auto mb-6">If you're not completely in love with your PawCase, we'll make it right. No hassle, no questions. That's our promise to every pet lover.</p>
          <div className="flex justify-center gap-6 flex-wrap text-sm text-gray-600">
            <span className="flex items-center gap-2"><Shield className="w-4 h-4 text-primary" /> 30-Day Returns</span>
            <span className="flex items-center gap-2"><RotateCcw className="w-4 h-4 text-primary" /> Free Replacement</span>
            <span className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-primary" /> Quality Guaranteed</span>
          </div>
        </section>

        {related.length > 0 && (
          <section>
            <h2 className="text-2xl font-bold mb-6">You May Also Like</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {related.map(p => <ProductCard key={p.id} product={p} />)}
            </div>
          </section>
        )}

        <div className="mt-12">
          <TrustBadges variant="horizontal" />
        </div>
      </div>

      <StickyATC
        product={product}
        selectedModel={selectedModel}
        onAddToCart={handleAddToCart}
        onBuyNow={handleBuyNow}
        added={added}
      />
      <RecentPurchaseNotification />
    </>
  );
}
