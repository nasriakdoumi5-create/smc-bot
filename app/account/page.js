'use client';
import { useSession } from 'next-auth/react';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const STATUS_LABELS = {
  PENDING: { label: 'قيد الانتظار', color: 'bg-yellow-100 text-yellow-700' },
  PROCESSING: { label: 'قيد التجهيز', color: 'bg-blue-100 text-blue-700' },
  SHIPPED: { label: 'تم الشحن', color: 'bg-indigo-100 text-indigo-700' },
  DELIVERED: { label: 'تم التوصيل', color: 'bg-green-100 text-green-700' },
  CANCELLED: { label: 'ملغي', color: 'bg-red-100 text-red-700' },
};

export default function AccountPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (status === 'unauthenticated') router.push('/login');
  }, [status]);

  useEffect(() => {
    if (session) {
      fetch('/api/orders').then(r => r.json()).then(d => { setOrders(d.slice(0,3)); setLoading(false); });
    }
  }, [session]);

  if (status === 'loading') return <div className="flex justify-center py-20"><div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" /></div>;
  if (!session) return null;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-8">حسابي</h1>

      {/* Profile card */}
      <div className="card p-6 mb-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center text-2xl font-bold text-primary-700">
            {session.user.name?.[0]}
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-800">{session.user.name}</h2>
            <p className="text-gray-500">{session.user.email}</p>
            {session.user.role === 'ADMIN' && <span className="badge bg-primary-100 text-primary-700 mt-1">مدير النظام</span>}
          </div>
        </div>
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        {[
          { href:'/account/orders', icon:'📦', label:'طلباتي' },
          { href:'/account/wishlist', icon:'❤️', label:'المفضلة' },
          { href:'/products', icon:'🛍️', label:'تسوق الآن' },
          ...(session.user.role === 'ADMIN' ? [{ href:'/admin', icon:'⚙️', label:'لوحة التحكم' }] : []),
        ].map(l => (
          <Link key={l.href} href={l.href} className="card p-4 text-center hover:shadow-md transition-shadow">
            <div className="text-3xl mb-2">{l.icon}</div>
            <p className="font-semibold text-gray-700 text-sm">{l.label}</p>
          </Link>
        ))}
      </div>

      {/* Recent orders */}
      <div className="card p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-bold text-gray-700 text-lg">آخر الطلبات</h3>
          <Link href="/account/orders" className="text-primary-600 text-sm font-semibold hover:text-primary-700">عرض الكل</Link>
        </div>
        {loading ? (
          <div className="space-y-3">{[1,2].map(i => <div key={i} className="h-16 bg-gray-100 rounded-xl animate-pulse" />)}</div>
        ) : orders.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <p>لا توجد طلبات بعد</p>
            <Link href="/products" className="btn-primary mt-3 text-sm inline-block">ابدأ التسوق</Link>
          </div>
        ) : orders.map(order => {
          const s = STATUS_LABELS[order.status] || STATUS_LABELS.PENDING;
          return (
            <div key={order.id} className="flex items-center justify-between py-3 border-b last:border-0">
              <div>
                <p className="font-mono text-sm font-bold text-gray-600">#{order.id.slice(-8).toUpperCase()}</p>
                <p className="text-xs text-gray-400">{new Date(order.createdAt).toLocaleDateString('ar-SA')} — {order.items?.length} منتج</p>
              </div>
              <div className="text-left">
                <span className={`badge ${s.color} mb-1`}>{s.label}</span>
                <p className="text-sm font-bold text-primary-600">{order.total} ر.س</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
