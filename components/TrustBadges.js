'use client';
import { Shield, RotateCcw, Truck, Leaf, Lock } from 'lucide-react';

export default function TrustBadges({ variant = 'horizontal' }) {
  const badges = [
    { icon: Shield, label: '30-Day Returns', sub: 'Hassle-free guarantee' },
    { icon: Lock, label: 'Secure Checkout', sub: 'SSL encrypted' },
    { icon: Truck, label: 'EU Shipping', sub: '3–5 business days' },
    { icon: Leaf, label: 'Eco Printed', sub: 'No overproduction' },
  ];

  if (variant === 'compact') {
    return (
      <div className="flex flex-wrap gap-3 justify-center">
        {badges.map(b => (
          <div key={b.label} className="flex items-center gap-1.5 text-xs text-gray-600 bg-white border border-gray-100 rounded-lg px-3 py-2">
            <b.icon className="w-3.5 h-3.5 text-primary" />
            <span className="font-medium">{b.label}</span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {badges.map(b => (
        <div key={b.label} className="flex flex-col items-center text-center gap-1.5 bg-secondary rounded-xl p-3">
          <b.icon className="w-5 h-5 text-primary" />
          <p className="font-semibold text-xs text-dark">{b.label}</p>
          <p className="text-xs text-gray-500">{b.sub}</p>
        </div>
      ))}
    </div>
  );
}
