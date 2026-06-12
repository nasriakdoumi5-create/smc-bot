'use client';
import { Suspense, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'ttclid'];

function UTMCaptureInner() {
  const searchParams = useSearchParams();

  useEffect(() => {
    const utms = {};
    UTM_KEYS.forEach(k => {
      const v = searchParams.get(k);
      if (v) utms[k] = v;
    });
    if (Object.keys(utms).length > 0) {
      try {
        localStorage.setItem('pawcase-utm', JSON.stringify({
          ...utms,
          captured_at: new Date().toISOString(),
          landing_page: window.location.pathname,
        }));
      } catch {}
    }
  }, []);

  return null;
}

export default function UTMCapture() {
  return (
    <Suspense fallback={null}>
      <UTMCaptureInner />
    </Suspense>
  );
}
