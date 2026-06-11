/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/**/*.{js,jsx}', './components/**/*.{js,jsx}', './data/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#2D6A4F', light: '#52B788', dark: '#1B4332' },
        secondary: { DEFAULT: '#F5F0E8', dark: '#E8E0CF' },
        accent: { DEFAULT: '#FF6B35', light: '#FF8C5A' },
        dark: '#1A1A2E',
      },
      fontFamily: { sans: ['Inter', 'sans-serif'] },
      borderRadius: { xl: '12px', '2xl': '16px', '3xl': '24px' },
    },
  },
  plugins: [],
};
