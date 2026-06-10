import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../lib/auth';
import { db } from '../../../lib/db';

export async function GET(req) {
  const session = await getServerSession(authOptions);
  if (!session) return NextResponse.json({ error: 'غير مسموح' }, { status: 401 });

  let orders;
  if (session.user.role === 'ADMIN') {
    orders = await db.order.findMany({ include: { items: true, user: { select: { name: true, email: true } } }, orderBy: { createdAt: 'desc' } });
  } else {
    orders = await db.order.findMany({ where: { userId: session.user.id }, include: { items: true }, orderBy: { createdAt: 'desc' } });
  }
  return NextResponse.json(orders);
}

export async function POST(req) {
  try {
    const session = await getServerSession(authOptions);
    const body = await req.json();
    const { items, name, phone, city, address, payMethod, notes, total } = body;

    const order = await db.order.create({
      data: {
        userId:    session?.user?.id || null,
        total, name, phone, city, address, payMethod, notes,
        items: {
          create: items.map(i => ({
            productId: i.id,
            name:  i.name,
            price: i.price,
            qty:   i.qty,
            image: Array.isArray(i.images) ? (i.images[0] || '') : '',
          })),
        },
      },
      include: { items: true },
    });

    for (const item of items) {
      await db.product.update({
        where: { id: item.id },
        data:  { stock: { decrement: item.qty } },
      }).catch(() => {});
    }

    return NextResponse.json(order, { status: 201 });
  } catch (e) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
