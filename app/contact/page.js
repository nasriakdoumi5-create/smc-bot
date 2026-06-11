'use client';
import { useState } from 'react';

export default function ContactPage() {
  const [form, setForm] = useState({ name: '', email: '', message: '' });
  const [sent, setSent] = useState(false);
  const handle = e => { e.preventDefault(); setSent(true); };

  return (
    <div className="max-w-2xl mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-center mb-3">Get in Touch</h1>
      <p className="text-center text-gray-500 mb-10">We respond within 24 hours. We love hearing from pet lovers! 🐾</p>
      <div className="card p-8">
        {sent ? (
          <div className="text-center py-8">
            <div className="text-5xl mb-4">✉️</div>
            <h2 className="text-2xl font-bold mb-2">Message Sent!</h2>
            <p className="text-gray-500">We'll get back to you within 24 hours.</p>
          </div>
        ) : (
          <form onSubmit={handle} className="space-y-5">
            <div>
              <label className="block font-medium mb-1.5 text-sm">Name</label>
              <input type="text" required value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-primary" placeholder="Your name" />
            </div>
            <div>
              <label className="block font-medium mb-1.5 text-sm">Email</label>
              <input type="email" required value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-primary" placeholder="hello@example.com" />
            </div>
            <div>
              <label className="block font-medium mb-1.5 text-sm">Message</label>
              <textarea required value={form.message} onChange={e => setForm({...form, message: e.target.value})}
                rows={5} className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-primary resize-none" placeholder="How can we help?" />
            </div>
            <button type="submit" className="btn-primary w-full">Send Message</button>
          </form>
        )}
        <div className="mt-6 pt-6 border-t text-center text-sm text-gray-500">
          <p>📧 hello@pawcase.eu</p>
          <p className="mt-1">Response time: within 24 hours</p>
        </div>
      </div>
    </div>
  );
}
