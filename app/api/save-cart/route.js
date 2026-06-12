import { NextResponse } from 'next/server';

const ABANDON_DELAY_MS = 30 * 60 * 1000; // 30 minutes

export async function POST(req) {
  try {
    const { email, name, items, total } = await req.json();
    if (!email || !items?.length) {
      return NextResponse.json({ ok: true });
    }

    // Schedule abandoned cart email after 30 minutes
    // We use a fire-and-forget approach with a delayed fetch
    // In production, use a job queue (Vercel Cron or Upstash)
    setTimeout(async () => {
      try {
        const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://ecommerce-store-smoky-ten.vercel.app';
        await fetch(`${siteUrl}/api/send-abandoned-cart-email`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, name, items, total }),
        });
      } catch (e) {
        console.error('Abandoned cart email failed:', e);
      }
    }, ABANDON_DELAY_MS);

    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ ok: true });
  }
}
