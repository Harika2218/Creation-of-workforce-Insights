/**
 * HRvantage Enterprise PWA Service Worker
 * ---------------------------------------
 * Safe Enterprise Caching Policy:
 * 1. CACHED: Application shell (/index.html), static scripts, styles, icons, fonts.
 * 2. NEVER CACHED:
 *    - All REST API calls (/api/*)
 *    - Authentication endpoints (/api/v1/auth/*)
 *    - Confidential payroll data (/api/v1/payroll/*)
 *    - Employee private records and AI predictions
 *    - WebSocket real-time connections
 * 3. OFFLINE BEHAVIOR:
 *    - Navigations fallback to cached app shell to present the offline UI.
 *    - API calls return 503 JSON offline payload rather than stale employee records.
 */

const CACHE_NAME = 'hrvantage-shell-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.svg',
  '/icon-192.svg',
  '/icon-512.svg'
];

// 1. Install Event: Precache Application Shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// 2. Activate Event: Clean up outdated caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// 3. Fetch Event: Strict segregation between Shell and Sensitive API
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // A. Never intercept or cache non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // B. Never cache API requests, WebSocket, or Auth
  if (url.pathname.startsWith('/api') || url.pathname.includes('/auth') || url.protocol.startsWith('ws')) {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(
          JSON.stringify({
            error: 'NETWORK_OFFLINE',
            message: 'Enterprise network unavailable. Reconnect to process live HR actions.',
            offline: true,
            timestamp: new Date().toISOString()
          }),
          {
            status: 503,
            statusText: 'Service Unavailable (Offline)',
            headers: { 'Content-Type': 'application/json' }
          }
        );
      })
    );
    return;
  }

  // C. Navigation requests: Network-first, fallback to cached App Shell
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => {
        return caches.match('/index.html');
      })
    );
    return;
  }

  // D. Static Assets (JS, CSS, SVGs, Fonts): Stale-While-Revalidate
  const isStaticAsset =
    url.pathname.endsWith('.js') ||
    url.pathname.endsWith('.css') ||
    url.pathname.endsWith('.svg') ||
    url.pathname.endsWith('.woff2') ||
    url.pathname.endsWith('.ttf') ||
    url.pathname.endsWith('.png');

  if (isStaticAsset) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        const fetchPromise = fetch(request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const clone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return networkResponse;
        }).catch(() => cachedResponse);

        return cachedResponse || fetchPromise;
      })
    );
    return;
  }

  // Default: Network with cache fallback
  event.respondWith(
    caches.match(request).then((cached) => cached || fetch(request))
  );
});

// 4. Message Event: Support User-Initiated App Updates
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
