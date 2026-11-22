/* =====================================================================
   TraceCam Service Worker
   - 以 VERSION 常數命名快取；每次更新發佈都必須遞增 VERSION，
     已安裝的使用者才會偵測到新版並看到「有新版本可用．立即更新」。
   - 頁面導覽：網路優先，離線退回快取
   - 靜態資源：先回快取，背景同步更新（stale-while-revalidate）
   - activate：清除舊版快取
   ===================================================================== */
const VERSION = 'v1.0.0';
const CACHE = 'tracecam-' + VERSION;

// 預先快取的核心檔案（相對路徑，部署在 /<repo>/ 子路徑也能運作）
const CORE = [
  './',
  './index.html',
  './install.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png',
  './apple-touch-icon.png',
  './qr-install.png'
];

self.addEventListener('install', event => {
  // 不主動 skipWaiting：等使用者在畫面上按下「立即更新」才切換
  event.waitUntil(
    caches.open(CACHE).then(cache => Promise.all(
      CORE.map(url => cache.add(new Request(url, { cache: 'reload' })).catch(err => console.warn('預快取失敗', url, err)))
    ))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('tracecam-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('message', event => {
  const d = event.data;
  if (d === 'SKIP_WAITING' || (d && d.type === 'SKIP_WAITING')) self.skipWaiting();
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   // 地圖磚等跨網域請求交給瀏覽器處理

  // 頁面導覽：網路優先 → 失敗退回快取
  if (req.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const net = await fetch(req);
        if (net && net.ok) { const cache = await caches.open(CACHE); cache.put(req, net.clone()); }
        return net;
      } catch (e) {
        const cache = await caches.open(CACHE);
        return (await cache.match(req, { ignoreSearch: true })) || (await cache.match('./index.html')) || (await cache.match('./')) ||
          new Response('目前離線，且尚未快取此頁面', { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
      }
    })());
    return;
  }

  // 靜態資源：先回快取，同時背景更新
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const hit = await cache.match(req);
    const update = fetch(req).then(net => { if (net && net.ok) cache.put(req, net.clone()); return net; }).catch(() => null);
    if (hit) { event.waitUntil(update); return hit; }
    return (await update) || new Response('', { status: 504 });
  })());
});
