import { NextResponse } from 'next/server';

const AUTO_REPLIES = [
  {
    keywords: ['order', 'tracking', 'track', 'طلب', 'تتبع', 'where is'],
    reply: `Your order is being carefully prepared! 🐾\n\nOrders ship in 1–3 business days and arrive in 3–5 days. Check your confirmation email for tracking updates.\n\nNeed help? Email us: hello@pawcase.eu`,
  },
  {
    keywords: ['return', 'refund', 'exchange', 'إرجاع', 'استرداد'],
    reply: `We have a 30-day hassle-free return policy! 🐾\n\nJust email us at hello@pawcase.eu with your order number and we'll sort everything out quickly.`,
  },
  {
    keywords: ['shipping', 'delivery', 'ship', 'how long', 'شحن', 'توصيل'],
    reply: `We ship from our EU facility! 🚚\n\n• Delivery: 3–5 business days\n• Fully tracked shipment\n• Free shipping on orders over €40\n\nAny more questions? We're here!`,
  },
  {
    keywords: ['price', 'cost', 'how much', 'cheap', 'سعر', 'ثمن'],
    reply: `Our cases start at just €22! 🐾\n\nSee all designs at:\nwww.pawcase.eu/products\n\nCustom pet cases from €35 — your pet's actual photo!`,
  },
  {
    keywords: ['custom', 'photo', 'upload', 'my pet', 'مخصص', 'صورة'],
    reply: `Custom pet cases are our specialty! 📸\n\nUpload your pet's photo and we'll make a stunning case:\nwww.pawcase.eu/product/custom-pet-phone-case\n\n✅ Mockup sent within 24 hours\n✅ We don't print until you approve\n✅ Museum-quality UV print`,
  },
  {
    keywords: ['iphone', 'samsung', 'galaxy', 'model', 'models', 'موديل'],
    reply: `We support all major models! 📱\n\niPhone: 12, 13, 14, 15, 16 (all Pro versions too)\nSamsung: S22, S23, S24, S25, S26\n\nSelect your model at checkout:\nwww.pawcase.eu/products`,
  },
];

function twiml(message) {
  const escaped = message
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  return `<?xml version="1.0" encoding="UTF-8"?><Response><Message>${escaped}</Message></Response>`;
}

export async function POST(req) {
  const text = await req.text();
  const params = new URLSearchParams(text);
  const incoming = (params.get('Body') || '').toLowerCase().trim();

  let reply = `Hi! Thanks for contacting PawCase 🐾\n\nI can help with:\n• Order tracking\n• Shipping & delivery\n• Returns & refunds\n• Product info\n• Custom pet cases\n\nOr visit: www.pawcase.eu\nEmail: hello@pawcase.eu`;

  for (const { keywords, reply: r } of AUTO_REPLIES) {
    if (keywords.some((kw) => incoming.includes(kw))) {
      reply = r;
      break;
    }
  }

  return new NextResponse(twiml(reply), {
    headers: { 'Content-Type': 'text/xml' },
  });
}
