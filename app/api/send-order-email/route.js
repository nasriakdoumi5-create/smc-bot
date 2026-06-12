import { NextResponse } from 'next/server';

export async function POST(req) {
  if (!process.env.RESEND_API_KEY) {
    return NextResponse.json({ error: 'Email service not configured' }, { status: 503 });
  }

  const { email, orderNum, amount, name, items } = await req.json();

  const deliveryDate = new Date();
  deliveryDate.setDate(deliveryDate.getDate() + 5);
  const estimatedDelivery = deliveryDate.toLocaleDateString('en-GB', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  const itemsHtml =
    items && items.length > 0
      ? `<table width="100%" cellpadding="0" cellspacing="0" style="margin:16px 0;border-collapse:collapse;">
          ${items
            .map(
              (item) => `<tr>
            <td style="padding:8px 0;border-bottom:1px solid #e5e7eb;font-size:14px;color:#333;">
              ${item.name}${item.quantity > 1 ? ` × ${item.quantity}` : ''}
            </td>
            <td style="padding:8px 0;border-bottom:1px solid #e5e7eb;font-size:14px;color:#333;text-align:right;">
              €${(item.price * (item.quantity || 1)).toFixed(2)}
            </td>
          </tr>`
            )
            .join('')}
        </table>`
      : '';

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>Order Confirmed</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f5;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06);">

          <!-- Header -->
          <tr>
            <td style="background:#2D6A4F;padding:32px 40px;text-align:center;">
              <p style="margin:0;font-size:32px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">PawCase 🐾</p>
              <p style="margin:8px 0 0;font-size:15px;color:#b7dfc9;">Premium custom phone cases for pet lovers</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px 40px 0;">
              <p style="margin:0 0 8px;font-size:22px;font-weight:700;color:#1a1a1a;">Hi ${name},</p>
              <p style="margin:0 0 24px;font-size:16px;color:#555;">Thank you for your order! We&apos;re already getting started on your custom PawCase.</p>

              <!-- Order box -->
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;border-radius:8px;border:1px solid #e5e7eb;margin-bottom:28px;">
                <tr>
                  <td style="padding:24px;">
                    <p style="margin:0 0 16px;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;color:#888;">Order Summary</p>
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="font-size:14px;color:#555;padding:4px 0;">Order number</td>
                        <td style="font-size:14px;font-weight:600;color:#1a1a1a;text-align:right;">${orderNum}</td>
                      </tr>
                      <tr>
                        <td style="font-size:14px;color:#555;padding:4px 0;">Amount paid</td>
                        <td style="font-size:14px;font-weight:600;color:#1a1a1a;text-align:right;">€${Number(amount).toFixed(2)}</td>
                      </tr>
                      <tr>
                        <td style="font-size:14px;color:#555;padding:4px 0;">Estimated delivery</td>
                        <td style="font-size:14px;font-weight:600;color:#2D6A4F;text-align:right;">${estimatedDelivery}</td>
                      </tr>
                    </table>
                    ${itemsHtml}
                  </td>
                </tr>
              </table>

              <!-- What happens next -->
              <p style="margin:0 0 16px;font-size:16px;font-weight:700;color:#1a1a1a;">What happens next?</p>
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
                ${[
                  ['Printing', 'Your design is sent to our printing facility.'],
                  ['Quality check', 'Every case is inspected before it leaves us.'],
                  ['Shipping with tracking', "You'll receive a tracking link by email."],
                  ['Enjoy!', 'Show off your PawCase to the world 🐾'],
                ]
                  .map(
                    ([title, desc], i) => `<tr>
                  <td style="padding:10px 0;vertical-align:top;">
                    <table cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="width:28px;height:28px;background:#2D6A4F;border-radius:50%;text-align:center;vertical-align:middle;font-size:13px;font-weight:700;color:#fff;flex-shrink:0;">${i + 1}</td>
                        <td style="padding-left:12px;vertical-align:top;">
                          <p style="margin:0 0 2px;font-size:14px;font-weight:600;color:#1a1a1a;">${title}</p>
                          <p style="margin:0;font-size:13px;color:#666;">${desc}</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>`
                  )
                  .join('')}
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f9fafb;border-top:1px solid #e5e7eb;padding:24px 40px;text-align:center;">
              <p style="margin:0 0 6px;font-size:13px;color:#888;">Questions? Reply to this email or contact us at <a href="mailto:hello@pawcase.eu" style="color:#2D6A4F;text-decoration:none;">hello@pawcase.eu</a></p>
              <p style="margin:0;font-size:13px;color:#aaa;">30-day hassle-free returns guaranteed &nbsp;·&nbsp; PawCase</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;

  const { Resend } = await import('resend');
  const resend = new Resend(process.env.RESEND_API_KEY);

  const { error } = await resend.emails.send({
    from: 'PawCase <orders@pawcase.eu>',
    to: email,
    subject: `Your PawCase order ${orderNum} is confirmed! 🐾`,
    html,
  });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ success: true });
}
