import { NextResponse } from 'next/server';

export async function POST(req) {
  const resendKey = process.env.RESEND_API_KEY;
  if (!resendKey) return NextResponse.json({ ok: true });

  try {
    const { email } = await req.json();
    if (!email || !email.includes('@')) return NextResponse.json({ ok: true });

    const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://ecommerce-store-smoky-ten.vercel.app';

    const html = `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f0e8;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:20px auto;background:#fff;border-radius:12px;overflow:hidden;">
    <div style="background:#2D6A4F;padding:28px 24px;text-align:center;">
      <h1 style="margin:0;color:#fff;font-size:26px;">PawCase 🐾</h1>
    </div>
    <div style="padding:32px 24px;text-align:center;">
      <div style="font-size:48px;margin-bottom:16px;">🎉</div>
      <h2 style="margin:0 0 8px;color:#1A1A2E;font-size:22px;">Your 10% discount is ready!</h2>
      <p style="color:#555;line-height:1.6;margin:0 0 24px;">Use this code at checkout and save on your first PawCase order:</p>
      <div style="background:#fff3f0;border:2px dashed #FF6B35;border-radius:10px;padding:20px;margin-bottom:24px;display:inline-block;min-width:200px;">
        <p style="margin:0 0 4px;font-size:12px;color:#888;text-transform:uppercase;letter-spacing:1px;">Your exclusive code</p>
        <p style="margin:0;font-size:28px;font-weight:bold;color:#FF6B35;letter-spacing:3px;">PAWS10</p>
      </div>
      <br/>
      <a href="${siteUrl}/products?coupon=PAWS10" style="display:inline-block;background:#2D6A4F;color:#fff;padding:14px 32px;border-radius:50px;font-size:16px;font-weight:bold;text-decoration:none;margin-bottom:24px;">
        Shop Now & Save 10% →
      </a>
      <div style="border-top:1px solid #eee;padding-top:20px;margin-top:8px;display:flex;gap:16px;justify-content:center;text-align:center;">
        <div style="flex:1;"><div style="font-size:18px;">🚚</div><div style="font-size:11px;color:#888;margin-top:4px;">Free EU Shipping over €40</div></div>
        <div style="flex:1;"><div style="font-size:18px;">🔄</div><div style="font-size:11px;color:#888;margin-top:4px;">30-Day Returns</div></div>
        <div style="flex:1;"><div style="font-size:18px;">⭐</div><div style="font-size:11px;color:#888;margin-top:4px;">5,000+ Happy Customers</div></div>
      </div>
    </div>
    <div style="background:#f5f0e8;padding:16px 24px;text-align:center;">
      <p style="margin:0;color:#aaa;font-size:11px;">© 2025 PawCase · <a href="mailto:hello@pawcase.eu" style="color:#888;">hello@pawcase.eu</a></p>
    </div>
  </div>
</body>
</html>`;

    const { Resend } = await import('resend');
    const resend = new Resend(resendKey);
    await resend.emails.send({
      from: 'PawCase <onboarding@resend.dev>',
      to: email,
      subject: 'Your exclusive 10% off is here 🐾',
      html,
    });

    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error('Save lead error:', err);
    return NextResponse.json({ ok: true });
  }
}
