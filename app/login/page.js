'use client';
import { useState } from 'react';
import { signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { toast } from 'sonner';

export default function LoginPage() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    const res = await signIn('credentials', { ...form, redirect: false });
    if (res?.ok) {
      toast.success('مرحباً بك! 👋');
      router.push('/');
      router.refresh();
    } else {
      toast.error('البريد الإلكتروني أو كلمة المرور غير صحيحة');
    }
    setLoading(false);
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <span className="text-5xl">🛍️</span>
          <h1 className="text-2xl font-extrabold text-gray-800 mt-3">مرحباً بعودتك</h1>
          <p className="text-gray-500 mt-1">سجّل دخولك للمتابعة</p>
        </div>
        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">البريد الإلكتروني</label>
              <input type="email" value={form.email} onChange={e => setForm(f => ({...f, email: e.target.value}))}
                required className="input-field" placeholder="example@email.com" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">كلمة المرور</label>
              <input type="password" value={form.password} onChange={e => setForm(f => ({...f, password: e.target.value}))}
                required className="input-field" placeholder="••••••••" />
            </div>
            <button type="submit" disabled={loading} className="w-full btn-primary py-3.5 text-base">
              {loading ? '⏳ جاري تسجيل الدخول...' : 'تسجيل الدخول'}
            </button>
          </form>
          <div className="mt-6 text-center">
            <p className="text-gray-500 text-sm">ليس لديك حساب؟ <Link href="/register" className="text-primary-600 font-semibold hover:text-primary-700">إنشاء حساب</Link></p>
          </div>
          <div className="mt-4 p-3 bg-gray-50 rounded-xl text-xs text-gray-500 text-center">
            <p className="font-medium mb-1">للتجربة:</p>
            <p>مدير: admin@store.com / admin123</p>
            <p>مستخدم: user@store.com / user123</p>
          </div>
        </div>
      </div>
    </div>
  );
}
