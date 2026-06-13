import { NextResponse } from 'next/server';

export async function GET() {
  const key = process.env.RESEND_API_KEY;
  if (!key) return NextResponse.json({ status: 'ERROR', problem: 'RESEND_API_KEY not set in Vercel' }, { status: 500 });
  try {
    const { Resend } = await import('resend');
    const resend = new Resend(key);
    const r = await resend.emails.send({
      from: 'PawCase <onboarding@resend.dev>',
      to: 'nasriakdoumi5@gmail.com',
      subject: '✅ PawCase Test Email',
      html: '<h1>✅ يعمل! Check Gmail now</h1>',
    });
    return NextResponse.json({ status: 'SENT', id: r?.data?.id, error: r?.error });
  } catch (e) {
    return NextResponse.json({ status: 'ERROR', problem: e.message }, { status: 500 });
  }
}

export async function POST(req) {
  try {
    const { email, name, items, total } = await req.json();
    if (!email || !items?.length) return NextResponse.json({ ok: true });

    const resendKey = process.env.RESEND_API_KEY;
    if (!resendKey) return NextResponse.json({ ok: true });

    const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://ecommerce-store-smoky-ten.vercel.app';
    const firstName = name?.split(' ')[0] || 'there';
    const checkoutUrl = `${siteUrl}/checkout?coupon=PAWS10`;

    const itemsHtml = items.map(item => `
      <tr>
        <td style="padding:8px 4px;border-bottom:1px solid #f0f0f0;">
          <strong style="color:#1A1A2E;">${item.name}</strong><br>
          <span style="color:#888;font-size:12px;">${item.model || ''} × ${item.qty}</span>
        </td>
        <td style="padding:8px 4px;border-bottom:1px solid #f0f0f0;text-align:right;font-weight:700;color:#FF6B35;">
          €${(item.price * item.qty).toFixed(2)}
        </td>
      </tr>
    `).join('');

    const html = `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f0e8;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:20px auto;background:#fff;border-radius:12px;overflow:hidden;">
    <div style="background:#2D6A4F;padding:28px 24px;text-align:center;">
      <h1 style="margin:0;color:#fff;font-size:26px;">PawCase 🐾</h1>
      <p style="margin:8px 0 0;color:#a8d5be;font-size:13px;">Your cart is saved and waiting</p>
    </div>
    <div style="padding:32px 24px;">
      <h2 style="margin:0 0 8px;color:#1A1A2E;font-size:22px;">Hey ${firstName}, your cart is saved!</h2>
      <p style="color:#555;line-height:1.6;margin:0 0 24px;">Your items are reserved. Complete your order whenever you're ready — and here's an extra <strong style="color:#FF6B35;">10% off</strong> on us.</p>

      <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
        <tbody>${itemsHtml}</tbody>
        <tfoot>
          <tr>
            <td style="padding:12px 4px;font-weight:bold;font-size:15px;color:#1A1A2E;">Total</td>
            <td style="padding:12px 4px;font-weight:bold;font-size:15px;text-align:right;color:#FF6B35;">€${parseFloat(total || 0).toFixed(2)}</td>
          </tr>
        </tfoot>
      </table>

      <div style="background:#fff3f0;border:2px dashed #FF6B35;border-radius:10px;padding:16px;margin-bottom:24px;text-align:center;">
        <p style="margin:0 0 4px;font-size:12px;color:#888;text-transform:uppercase;letter-spacing:1px;">Extra 10% off — use at checkout</p>
        <p style="margin:0;font-size:26px;font-weight:bold;color:#FF6B35;letter-spacing:3px;">PAWS10</p>
      </div>

      <div style="text-align:center;margin-bottom:20px;">
        <a href="${checkoutUrl}" style="display:inline-block;background:#2D6A4F;color:#fff;padding:16px 36px;border-radius:50px;font-size:16px;font-weight:bold;text-decoration:none;">
          Complete My Order →
        </a>
      </div>

      <div style="border-top:1px solid #eee;padding-top:20px;display:flex;gap:12px;justify-content:center;text-align:center;">
        <div style="flex:1;"><div style="font-size:20px;">🚚</div><div style="font-size:11px;color:#888;margin-top:4px;">Free EU Shipping over €40</div></div>
        <div style="flex:1;"><div style="font-size:20px;">🔄</div><div style="font-size:11px;color:#888;margin-top:4px;">30-Day Returns</div></div>
        <div style="flex:1;"><div style="font-size:20px;">⭐</div><div style="font-size:11px;color:#888;margin-top:4px;">Rated 4.9/5</div></div>
      </div>
    </div>
    <div style="background:#f5f0e8;padding:16px 24px;text-align:center;">
      <p style="margin:0 0 4px;color:#aaa;font-size:11px;">© 2025 PawCase · <a href="mailto:hello@pawcase.eu" style="color:#888;">hello@pawcase.eu</a></p>
      <p style="margin:0;"><a href="#" style="color:#aaa;font-size:11px;">Unsubscribe</a></p>
    </div>
  </div>
</body>
</html>`;

    const { Resend } = await import('resend');
    const resend = new Resend(resendKey);
    await resend.emails.send({
      from: 'PawCase <onboarding@resend.dev>',
      to: email,
      subject: `${firstName}, your cart is saved — 10% off inside 🐾`,
      html,
    });

    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error('Save cart error:', err);
    return NextResponse.json({ ok: true });
  }
}
