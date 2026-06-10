'use client';

import { PRODUCTS, CATEGORIES } from '../../data/products';
import { useState } from 'react';
import Image from 'next/image';

const MOCK_ORDERS = [
  { id: 'ORD-001', customer: 'أحمد محمد', total: 849, status: 'delivered', date: '2024-01-10', items: 3 },
  { id: 'ORD-002', customer: 'سارة أحمد',  total: 299,  status: 'shipped',   date: '2024-01-11', items: 1 },
  { id: 'ORD-003', customer: 'خالد العتيبي', total: 1449, status: 'pending',  date: '2024-01-12', items: 2 },
  { id: 'ORD-004', customer: 'نورة السالم',  total: 655,  status: 'processing', date: '2024-01-12', items: 4 },
  { id: 'ORD-005', customer: 'عمر الزهراني', total: 3599, status: 'delivered', date: '2024-01-09', items: 1 },
];

const STATUS_CONFIG = {
  pending:    { label: 'قيد الانتظار', color: 'bg-yellow-100 text-yellow-700' },
  processing: { label: 'قيد المعالجة', color: 'bg-blue-100 text-blue-700' },
  shipped:    { label: 'تم الشحن',     color: 'bg-purple-100 text-purple-700' },
  delivered:  { label: 'تم التسليم',   color: 'bg-green-100 text-green-700' },
  cancelled:  { label: 'ملغي',          color: 'bg-red-100 text-red-700' },
};

export default function AdminPage() {
  const [tab, setTab]             = useState('dashboard');
  const [products, setProducts]   = useState(PRODUCTS);
  const [editProduct, setEdit]    = useState(null);
  const [showModal, setModal]     = useState(false);
  const [newProduct, setNew]      = useState({
    name: '', price: '', originalPrice: '', category: 'electronics',
    description: '', stock: '', image: '',
  });

  const totalRevenue  = MOCK_ORDERS.filter(o => o.status === 'delivered').reduce((s, o) => s + o.total, 0);
  const totalOrders   = MOCK_ORDERS.length;
  const pendingOrders = MOCK_ORDERS.filter(o => o.status === 'pending').length;
  const totalProducts = products.length;

  function handleDelete(id) {
    if (confirm('هل تريد حذف هذا المنتج؟')) {
      setProducts(p => p.filter(x => x.id !== id));
    }
  }

  function handleSave() {
    if (!newProduct.name || !newProduct.price) return;
    const id = Math.max(...products.map(p => p.id)) + 1;
    setProducts(p => [...p, {
      ...newProduct,
      id,
      price:         Number(newProduct.price),
      originalPrice: Number(newProduct.originalPrice) || Number(newProduct.price),
      stock:         Number(newProduct.stock) || 0,
      rating: 0, reviews: 0, featured: false, tags: [],
      image: newProduct.image || `https://picsum.photos/seed/${id}/400/400`,
    }]);
    setModal(false);
    setNew({ name: '', price: '', originalPrice: '', category: 'electronics', description: '', stock: '', image: '' });
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">⚙️ لوحة التحكم</h1>
          <p className="text-gray-400 text-sm mt-1">إدارة المتجر والمنتجات والطلبات</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-2xl p-1 mb-8 w-fit">
        {[
          { id: 'dashboard', label: 'الإحصائيات', icon: '📊' },
          { id: 'products',  label: 'المنتجات',    icon: '📦' },
          { id: 'orders',    label: 'الطلبات',     icon: '🛒' },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-5 py-2.5 rounded-xl text-sm font-medium transition-all ${
              tab === t.id ? 'bg-white shadow-sm text-primary-600' : 'text-gray-500 hover:text-gray-700'
            }`}>
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      {/* Dashboard */}
      {tab === 'dashboard' && (
        <div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              { label: 'إيرادات هذا الشهر', value: `${totalRevenue.toLocaleString()} ر.س`, icon: '💰', color: 'text-green-600', bg: 'bg-green-50' },
              { label: 'إجمالي الطلبات',    value: totalOrders,                             icon: '📋', color: 'text-blue-600',  bg: 'bg-blue-50' },
              { label: 'طلبات معلقة',        value: pendingOrders,                          icon: '⏳', color: 'text-yellow-600', bg: 'bg-yellow-50' },
              { label: 'إجمالي المنتجات',   value: totalProducts,                          icon: '📦', color: 'text-purple-600', bg: 'bg-purple-50' },
            ].map(s => (
              <div key={s.label} className="card p-5">
                <div className={`w-12 h-12 ${s.bg} rounded-xl flex items-center justify-center text-2xl mb-3`}>
                  {s.icon}
                </div>
                <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
                <div className="text-sm text-gray-400 mt-1">{s.label}</div>
              </div>
            ))}
          </div>

          {/* Top Products */}
          <div className="card p-6">
            <h2 className="font-bold text-gray-800 text-lg mb-4">المنتجات الأكثر مبيعاً</h2>
            <div className="space-y-3">
              {products.sort((a, b) => b.reviews - a.reviews).slice(0, 5).map((p, i) => (
                <div key={p.id} className="flex items-center gap-3">
                  <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                    i === 0 ? 'bg-yellow-400 text-white' :
                    i === 1 ? 'bg-gray-300 text-white' :
                    i === 2 ? 'bg-orange-400 text-white' :
                              'bg-gray-100 text-gray-500'
                  }`}>{i + 1}</span>
                  <div className="relative w-10 h-10 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
                    <Image src={p.image} alt={p.name} fill className="object-cover" sizes="40px" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-700 line-clamp-1">{p.name}</p>
                    <p className="text-xs text-gray-400">{p.reviews} تقييم</p>
                  </div>
                  <span className="text-sm font-bold text-primary-600">{p.price} ر.س</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Products */}
      {tab === 'products' && (
        <div>
          <div className="flex justify-between items-center mb-5">
            <h2 className="text-xl font-bold text-gray-700">إدارة المنتجات ({products.length})</h2>
            <button onClick={() => setModal(true)} className="btn-primary flex items-center gap-2">
              + إضافة منتج
            </button>
          </div>

          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <th className="text-right py-3 px-4 font-semibold text-gray-600">المنتج</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-600">الفئة</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-600">السعر</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-600">المخزون</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-600">التقييم</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-600">الإجراءات</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {products.map(p => (
                    <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          <div className="relative w-10 h-10 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
                            <Image src={p.image} alt={p.name} fill className="object-cover" sizes="40px" />
                          </div>
                          <span className="font-medium text-gray-700 line-clamp-1 max-w-[200px]">{p.name}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-gray-500">
                        {CATEGORIES.find(c => c.id === p.category)?.label}
                      </td>
                      <td className="py-3 px-4 font-bold text-primary-600">{p.price} ر.س</td>
                      <td className="py-3 px-4">
                        <span className={`badge text-xs ${
                          p.stock > 10 ? 'bg-green-100 text-green-700' :
                          p.stock > 0  ? 'bg-orange-100 text-orange-700' :
                                         'bg-red-100 text-red-700'
                        }`}>
                          {p.stock} قطعة
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-yellow-500">★</span>
                        <span className="text-gray-600 font-medium">{p.rating}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleDelete(p.id)}
                            className="text-red-400 hover:text-red-600 p-1.5 hover:bg-red-50 rounded-lg transition-colors"
                            title="حذف"
                          >
                            🗑
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Orders */}
      {tab === 'orders' && (
        <div>
          <h2 className="text-xl font-bold text-gray-700 mb-5">إدارة الطلبات ({MOCK_ORDERS.length})</h2>
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <th className="text-right py-3 px-4 font-semibold text-gray-600">رقم الطلب</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-600">العميل</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-600">التاريخ</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-600">المنتجات</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-600">المجموع</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-600">الحالة</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {MOCK_ORDERS.map(o => (
                    <tr key={o.id} className="hover:bg-gray-50 transition-colors">
                      <td className="py-3 px-4 font-mono font-medium text-gray-700">{o.id}</td>
                      <td className="py-3 px-4 text-gray-700">{o.customer}</td>
                      <td className="py-3 px-4 text-gray-400">{o.date}</td>
                      <td className="py-3 px-4 text-gray-500">{o.items} منتج</td>
                      <td className="py-3 px-4 font-bold text-primary-600">{o.total.toLocaleString()} ر.س</td>
                      <td className="py-3 px-4">
                        <span className={`badge text-xs ${STATUS_CONFIG[o.status].color}`}>
                          {STATUS_CONFIG[o.status].label}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Add Product Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-5">
              <h3 className="text-xl font-bold text-gray-800">إضافة منتج جديد</h3>
              <button onClick={() => setModal(false)} className="text-gray-400 hover:text-gray-600 text-2xl">✕</button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">اسم المنتج *</label>
                <input value={newProduct.name} onChange={e => setNew(n => ({...n, name: e.target.value}))}
                  className="input-field" placeholder="اسم المنتج" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">السعر *</label>
                  <input value={newProduct.price} onChange={e => setNew(n => ({...n, price: e.target.value}))}
                    className="input-field" placeholder="0" type="number" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">السعر الأصلي</label>
                  <input value={newProduct.originalPrice} onChange={e => setNew(n => ({...n, originalPrice: e.target.value}))}
                    className="input-field" placeholder="0" type="number" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الفئة</label>
                  <select value={newProduct.category} onChange={e => setNew(n => ({...n, category: e.target.value}))}
                    className="input-field">
                    {CATEGORIES.filter(c => c.id !== 'all').map(c => (
                      <option key={c.id} value={c.id}>{c.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الكمية</label>
                  <input value={newProduct.stock} onChange={e => setNew(n => ({...n, stock: e.target.value}))}
                    className="input-field" placeholder="0" type="number" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الوصف</label>
                <textarea value={newProduct.description} onChange={e => setNew(n => ({...n, description: e.target.value}))}
                  className="input-field resize-none" rows={3} placeholder="وصف المنتج..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">رابط الصورة</label>
                <input value={newProduct.image} onChange={e => setNew(n => ({...n, image: e.target.value}))}
                  className="input-field" placeholder="https://..." />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={handleSave} className="btn-primary flex-1">حفظ المنتج</button>
              <button onClick={() => setModal(false)} className="btn-outline flex-1">إلغاء</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
