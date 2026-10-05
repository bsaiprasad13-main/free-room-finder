const CACHE_NAME = 'free-rooms-v4';

// How long to wait for the network before showing the cached page (slow campus Wi-Fi)
const NETWORK_TIMEOUT_MS = 3000;

// Files to cache on install
const PRECACHE_URLS = [
  './index.html',
  './timetable.json',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png'
];

// ── Install: pre-cache shell ──────────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      // cache: 'reload' skips the browser's HTTP cache so we never pre-cache a stale copy
      .then(cache => cache.addAll(PRECACHE_URLS.map(u => new Request(u, { cache: 'reload' }))))
      .then(() => self.skipWaiting())   // activate immediately
  );
});

// ── Activate: delete old caches ───────────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys =>
        Promise.all(
          keys
            .filter(key => key !== CACHE_NAME)
            .map(key => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())  // take control immediately
  );
});

// ── Network-first for the page and timetable, so updates show on the very next open ──
// Falls back to the cached copy (stored under cacheKey) when offline or the network is too slow.
function networkFirst(request, cacheKey) {
  const network = fetch(request, { cache: 'no-cache' })
    .then(response => {
      if (response && response.status === 200) {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(cacheKey, clone));
      }
      return response;
    });

  const timeout = new Promise(resolve => setTimeout(resolve, NETWORK_TIMEOUT_MS))
    .then(() => caches.match(cacheKey));

  return Promise.race([network, timeout])
    .then(response => response || network)   // timed out with nothing cached: keep waiting
    .catch(() => caches.match(cacheKey));
}

// ── Fetch: network-first for page + timetable, stale-while-revalidate for other assets ──
self.addEventListener('fetch', event => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Skip cross-origin requests (Google Fonts, Analytics, etc.)
  if (url.origin !== location.origin) return;

  if (event.request.mode === 'navigate') {
    event.respondWith(networkFirst(event.request, './index.html'));
    return;
  }

  if (url.pathname.endsWith('/timetable.json')) {
    event.respondWith(networkFirst(event.request, './timetable.json'));
    return;
  }

  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) {
        // Serve from cache, but refresh it in the background
        const networkRefresh = fetch(event.request)
          .then(response => {
            if (response && response.status === 200) {
              const clone = response.clone();
              caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
            }
            return response;
          })
          .catch(() => {/* offline – cached copy already served */});

        return cached;   // return cache immediately; background refresh runs async
      }

      // Not in cache – fetch from network, cache it, return it
      return fetch(event.request)
        .then(response => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() =>
          // Fallback: serve index.html for navigation requests so the app shell loads
          event.request.mode === 'navigate'
            ? caches.match('./index.html')
            : Response.error()
        );
    })
  );
});
