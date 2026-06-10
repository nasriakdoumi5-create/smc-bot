import { NextResponse } from 'next/server';
import { db } from '../../../../lib/db';

export async function PATCH(req, { params }) {
  const { status } = await req.json();
  const order = await db.order.update({ where: { id: params.id }, data: { status } });
  return NextResponse.json(order);
}
