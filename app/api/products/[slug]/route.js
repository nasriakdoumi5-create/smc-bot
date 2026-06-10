import { NextResponse } from 'next/server';
import { db } from '../../../../lib/db';

export async function GET(req, { params }) {
  const product = await db.product.findUnique({
    where: { slug: params.slug },
    include: {
      category: true,
      reviews: { include: { user: { select: { name: true } } }, orderBy: { createdAt: 'desc' } },
      _count: { select: { reviews: true } },
    },
  });
  if (!product) return NextResponse.json({ error: 'غير موجود' }, { status: 404 });
  return NextResponse.json({
    ...product,
    images: JSON.parse(product.images),
    avgRating: product.reviews.length ? (product.reviews.reduce((s, r) => s + r.rating, 0) / product.reviews.length).toFixed(1) : 0,
  });
}

export async function PUT(req, { params }) {
  try {
    const data = await req.json();
    if (data.images) data.images = JSON.stringify(data.images);
    const product = await db.product.update({ where: { slug: params.slug }, data });
    return NextResponse.json(product);
  } catch (e) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}

export async function DELETE(req, { params }) {
  await db.product.delete({ where: { slug: params.slug } });
  return NextResponse.json({ ok: true });
}
