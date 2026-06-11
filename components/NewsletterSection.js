'use client';
import { useState } from 'react';

export default function NewsletterSection() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (email) setSubmitted(true);
  };

  return (
    <section className="bg-primary text-white py-16 px-4">
      <div className="max-w-2xl mx-auto text-center">
        <div className="text-4xl mb-4">📧</div>
        <h2 className="text-3xl font-bold mb-2">Join the PawCase Family</h2>
        <p className="text-green-200 mb-8">Get exclusive deals, new design alerts & pet care tips. Join 5,000+ pet lovers!</p>
        {submitted ? (
          <div className="bg-white/20 rounded-2xl p-6">
            <p className="text-xl font-bold">🎉 You're in!</p>
            <p className="text-green-200 mt-1">Check your email for a welcome discount.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              className="flex-1 px-4 py-3 rounded-xl text-dark focus:outline-none focus:ring-2 focus:ring-accent"
            />
            <button type="submit" className="bg-accent px-6 py-3 rounded-xl font-bold hover:bg-orange-600 transition-colors whitespace-nowrap">
              Subscribe
            </button>
          </form>
        )}
      </div>
    </section>
  );
}
