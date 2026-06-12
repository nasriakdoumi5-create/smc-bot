import './globals.css';
import { CartProvider } from '@/context/CartContext';
import Navbar from '@/components/Navbar';
import CartDrawer from '@/components/CartDrawer';
import ExitIntentPopup from '@/components/ExitIntentPopup';
import SessionWrapper from '@/components/SessionWrapper';
import Footer from '@/components/Footer';
import WhatsAppButton from '@/components/WhatsAppButton';
import { MetaPixelInit } from '@/components/MetaPixel';
import { TikTokPixelInit } from '@/components/TikTokPixel';

export const metadata = {
  title: { default: 'PawCase — Custom Pet Phone Cases', template: '%s | PawCase' },
  description: 'Turn your pet into wearable art. Premium custom phone cases for dog and cat lovers across Europe. Ships in 3–5 days. 30-day money-back guarantee.',
  keywords: ['pet phone case', 'custom pet case', 'dog phone case', 'cat phone case', 'personalised phone case', 'pet gift'],
  icons: { icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🐾</text></svg>' },
  openGraph: {
    type: 'website',
    siteName: 'PawCase',
    title: 'PawCase — Your Pet on Your Phone',
    description: 'Turn your pet into wearable art. Premium custom phone cases shipped from EU in 3–5 days. 5,000+ happy customers.',
    images: [{ url: 'https://picsum.photos/seed/golden1/1200/630', width: 1200, height: 630, alt: 'PawCase custom pet phone cases' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'PawCase — Your Pet on Your Phone',
    description: 'Premium custom pet phone cases. Ships from EU in 3–5 days.',
    images: ['https://picsum.photos/seed/golden1/1200/630'],
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <MetaPixelInit />
        <TikTokPixelInit />
        <SessionWrapper>
          <CartProvider>
            <Navbar />
            <CartDrawer />
            <ExitIntentPopup />
            <main>{children}</main>
            <Footer />
            <WhatsAppButton />
          </CartProvider>
        </SessionWrapper>
      </body>
    </html>
  );
}
