// service-worker-registration.js
export function setupServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('Service Worker registered with scope:', registration.scope);
            })
            .catch(error => {
                console.error('Service Worker registration failed:', error);
            });
    } else {
        console.warn('Service Workers not supported');
    }
}

// Create a basic service-worker.js file in the same directory
const swContent = `
self.addEventListener('install', (event) => {
    console.log('Service Worker installing');
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});
`;
// Write this to a file named 'service-worker.js' or include it in your build process
console.log('Service Worker content (save as service-worker.js):', swContent);