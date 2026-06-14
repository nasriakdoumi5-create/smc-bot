import { NextResponse } from 'next/server';

const PRINTFUL_API = 'https://api.printful.com';

async function pf(path) {
  const res = await fetch(`${PRINTFUL_API}${path}`, {
    headers: {
      Authorization: `Bearer ${process.env.PRINTFUL_API_KEY}`,
      'X-PF-Store-Id': '18330357',
    },
  });
  return res.json();
}

export async function GET() {
  if (!process.env.PRINTFUL_API_KEY) {
    return NextResponse.json({ error: 'Printful not configured' }, { status: 503 });
  }

  try {
    // Try multiple endpoints to diagnose
    const [store, products] = await Promise.all([
      pf('/store'),
      pf('/store/products?limit=100'),
    ]);

    if (!products.result?.length) {
      return NextResponse.json({
        debug: true,
        store: store.result,
        products_raw: products,
        message: 'No sync products found. Check store connection.',
      });
    }

    const details = await Promise.all(
      products.result.map(async (p) => {
        const d = await pf(`/store/products/${p.id}`);
        return {
          id: p.id,
          name: p.name,
          variants: (d.result?.sync_variants || []).map((v) => ({
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
