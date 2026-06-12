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
import { trackViewContent } from '@/components/MetaPixel';
import { ttqViewContent } from '@/components/TikTokPixel';

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
  const [bundleQty, setBundleQty] = useState(1);
  const { addToCart, addToRecentlyViewed } = useCart();

  useEffect(() => {
    if (product) {
      addToRecentlyViewed(product.id);
      trackViewContent(product);
      ttqViewContent(product);
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
    for (let i = 0; i < bundleQty; i++) {
      addToCart(product, selectedModel);
    }
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  };

  const handleBuyNow = () => {
    addToCart(product, selectedModel);
    router.push('/checkout');
  };

  // Emotional headline logic
  const emotionalHeadlines = {
    dogs: "The Face That Greets You Every Morning — Now on Your Phone",
    cats: "Cool, Mysterious, and Completely Yours — Just Like Your Cat",
    custom: "Because Your Pet Is One of a Kind",
  };
  const emotionalSubs = {
    dogs: "Every time you pick up your phone, you'll see that wagging tail and feel that rush of joy.",
    cats: "Every glance at your phone brings a smile. Every stranger wants to know where you got it.",
    custom: "Your pet's face, your phone case, your story. Unlike anything else in the world.",
  };
  const headline = product.emotionalHook || emotionalHeadlines[product.category] || "Carry Your Best Friend Everywhere";
  const subHeadline = product.emotionalSub || emotionalSubs[product.category] || "Turn your pet's love into wearable art. Premium cases that protect your phone and show the world who you love most.";

  return (
    <>
      <div className="max-w-6xl mx-auto px-4 py-8 pb-24 md:pb-8">
        {/* JSON-LD Product Schema */}
        <script type="application/ld+json" dangerouslySetInnerHTML={{__html: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "Product",
          "name": product.name,
          "description": product.description,
          "image": product.images,
          "brand": { "@type": "Brand", "name": "PawCase" },
          "offers": {
            "@type": "Offer",
            "price": product.price,
            "priceCurrency": "EUR",
            "availability": product.stock > 0 ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
            "seller": { "@type": "Organization", "name": "PawCase" }
          },
          "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": product.rating,
            "reviewCount": product.reviewCount
          }
        })}} />

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

            {/* Emotional headline block */}
            <h1 className="text-3xl font-extrabold text-dark mb-1">{headline}</h1>
            <p className="text-lg font-semibold text-gray-700 mb-2">{product.name}</p>
            <p className="text-gray-500 text-sm mb-4">{subHeadline}</p>

            {/* Emotional callout — Turn Your Pet Into Art */}
            <div className="bg-gradient-to-r from-primary/10 to-accent/10 rounded-2xl p-4 mb-4 border border-primary/20">
              <div className="flex items-start gap-3">
                <span className="text-2xl flex-shrink-0">💝</span>
                <div>
                  <p className="font-bold text-dark text-sm mb-1">The perfect gift that always gets tears</p>
                  <p className="text-xs text-gray-600">Over 5,000 pet lovers gave this as a gift. The reaction? Always emotional. Always unforgettable.</p>
                </div>
              </div>
            </div>

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
              <BundleOffer product={product} selectedModel={selectedModel} bundleQty={bundleQty} onBundleChange={setBundleQty} />
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

            {/* 30-Day Money-Back Guarantee badge */}
            <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-xl px-4 py-2.5 mb-3">
              <span className="text-lg">🏆</span>
              <div>
                <p className="text-xs font-bold text-green-700">30-Day Money-Back Guarantee</p>
                <p className="text-xs text-green-600">Not in love with it? Full refund. No questions asked.</p>
              </div>
            </div>

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

            <div className="mt-4 flex items-center gap-2 text-sm bg-green-50 rounded-xl px-4 py-3 mb-4">
              <span className="text-lg">🚚</span>
              <span className="text-gray-700">
                {product.price >= 40
                  ? <span className="text-green-700 font-semibold">This order qualifies for free shipping!</span>
                  : <span>Add <span className="font-bold text-primary">€{(40 - product.price).toFixed(2)}</span> more for free shipping</span>
                }
              </span>
            </div>

            {/* Delivery timeline */}
            <div className="grid grid-cols-3 gap-2 mb-4 text-center">
              {[
                { emoji: '🎨', label: 'Today', desc: 'Order placed' },
                { emoji: '📦', label: '1–2 days', desc: 'Printed & packed' },
                { emoji: '🚚', label: '3–5 days', desc: 'Delivered to you' },
              ].map(step => (
                <div key={step.label} className="bg-secondary rounded-xl p-2">
                  <p className="text-lg">{step.emoji}</p>
                  <p className="text-xs font-bold text-dark">{step.label}</p>
                  <p className="text-xs text-gray-500">{step.desc}</p>
                </div>
              ))}
            </div>

            <TrustBadges variant="compact" />
          </div>
        </div>

        {/* UGC Lifestyle Gallery */}
        <section className="mb-12">
          <h2 className="text-2xl font-extrabold mb-2 text-center">Loved by Pet Parents Across Europe</h2>
          <p className="text-center text-gray-500 text-sm mb-6">Real customers, real reactions 🐾</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {['ugc1','ugc2','ugc3','ugc4','ugc5','ugc6','ugc7','ugc8'].map((seed, i) => (
              <div key={i} className="rounded-2xl overflow-hidden aspect-square relative group cursor-pointer">
                <img src={`https://picsum.photos/seed/${seed}/300/300`} alt="Customer photo" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-2">
                  <p className="text-white text-xs font-semibold">★★★★★</p>
                </div>
              </div>
            ))}
          </div>
        </section>

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
                  <div className="flex items-start gap-3">
                    <div className="w-9 h-9 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold text-sm flex-shrink-0">
                      {r.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-bold text-dark">{r.name}</span>
                        {r.verified && (
                          <span className="text-xs bg-green-100 text-green-700 font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
                            <CheckCircle className="w-3 h-3" /> Verified Purchase
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-400">{r.location} · {r.date}</p>
                    </div>
                  </div>
                  <div className="flex text-yellow-400 text-base">
                    {'★'.repeat(Math.round(r.rating))}{'☆'.repeat(5 - Math.round(r.rating))}
                  </div>
                </div>
                <p className="text-gray-700 text-sm leading-relaxed">"{r.text}"</p>
              </div>
            ))}
          </div>
        </section>

        {/* Frequently Bought Together */}
        <section className="mb-12">
          <h2 className="text-2xl font-extrabold mb-6">Frequently Bought Together</h2>
          <div className="bg-white rounded-2xl p-5 border border-gray-100">
            <div className="flex items-center gap-4 flex-wrap mb-4">
              {[product, ...products.filter(p => p.id === '5' && p.id !== product.id).slice(0,1), ...related.slice(0,1)].slice(0,2).map((p, i) => (
                <div key={p.id} className="flex items-center gap-3">
                  {i > 0 && <span className="text-2xl font-bold text-gray-300">+</span>}
                  <div className="flex items-center gap-2">
                    <img src={p.image} alt={p.name} className="w-16 h-16 rounded-xl object-cover" />
                    <div>
                      <p className="text-sm font-semibold text-dark">{p.name}</p>
                      <p className="text-accent font-bold">€{p.price}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {(() => {
              const fbtProducts = [product, ...products.filter(p => p.id === '5' && p.id !== product.id).slice(0,1)].slice(0,2);
              const combinedOriginal = fbtProducts.reduce((s, p) => s + p.price, 0);
              const combinedDiscounted = (combinedOriginal * 0.9).toFixed(2);
              return (
                <div className="flex items-center justify-between flex-wrap gap-3">
                  <div>
                    <span className="text-xl font-extrabold text-accent">€{combinedDiscounted}</span>
                    <span className="text-sm text-gray-400 line-through ml-2">€{combinedOriginal.toFixed(2)}</span>
                    <span className="ml-2 text-xs text-green-600 font-bold">Save 10% when bought together</span>
                  </div>
                  <button
                    onClick={() => {
                      fbtProducts.forEach(p => addToCart(p, p.models[0]));
                    }}
                    className="bg-dark text-white px-5 py-2.5 rounded-xl font-bold text-sm hover:bg-gray-800 transition-colors"
                  >
                    Add Both to Cart
                  </button>
                </div>
              );
            })()}
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
