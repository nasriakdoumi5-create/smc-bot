'use client';
import { Tag } from 'lucide-react';

const bundles = [
  { qty: 1, label: '1 Case', discount: 0, badge: null },
  { qty: 2, label: '2 Cases', discount: 15, badge: 'Most Popular' },
  { qty: 3, label: '3 Cases', discount: 25, badge: 'Best Value' },
];

export default function BundleOffer({ product, bundleQty = 1, onBundleChange }) {
  const finalPrice = (qty) => {
    const bundle = bundles.find(b => b.qty === qty);
    return (product.price * qty * (1 - bundle.discount / 100)).toFixed(2);
  };

  const perUnit = (qty) => {
    const bundle = bundles.find(b => b.qty === qty);
    return (product.price * (1 - bundle.discount / 100)).toFixed(2);
  };

  return (
    <div className="border-2 border-primary/20 rounded-2xl p-4 bg-white">
      <div className="flex items-center gap-2 mb-3">
        <Tag className="w-4 h-4 text-accent" />
        <h3 className="font-bold text-sm text-dark">Bundle &amp; Save</h3>
        <span className="text-xs bg-accent/10 text-accent font-semibold px-2 py-0.5 rounded-full">Up to 25% off</span>
      </div>
      <div className="space-y-2">
        {bundles.map(b => (
          <label
            key={b.qty}
            className={`flex items-center gap-3 cursor-pointer rounded-xl p-2.5 border-2 transition-all ${
              bundleQty === b.qty ? 'border-primary bg-primary/5' : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <input
              type="radio"
              name="bundle"
              value={b.qty}
              checked={bundleQty === b.qty}
              onChange={() => onBundleChange?.(b.qty)}
              className="accent-primary"
            />
            <div className="flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-semibold text-sm text-dark">{b.label}</span>
                {b.badge && (
                  <span className="text-xs bg-accent text-white font-bold px-2 py-0.5 rounded-full">{b.badge}</span>
                )}
              </div>
              {b.discount > 0 ? (
                <p className="text-xs text-green-600 font-medium">
                  Save {b.discount}% — €{perUnit(b.qty)} per case
                </p>
              ) : (
                <p className="text-xs text-gray-400">€{perUnit(b.qty)} per case</p>
              )}
            </div>
            <div className="text-right">
              <p className="font-bold text-accent">€{finalPrice(b.qty)}</p>
              {b.qty > 1 && (
                <p className="text-xs text-gray-400 line-through">€{(product.price * b.qty).toFixed(2)}</p>
              )}
            </div>
          </label>
        ))}
      </div>
    </div>
  );
}
