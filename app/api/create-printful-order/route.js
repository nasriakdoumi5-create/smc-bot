import { NextResponse } from 'next/server';
import { createPrintfulOrder } from '@/lib/printful';

export async function POST(req) {
  if (!process.env.PRINTFUL_API_KEY) {
    return NextResponse.json({ error: 'Printful not configured' }, { status: 503 });
  }

  try {
    const { recipient, items, orderNum } = await req.json();

    if (!recipient || !items?.length || !orderNum) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    const order = await createPrintfulOrder({ recipient, items, orderNum });
    console.log(`Printful order created: ${order.id} (${orderNum})`);
    return NextResponse.json({ success: true, printfulOrderId: order.id });
  } catch (err) {
    console.error('Printful order error:', err.message);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
