'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

const steps = [
  {
    id: 1,
    emoji: '📸',
    title: 'Upload Your Pet Photo',
    desc: 'Send us your favourite high-res photo',
    color: 'from-emerald-400 to-green-600',
    bg: 'bg-green-50',
    border: 'border-green-200',
  },
  {
    id: 2,
    emoji: '🎨',
    title: 'We Design Your Case',
    desc: 'Digital mockup ready within 24 hours',
    color: 'from-purple-400 to-purple-600',
    bg: 'bg-purple-50',
    border: 'border-purple-200',
  },
  {
    id: 3,
    emoji: '🖨️',
    title: 'Premium UV Printing',
    desc: 'Museum-quality, vibrant & fade-resistant',
    color: 'from-blue-400 to-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
  },
  {
    id: 4,
    emoji: '📦',
    title: 'Delivered in 3-5 Days',
    desc: 'Fully tracked, ships from within the EU',
    color: 'from-orange-400 to-red-500',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
  },
];

export default function ProcessShowcase() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActive(prev => (prev + 1) % steps.length);
    }, 2800);
    return () => clearInterval(timer);
  }, []);

  return (
    <section className="bg-white py-14 border-b border-gray-100">
      <div className="max-w-5xl mx-auto px-4">
        <div className="text-center mb-10">
          <span className="inline-block bg-primary/10 text-primary text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-widest mb-3">
            How It Works
          </span>
          <h2 className="text-3xl font-extrabold text-dark">
            From Your Photo to a Masterpiece in 4 Steps
          </h2>
          <p className="text-gray-500 mt-2 text-base">
            Every PawCase is handcrafted with love
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {steps.map((step, i) => (
            <button
              key={step.id}
              onClick={() => setActive(i)}
              className={`rounded-2xl p-5 text-left transition-all duration-300 border-2 cursor-pointer w-full ${
                active === i
                  ? step.bg + ' ' + step.border + ' shadow-md scale-[1.03]'
                  : 'bg-gray-50 border-transparent hover:border-gray-200'
              }`}
            >
              <div className={`w-11 h-11 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center text-2xl mb-3`}>
                {step.emoji}
              </div>
              <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center mb-2 text-xs font-bold ${
                active === i ? 'bg-primary border-primary text-white' : 'border-gray-300 text-gray-400'
              }`}>
                {step.id}
              </div>
              <h3 className="font-bold text-dark text-sm mb-1">{step.title}</h3>
              <p className="text-xs text-gray-500 leading-relaxed">{step.desc}</p>
            </button>
          ))}
        </div>

        <div className="flex justify-center gap-2 mb-8">
          {steps.map((_, i) => (
            <button
              key={i}
              onClick={() => setActive(i)}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                active === i ? 'bg-primary w-8' : 'bg-gray-300 w-1.5'
              }`}
            />
          ))}
        </div>

        <div className="text-center">
          <Link
            href="/product/custom-pet-phone-case"
            className="bg-accent text-white px-8 py-3.5 rounded-xl font-bold text-base hover:bg-orange-600 transition-colors inline-flex items-center gap-2 shadow-lg shadow-orange-200"
          >
            Create My Custom Case
          </Link>
          <p className="text-gray-400 text-xs mt-3">
            Digital preview sent within 24 hours · No print until you approve
          </p>
        </div>
      </div>
    </section>
  );
}
