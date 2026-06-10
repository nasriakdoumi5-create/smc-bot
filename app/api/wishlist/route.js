import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../lib/auth';
import { db } from '../../../lib/db';

export async function GET() {
  const session = await getServerSession(authOptions);
  if (!session) return NextResponse.json([]);
  const items = await db.wishlistItem.findMany({
    where: { userId: session.user.id },
    include: { product: { include: { category: true } } },
  });
  return NextResponse.json(items.map(i => ({ ...i.product, images: JSON.parse(i.product.images) })));
}

export async function POST(req) {
  const session = await getServerSession(authOptions);
  if (!session) return NextResponse.json({ error: 'يجب تسجيل الدخول' }, { status: 401 });
  const { productId } = await req.json();
  const existing = await db.wishlistItem.findUnique({ where: { userId_productId: { userId: session.user.id, productId } } });
  if (existing) {
    await db.wishlistItem.delete({ where: { id: existing.id } });
    return NextResponse.json({ action: 'removed' });
  }
  await db.wishlistItem.create({ data: { userId: session.user.id, productId } });
  return NextResponse.json({ action: 'added' });
}
