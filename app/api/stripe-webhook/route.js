import { NextResponse } from 'next/server';
import { createPrintfulOrder } from '@/lib/printful';

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
    const meta = pi.metadata || {};
    const { email, name, orderNum: rawOrderNum, address, city, country, zip, ic } = meta;
    const orderNum = rawOrderNum || 'PW' + Date.now().toString().slice(-6);
    const amountEur = (pi.amount / 100).toFixed(2);

    // Reconstruct items from per-item metadata keys (i0, i1, ...)
    const itemCount = parseInt(ic || '0', 10);
    const items = [];
    for (let i = 0; i < itemCount; i++) {
      const raw = meta[`i${i}`];
      if (raw) {
        const [id, model, qty, price] = raw.split('|');
        items.push({ id, model: model.replace(/_/g, '|'), qty: parseInt(qty, 10), price: parseFloat(price) });
      }
    }

    // Fallback for legacy single-item JSON format
    if (items.length === 0 && meta.items) {
      try {
        items.push(...JSON.parse(meta.items));
      } catch {}
    }

    // 1 — Printful fulfillment
    if (process.env.PRINTFUL_API_KEY && items.length > 0 && address) {
      try {
        await createPrintfulOrder({
          orderNum,
          recipient: { name, email, address, city, country, zip },
          items,
        });
        console.log(`Printful order created: ${orderNum}`);
      } catch (e) {
        console.error('Printful fulfillment failed:', e.message);
      }
    }

    const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://www.pawcase.eu';

    // 2 — Customer confirmation email
    if (email && process.env.RESEND_API_KEY) {
      try {
        const emailItems = items.map((item) => ({
          name: item.model ? `${item.model} Case` : 'Phone Case',
          quantity: item.qty,
          price: item.price,
        }));
        await fetch(`${siteUrl}/api/send-order-email`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, orderNum, amount: amountEur, name: name || '', items: emailItems }),
        });
      } catch (e) {
        console.error('Customer email failed:', e);
      }
    }

    // 3 — Admin notification
    if (process.env.RESEND_API_KEY) {
      try {
        const { Resend } = await import('resend');
        const resend = new Resend(process.env.RESEND_API_KEY);
        const itemLines = items
          .map((i) => `<li>${i.model || i.id} × ${i.qty} — €${Number(i.price).toFixed(2)}</li>`)
          .join('');
        await resend.emails.send({
          from: 'PawCase Orders <hello@pawcase.eu>',
          to: 'nasriakdoumi5@gmail.com',
          subject: `New order ${orderNum} — €${amountEur}`,
          html: `<h2 style="color:#2D6A4F">New PawCase Order 🐾</h2>
<p><strong>Order:</strong> ${orderNum}</p>
<p><strong>Amount:</strong> €${amountEur}</p>
<p><strong>Customer:</strong> ${name || 'N/A'} — <a href="mailto:${email}">${email || 'N/A'}</a></p>
<p><strong>Address:</strong> ${address || 'N/A'}, ${city || ''}, ${zip || ''}, ${country || ''}</p>
<h3>Items:</h3><ul>${itemLines || '<li>No item data</li>'}</ul>`,
        });
      } catch (e) {
        console.error('Admin notification failed:', e);
      }
    }
  }

  return NextResponse.json({ received: true });
}
