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
    description: 'Show your love for Golden Retrievers with this premium custom case. Durable, scratch-resistant, available for all major iPhone and Samsung models.',
    price: 22,
    originalPrice: 32,
    category: 'dogs',
    image: 'https://picsum.photos/seed/golden1/600/600',
    images: ['https://picsum.photos/seed/golden1/600/600', 'https://picsum.photos/seed/golden2/600/600'],
    featured: true,
    models: ['iPhone 15 Pro', 'iPhone 14 Pro', 'iPhone 13 Pro', 'iPhone 12 Pro', 'Samsung S24', 'Samsung S23', 'Samsung S22'],
  },
  {
    id: '2',
    slug: 'black-cat-phone-case',
    name: 'Black Cat Phone Case',
    description: 'Sleek and mysterious. Perfect for cat lovers. High-quality print that won\'t fade.',
    price: 22,
    originalPrice: 30,
    category: 'cats',
    image: 'https://picsum.photos/seed/blackcat1/600/600',
    images: ['https://picsum.photos/seed/blackcat1/600/600', 'https://picsum.photos/seed/blackcat2/600/600'],
    featured: true,
    models: ['iPhone 15 Pro', 'iPhone 14 Pro', 'iPhone 13 Pro', 'iPhone 12 Pro', 'Samsung S24', 'Samsung S23', 'Samsung S22'],
  },
  {
    id: '3',
    slug: 'french-bulldog-phone-case',
    name: 'French Bulldog Phone Case',
    description: 'The most loved dog breed in Europe, now on your phone. Premium matte finish.',
    price: 24,
    originalPrice: 34,
    category: 'dogs',
    image: 'https://picsum.photos/seed/frenchbull1/600/600',
    images: ['https://picsum.photos/seed/frenchbull1/600/600', 'https://picsum.photos/seed/frenchbull2/600/600'],
    featured: true,
    models: ['iPhone 15 Pro', 'iPhone 14 Pro', 'iPhone 13 Pro', 'iPhone 12 Pro', 'Samsung S24', 'Samsung S23', 'Samsung S22'],
  },
  {
    id: '4',
    slug: 'tabby-cat-phone-case',
    name: 'Tabby Cat Phone Case',
    description: 'Adorable tabby cat design for true cat lovers. Slim fit, full protection.',
    price: 22,
    originalPrice: 30,
    category: 'cats',
    image: 'https://picsum.photos/seed/tabbycat1/600/600',
    images: ['https://picsum.photos/seed/tabbycat1/600/600', 'https://picsum.photos/seed/tabbycat2/600/600'],
    featured: false,
    models: ['iPhone 15 Pro', 'iPhone 14 Pro', 'iPhone 13 Pro', 'iPhone 12 Pro', 'Samsung S24', 'Samsung S23', 'Samsung S22'],
  },
  {
    id: '5',
    slug: 'custom-pet-phone-case',
    name: 'Custom Pet Phone Case',
    description: 'Upload your pet\'s photo and we\'ll print it on a premium case. 100% unique, made just for you.',
    price: 35,
    originalPrice: 50,
    category: 'custom',
    image: 'https://picsum.photos/seed/custompet1/600/600',
    images: ['https://picsum.photos/seed/custompet1/600/600'],
    featured: true,
    isCustom: true,
    models: ['iPhone 15 Pro', 'iPhone 14 Pro', 'iPhone 13 Pro', 'iPhone 12 Pro', 'Samsung S24', 'Samsung S23', 'Samsung S22'],
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
