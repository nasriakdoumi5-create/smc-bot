export const metadata = { title: 'FAQ — Frequently Asked Questions' };

const faqs = [
  { q: 'How long does shipping take?', a: '3-5 business days within Europe via our Printful EU facilities. Orders are processed within 1-2 days.' },
  { q: 'What phone models do you support?', a: 'We currently support iPhone 12 to 15 Pro, and Samsung S22 to S24. More models are added regularly.' },
  { q: 'Can I return my order?', a: "Yes! We offer a 30-day return policy on all orders. If you're not happy with your case, contact us at hello@pawcase.eu." },
  { q: "How do I submit my pet's photo for a custom case?", a: "On the Custom Pet Phone Case product page, you'll find a photo upload field. Upload a high-resolution image of your pet (JPG, PNG, or HEIC, max 10MB)." },
  { q: 'What payment methods do you accept?', a: 'We accept Visa, Mastercard, PayPal, and Apple Pay. All payments are secured with SSL encryption.' },
  { q: 'Is free shipping available?', a: 'Yes! Orders over €40 qualify for free shipping across Europe. Orders under €40 have a flat €4.99 shipping fee.' },
];

export default function FAQPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-center mb-3">Frequently Asked Questions</h1>
      <p className="text-center text-gray-500 mb-12">Everything you need to know about PawCase 🐾</p>
      <div className="space-y-4">
        {faqs.map((faq, i) => (
          <div key={i} className="card p-6">
            <h3 className="font-bold text-lg mb-2 text-dark">Q: {faq.q}</h3>
            <p className="text-gray-600 leading-relaxed">{faq.a}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
