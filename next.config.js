module.exports = {
  images: {
    remotePatterns: [{ protocol:'https', hostname:'picsum.photos' }],
  },
  experimental: {
    outputFileTracingIncludes: {
      '/**': ['./prisma/seed.db', './prisma/migrations/**'],
    },
  },
};
