import Link from 'next/link';
export default function Footer() {
  return (
    <footer className="bg-slate-800 text-gray-400 mt-16">
      <div className="max-w-7xl mx-auto px-4 py-10 grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <h3 className="text-white font-bold text-lg mb-3">🛍️ متجري</h3>
          <p className="text-sm leading-relaxed">متجر إلكتروني متكامل يوفر أفضل المنتجات بأسعار منافسة وجودة مضمونة.</p>
        </div>
        <div>
          <h4 className="text-white font-semibold mb-3">المتجر</h4>
          <ul className="space-y-2 text-sm">
            <li><Link href="/products" className="hover:text-white transition-colors">جميع المنتجات</Link></li>
            <li><Link href="/products?category=electronics" className="hover:text-white transition-colors">إلكترونيات</Link></li>
            <li><Link href="/products?category=clothing" className="hover:text-white transition-colors">ملابس</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="text-white font-semibold mb-3">حسابي</h4>
          <ul className="space-y-2 text-sm">
            <li><Link href="/login" className="hover:text-white transition-colors">تسجيل الدخول</Link></li>
            <li><Link href="/register" className="hover:text-white transition-colors">إنشاء حساب</Link></li>
            <li><Link href="/account/orders" className="hover:text-white transition-colors">طلباتي</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="text-white font-semibold mb-3">تواصل معنا</h4>
          <ul className="space-y-2 text-sm">
            <li>📧 support@matajer.sa</li>
            <li>📞 920 000 0000</li>
            <li>🕐 السبت–الخميس، 9ص–6م</li>
          </ul>
          <div className="flex gap-3 mt-4">
            {['X','📘','📸','🎵'].map(s => <span key={s} className="w-8 h-8 bg-slate-700 rounded-lg flex items-center justify-center hover:bg-slate-600 cursor-pointer transition-colors text-sm">{s}</span>)}
          </div>
        </div>
      </div>
      <div className="border-t border-slate-700 py-4 text-center text-xs text-gray-500">
        © 2024 متجري — جميع الحقوق محفوظة | 🔒 دفع آمن | 🚚 توصيل سريع
      </div>
    </footer>
  );
}
