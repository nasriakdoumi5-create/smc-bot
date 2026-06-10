'use client';
import { useSession } from 'next-auth/react';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

const STATUS_LABELS = {
  PENDING: { label: 'قيد الانتظار', color: 'bg-yellow-100 text-yellow-700' },
  PROCESSING: { label: 'قيد التجهيز', color: 'bg-blue-100 text-blue-700' },
  SHIPPED: { label: 'تم الشحن', color: 'bg-indigo-100 text-indigo-700' },
  DELIVERED: { label: 'تم التوصيل', color: 'bg-green-100 text-green-700' },
  CANCELLED: { label: 'ملغي', color: 'bg-red-100 text-red-700' },
};

export default function AdminPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [tab, setTab]       = useState('stats');
  const [stats, setStats]   = useState(null);
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [newProduct, setNewProduct] = useState({ name:'', slug:'', description:'', price:'', originalPrice:'', stock:'', categorySlug:'', featured:false });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (status === 'unauthenticated') router.push('/login');
    if (status === 'authenticated' && session?.user?.role !== 'ADMIN') router.push('/');
  }, [status, session]);

  useEffect(() => {
    if (session?.user?.role === 'ADMIN') loadData();
  }, [session]);

  async function loadData() {
    setLoading(true);
    const [s, o, p] = await Promise.all([
      fetch('/api/admin/stats').then(r => r.json()),
      fetch('/api/orders').then(r => r.json()),
      fetch('/api/products').then(r => r.json()),
    ]);
    setStats(s);
    setOrders(Array.isArray(o) ? o : []);
    setProducts(Array.isArray(p) ? p : []);
    setLoading(false);
  }

  async function updateOrderStatus(id, status) {
    const res = await fetch(`/api/orders/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    if (res.ok) {
      setOrders(orders.map(o => o.id === id ? { ...o, status } : o));
      toast.success('تم تحديث حالة الطلب');
    }
  }

  async function deleteProduct(slug) {
    if (!confirm('هل أنت متأكد من حذف هذا المنتج؟')) return;
    const res = await fetch(`/api/products/${slug}`, { method: 'DELETE' });
    if (res.ok) {
      setProducts(products.filter(p => p.slug !== slug));
      toast.success('تم حذف المنتج');
    }
  }

  async function handleAddProduct(e) {
    e.preventDefault();
    setSaving(true);
    const categories = { electronics: null, clothing: null, home: null, sports: null, books: null };
    // Fetch category id
    const catRes = await fetch(`/api/products?category=${newProduct.categorySlug}`);
    const catProducts = await catRes.json();
    const categoryId = catProducts[0]?.categoryId || catProducts[0]?.category?.id;

    if (!categoryId) {
      toast.error('الفئة غير موجودة');
      setSaving(false);
      return;
    }

    const res = await fetch('/api/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: newProduct.name,
        slug: newProduct.slug || newProduct.name.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, ''),
        description: newProduct.description,
        price: parseFloat(newProduct.price),
        originalPrice: newProduct.originalPrice ? parseFloat(newProduct.originalPrice) : null,
        stock: parseInt(newProduct.stock),
        categoryId,
        featured: newProduct.featured,
        images: [`https://picsum.photos/seed/${Date.now()}/600/600`],
      }),
    });
    if (res.ok) {
      toast.success('تم إضافة المنتج بنجاح ✓');
      setNewProduct({ name:'', slug:'', description:'', price:'', originalPrice:'', stock:'', categorySlug:'', featured:false });
      await loadData();
      setTab('products');
    } else {
      const err = await res.json();
      toast.error(err.error || 'حدث خطأ');
    }
    setSaving(false);
  }

  if (status === 'loading' || loading) return <div className="flex justify-center py-20"><div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" /></div>;
  if (!session || session.user.role !== 'ADMIN') return null;

  const TABS = [
    { id:'stats', label:'الإحصائيات', icon:'📊' },
    { id:'orders', label:'الطلبات', icon:'📦' },
    { id:'products', label:'المنتجات', icon:'🛍️' },
    { id:'add-product', label:'إضافة منتج', icon:'➕' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">⚙️ لوحة التحكم</h1>
        <span className="badge bg-primary-100 text-primary-700">مدير النظام</span>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex-shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-colors ${tab === t.id ? 'bg-primary-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'}`}>
            <span>{t.icon}</span>{t.label}
          </button>
        ))}
      </div>

      {/* Stats Tab */}
      {tab === 'stats' && stats && (
        <div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              { icon:'📦', label:'الطلبات', value: stats.totalOrders, color:'bg-blue-50 text-blue-700' },
              { icon:'🛍️', label:'المنتجات', value: stats.totalProducts, color:'bg-purple-50 text-purple-700' },
              { icon:'👤', label:'المستخدمون', value: stats.totalUsers, color:'bg-pink-50 text-pink-700' },
              { icon:'💰', label:'الإيرادات', value: `${stats.revenue} ر.س`, color:'bg-green-50 text-green-700' },
            ].map(s => (
              <div key={s.label} className={`card p-5 ${s.color}`}>
                <div className="text-3xl mb-2">{s.icon}</div>
                <p className="text-2xl font-extrabold">{s.value}</p>
                <p className="text-sm font-medium opacity-80">{s.label}</p>
              </div>
            ))}
          </div>
          <div className="card p-6">
            <h3 className="font-bold text-gray-700 mb-4">آخر الطلبات</h3>
            {stats.recentOrders?.map(o => (
              <div key={o.id} className="flex justify-between items-center py-3 border-b last:border-0 text-sm">
                <div>
                  <p className="font-mono font-bold">#{o.id.slice(-8).toUpperCase()}</p>
                  <p className="text-gray-400 text-xs">{new Date(o.createdAt).toLocaleDateString('ar-SA')} — {o.items?.length} منتج</p>
                </div>
                <div className="text-left">
                  <span className={`badge ${STATUS_LABELS[o.status]?.color || 'bg-gray-100 text-gray-700'}`}>{STATUS_LABELS[o.status]?.label || o.status}</span>
                  <p className="font-bold text-primary-600 text-xs mt-1">{o.total} ر.س</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Orders Tab */}
      {tab === 'orders' && (
        <div className="space-y-4">
          {orders.length === 0 ? <p className="text-center text-gray-400 py-10">لا توجد طلبات</p> : orders.map(order => {
            const s = STATUS_LABELS[order.status] || STATUS_LABELS.PENDING;
            return (
              <div key={order.id} className="card p-5">
                <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
                  <div>
                    <p className="font-mono font-bold text-gray-700">#{order.id.slice(-8).toUpperCase()}</p>
                    <p className="text-sm text-gray-500">{order.name} — {order.phone}</p>
                    <p className="text-xs text-gray-400">{new Date(order.createdAt).toLocaleDateString('ar-SA')}</p>
                    {order.user && <p className="text-xs text-gray-400">العميل: {order.user.name} ({order.user.email})</p>}
                  </div>
                  <div className="text-left">
                    <p className="font-bold text-primary-600 text-lg">{order.total} ر.س</p>
                    <select value={order.status} onChange={e => updateOrderStatus(order.id, e.target.value)}
                      className={`mt-1 text-xs font-semibold rounded-lg px-2 py-1 border-0 cursor-pointer ${s.color}`}>
                      {Object.entries(STATUS_LABELS).map(([v, {label}]) => <option key={v} value={v}>{label}</option>)}
                    </select>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 text-xs text-gray-500">
                  {order.items?.map(i => <span key={i.id} className="bg-gray-100 rounded-lg px-2 py-1">{i.name} × {i.qty}</span>)}
                </div>
                <p className="text-xs text-gray-400 mt-2">📍 {order.city} — {order.address}</p>
              </div>
            );
          })}
        </div>
      )}

      {/* Products Tab */}
      {tab === 'products' && (
        <div className="overflow-x-auto">
          <table className="w-full bg-white rounded-2xl shadow-sm overflow-hidden text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">المنتج</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">الفئة</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">السعر</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">المخزون</th>
                <th className="text-right px-4 py-3 font-semibold text-gray-600">إجراءات</th>
              </tr>
            </thead>
            <tbody>
              {products.map(p => (
                <tr key={p.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-700 line-clamp-1">{p.name}</p>
                    {p.featured && <span className="badge bg-primary-100 text-primary-700 text-xs">مميز</span>}
                  </td>
                  <td className="px-4 py-3 text-gray-500">{p.category?.name}</td>
                  <td className="px-4 py-3 font-bold text-primary-600">{p.price} ر.س</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${p.stock > 5 ? 'bg-green-100 text-green-700' : p.stock > 0 ? 'bg-orange-100 text-orange-700' : 'bg-red-100 text-red-700'}`}>{p.stock}</span>
                  </td>
                  <td className="px-4 py-3">
                    <button onClick={() => deleteProduct(p.slug)} className="text-red-400 hover:text-red-600 text-xs font-medium hover:bg-red-50 px-2 py-1 rounded-lg transition-colors">حذف</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add Product Tab */}
      {tab === 'add-product' && (
        <div className="card p-6 max-w-2xl">
          <h2 className="font-bold text-gray-700 text-lg mb-6">إضافة منتج جديد</h2>
          <form onSubmit={handleAddProduct} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1.5">اسم المنتج *</label>
                <input value={newProduct.name} onChange={e => setNewProduct(p => ({...p, name:e.target.value}))} required className="input-field" placeholder="مثال: سماعات لاسلكية" />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1.5">الوصف *</label>
                <textarea value={newProduct.description} onChange={e => setNewProduct(p => ({...p, description:e.target.value}))} required className="input-field h-24 resize-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">السعر *</label>
                <input type="number" value={newProduct.price} onChange={e => setNewProduct(p => ({...p, price:e.target.value}))} required className="input-field" placeholder="299" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">السعر الأصلي</label>
                <input type="number" value={newProduct.originalPrice} onChange={e => setNewProduct(p => ({...p, originalPrice:e.target.value}))} className="input-field" placeholder="399" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">المخزون *</label>
                <input type="number" value={newProduct.stock} onChange={e => setNewProduct(p => ({...p, stock:e.target.value}))} required className="input-field" placeholder="10" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">الفئة *</label>
                <select value={newProduct.categorySlug} onChange={e => setNewProduct(p => ({...p, categorySlug:e.target.value}))} required className="input-field">
                  <option value="">اختر الفئة</option>
                  <option value="electronics">إلكترونيات</option>
                  <option value="clothing">ملابس</option>
                  <option value="home">المنزل</option>
                  <option value="sports">رياضة</option>
                  <option value="books">كتب</option>
                </select>
              </div>
              <div className="flex items-center gap-3">
                <input type="checkbox" id="featured" checked={newProduct.featured} onChange={e => setNewProduct(p => ({...p, featured:e.target.checked}))} className="w-5 h-5 rounded text-primary-600" />
                <label htmlFor="featured" className="text-sm font-medium text-gray-700">منتج مميز</label>
              </div>
            </div>
            <button type="submit" disabled={saving} className="btn-primary w-full py-3">
              {saving ? '⏳ جاري الحفظ...' : '+ إضافة المنتج'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
