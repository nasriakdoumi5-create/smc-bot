import { NextResponse } from 'next/server';
import bcrypt from 'bcryptjs';
import { db } from '../../../lib/db';

export async function POST(req) {
  try {
    const { name, email, password, phone } = await req.json();
    if (!name || !email || !password) return NextResponse.json({ error: 'البيانات ناقصة' }, { status: 400 });
    const exists = await db.user.findUnique({ where: { email } });
    if (exists) return NextResponse.json({ error: 'البريد الإلكتروني مسجل مسبقاً' }, { status: 400 });
    const hashed = await bcrypt.hash(password, 10);
    const user = await db.user.create({ data: { name, email, password: hashed, phone } });
    return NextResponse.json({ id: user.id, name: user.name, email: user.email });
  } catch (e) {
    return NextResponse.json({ error: 'خطأ في الخادم' }, { status: 500 });
  }
}
