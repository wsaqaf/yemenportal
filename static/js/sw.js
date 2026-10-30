/**
 * Yemen Portal (يمن بورتال) - Service Worker
 * PWA Offline support, smart caching, and background sync.
 */

const CACHE_VERSION = 'yp-pwa-v1.0.0';
const STATIC_CACHE = `yp-static-${CACHE_VERSION}`;
const PAGES_CACHE = `yp-pages-${CACHE_VERSION}`;
const OFFLINE_URL = '/offline/';

const PRECACHE_ASSETS = [
    '/',
    OFFLINE_URL,
    '/static/images/favicon.ico',
    '/static/logo.png',
    '/static/images/pwa/icon-192x192.png',
    '/static/images/pwa/icon-512x512.png',
    '/static/images/pwa/apple-touch-icon.png',
    'https://cdn.tailwindcss.com',
    'https://unpkg.com/htmx.org@1.9.10',
    'https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js'
];

// 1. Install Event: Precache Core Assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(STATIC_CACHE).then((cache) => {
            return cache.addAll(PRECACHE_ASSETS).catch((err) => {
                console.warn('[PWA SW] Precache partial error:', err);
            });
        }).then(() => self.skipWaiting())
    );
});

// 2. Activate Event: Clean up outdated caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== STATIC_CACHE && key !== PAGES_CACHE) {
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Helper: Check if request is an internal navigation (HTML)
function isNavigationRequest(request) {
    return request.mode === 'navigate' || 
           (request.method === 'GET' && request.headers.get('accept')?.includes('text/html'));
}

// Helper: Check if request is for admin or auth
function isBypassUrl(url) {
    const pathname = new URL(url).pathname;
    return pathname.startsWith('/admin/') || 
           pathname.startsWith('/accounts/') ||
           pathname.startsWith('/__debug__/');
}

// 3. Fetch Event: Smart Routing
self.addEventListener('fetch', (event) => {
    const request = event.request;
    const url = request.url;

    // Only handle GET requests and avoid admin/auth routes
    if (request.method !== 'GET' || isBypassUrl(url)) {
        return;
    }

    // A. Navigation Requests (HTML Pages): Network-First with Offline Fallback
    if (isNavigationRequest(request)) {
        event.respondWith(
            fetchWithTimeout(request, 3500)
                .then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        const copy = networkResponse.clone();
                        caches.open(PAGES_CACHE).then((cache) => cache.put(request, copy));
                    }
                    return networkResponse;
                })
                .catch(async () => {
                    // Try cached page
                    const cachedResponse = await caches.match(request);
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    // If not in cache, return the offline fallback page
                    const offlinePage = await caches.match(OFFLINE_URL);
                    return offlinePage || new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
                })
        );
        return;
    }

    // B. Static Assets (CSS, JS, Fonts, Images): Stale-While-Revalidate
    if (
        request.destination === 'style' ||
        request.destination === 'script' ||
        request.destination === 'image' ||
        request.destination === 'font' ||
        url.includes('/static/')
    ) {
        event.respondWith(
            caches.match(request).then((cachedResponse) => {
                const fetchPromise = fetch(request)
                    .then((networkResponse) => {
                        if (networkResponse && networkResponse.status === 200) {
                            const copy = networkResponse.clone();
                            caches.open(STATIC_CACHE).then((cache) => cache.put(request, copy));
                        }
                        return networkResponse;
                    })
                    .catch(() => cachedResponse);

                return cachedResponse || fetchPromise;
            })
        );
        return;
    }

    // C. Default: Network with Cache Fallback
    event.respondWith(
        fetch(request).catch(() => caches.match(request))
    );
});

// Helper for fetch timeout
function fetchWithTimeout(request, timeoutMs) {
    return new Promise((resolve, reject) => {
        const timer = setTimeout(() => {
            reject(new Error('Network timeout'));
        }, timeoutMs);

        fetch(request).then(
            (response) => {
                clearTimeout(timer);
                resolve(response);
            },
            (err) => {
                clearTimeout(timer);
                reject(err);
            }
        );
    });
}
