'use client';
import { useEffect, useState } from 'react';
import { ShoppingBag } from 'lucide-react';

const notifications = [
  { name: 'Sofia M.', location: 'Madrid', product: 'Golden Retriever Case', time: 'Recently' },
  { name: 'Lucas K.', location: 'Berlin', product: 'Custom Pet Case', time: 'Recently' },
  { name: 'Emma V.', location: 'Amsterdam', product: 'Black Cat Case', time: 'Recently' },
  { name: 'Marie D.', location: 'Paris', product: 'French Bulldog Case', time: 'Recently' },
  { name: 'Anna S.', location: 'Stockholm', product: 'Tabby Cat Case', time: 'Recently' },
  { name: 'James R.', location: 'London', product: 'Golden Retriever Case', time: 'Recently' },
  { name: 'Clara B.', location: 'Brussels', product: 'Custom Pet Case', time: 'Recently' },
];

export default function RecentPurchaseNotification() {
  const [visible, setVisible] = useState(false);
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const initTimer = setTimeout(() => {
      setVisible(true);
      const interval = setInterval(() => {
        setVisible(false);
        setTimeout(() => {
          setCurrent(c => (c + 1) % notifications.length);
          setVisible(true);
        }, 500);
      }, 12000);
      return () => clearInterval(interval);
    }, 8000);
    return () => clearTimeout(initTimer);
  }, []);

  const n = notifications[current];

  if (!visible) return null;

  return (
    <div className="fixed bottom-24 left-4 z-50 bg-white rounded-xl shadow-xl border border-gray-100 p-3 flex items-center gap-3 max-w-xs animate-fade-in">
      <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
        <ShoppingBag className="w-5 h-5 text-primary" />
      </div>
      <div>
        <p className="text-xs font-bold text-dark">{n.name} from {n.location}</p>
        <p className="text-xs text-gray-500">Ordered a <span className="font-medium text-primary">{n.product}</span></p>
        <p className="text-xs text-gray-400">{n.time}</p>
      </div>
      <button onClick={() => setVisible(false)} className="absolute top-1.5 right-1.5 text-gray-300 hover:text-gray-500 text-xs">✕</button>
    </div>
  );
}
