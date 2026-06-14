import { NextResponse } from 'next/server';
import { getSyncProducts, getSyncProductDetail } from '@/lib/printful';

// Admin endpoint to inspect Printful sync products and variant IDs
export async function GET() {
  if (!process.env.PRINTFUL_API_KEY) {
    return NextResponse.json({ error: 'Printful not configured' }, { status: 503 });
  }

  try {
    const products = await getSyncProducts();
    const details = await Promise.all(
      products.map(async (p) => {
        const d = await getSyncProductDetail(p.id);
        return {
          id: p.id,
          name: p.name,
          variants: (d.sync_variants || []).map((v) => ({
            id: v.id,
            name: v.name,
            sku: v.sku,
          })),
        };
      })
    );
    return NextResponse.json({ products: details });
  } catch (err) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
