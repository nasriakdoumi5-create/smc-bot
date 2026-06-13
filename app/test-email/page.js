import { Resend } from 'resend';

export const dynamic = 'force-dynamic';

export default async function TestEmailPage() {
  const resendKey = process.env.RESEND_API_KEY;

  if (!resendKey) {
    return (
      <div style={{ fontFamily: 'monospace', padding: 40, background: '#fff3f0', minHeight: '100vh' }}>
        <h1 style={{ color: '#e53e3e' }}>❌ RESEND_API_KEY غير موجود</h1>
        <p>المتغير <code>RESEND_API_KEY</code> غير مضاف في Vercel Environment Variables.</p>
        <p>اذهب إلى: <strong>Vercel → Project → Settings → Environment Variables</strong></p>
      </div>
    );
  }

  let result = null;
  let error = null;

  try {
    const resend = new Resend(resendKey);
    const response = await resend.emails.send({
      from: 'PawCase <onboarding@resend.dev>',
      to: 'nasriakdoumi5@gmail.com',
      subject: '✅ PawCase Email Test — Working!',
      html: `<div style="font-family:Arial;padding:32px;background:#f5f0e8;">
        <div style="max-width:500px;margin:0 auto;background:#fff;border-radius:12px;padding:32px;text-align:center;">
          <h1 style="color:#2D6A4F;">✅ Resend يعمل!</h1>
          <p style="color:#555;">تحقق من بريدك الإلكتروني الآن.</p>
          <p style="color:#888;font-size:12px;">Sent: ${new Date().toISOString()}</p>
        </div>
      </div>`,
    });
    result = response;
  } catch (err) {
    error = err.message;
  }

  return (
    <div style={{ fontFamily: 'monospace', padding: 40, minHeight: '100vh', background: error ? '#fff3f0' : '#f0fff4' }}>
      {error ? (
        <>
          <h1 style={{ color: '#e53e3e' }}>❌ خطأ في الإرسال</h1>
          <p><strong>الخطأ:</strong> {error}</p>
          <p><strong>API Key موجود:</strong> ✅ نعم (أول 8 أحرف: {resendKey.slice(0, 8)}...)</p>
        </>
      ) : (
        <>
          <h1 style={{ color: '#2D6A4F' }}>✅ تم الإرسال بنجاح!</h1>
          <p>تحقق من Gmail الآن (وأيضاً مجلد Spam)</p>
          <p><strong>Email ID:</strong> {result?.data?.id}</p>
        </>
      )}
    </div>
  );
}
