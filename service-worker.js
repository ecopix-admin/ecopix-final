const CACHE = 'az-v1';
self.addEventListener('install', (e) => {
    e.waitUntil(caches.open(CACHE).then(c => c.addAll(['/', '/index.html', '/app.js', '/p2p-engine.js'])));
});
self.addEventListener('fetch', (e) => {
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
