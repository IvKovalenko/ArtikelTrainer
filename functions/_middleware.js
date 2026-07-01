/**
 * Гейт доступа ко всему сайту по паролю (проверка на сервере).
 *
 * Защита включается, ТОЛЬКО если задан секрет SITE_PASSWORD:
 *   npx wrangler pages secret put SITE_PASSWORD
 * Если секрет не задан — сайт открыт (как было раньше).
 *
 * Сессия — stateless-кука: её значение = HMAC-SHA256(ключ=пароль, "artikel-session").
 * Подделать куку, не зная пароля, нельзя, а на сервере ничего хранить не нужно.
 * Проверка проходит перед статикой И перед /api/* — значит, посторонний не может
 * ни открыть приложение, ни дёрнуть API, чтобы сбросить статистику.
 */

const COOKIE = "artikel_auth";
const SESSION_MSG = "artikel-session-v1";

// значение сессионной куки для данного пароля
async function sessionToken(password) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(password),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(SESSION_MSG));
  return btoa(String.fromCharCode(...new Uint8Array(sig)));
}

function getCookie(request, name) {
  const raw = request.headers.get("Cookie") || "";
  for (const part of raw.split(/;\s*/)) {
    const i = part.indexOf("=");
    if (i > -1 && part.slice(0, i) === name) return part.slice(i + 1);
  }
  return null;
}

// сравнение строк без утечки по времени
function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const path = url.pathname;
  const password = env.SITE_PASSWORD;

  // защита выключена → пропускаем всё
  if (!password) return next();

  // страница входа и её обработчики доступны без авторизации
  if (path === "/login" || path === "/login.html" ||
      path === "/api/login" || path === "/api/logout") {
    return next();
  }

  const expected = await sessionToken(password);
  const provided = getCookie(request, COOKIE);
  if (provided && safeEqual(provided, expected)) {
    return next(); // авторизован — пропускаем к статике/функциям
  }

  // не авторизован: навигацию по страницам уводим на форму входа, остальное — 401
  const wantsHtml = (request.headers.get("Accept") || "").includes("text/html");
  if (wantsHtml) {
    return Response.redirect(url.origin + "/login.html", 302);
  }
  return new Response(JSON.stringify({ error: "unauthorized" }), {
    status: 401,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}
