'use client';

import { useState, useEffect } from 'react';
import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { getStripe } from '@/lib/stripe';
import { Lock } from 'lucide-react';

function PaymentForm({ finalTotal, orderMeta, orderNum, onBack, discount, shipping }) {
  const stripe = useStripe();
  const elements = useElements();
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!stripe || !elements) return;
    setLoading(true);
    setErrorMsg('');
    const result = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/order-success?order=${orderNum}&email=${encodeURIComponent(orderMeta.email)}&amount=${finalTotal.toFixed(2)}`,
      },
    });
    if (result.error) {
      setErrorMsg(result.error.message);
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
        <button
          type="button"
          onClick={onBack}
          style={{ background: 'none', border: 'none', color: '#2D6A4F', cursor: 'pointer', fontSize: '14px', padding: '4px 0' }}
        >
          ← Edit shipping
        </button>
        <span style={{ fontSize: '13px', color: '#555' }}>
          {orderMeta.firstName} {orderMeta.lastName} · {orderMeta.address}, {orderMeta.zip} {orderMeta.city}, {orderMeta.country}
        </span>
      </div>

      <PaymentElement options={{ layout: 'tabs' }} />

      {errorMsg && (
        <p style={{ color: '#c0392b', fontSize: '14px', marginTop: '12px' }}>{errorMsg}</p>
      )}

      <button
        type="submit"
        disabled={!stripe || loading}
        style={{
          marginTop: '20px',
          width: '100%',
          padding: '14px',
          backgroundColor: loading || !stripe ? '#aaa' : '#2D6A4F',
          color: '#fff',
          border: 'none',
          borderRadius: '8px',
          fontSize: '16px',
          fontWeight: '600',
          cursor: loading || !stripe ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
        }}
      >
        <Lock size={16} />
        {loading ? 'Processing…' : `Pay Securely €${finalTotal.toFixed(2)}`}
      </button>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '16px', fontSize: '12px', color: '#888' }}>
        <span>🔒 SSL Encrypted</span>
        <span>↩ 30-Day Returns</span>
        <span>✓ Secure Payment</span>
      </div>
    </form>
  );
}

export default function StripePaymentStep({ totalAmount, orderMeta, onBack, discount, shipping, finalTotal }) {
  const stripePromise = getStripe();
  const [clientSecret, setClientSecret] = useState('');
  const [orderNum] = useState('PW' + Date.now().toString().slice(-6));
  const [loadingIntent, setLoadingIntent] = useState(true);
  const [intentError, setIntentError] = useState('');

  useEffect(() => {
    if (!stripePromise) return;
    fetch('/api/create-payment-intent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        amount: finalTotal,
        currency: 'eur',
        metadata: {
          email: orderMeta.email,
          name: orderMeta.name,
          orderNum,
        },
      }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.clientSecret) {
          setClientSecret(data.clientSecret);
        } else {
          setIntentError('Could not initialise payment. Please try again.');
        }
      })
      .catch(() => setIntentError('Could not initialise payment. Please try again.'))
      .finally(() => setLoadingIntent(false));
  }, []);

  if (!process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY) return null;

  const appearance = { theme: 'stripe', variables: { colorPrimary: '#2D6A4F' } };

  return (
    <div style={{ maxWidth: '520px', margin: '0 auto' }}>
      <h2 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '20px', color: '#1a1a1a' }}>
        Payment
      </h2>

      <div style={{ background: '#f9fafb', borderRadius: '8px', padding: '12px 16px', marginBottom: '20px', fontSize: '13px', color: '#555' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Subtotal</span><span>€{totalAmount.toFixed(2)}</span>
        </div>
        {discount > 0 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#2D6A4F' }}>
            <span>Discount</span><span>−€{discount.toFixed(2)}</span>
          </div>
        )}
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Shipping</span><span>{shipping === 0 ? 'Free' : `€${shipping.toFixed(2)}`}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: '700', borderTop: '1px solid #e5e7eb', marginTop: '8px', paddingTop: '8px', color: '#1a1a1a' }}>
          <span>Total</span><span>€{finalTotal.toFixed(2)}</span>
        </div>
      </div>

      {loadingIntent && (
        <div style={{ textAlign: 'center', padding: '40px 0', color: '#888' }}>
          <div style={{
            width: '32px', height: '32px', border: '3px solid #e5e7eb',
            borderTop: '3px solid #2D6A4F', borderRadius: '50%',
            animation: 'spin 0.8s linear infinite', margin: '0 auto 12px',
          }} />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          <p style={{ fontSize: '14px' }}>Setting up secure payment…</p>
        </div>
      )}

      {intentError && (
        <p style={{ color: '#c0392b', fontSize: '14px', textAlign: 'center' }}>{intentError}</p>
      )}

      {!loadingIntent && clientSecret && (
        <Elements stripe={stripePromise} options={{ clientSecret, appearance }}>
          <PaymentForm
            finalTotal={finalTotal}
            orderMeta={orderMeta}
            orderNum={orderNum}
            onBack={onBack}
          />
        </Elements>
      )}
    </div>
  );
}
