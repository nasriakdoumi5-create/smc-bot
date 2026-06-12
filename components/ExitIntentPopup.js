'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { X } from 'lucide-react';

export default function ExitIntentPopup() {
  const [visible, setVisible] = useState(false);
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (sessionStorage.getItem('pawcase-exit-dismissed')) return;

    // Desktop: mouse leaves top of screen
    const handleMouseLeave = (e) => {
      if (e.clientY <= 0) setVisible(true);
    };

    // Mobile: show after 25 seconds of inactivity
    const mobileTimer = setTimeout(() => {
      if (window.innerWidth < 768 && !sessionStorage.getItem('pawcase-exit-dismissed')) {
        setVisible(true);
      }
    }, 25000);

    document.addEventListener('mouseleave', handleMouseLeave);
    return () => {
      document.removeEventListener('mouseleave', handleMouseLeave);
      clearTimeout(mobileTimer);
    };
  }, []);

  const handleDismiss = () => {
    setVisible(false);
    sessionStorage.setItem('pawcase-exit-dismissed', '1');
  };

  const handleClaim = () => {
    if (!email) return;
    setSubmitted(true);
  };

  const handleShopNow = () => {
    handleDismiss();
    router.push('/checkout?coupon=PAWS10');
  };

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 animate-fade-in">
      <div className="bg-white rounded-3xl max-w-md w-full p-8 relative text-center shadow-2xl">
        <button onClick={handleDismiss} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors">
          <X className="w-5 h-5" />
        </button>

        {submitted ? (
          <>
            <div className="text-5xl mb-3">🎉</div>
            <h2 className="text-2xl font-extrabold mb-2 text-dark">You got it!</h2>
            <p className="text-gray-500 mb-2">Use code at checkout:</p>
            <div className="bg-accent/10 border-2 border-accent border-dashed rounded-2xl py-3 px-6 mb-5">
              <p className="text-2xl font-extrabold text-accent tracking-widest">PAWS10</p>
              <p className="text-xs text-gray-500 mt-1">10% off your entire order</p>
            </div>
            <button onClick={handleShopNow} className="btn-primary w-full">
              Shop Now & Save 10% →
            </button>
            <button onClick={handleDismiss} className="mt-3 text-xs text-gray-400 hover:text-gray-500 w-full">
              I'll use it later
            </button>
          </>
        ) : (
          <>
            <div className="text-5xl mb-3">🐾</div>
            <h2 className="text-2xl font-extrabold mb-1 text-dark">Wait — Before You Go!</h2>
            <p className="text-accent font-bold text-lg mb-1">Grab 10% OFF your first order</p>
            <p className="text-gray-500 text-sm mb-5">
              Join 5,000+ pet lovers who got their exclusive discount code.
            </p>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleClaim()}
              placeholder="your@email.com"
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 mb-3 focus:outline-none focus:border-primary"
            />
            <button onClick={handleClaim} className="btn-primary w-full">
              Get My 10% Discount 🐾
            </button>
            <button onClick={handleDismiss} className="mt-3 text-xs text-gray-400 hover:text-gray-500 w-full">
              No thanks, I'll pay full price
            </button>
          </>
        )}
      </div>
    </div>
  );
}
