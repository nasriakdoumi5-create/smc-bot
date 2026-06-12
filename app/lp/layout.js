'use client';
import { useEffect } from 'react';

export default function LPLayout({ children }) {
  useEffect(() => {
    // Collect all global chrome elements rendered by the root layout
    const nav = document.querySelector('nav');
    const footer = document.querySelector('footer');

    // The Navbar component renders an announcement bar <div> immediately before <nav>
    // in the DOM. Target it via its sibling relationship.
    const announcementBar = nav ? nav.previousElementSibling : null;

    // WhatsAppButton renders a fixed <a> — target by href pattern
    const whatsapp = document.querySelector('a[href^="https://wa.me"]');

    const elements = [announcementBar, nav, footer, whatsapp].filter(Boolean);
    const previous = elements.map(el => el.style.display);

    elements.forEach(el => { el.style.display = 'none'; });

    return () => {
      elements.forEach((el, i) => { el.style.display = previous[i]; });
    };
  }, []);

  return <>{children}</>;
}
