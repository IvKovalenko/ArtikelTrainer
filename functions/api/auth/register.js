/**
 * POST /api/auth/register  { email, password }
 * Создаёт пользователя, заводит пустой прогресс, выдаёт JWT (в теле и в cookie).
 */
import { hashPassword, signToken, sessionCookie, json, TTL } from "../../_lib/auth.js";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ error: "D1 binding DB is missing" }, 500);
  if (!env.JWT_SECRET) return json({ error: "JWT_SECRET is not set" }, 500);

  let body;
  try { body = await request.json(); } catch { return json({ error: "invalid JSON" }, 400); }

  const email = String(body?.email || "").trim().toLowerCase();
  const password = String(body?.password || "");
  if (!EMAIL_RE.test(email)) return json({ error: "invalid-email" }, 400);
  if (password.length < 8) return json({ error: "weak-password" }, 400); // минимум 8 символов

  const existing = await env.DB.prepare("SELECT id FROM users WHERE email = ?").bind(email).first();
  if (existing) return json({ error: "email-taken" }, 409);

  const id = crypto.randomUUID();
  const now = Date.now();
  const password_hash = await hashPassword(password);

  await env.DB.batch([
    env.DB.prepare("INSERT INTO users (id, email, password_hash, created_at) VALUES (?, ?, ?, ?)")
      .bind(id, email, password_hash, now),
    env.DB.prepare("INSERT INTO progress (user_id, data, updated_at) VALUES (?, '{}', ?)")
      .bind(id, now),
  ]);

  const token = await signToken({ sub: id, email }, env.JWT_SECRET);
  return json({ ok: true, token, user: { id, email } }, 200, {
    "Set-Cookie": sessionCookie(token, request, TTL),
  });
}
