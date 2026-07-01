/**
 * Cloudflare Pages Function: /api/progress
 * GET  → вернуть JSON статистики из KV
 * POST → сохранить JSON статистики в KV
 *
 * Привязка KV: namespace binding с именем PROGRESS (см. wrangler.toml / дашборд).
 * Необязательная защита: если задан env.SYNC_TOKEN, требуется заголовок
 *   Authorization: Bearer <SYNC_TOKEN>
 */

const KEY = "article-progress";

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

function authError(env, request) {
  const token = env.SYNC_TOKEN;
  if (!token) return null; // защита выключена
  const header = request.headers.get("Authorization") || "";
  if (header === "Bearer " + token) return null;
  return json({ error: "unauthorized" }, 401);
}

export async function onRequestGet({ env, request }) {
  const denied = authError(env, request);
  if (denied) return denied;
  if (!env.PROGRESS) return json({ error: "KV binding PROGRESS is missing" }, 500);

  const raw = await env.PROGRESS.get(KEY);
  return json(raw ? JSON.parse(raw) : {});
}

export async function onRequestPost({ env, request }) {
  const denied = authError(env, request);
  if (denied) return denied;
  if (!env.PROGRESS) return json({ error: "KV binding PROGRESS is missing" }, 500);

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "invalid JSON" }, 400);
  }
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return json({ error: "expected an object" }, 400);
  }

  await env.PROGRESS.put(KEY, JSON.stringify(body));
  return json({ ok: true, words: Object.keys(body).length });
}
