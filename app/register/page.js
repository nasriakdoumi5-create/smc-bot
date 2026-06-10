'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { toast } from 'sonner';

export default function RegisterPage() {
  const [form, setForm] = useState({ name: '', email: '', password: '', phone: '' });
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e) {
    e.preventDefault();
    if (form.password.length < 6) { toast.error('كلمة المرور يجب أن تكون 6 أحرف على الأقل'); return; }
    setLoading(true);
    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      toast.success('تم إنشاء حسابك بنجاح! 🎉');
      router.push('/login');
    } catch (e) {
      toast.error(e.message || 'حدث خطأ، حاول مرة أخرى');
    }
    setLoading(false);
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <span className="text-5xl">🛍️</span>
          <h1 className="text-2xl font-extrabold text-gray-800 mt-3">إنشاء حساب جديد</h1>
          <p className="text-gray-500 mt-1">انضم إلينا وتمتع بأفضل العروض</p>
        </div>
        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">الاسم الكامل</label>
              <input value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))}
                required className="input-field" placeholder="أحمد محمد" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">البريد الإلكتروني</label>
              <input type="email" value={form.email} onChange={e => setForm(f => ({...f, email: e.target.value}))}
                required className="input-field" placeholder="example@email.com" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">رقم الجوال (اختياري)</label>
              <input value={form.phone} onChange={e => setForm(f => ({...f, phone: e.target.value}))}
                className="input-field" placeholder="05xxxxxxxx" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">كلمة المرور</label>
              <input type="password" value={form.password} onChange={e => setForm(f => ({...f, password: e.target.value}))}
                required className="input-field" placeholder="6 أحرف على الأقل" />
            </div>
            <button type="submit" disabled={loading} className="w-full btn-primary py-3.5 text-base">
              {loading ? '⏳ جاري الإنشاء...' : 'إنشاء الحساب'}
            </button>
          </form>
          <div className="mt-6 text-center">
            <p className="text-gray-500 text-sm">لديك حساب؟ <Link href="/login" className="text-primary-600 font-semibold hover:text-primary-700">تسجيل الدخول</Link></p>
          </div>
        </div>
      </div>
    </div>
  );
}
