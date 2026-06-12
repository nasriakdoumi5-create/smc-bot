import { NextResponse } from 'next/server';

export async function GET() {
  const resendKey = process.env.RESEND_API_KEY;
  if (!resendKey) {
    return NextResponse.json({ error: 'RESEND_API_KEY not set in environment variables' }, { status: 503 });
  }

  try {
    const { Resend } = await import('resend');
    const resend = new Resend(resendKey);

    const result = await resend.emails.send({
      from: 'PawCase <onboarding@resend.dev>',
      to: 'nasriakdoumi5@gmail.com',
      subject: '✅ PawCase Email Test — Working!',
      html: `<div style="font-family:Arial;padding:32px;background:#f5f0e8;">
        <div style="max-width:500px;margin:0 auto;background:#fff;border-radius:12px;padding:32px;text-align:center;">
          <h1 style="color:#2D6A4F;">✅ PawCase Emails Work!</h1>
          <p style="color:#555;">Resend is configured correctly. Your store emails will now deliver.</p>
          <p style="color:#888;font-size:12px;">Sent at: ${new Date().toISOString()}</p>
        </div>
      </div>`,
    });

    return NextResponse.json({ success: true, id: result?.data?.id, result });
  } catch (err) {
    return NextResponse.json({ error: err.message, details: err }, { status: 500 });
  }
}
