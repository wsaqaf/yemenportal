/**
 * Yemen Portal (يمن بورتال) - Service Worker
 * PWA Offline support, smart caching, and background sync.
 */

const CACHE_VERSION = 'yp-pwa-v1.0.1';
const STATIC_CACHE = `yp-static-${CACHE_VERSION}`;
const PAGES_CACHE = `yp-pages-${CACHE_VERSION}`;
const OFFLINE_URL = '/offline/';

const CORE_ASSETS = [
    '/',
    OFFLINE_URL,
    '/static/images/favicon.ico',
    '/static/logo.png',
    '/static/images/pwa/icon-192x192.png',
    '/static/images/pwa/icon-512x512.png',
    '/static/images/pwa/apple-touch-icon.png'
];

// 1. Install Event: Precache Core Assets safely
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(STATIC_CACHE).then((cache) => {
            // Cache each asset independently so one failure never blocks the others
            return Promise.allSettled(
                CORE_ASSETS.map((url) =>
                    fetch(url, { cache: 'no-cache' })
                        .then((res) => {
                            if (res.ok) {
                                return cache.put(url, res);
                            }
                        })
                        .catch((err) => {
                            console.warn('[PWA SW] Precache failed for:', url, err);
                        })
                )
            );
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

// Helper: Check if request is for admin, moderation, or auth
function isBypassUrl(url) {
    const pathname = new URL(url).pathname;
    return pathname.startsWith('/admin/') || 
           pathname.startsWith('/accounts/') ||
           pathname.startsWith('/moderation/') ||
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

    // A. Navigation Requests (HTML Pages): True Network-First with Offline Fallback
    // Never abort healthy requests with artificial short timeouts!
    if (isNavigationRequest(request)) {
        event.respondWith(
            fetch(request)
                .then((networkResponse) => {
                    if (networkResponse && networkResponse.status === 200) {
                        const copy = networkResponse.clone();
                        caches.open(PAGES_CACHE).then((cache) => cache.put(request, copy));
                    }
                    return networkResponse;
                })
                .catch(async () => {
                    // Network failed (device is offline or connection dropped)
                    // 1. Try cached page first
                    const cachedResponse = await caches.match(request);
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    // 2. If not in cache, return the styled offline fallback page
                    const offlinePage = await caches.match(OFFLINE_URL);
                    if (offlinePage) {
                        return offlinePage;
                    }
                    // 3. Final safety net with styled Arabic message (never raw plain text 'Offline')
                    return new Response(
                        `<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>غير متصل</title></head><body style="font-family:sans-serif;text-align:center;padding:50px;"><h2>تعذر الاتصال بالإنترنت</h2><p>يرجى التحقق من اتصال الشبكة وإعادة المحاولة.</p><button onclick="location.reload()" style="padding:10px 20px;border-radius:8px;background:#1779ba;color:#fff;border:none;cursor:pointer;">إعادة المحاولة</button></body></html>`,
                        { headers: { 'Content-Type': 'text/html; charset=utf-8' }, status: 503 }
                    );
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
