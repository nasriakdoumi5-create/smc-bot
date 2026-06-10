import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../lib/auth';
import { db } from '../../../lib/db';

export async function POST(req) {
  const session = await getServerSession(authOptions);
  if (!session) return NextResponse.json({ error: 'يجب تسجيل الدخول' }, { status: 401 });
  const { productId, rating, comment } = await req.json();
  const review = await db.review.upsert({
    where:  { userId_productId: { userId: session.user.id, productId } },
    update: { rating, comment },
    create: { userId: session.user.id, productId, rating, comment },
    include: { user: { select: { name: true } } },
  });
  return NextResponse.json(review);
}
