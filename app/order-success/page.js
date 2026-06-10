'use client';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

function SuccessContent() {
  const params = useSearchParams();
  const id = params.get('id');
  return (
    <div className="max-w-lg mx-auto px-4 py-20 text-center">
      <div className="text-7xl mb-6 animate-bounce">🎉</div>
      <h1 className="text-3xl font-extrabold text-gray-800 mb-3">تم تأكيد طلبك!</h1>
      {id && <p className="text-gray-500 mb-2 text-sm">رقم الطلب: <span className="font-mono font-bold text-gray-700">{id.slice(-8).toUpperCase()}</span></p>}
      <p className="text-gray-500 mb-8">سيتم التواصل معك قريباً لتأكيد التوصيل. شكراً لثقتك بنا!</p>
      <div className="flex gap-3 justify-center flex-wrap">
        <Link href="/products" className="btn-primary px-8">مواصلة التسوق</Link>
        <Link href="/account/orders" className="btn-outline px-8">متابعة طلباتي</Link>
      </div>
    </div>
  );
}

export default function OrderSuccessPage() {
  return (
    <Suspense fallback={<div className="text-center py-20">جاري التحميل...</div>}>
      <SuccessContent />
    </Suspense>
  );
}
