export const metadata = { title: 'About Us' };

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-16">
      <div className="text-center mb-12">
        <div className="text-6xl mb-4">🐾</div>
        <h1 className="text-4xl font-bold mb-4">Our Story</h1>
        <p className="text-xl text-gray-500 max-w-2xl mx-auto">Born from love for pets, designed for people who wear that love proudly.</p>
      </div>
      <div className="card p-8 mb-8">
        <p className="text-lg text-gray-700 leading-relaxed mb-6">
          PawCase was born from a simple idea — <strong>your phone case should say something about who you love most.</strong>
        </p>
        <p className="text-gray-600 leading-relaxed mb-6">
          We're pet lovers based in Europe, creating premium custom cases that celebrate the bond between you and your furry friend. Whether it's a golden retriever, a black cat, or your very own pet's face — we print it with care on high-quality cases that protect your phone in style.
        </p>
        <p className="text-gray-600 leading-relaxed">
          Every case is produced through our Printful EU facility, meaning fast shipping times across Europe, lower carbon footprint, and consistent quality you can trust.
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
        {[
          { emoji: '🌿', title: 'Eco-Friendly', desc: 'Print on demand — no overproduction, no waste' },
          { emoji: '🇪🇺', title: 'Made in EU', desc: 'Produced and shipped from European facilities' },
          { emoji: '💖', title: 'Pet Lovers First', desc: 'A small team that genuinely loves animals' },
        ].map(v => (
          <div key={v.title} className="card p-6">
            <div className="text-4xl mb-3">{v.emoji}</div>
            <h3 className="font-bold mb-2">{v.title}</h3>
            <p className="text-gray-500 text-sm">{v.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
