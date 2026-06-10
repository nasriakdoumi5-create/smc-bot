export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300 mt-16">
      <div className="max-w-7xl mx-auto px-4 py-10 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <h3 className="text-white font-bold text-lg mb-3 flex items-center gap-2">
            🛍️ متجري
          </h3>
          <p className="text-sm leading-relaxed text-gray-400">
            متجر إلكتروني متكامل يوفر أفضل المنتجات بأسعار منافسة وجودة عالية.
          </p>
        </div>
        <div>
          <h4 className="text-white font-semibold mb-3">روابط سريعة</h4>
          <ul className="space-y-2 text-sm">
            <li><a href="/" className="hover:text-white transition-colors">الرئيسية</a></li>
            <li><a href="/products" className="hover:text-white transition-colors">المنتجات</a></li>
            <li><a href="/cart" className="hover:text-white transition-colors">السلة</a></li>
          </ul>
        </div>
        <div>
          <h4 className="text-white font-semibold mb-3">تواصل معنا</h4>
          <ul className="space-y-2 text-sm">
            <li>📧 support@matajer.com</li>
            <li>📞 +966 50 000 0000</li>
            <li>🕐 السبت - الخميس، 9ص - 6م</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-gray-800 text-center py-4 text-xs text-gray-500">
        © 2024 متجري — جميع الحقوق محفوظة
      </div>
    </footer>
  );
}
