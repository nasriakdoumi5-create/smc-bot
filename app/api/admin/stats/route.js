import { NextResponse } from 'next/server';
import { db } from '../../../../lib/db';

export async function GET() {
  const [totalOrders, totalProducts, totalUsers, recentOrders] = await Promise.all([
    db.order.count(),
    db.product.count(),
    db.user.count(),
    db.order.findMany({ take: 5, orderBy: { createdAt: 'desc' }, include: { items: true } }),
  ]);
  const revenue = await db.order.aggregate({ _sum: { total: true }, where: { status: 'DELIVERED' } });
  return NextResponse.json({
    totalOrders, totalProducts, totalUsers,
    revenue: revenue._sum.total || 0,
    recentOrders,
  });
}
