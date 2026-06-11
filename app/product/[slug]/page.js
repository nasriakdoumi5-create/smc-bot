'use client';
import { useState } from 'react';
import { useParams } from 'next/navigation';
import { getProductBySlug, products } from '@/data/products';
import { useCart } from '@/context/CartContext';
import ProductCard from '@/components/ProductCard';
import { ShoppingCart, Shield, Truck, Star } from 'lucide-react';
import Link from 'next/link';

export default function ProductPage() {
  const { slug } = useParams();
  const product = getProductBySlug(slug);

  const [selectedModel, setSelectedModel] = useState(product ? product.models[0] : '');
  const [selectedImg, setSelectedImg] = useState(0);
  const [photoFile, setPhotoFile] = useState(null);
  const [added, setAdded] = useState(false);
  const { addToCart } = useCart();

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

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <nav className="text-sm text-gray-500 mb-8 flex items-center gap-2">
        <Link href="/" className="hover:text-primary">Home</Link>
        <span>/</span>
        <Link href="/products" className="hover:text-primary">Products</Link>
        <span>/</span>
        <span className="text-dark font-medium">{product.name}</span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
        {/* Images */}
        <div>
          <div className="rounded-2xl overflow-hidden mb-4 bg-white shadow-sm">
            <img src={product.images[selectedImg]} alt={product.name} className="w-full h-96 object-cover" />
          </div>
          {product.images.length > 1 && (
            <div className="flex gap-3">
              {product.images.map((img, i) => (
                <button key={i} onClick={() => setSelectedImg(i)} className={`rounded-xl overflow-hidden border-2 transition-colors ${selectedImg === i ? 'border-primary' : 'border-transparent'}`}>
                  <img src={img} alt="" className="w-16 h-16 object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="bg-primary/10 text-primary text-xs font-semibold px-3 py-1 rounded-full capitalize">{product.category}</span>
            {discount > 0 && <span className="bg-accent/10 text-accent text-xs font-semibold px-3 py-1 rounded-full">-{discount}% OFF</span>}
          </div>
          <h1 className="text-3xl font-bold text-dark mb-3">{product.name}</h1>
          <div className="flex items-center gap-3 mb-4">
            <span className="text-3xl font-extrabold text-accent">€{product.price}</span>
            {product.originalPrice && <span className="text-xl text-gray-400 line-through">€{product.originalPrice}</span>}
          </div>
          <p className="text-gray-600 mb-6 leading-relaxed">{product.description}</p>

          {/* Phone model selector */}
          <div className="mb-6">
            <label className="block font-semibold mb-2 text-sm">Select Phone Model <span className="text-red-500">*</span></label>
            <select
              value={selectedModel}
              onChange={e => setSelectedModel(e.target.value)}
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-primary text-dark bg-white"
            >
              {product.models.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>

          {/* Custom photo upload */}
          {product.isCustom && (
            <div className="mb-6 bg-secondary rounded-xl p-4">
              <label className="block font-semibold mb-2 text-sm">Upload Your Pet's Photo <span className="text-red-500">*</span></label>
              <input
                type="file"
                accept="image/*"
                onChange={e => setPhotoFile(e.target.files[0])}
                className="w-full text-sm text-gray-600 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:font-medium file:bg-primary file:text-white hover:file:bg-primary-dark cursor-pointer"
              />
              <p className="text-xs text-gray-500 mt-2">JPG, PNG or HEIC. Max 10MB. High resolution recommended.</p>
            </div>
          )}

          <button
            onClick={handleAddToCart}
            className={`w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-3 transition-all ${
              added ? 'bg-green-600 text-white' : 'btn-primary'
            }`}
          >
            <ShoppingCart className="w-5 h-5" />
            {added ? '✓ Added to Cart!' : 'Add to Cart'}
          </button>

          {/* Why you'll love it */}
          <div className="mt-8 grid grid-cols-1 gap-3">
            {[
              { icon: Star, text: 'Premium print quality — vibrant, long-lasting colors' },
              { icon: Truck, text: 'EU shipping in 3–5 business days via Printful' },
              { icon: Shield, text: '30-day money-back guarantee on all orders' },
            ].map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-3 text-sm text-gray-600">
                <Icon className="w-4 h-4 text-primary flex-shrink-0" />
                {text}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Related products */}
      {related.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold mb-6">You May Also Like</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {related.map(p => <ProductCard key={p.id} product={p} />)}
          </div>
        </div>
      )}
    </div>
  );
}
