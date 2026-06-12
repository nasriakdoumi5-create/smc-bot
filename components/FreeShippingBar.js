'use client';
import { Truck } from 'lucide-react';

export default function FreeShippingBar({ total }) {
  const threshold = 40;
  const remaining = Math.max(0, threshold - total);
  const progress = Math.min(100, (total / threshold) * 100);
  const isFree = total >= threshold;

  return (
    <div className="bg-secondary rounded-xl p-3 mb-4">
      <div className="flex items-center gap-2 mb-2">
        <Truck className={`w-4 h-4 ${isFree ? 'text-green-600' : 'text-primary'}`} />
        {isFree ? (
          <p className="text-sm font-bold text-green-600">🎉 You've unlocked free shipping!</p>
        ) : (
          <p className="text-sm text-gray-700">
            Add <span className="font-bold text-primary">€{remaining.toFixed(2)}</span> more for free shipping
          </p>
        )}
      </div>
      <div className="bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${isFree ? 'bg-green-500' : 'bg-primary'}`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}
