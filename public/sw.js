/* Service worker: сеть-в-приоритете (network-first), кэш — резерв для офлайна.
   API (/api/*) не кэшируется никогда. Такой режим исключает «залипание» на
   старых версиях файлов при частых обновлениях. */
const CACHE = "artikel-v8";
const SHELL = [
  "./",
  "./index.html",
  "./style.css",
  "./app.js",
  "./words.json",
  "./manifest.webmanifest",
  "./icons/icon.svg",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);

  // только GET и только свой origin
  if (req.method !== "GET" || url.origin !== location.origin) return;
  // API — только сеть, без кэша
  if (url.pathname.startsWith("/api/")) return;

  // network-first: всегда пробуем свежее, при офлайне — из кэша
  e.respondWith(
    fetch(req)
      .then((res) => {
        // не кэшируем редиректы (напр. переадресацию на страницу входа),
        // иначе форма логина может «прилипнуть» под адресом приложения
        if (res && res.ok && !res.redirected) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      })
      .catch(() => caches.match(req))
  );
});
