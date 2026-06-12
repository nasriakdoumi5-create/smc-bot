import './globals.css';
import { CartProvider } from '@/context/CartContext';
import Navbar from '@/components/Navbar';
import CartDrawer from '@/components/CartDrawer';
import ExitIntentPopup from '@/components/ExitIntentPopup';
import SessionWrapper from '@/components/SessionWrapper';
import Footer from '@/components/Footer';
import WhatsAppButton from '@/components/WhatsAppButton';

export const metadata = {
  title: { default: 'PawCase — Custom Pet Phone Cases', template: '%s | PawCase' },
  description: 'Premium custom phone cases featuring your favorite pet breeds. Dogs, cats, and custom pet photos. Ships from EU in 3-5 days.',
  icons: { icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🐾</text></svg>' },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
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
