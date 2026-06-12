'use client';
import { Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { CheckCircle, Truck, Mail, ArrowRight } from 'lucide-react';

function OrderSuccessContent() {
  const params = useSearchParams();
  const orderNum = params.get('order') || 'PW' + Date.now().toString().slice(-6);
  const email = params.get('email') || '';

  const deliveryDate = (() => {
    const d = new Date();
    d.setDate(d.getDate() + 5);
    const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    return `${days[d.getDay()]}, ${d.getDate()} ${months[d.getMonth()]}`;
  })();

  return (
    <div className="max-w-lg mx-auto px-4 py-16 text-center">
      <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <CheckCircle className="w-10 h-10 text-green-500" />
      </div>

      <h1 className="text-3xl font-extrabold text-dark mb-2">Order Confirmed! 🐾</h1>
      <p className="text-gray-500 mb-6">Thank you for your order. We're already preparing your case.</p>

      <div className="card p-6 mb-6 text-left space-y-4">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-primary font-bold text-sm">#</span>
          </div>
          <div>
            <p className="text-xs text-gray-400 font-medium">Order Number</p>
            <p className="font-bold text-dark text-lg">{orderNum}</p>
          </div>
        </div>

        {email && (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-blue-50 rounded-full flex items-center justify-center flex-shrink-0">
              <Mail className="w-4 h-4 text-blue-500" />
            </div>
            <div>
              <p className="text-xs text-gray-400 font-medium">Confirmation sent to</p>
              <p className="font-semibold text-dark">{email}</p>
            </div>
          </div>
        )}

        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-green-50 rounded-full flex items-center justify-center flex-shrink-0">
            <Truck className="w-4 h-4 text-green-500" />
          </div>
          <div>
            <p className="text-xs text-gray-400 font-medium">Estimated Delivery</p>
            <p className="font-semibold text-dark">{deliveryDate}</p>
            <p className="text-xs text-gray-400">Shipped from our EU facility · Fully tracked</p>
          </div>
        </div>
      </div>

      {/* What happens next */}
      <div className="bg-secondary rounded-2xl p-5 mb-6 text-left">
        <h2 className="font-bold mb-3 text-dark">What happens next?</h2>
        <ol className="space-y-2">
          {[
            { step: '1', text: 'We print your case with UV-resistant inks' },
            { step: '2', text: 'Quality checked & carefully packed' },
            { step: '3', text: 'Shipped to you with tracking number via email' },
            { step: '4', text: 'Enjoy your personalised PawCase! 🐾' },
          ].map(s => (
            <li key={s.step} className="flex items-center gap-3 text-sm text-gray-700">
              <span className="w-5 h-5 bg-primary text-white rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">{s.step}</span>
              {s.text}
            </li>
          ))}
        </ol>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <Link href="/products" className="btn-primary flex items-center justify-center gap-2">
          Continue Shopping <ArrowRight className="w-4 h-4" />
        </Link>
        <Link href="/" className="btn-outline">Back to Home</Link>
      </div>

      <p className="text-xs text-gray-400 mt-6">
        Questions? Email us at <a href="mailto:hello@pawcase.eu" className="underline hover:text-primary">hello@pawcase.eu</a>
      </p>
    </div>
  );
}

export default function OrderSuccessPage() {
  return (
    <Suspense fallback={<div className="flex justify-center py-20"><div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" /></div>}>
      <OrderSuccessContent />
    </Suspense>
  );
}
