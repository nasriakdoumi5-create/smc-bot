import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-dark text-white">
      {/* Payment methods bar */}
      <div className="border-b border-gray-700 py-4">
        <div className="max-w-5xl mx-auto px-4 flex flex-wrap items-center justify-center gap-3">
          <span className="text-xs text-gray-400 mr-1">Secure payments:</span>
          {['VISA','MASTERCARD','PAYPAL','AMEX','APPLE PAY'].map(p => (
            <span key={p} className="text-xs font-bold bg-white/10 text-gray-300 px-3 py-1.5 rounded-lg border border-white/10">{p}</span>
          ))}
          <span className="text-xs text-green-400 ml-1">🔒 SSL Encrypted</span>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-12 grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Brand */}
        <div>
          <div className="text-2xl font-extrabold mb-3">🐾 PawCase</div>
          <p className="text-gray-400 text-sm leading-relaxed mb-5">
            Premium custom pet phone cases for pet lovers across Europe. Printed with care, shipped fast.
          </p>
          <div className="flex gap-3">
            {[
              { label: 'Instagram', emoji: '📸', href: '#' },
              { label: 'TikTok', emoji: '🎵', href: '#' },
              { label: 'Facebook', emoji: '📘', href: '#' },
            ].map(s => (
              <a key={s.label} href={s.href} aria-label={s.label}
                className="w-9 h-9 bg-white/10 rounded-xl flex items-center justify-center text-sm hover:bg-white/20 transition-colors">
                {s.emoji}
              </a>
            ))}
          </div>
        </div>

        {/* Shop */}
        <div>
          <h4 className="font-semibold mb-4 text-white">Shop</h4>
          <ul className="space-y-2.5 text-gray-400 text-sm">
            {[
              { href: '/products', label: 'All Cases' },
              { href: '/products?cat=dogs', label: '🐕 Dog Lovers' },
              { href: '/products?cat=cats', label: '🐈 Cat Lovers' },
              { href: '/product/custom-pet-phone-case', label: '✨ Custom Cases' },
              { href: '/wishlist', label: '♡ My Wishlist' },
            ].map(l => (
              <li key={l.href}>
                <Link href={l.href} className="hover:text-white transition-colors">{l.label}</Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Help */}
        <div>
          <h4 className="font-semibold mb-4 text-white">Help</h4>
          <ul className="space-y-2.5 text-gray-400 text-sm">
            {[
              { href: '/faq', label: 'FAQ' },
              { href: '/contact', label: 'Contact Us' },
              { href: '/about', label: 'About PawCase' },
              { href: '/faq', label: 'Returns Policy' },
              { href: '/faq', label: 'Shipping Info' },
            ].map((l, i) => (
              <li key={i}>
                <Link href={l.href} className="hover:text-white transition-colors">{l.label}</Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Contact & Trust */}
        <div>
          <h4 className="font-semibold mb-4 text-white">Contact</h4>
          <ul className="space-y-2.5 text-gray-400 text-sm">
            <li>
              <a href="mailto:hello@pawcase.eu" className="hover:text-white transition-colors">
                📧 hello@pawcase.eu
              </a>
            </li>
            <li>💬 Reply within 24 hours</li>
            <li>🇪🇺 Ships from Europe</li>
            <li>🚚 3–5 business days</li>
          </ul>
          <div className="mt-5 space-y-1.5">
            {[
              '✓ 5,000+ happy customers',
              '✓ 30-day hassle-free returns',
              '✓ Print quality guaranteed',
            ].map(b => (
              <p key={b} className="text-xs text-green-400">{b}</p>
            ))}
          </div>
        </div>
      </div>

      <div className="border-t border-gray-700 py-5">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-gray-500">
          <p>© 2025 PawCase — All rights reserved</p>
          <div className="flex gap-4">
            <Link href="/faq" className="hover:text-gray-300 transition-colors">Privacy Policy</Link>
            <Link href="/faq" className="hover:text-gray-300 transition-colors">Terms</Link>
            <Link href="/faq" className="hover:text-gray-300 transition-colors">Returns</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
