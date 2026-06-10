import './globals.css';
import { CartProvider } from '../context/CartContext';
import Navbar from '../components/Navbar';
import CartDrawer from '../components/CartDrawer';
import Footer from '../components/Footer';
import { Toaster } from 'sonner';
import SessionWrapper from '../components/SessionWrapper';

export const metadata = { title: 'متجري — تسوق بذكاء', description: 'متجر إلكتروني متكامل' };

export default function RootLayout({ children }) {
  return (
    <html lang="ar" dir="rtl">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet" />
      </head>
      <body>
        <SessionWrapper>
          <CartProvider>
            <Navbar />
            <CartDrawer />
            <main className="min-h-screen">{children}</main>
            <Footer />
          </CartProvider>
        </SessionWrapper>
        <Toaster position="top-center" richColors />
      </body>
    </html>
  );
}
