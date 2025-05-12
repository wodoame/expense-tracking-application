const CACHE_NAME = 'django-pwa-cache-v1';
const urlsToCache = [
  '/',
  '/static/css/output.css', // Replace with your CSS file path
//   '/static/js/main.js',    // Replace with your JS file path
  '/static/js/alpine.min.js',    // Replace with your JS file path
  '/static/js/htmx.min.js',    // Replace with your JS file path

  '/static/fonts/Poppins-Regular.ttf',
  '/static/imgs/logo-100x100.png'
];

// Install the service worker and cache assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

// Activate the service worker and clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    })
  );
});

// Fetch event to serve cached content or fetch from network
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request);
      })
  );
});