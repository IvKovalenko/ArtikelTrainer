/**
 * POST /api/auth/reset  { token, password }
 * Меняет пароль по одноразовому токену из письма, помечает email подтверждённым
 * (владение адресом доказано) и сразу логинит пользователя.
 */
import { hashPassword, signToken, sessionCookie, json, TTL, rateLimit, clientIp } from "../../_lib/auth.js";
import { consumeEmailToken } from "../../_lib/mail.js";

export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ error: "D1 binding DB is missing" }, 500);
  if (!env.JWT_SECRET) return json({ error: "JWT_SECRET is not set" }, 500);

  const rl = await rateLimit(env, "reset:" + clientIp(request), 10, 60 * 60 * 1000);
  if (!rl.ok) return json({ error: "rate-limited", retryAfter: rl.retryAfter }, 429, { "Retry-After": String(rl.retryAfter) });

  let body;
  try { body = await request.json(); } catch { return json({ error: "invalid JSON" }, 400); }
  const password = String(body?.password || "");
  if (password.length < 8) return json({ error: "weak-password" }, 400);

  const userId = await consumeEmailToken(env, body?.token, "reset");
  if (!userId) return json({ error: "invalid-token" }, 400);

  const user = await env.DB.prepare("SELECT id, email FROM users WHERE id = ?").bind(userId).first();
  if (!user) return json({ error: "invalid-token" }, 400);

  await env.DB.batch([
    env.DB.prepare("UPDATE users SET password_hash = ?, email_verified = 1 WHERE id = ?")
      .bind(await hashPassword(password), userId),
    // все остальные невыгоревшие ссылки пользователя гаснут
    env.DB.prepare("DELETE FROM email_tokens WHERE user_id = ?").bind(userId),
  ]);

  const token = await signToken({ sub: user.id, email: user.email }, env.JWT_SECRET);
  return json({ ok: true, token, user: { id: user.id, email: user.email } }, 200, {
    "Set-Cookie": sessionCookie(token, request, TTL),
  });
}
