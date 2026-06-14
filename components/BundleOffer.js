'use client';
import { Tag, Gift, Heart } from 'lucide-react';

const bundles = [
  { qty: 1, label: '1 Case', discount: 0, badge: null },
  { qty: 2, label: '2 Cases', discount: 15, badge: 'Most Popular' },
  { qty: 3, label: '3 Cases', discount: 25, badge: 'Best Value' },
];

const specialBundles = [
  {
    icon: '👨‍👩‍👧',
    title: 'Family Pet Bundle',
    desc: 'One for you, one for your partner, one for the kids — all featuring your pet.',
    tag: '3 Cases · Save 25%',
    qty: 3,
    color: 'bg-purple-50 border-purple-200',
    textColor: 'text-purple-700',
  },
  {
    icon: '🎁',
    title: 'Gift Bundle',
    desc: "The most emotional gift for any pet lover. Arrives gift-ready — they'll cry happy tears.",
    tag: '2 Cases · Save 15%',
    qty: 2,
    color: 'bg-pink-50 border-pink-200',
    textColor: 'text-pink-700',
  },
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
    <div className="space-y-3">
      {/* Main bundle selector */}
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

      {/* Special bundle suggestions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {specialBundles.map(sb => (
          <button
            key={sb.title}
            onClick={() => onBundleChange?.(sb.qty)}
            className={`text-left rounded-xl p-3 border-2 transition-all hover:shadow-sm ${
              bundleQty === sb.qty ? 'border-primary ring-1 ring-primary' : sb.color
            }`}
          >
            <div className="flex items-start gap-2">
              <span className="text-xl flex-shrink-0">{sb.icon}</span>
              <div>
                <p className={`font-bold text-xs ${sb.textColor}`}>{sb.title}</p>
                <p className="text-xs text-gray-500 leading-tight mt-0.5">{sb.desc}</p>
                <span className={`inline-block mt-1.5 text-xs font-bold px-2 py-0.5 rounded-full ${sb.color} ${sb.textColor}`}>
                  {sb.tag}
                </span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
