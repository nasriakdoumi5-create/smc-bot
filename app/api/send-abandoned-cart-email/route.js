import { NextResponse } from 'next/server';

export async function POST(req) {
  const resendKey = process.env.RESEND_API_KEY;
  if (!resendKey) {
    return NextResponse.json({ error: 'Not configured' }, { status: 503 });
  }

  try {
    const { email, name, items = [], total } = await req.json();
    if (!email) return NextResponse.json({ error: 'Email required' }, { status: 400 });

    const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://ecommerce-store-smoky-ten.vercel.app';
    const cartUrl = `${siteUrl}/checkout?coupon=PAWS10`;
    const firstName = name?.split(' ')[0] || 'there';

    const itemsHtml = items.map(item => `
      <tr>
        <td style="padding:8px;border-bottom:1px solid #eee;">
          <strong>${item.name}</strong><br/>
          <span style="color:#666;font-size:12px;">${item.model || ''} × ${item.qty}</span>
        </td>
        <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;font-weight:bold;">
          €${(item.price * item.qty).toFixed(2)}
        </td>
      </tr>
    `).join('');

    const html = `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f0e8;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;margin-top:20px;margin-bottom:20px;">

    <div style="background:#2D6A4F;padding:32px 24px;text-align:center;">
      <h1 style="margin:0;color:#fff;font-size:28px;letter-spacing:-0.5px;">PawCase 🐾</h1>
      <p style="margin:8px 0 0;color:#a8d5be;font-size:14px;">You left something behind...</p>
    </div>

    <div style="padding:32px 24px;">
      <h2 style="margin:0 0 8px;color:#1A1A2E;font-size:22px;">Hey ${firstName}, your cart misses you!</h2>
      <p style="color:#555;line-height:1.6;margin:0 0 24px;">You were so close! Your pet is still waiting to become a phone case. We saved your cart — and we're giving you an extra <strong style="color:#FF6B35;">10% off</strong> to come back.</p>

      ${items.length > 0 ? `
      <table style="width:100%;border-collapse:collapse;margin-bottom:24px;">
        <thead>
          <tr style="background:#f5f0e8;">
            <th style="padding:10px 8px;text-align:left;font-size:12px;color:#666;font-weight:600;text-transform:uppercase;">Item</th>
            <th style="padding:10px 8px;text-align:right;font-size:12px;color:#666;font-weight:600;text-transform:uppercase;">Price</th>
          </tr>
        </thead>
        <tbody>${itemsHtml}</tbody>
        <tfoot>
          <tr>
            <td style="padding:12px 8px;font-weight:bold;font-size:16px;">Total</td>
            <td style="padding:12px 8px;font-weight:bold;font-size:16px;text-align:right;color:#FF6B35;">€${parseFloat(total || 0).toFixed(2)}</td>
          </tr>
        </tfoot>
      </table>
      ` : ''}

      <div style="background:#fff3f0;border:2px solid #FF6B35;border-radius:10px;padding:16px;margin-bottom:24px;text-align:center;">
        <p style="margin:0 0 4px;font-size:13px;color:#666;">Use code at checkout for 10% off:</p>
        <p style="margin:0;font-size:24px;font-weight:bold;color:#FF6B35;letter-spacing:2px;">PAWS10</p>
      </div>

      <div style="text-align:center;margin-bottom:24px;">
        <a href="${cartUrl}" style="display:inline-block;background:#2D6A4F;color:#fff;padding:16px 36px;border-radius:50px;font-size:16px;font-weight:bold;text-decoration:none;letter-spacing:0.3px;">
          Complete My Order →
        </a>
      </div>

      <p style="color:#555;line-height:1.6;font-size:14px;text-align:center;">Your cart is saved for <strong>24 hours</strong>. Don't let your pet miss out!</p>

      <div style="border-top:1px solid #eee;padding-top:20px;margin-top:20px;display:flex;gap:16px;justify-content:center;text-align:center;">
        <div style="flex:1;min-width:120px;">
          <div style="font-size:20px;margin-bottom:4px;">🚚</div>
          <div style="font-size:12px;font-weight:600;color:#2D6A4F;">Fast EU Shipping</div>
          <div style="font-size:11px;color:#888;">3–5 business days</div>
        </div>
        <div style="flex:1;min-width:120px;">
          <div style="font-size:20px;margin-bottom:4px;">🔄</div>
          <div style="font-size:12px;font-weight:600;color:#2D6A4F;">30-Day Returns</div>
          <div style="font-size:11px;color:#888;">Hassle-free guarantee</div>
        </div>
        <div style="flex:1;min-width:120px;">
          <div style="font-size:20px;margin-bottom:4px;">⭐</div>
          <div style="font-size:12px;font-weight:600;color:#2D6A4F;">5,000+ Happy Pets</div>
          <div style="font-size:11px;color:#888;">Rated 4.9/5</div>
        </div>
      </div>
    </div>

    <div style="background:#f5f0e8;padding:20px 24px;text-align:center;">
      <p style="margin:0 0 8px;color:#888;font-size:12px;">Questions? <a href="mailto:hello@pawcase.eu" style="color:#2D6A4F;">hello@pawcase.eu</a></p>
      <p style="margin:0;color:#aaa;font-size:11px;">© 2025 PawCase. You're receiving this because you started a checkout.</p>
      <p style="margin:4px 0 0;"><a href="#" style="color:#aaa;font-size:11px;">Unsubscribe</a></p>
    </div>
  </div>
</body>
</html>`;

    const { Resend } = await import('resend');
    const resend = new Resend(resendKey);

    await resend.emails.send({
      from: 'PawCase <hello@pawcase.eu>',
      to: email,
      subject: `${firstName}, you left something behind 🐾 — 10% off inside`,
      html,
    });

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error('Abandoned cart email error:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
