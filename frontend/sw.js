/**
 * Service Worker for Hospital Management System PWA
 * Provides offline support and caching strategies
 */

const CACHE_NAME = 'hms-cache-v3';
const OFFLINE_URL = '/offline.html';

// Resources to pre-cache
const PRECACHE_RESOURCES = [
    '/',
    '/static/css/style.css',
    '/src/services/api.js',
    '/src/services/auth.js',
    '/src/services/validation.js',
    '/src/components/Navbar.js',
    '/src/views/Login.js',
    '/src/views/Register.js',
    '/src/router/index.js',
    '/src/main.js',
    '/offline.html',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
    'https://unpkg.com/vue@3/dist/vue.global.js',
    'https://unpkg.com/vue-router@4/dist/vue-router.global.js'
];

// Install event - pre-cache resources
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[Service Worker] Pre-caching resources');
                return cache.addAll(PRECACHE_RESOURCES);
            })
            .then(() => {
                console.log('[Service Worker] Installation complete');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('[Service Worker] Pre-cache failed:', error);
            })
    );
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Activating...');
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((cacheName) => cacheName !== CACHE_NAME)
                        .map((cacheName) => {
                            console.log('[Service Worker] Removing old cache:', cacheName);
                            return caches.delete(cacheName);
                        })
                );
            })
            .then(() => {
                console.log('[Service Worker] Activation complete');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip API requests (always go to network)
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    return new Response(JSON.stringify({
                        success: false,
                        message: 'You are offline. Please check your connection.',
                        error: 'offline'
                    }), {
                        status: 503,
                        headers: { 'Content-Type': 'application/json' }
                    });
                })
        );
        return;
    }

    // Cache-first strategy for static assets
    if (event.request.url.match(/\.(css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2)$/)) {
        // Skip caching for chrome-extension and other unsupported schemes
        if (!event.request.url.startsWith('http')) {
            return;
        }
        event.respondWith(
            caches.match(event.request)
                .then((cachedResponse) => {
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    return fetch(event.request)
                        .then((networkResponse) => {
                            // Cache the fetched response
                            if (networkResponse && networkResponse.status === 200) {
                                const responseClone = networkResponse.clone();
                                caches.open(CACHE_NAME)
                                    .then((cache) => cache.put(event.request, responseClone));
                            }
                            return networkResponse;
                        });
                })
        );
        return;
    }

    // Network-first strategy for HTML pages
    event.respondWith(
        fetch(event.request)
            .then((networkResponse) => {
                // Cache the response
                if (networkResponse && networkResponse.status === 200) {
                    const responseClone = networkResponse.clone();
                    caches.open(CACHE_NAME)
                        .then((cache) => cache.put(event.request, responseClone));
                }
                return networkResponse;
            })
            .catch(() => {
                // Fallback to cache
                return caches.match(event.request)
                    .then((cachedResponse) => {
                        if (cachedResponse) {
                            return cachedResponse;
                        }
                        // Return offline page for navigation requests
                        if (event.request.mode === 'navigate') {
                            return caches.match(OFFLINE_URL);
                        }
                        return null;
                    });
            })
    );
});

// Handle messages from clients
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// Background sync for offline form submissions
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-appointments') {
        console.log('[Service Worker] Syncing appointments...');
        event.waitUntil(syncAppointments());
    }
});

// Sync queued appointment requests
async function syncAppointments() {
    try {
        const db = await openDB();
        const requests = await getAllQueuedRequests(db);

        for (const request of requests) {
            try {
                await fetch(request.url, {
                    method: request.method,
                    headers: request.headers,
                    body: request.body
                });
                await deleteQueuedRequest(db, request.id);
            } catch (error) {
                console.error('[Service Worker] Sync failed for request:', request.id);
            }
        }
    } catch (error) {
        console.error('[Service Worker] Sync failed:', error);
    }
}

// Simple IndexedDB operations for offline queue
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('hms-offline', 1);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('queue')) {
                db.createObjectStore('queue', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

function getAllQueuedRequests(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['queue'], 'readonly');
        const store = transaction.objectStore('queue');
        const request = store.getAll();
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

function deleteQueuedRequest(db, id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['queue'], 'readwrite');
        const store = transaction.objectStore('queue');
        const request = store.delete(id);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve();
    });
}

console.log('[Service Worker] Script loaded');
