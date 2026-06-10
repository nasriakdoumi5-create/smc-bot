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

export default function OrdersPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (status === 'unauthenticated') router.push('/login');
  }, [status]);

  useEffect(() => {
    if (session) {
      fetch('/api/orders').then(r => r.json()).then(d => { setOrders(d); setLoading(false); });
    }
  }, [session]);

  if (status === 'loading' || loading) return <div className="flex justify-center py-20"><div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" /></div>;
  if (!session) return null;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center gap-3 mb-8">
        <Link href="/account" className="text-gray-400 hover:text-gray-600">← حسابي</Link>
        <h1 className="text-2xl font-bold text-gray-800">طلباتي</h1>
      </div>

      {orders.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <div className="text-6xl mb-4">📦</div>
          <p className="text-lg font-medium">لا توجد طلبات بعد</p>
          <Link href="/products" className="btn-primary mt-4 inline-block">ابدأ التسوق</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map(order => {
            const s = STATUS_LABELS[order.status] || STATUS_LABELS.PENDING;
            return (
              <div key={order.id} className="card p-5">
                <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
                  <div>
                    <p className="font-mono font-bold text-gray-700">#{order.id.slice(-8).toUpperCase()}</p>
                    <p className="text-sm text-gray-400 mt-0.5">{new Date(order.createdAt).toLocaleDateString('ar-SA', {year:'numeric',month:'long',day:'numeric'})}</p>
                  </div>
                  <div className="text-left">
                    <span className={`badge ${s.color} text-sm mb-1`}>{s.label}</span>
                    <p className="font-bold text-primary-600 text-lg">{order.total} ر.س</p>
                  </div>
                </div>
                <div className="space-y-2 mb-4">
                  {order.items?.map(item => (
                    <div key={item.id} className="flex justify-between text-sm text-gray-600 bg-gray-50 rounded-lg px-3 py-2">
                      <span className="font-medium line-clamp-1">{item.name}</span>
                      <span className="flex-shrink-0 mr-2">× {item.qty} — {(item.price * item.qty).toFixed(0)} ر.س</span>
                    </div>
                  ))}
                </div>
                <div className="text-sm text-gray-500 flex flex-wrap gap-4">
                  <span>📍 {order.city} — {order.address}</span>
                  <span>📞 {order.phone}</span>
                  <span>💳 {order.payMethod === 'cod' ? 'دفع عند الاستلام' : order.payMethod === 'card' ? 'بطاقة ائتمانية' : 'STC Pay'}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
