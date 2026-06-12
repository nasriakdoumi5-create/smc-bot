'use client';
import { useEffect, useState } from 'react';
import { X } from 'lucide-react';

export default function ExitIntentPopup() {
  const [visible, setVisible] = useState(false);
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    const dismissed = sessionStorage.getItem('pawcase-exit-dismissed');
    if (dismissed) return;

    const handleMouseLeave = (e) => {
      if (e.clientY <= 0 && !visible) {
        setVisible(true);
      }
    };
    document.addEventListener('mouseleave', handleMouseLeave);
    return () => document.removeEventListener('mouseleave', handleMouseLeave);
  }, [visible]);

  const handleDismiss = () => {
    setVisible(false);
    sessionStorage.setItem('pawcase-exit-dismissed', '1');
  };

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60">
      <div className="bg-white rounded-3xl max-w-md w-full p-8 relative text-center shadow-2xl">
        <button onClick={handleDismiss} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
        <div className="text-5xl mb-3">🐾</div>
        {submitted ? (
          <>
            <h2 className="text-2xl font-extrabold mb-2">Your 10% code is on its way!</h2>
            <p className="text-gray-500">Check your inbox. Use code <strong className="text-accent">PAWS10</strong> at checkout.</p>
            <button onClick={handleDismiss} className="mt-6 btn-primary w-full">Continue Shopping</button>
          </>
        ) : (
          <>
            <h2 className="text-2xl font-extrabold mb-2 text-dark">Wait — Before You Go!</h2>
            <p className="text-accent font-bold text-lg mb-1">Get 10% OFF your first order</p>
            <p className="text-gray-500 text-sm mb-6">Enter your email and we'll send your exclusive discount code instantly.</p>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 mb-3 focus:outline-none focus:border-primary"
            />
            <button
              onClick={() => { if (email) setSubmitted(true); }}
              className="btn-primary w-full"
            >
              Get My 10% Discount
            </button>
            <button onClick={handleDismiss} className="mt-3 text-xs text-gray-400 hover:text-gray-500 w-full">No thanks, I'll pay full price</button>
          </>
        )}
      </div>
    </div>
  );
}
