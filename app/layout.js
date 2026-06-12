import './globals.css';
import { CartProvider } from '@/context/CartContext';
import Navbar from '@/components/Navbar';
import CartDrawer from '@/components/CartDrawer';
import ExitIntentPopup from '@/components/ExitIntentPopup';
import SessionWrapper from '@/components/SessionWrapper';

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
            <footer className="bg-dark text-white py-12 mt-20">
              <div className="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-8">
                <div>
                  <div className="text-2xl font-bold mb-2">🐾 PawCase</div>
                  <p className="text-gray-400 text-sm">Your pet, your style. Premium custom phone cases for pet lovers across Europe.</p>
                </div>
                <div>
                  <h4 className="font-semibold mb-3">Quick Links</h4>
                  <ul className="space-y-2 text-gray-400 text-sm">
                    <li><a href="/products" className="hover:text-white transition-colors">Shop All</a></li>
                    <li><a href="/wishlist" className="hover:text-white transition-colors">Wishlist</a></li>
                    <li><a href="/about" className="hover:text-white transition-colors">About Us</a></li>
                    <li><a href="/faq" className="hover:text-white transition-colors">FAQ</a></li>
                    <li><a href="/contact" className="hover:text-white transition-colors">Contact</a></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-3">Contact</h4>
                  <p className="text-gray-400 text-sm">hello@pawcase.eu</p>
                  <p className="text-gray-400 text-sm mt-1">Ships from Europe 🇪🇺</p>
                </div>
              </div>
              <div className="max-w-7xl mx-auto px-4 mt-8 pt-8 border-t border-gray-700 text-center text-gray-500 text-sm">
                © 2025 PawCase — All rights reserved
              </div>
            </footer>
          </CartProvider>
        </SessionWrapper>
      </body>
    </html>
  );
}
