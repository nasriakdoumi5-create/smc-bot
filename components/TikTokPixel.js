'use client';
import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Script from 'next/script';

export function TikTokPixelInit() {
  const pixelId = process.env.NEXT_PUBLIC_TIKTOK_PIXEL_ID;
  const pathname = usePathname();

  useEffect(() => {
    if (!pixelId || typeof window === 'undefined' || !window.ttq) return;
    window.ttq.page();
  }, [pathname, pixelId]);

  if (!pixelId) return null;

  const initScript = `
    !function (w, d, t) {
      w.TiktokAnalyticsObject=t;
      var ttq=w[t]=w[t]||[];
      ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie","holdConsent","revokeConsent","grantConsent"];
      ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};
      for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);
      ttq.instance=function(t){for(var e=ttq._i[t]||[],n=0;n<ttq.methods.length;n++)ttq.setAndDefer(e,ttq.methods[n]);return e};
      ttq.load=function(e,n){var r="https://analytics.tiktok.com/i18n/pixel/events.js",o=n&&n.partner;ttq._i=ttq._i||{};ttq._i[e]=[];ttq._i[e]._u=r;ttq._t=ttq._t||{};ttq._t[e]=+new Date;ttq._o=ttq._o||{};ttq._o[e]=n||{};n=document.createElement("script");n.type="text/javascript";n.async=!0;n.src=r+"?sdkid="+e+"&lib="+t;e=document.getElementsByTagName("script")[0];e.parentNode.insertBefore(n,e)};
      ttq.load('${pixelId}');
      ttq.page();
    }(window, document, 'ttq');
  `;

  return (
    <Script
      id="tiktok-pixel-base"
      strategy="afterInteractive"
      dangerouslySetInnerHTML={{ __html: initScript }}
    />
  );
}

export function ttqViewContent(product) {
  if (typeof window === 'undefined' || !window.ttq) return;
  window.ttq.track('ViewContent', {
    content_name: product.name,
    content_id: product.id,
    content_type: 'product',
    value: product.price,
    currency: 'EUR',
  });
}

export function ttqAddToCart(product) {
  if (typeof window === 'undefined' || !window.ttq) return;
  window.ttq.track('AddToCart', {
    content_name: product.name,
    content_id: product.id,
    value: product.price,
    currency: 'EUR',
  });
}

export function ttqInitiateCheckout(total) {
  if (typeof window === 'undefined' || !window.ttq) return;
  window.ttq.track('InitiateCheckout', {
    value: total,
    currency: 'EUR',
  });
}

export function ttqPurchase(orderNum, total) {
  if (typeof window === 'undefined' || !window.ttq) return;
  window.ttq.track('CompletePayment', {
    value: total,
    currency: 'EUR',
    order_id: orderNum,
  });
}
