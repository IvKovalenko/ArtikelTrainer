/**
 * CORS для /api/* — нужно, когда приложение-обёртка Capacitor (другой origin)
 * обращается к API с токеном в заголовке Authorization: Bearer.
 *
 * Статика (index.html, app.js, words.json …) отдаётся публично: словарь не
 * секретный, а доступ к данным пользователя защищён JWT на уровне эндпоинтов
 * (/api/progress, /api/auth/me). Прежняя одно-парольная защита сайта убрана.
 */

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",         // Bearer-токен, без cookie-credentials
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age": "86400",
  };
}

export async function onRequest(context) {
  const { request, next } = context;
  const isApi = new URL(request.url).pathname.startsWith("/api/");

  if (isApi && request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders() });
  }

  const res = await next();
  if (!isApi) return res;

  const headers = new Headers(res.headers);
  for (const [k, v] of Object.entries(corsHeaders())) headers.set(k, v);
  return new Response(res.body, { status: res.status, statusText: res.statusText, headers });
}
