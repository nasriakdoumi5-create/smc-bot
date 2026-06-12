import { NextResponse } from 'next/server';

export async function POST(req) {
  const secretKey = process.env.STRIPE_SECRET_KEY;
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!secretKey || !webhookSecret) {
    return NextResponse.json({ error: 'Not configured' }, { status: 503 });
  }

  const Stripe = (await import('stripe')).default;
  const stripe = new Stripe(secretKey, { apiVersion: '2024-04-10' });

  const body = await req.text();
  const sig = req.headers.get('stripe-signature');

  let event;
  try {
    event = stripe.webhooks.constructEvent(body, sig, webhookSecret);
  } catch (err) {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  if (event.type === 'payment_intent.succeeded') {
    const pi = event.data.object;
    const email = pi.metadata?.email;
    const orderNum = pi.metadata?.orderNum || 'PW' + Date.now().toString().slice(-6);

    if (email) {
      try {
        await fetch(`${process.env.NEXT_PUBLIC_SITE_URL}/api/send-order-email`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email,
            orderNum,
            amount: (pi.amount / 100).toFixed(2),
            name: pi.metadata?.name || '',
          }),
        });
      } catch (e) {
        console.error('Email send failed:', e);
      }
    }
  }

  return NextResponse.json({ received: true });
}
