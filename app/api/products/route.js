import { NextResponse } from 'next/server';
import { db } from '../../../lib/db';

export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const category = searchParams.get('category');
  const search   = searchParams.get('search');
  const featured = searchParams.get('featured');
  const sort     = searchParams.get('sort') || 'createdAt';

  const where = {};
  if (category && category !== 'all') where.category = { slug: category };
  if (featured === 'true') where.featured = true;
  if (search) where.name = { contains: search };

  const orderBy = sort === 'price-asc'  ? { price: 'asc' }
                : sort === 'price-desc' ? { price: 'desc' }
                : sort === 'rating'     ? { createdAt: 'desc' }
                :                        { createdAt: 'desc' };

  const products = await db.product.findMany({
    where,
    include: {
      category: true,
      reviews: { select: { rating: true } },
      _count: { select: { reviews: true } },
    },
    orderBy,
  });

  return NextResponse.json(products.map(p => ({
    ...p,
    images:  JSON.parse(p.images),
    avgRating: p.reviews.length ? (p.reviews.reduce((s, r) => s + r.rating, 0) / p.reviews.length).toFixed(1) : 0,
    reviewCount: p._count.reviews,
  })));
}

export async function POST(req) {
  try {
    const data = await req.json();
    const product = await db.product.create({
      data: { ...data, images: JSON.stringify(data.images || []) },
    });
    return NextResponse.json(product, { status: 201 });
  } catch (e) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
