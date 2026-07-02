/**
 * Cloudflare Pages Function: /api/progress  (многопользовательская версия)
 * GET  → прогресс текущего пользователя (JSON-блоб из D1)
 * POST → сохранить прогресс текущего пользователя
 *
 * Пользователь определяется по JWT (cookie или Authorization: Bearer).
 * Хранилище — таблица progress в D1 (binding DB). KV больше не используется.
 */
import { getAuth, json } from "../_lib/auth.js";

export async function onRequestGet({ request, env }) {
  if (!env.DB) return json({ error: "D1 binding DB is missing" }, 500);
  const auth = await getAuth(request, env);
  if (!auth) return json({ error: "unauthorized" }, 401);

  const row = await env.DB.prepare("SELECT data FROM progress WHERE user_id = ?")
    .bind(auth.sub).first();
  return json(row ? JSON.parse(row.data) : {});
}

export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ error: "D1 binding DB is missing" }, 500);
  const auth = await getAuth(request, env);
  if (!auth) return json({ error: "unauthorized" }, 401);

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "invalid JSON" }, 400);
  }
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return json({ error: "expected an object" }, 400);
  }

  await env.DB.prepare(
    "INSERT INTO progress (user_id, data, updated_at) VALUES (?, ?, ?) " +
    "ON CONFLICT(user_id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at"
  ).bind(auth.sub, JSON.stringify(body), Date.now()).run();

  return json({ ok: true, words: Object.keys(body).length });
}
