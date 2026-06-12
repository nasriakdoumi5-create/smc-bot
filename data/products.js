export const categories = [
  { id: 'dogs', name: 'Dogs', icon: '🐕', slug: 'dogs' },
  { id: 'cats', name: 'Cats', icon: '🐈', slug: 'cats' },
  { id: 'custom', name: 'Custom', icon: '✨', slug: 'custom' },
];

export const products = [
  {
    id: '1',
    slug: 'golden-retriever-phone-case',
    name: 'Golden Retriever Phone Case',
    description: "Every time you pick up your phone, you'll see that golden smile. Our premium cases turn your favorite pet breed into wearable art — sharp print, zero fade, total protection.",
    price: 22,
    originalPrice: 32,
    category: 'dogs',
    image: 'https://picsum.photos/seed/golden1/600/600',
    images: ['https://picsum.photos/seed/golden1/600/600', 'https://picsum.photos/seed/golden2/600/600'],
    featured: true,
    badge: 'Best Seller',
    rating: 4.9,
    reviewCount: 312,
    stock: 8,
    viewerCount: 14,
    models: ['iPhone 15 Pro', 'iPhone 14 Pro', 'iPhone 13 Pro', 'iPhone 12 Pro', 'Samsung S24', 'Samsung S23', 'Samsung S22'],
    features: [
      'Slim fit, full 360° protection',
      'Premium matte finish — no fingerprints',
      "Vivid UV-resistant print that won't fade",
      'Raised edges protect your screen',
      'Wireless charging compatible',
    ],
    reviews: [
      { name: 'Sofia M.', location: 'Madrid, Spain', rating: 5, date: 'March 2025', text: 'My golden retriever case gets compliments everywhere I go! The print quality is incredible and it arrived in just 4 days. Already ordered one for my mum.', verified: true },
      { name: 'Lucas K.', location: 'Berlin, Germany', rating: 5, date: 'February 2025', text: 'Perfect quality. The image is super sharp and the case feels really sturdy. My dog Max approves too 😄', verified: true },
      { name: 'Emma V.', location: 'Amsterdam, Netherlands', rating: 5, date: 'February 2025', text: 'Bought this as a gift for my sister who is obsessed with goldens. She absolutely loved it! Great protection too.', verified: true },
      { name: 'Marie D.', location: 'Paris, France', rating: 4, date: 'January 2025', text: "Beautiful case, very well made. The matte finish is great and the print hasn't faded at all after 2 months.", verified: true },
      { name: 'Anna S.', location: 'Stockholm, Sweden', rating: 5, date: 'January 2025', text: 'Exceeded my expectations! Super fast delivery and the case looks exactly like the photo. Will buy again!', verified: true },
    ],
  },
  {
    id: '2',
    slug: 'black-cat-phone-case',
    name: 'Black Cat Phone Case',
    description: "Sleek, mysterious, and completely irresistible — just like your favourite feline. This case turns heads and protects your phone with the elegance only a black cat can bring.",
    price: 22,
    originalPrice: 30,
    category: 'cats',
    image: 'https://picsum.photos/seed/blackcat1/600/600',
    images: ['https://picsum.photos/seed/blackcat1/600/600', 'https://picsum.photos/seed/blackcat2/600/600'],
    featured: true,
    badge: null,
    rating: 4.8,
    reviewCount: 156,
    stock: 15,
    viewerCount: 9,
    models: ['iPhone 15 Pro', 'iPhone 14 Pro', 'iPhone 13 Pro', 'iPhone 12 Pro', 'Samsung S24', 'Samsung S23', 'Samsung S22'],
    features: [
      'Slim fit, full 360° protection',
      'Premium matte finish — no fingerprints',
      "Vivid UV-resistant print that won't fade",
      'Raised edges protect your screen',
      'Wireless charging compatible',
    ],
    reviews: [
      { name: 'Clara B.', location: 'Brussels, Belgium', rating: 5, date: 'March 2025', text: 'Obsessed with this case! My black cat Luna looks stunning on it. Everyone asks where I got it.', verified: true },
      { name: 'James R.', location: 'London, UK', rating: 5, date: 'February 2025', text: 'Great quality and fast delivery. The print is razor-sharp and the matte finish is gorgeous.', verified: true },
      { name: 'Lena F.', location: 'Hamburg, Germany', rating: 4, date: 'February 2025', text: "Really nice case, good protection. The image is vibrant and hasn't faded even with daily use.", verified: true },
      { name: 'Nina P.', location: 'Warsaw, Poland', rating: 5, date: 'January 2025', text: 'Perfect gift for cat lovers! My friend was over the moon when she received it.', verified: true },
      { name: 'Tom H.', location: 'Vienna, Austria', rating: 5, date: 'January 2025', text: "Bought this for my girlfriend who loves black cats. She hasn't put it down since!", verified: true },
    ],
  },
  {
    id: '3',
    slug: 'french-bulldog-phone-case',
    name: 'French Bulldog Phone Case',
    description: "The most loved dog breed in Europe now lives in your pocket. Bold, charming, and undeniably adorable — carry your Frenchie's spirit everywhere you go with this premium matte case.",
    price: 24,
    originalPrice: 34,
    category: 'dogs',
    image: 'https://picsum.photos/seed/frenchbull1/600/600',
    images: ['https://picsum.photos/seed/frenchbull1/600/600', 'https://picsum.photos/seed/frenchbull2/600/600'],
    featured: true,
    badge: 'Popular',
    rating: 4.8,
    reviewCount: 203,
    stock: 6,
    viewerCount: 17,
    models: ['iPhone 15 Pro', 'iPhone 14 Pro', 'iPhone 13 Pro', 'iPhone 12 Pro', 'Samsung S24', 'Samsung S23', 'Samsung S22'],
    features: [
      'Slim fit, full 360° protection',
      'Premium matte finish — no fingerprints',
      "Vivid UV-resistant print that won't fade",
      'Raised edges protect your screen',
      'Wireless charging compatible',
    ],
    reviews: [
      { name: 'Marco R.', location: 'Rome, Italy', rating: 5, date: 'March 2025', text: "I have a French Bulldog and this case is spot on! The colors are amazing. My friends always want to know where I got it.", verified: true },
      { name: 'Sarah L.', location: 'Dublin, Ireland', rating: 5, date: 'February 2025', text: 'Ordered this for my husband who has a Frenchie obsession. He absolutely loves it!', verified: true },
      { name: 'Peter V.', location: 'Rotterdam, Netherlands', rating: 4, date: 'February 2025', text: 'Good quality, arrived quickly. Print is vivid and the case fits perfectly.', verified: true },
      { name: 'Ingrid K.', location: 'Oslo, Norway', rating: 5, date: 'January 2025', text: 'Such a cute design! The premium finish makes it feel very high quality. Worth every cent.', verified: true },
      { name: 'Diego M.', location: 'Barcelona, Spain', rating: 5, date: 'January 2025', text: 'Perfect! Exactly as described. Fast shipping and excellent packaging.', verified: true },
    ],
  },
  {
    id: '4',
    slug: 'tabby-cat-phone-case',
    name: 'Tabby Cat Phone Case',
    description: "Capture the warm, playful energy of a tabby cat every time you reach for your phone. A beautiful tribute to the world's most popular cat, now protecting your screen in style.",
    price: 22,
    originalPrice: 30,
    category: 'cats',
    image: 'https://picsum.photos/seed/tabbycat1/600/600',
    images: ['https://picsum.photos/seed/tabbycat1/600/600', 'https://picsum.photos/seed/tabbycat2/600/600'],
    featured: false,
    badge: 'New',
    rating: 4.7,
    reviewCount: 89,
    stock: 23,
    viewerCount: 7,
    models: ['iPhone 15 Pro', 'iPhone 14 Pro', 'iPhone 13 Pro', 'iPhone 12 Pro', 'Samsung S24', 'Samsung S23', 'Samsung S22'],
    features: [
      'Slim fit, full 360° protection',
      'Premium matte finish — no fingerprints',
      "Vivid UV-resistant print that won't fade",
      'Raised edges protect your screen',
      'Wireless charging compatible',
    ],
    reviews: [
      { name: 'Mia T.', location: 'Copenhagen, Denmark', rating: 5, date: 'March 2025', text: 'My tabby cat Tiger is now immortalised on my phone case. The likeness is incredible and quality superb!', verified: true },
      { name: 'Chris B.', location: 'Edinburgh, UK', rating: 4, date: 'February 2025', text: 'Lovely case, really well made. Print is clear and vibrant. Arrived sooner than expected.', verified: true },
      { name: 'Hanna L.', location: 'Helsinki, Finland', rating: 5, date: 'February 2025', text: 'Bought for my cat-obsessed daughter and she was thrilled. Perfect quality!', verified: true },
      { name: 'Rene G.', location: 'Lyon, France', rating: 5, date: 'January 2025', text: 'Absolutely gorgeous. The detail in the print is impressive and it fits my phone perfectly.', verified: true },
      { name: 'Pablo S.', location: 'Valencia, Spain', rating: 4, date: 'January 2025', text: 'Great product and great service. Will order more designs for friends and family.', verified: true },
    ],
  },
  {
    id: '5',
    slug: 'custom-pet-phone-case',
    name: 'Custom Pet Phone Case',
    description: "Your pet is one of a kind — your phone case should be too. Upload your favourite photo and we'll transform it into a stunning, print-perfect case that tells the world who you love most.",
    price: 35,
    originalPrice: 50,
    category: 'custom',
    image: 'https://picsum.photos/seed/custompet1/600/600',
    images: ['https://picsum.photos/seed/custompet1/600/600'],
    featured: true,
    isCustom: true,
    badge: null,
    rating: 4.9,
    reviewCount: 127,
    stock: 3,
    viewerCount: 19,
    models: ['iPhone 15 Pro', 'iPhone 14 Pro', 'iPhone 13 Pro', 'iPhone 12 Pro', 'Samsung S24', 'Samsung S23', 'Samsung S22'],
    features: [
      'Your own pet photo, printed in stunning detail',
      'Premium matte finish — no fingerprints',
      "Vivid UV-resistant print that won't fade",
      'Raised edges protect your screen',
      'Wireless charging compatible',
    ],
    reviews: [
      { name: 'Julia M.', location: 'Munich, Germany', rating: 5, date: 'March 2025', text: 'I uploaded a photo of my dog Biscuit and the result blew me away. The detail is insane — every hair is visible!', verified: true },
      { name: 'David H.', location: 'Amsterdam, Netherlands', rating: 5, date: 'February 2025', text: 'Ordered custom cases for my whole family as Christmas gifts. Everyone cried (happy tears)! Amazing quality.', verified: true },
      { name: 'Chloe F.', location: 'Paris, France', rating: 5, date: 'February 2025', text: 'The mockup arrived within 24 hours and the final product looks even better in person. 10/10 service.', verified: true },
      { name: 'Ben A.', location: 'London, UK', rating: 4, date: 'January 2025', text: 'Great process — they sent a preview before printing and made changes until I was happy. Really impressive.', verified: true },
      { name: 'Lisa T.', location: 'Zurich, Switzerland', rating: 5, date: 'January 2025', text: 'Best gift I ever gave. My sister sobbed when she saw her cat on the case. Worth every euro!', verified: true },
    ],
  },
];

export function getProductBySlug(slug) {
  return products.find(p => p.slug === slug);
}

export function getProductById(id) {
  return products.find(p => p.id === id);
}

export function getFeaturedProducts() {
  return products.filter(p => p.featured);
}

export function getProductsByCategory(category) {
  if (!category || category === 'all') return products;
  return products.filter(p => p.category === category);
}
