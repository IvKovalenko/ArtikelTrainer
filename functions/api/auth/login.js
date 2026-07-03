/**
 * POST /api/auth/login  { email, password }
 * Проверяет пароль, выдаёт JWT (в теле и в cookie).
 */
import { verifyPassword, signToken, sessionCookie, json, TTL, rateLimit, clientIp } from "../../_lib/auth.js";

export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ error: "D1 binding DB is missing" }, 500);
  if (!env.JWT_SECRET) return json({ error: "JWT_SECRET is not set" }, 500);

  // не более 10 попыток входа с одного IP за 15 минут
  const rl = await rateLimit(env, "login:" + clientIp(request), 10, 15 * 60 * 1000);
  if (!rl.ok) return json({ error: "rate-limited", retryAfter: rl.retryAfter }, 429, { "Retry-After": String(rl.retryAfter) });

  let body;
  try { body = await request.json(); } catch { return json({ error: "invalid JSON" }, 400); }

  const email = String(body?.email || "").trim().toLowerCase();
  const password = String(body?.password || "");
  if (!email || !password) return json({ error: "missing-credentials" }, 400);

  const user = await env.DB.prepare("SELECT id, email, password_hash, email_verified FROM users WHERE email = ?")
    .bind(email).first();

  // одинаковый ответ для «нет пользователя» и «неверный пароль» — не раскрываем, есть ли email
  const ok = user && (await verifyPassword(password, user.password_hash));
  if (!ok) return json({ error: "invalid-credentials" }, 401);

  // пароль верен, но email не подтверждён → вход закрыт (письмо можно выслать повторно)
  if (!user.email_verified) return json({ error: "email-not-verified" }, 403);

  const token = await signToken({ sub: user.id, email: user.email }, env.JWT_SECRET);
  return json({ ok: true, token, user: { id: user.id, email: user.email } }, 200, {
    "Set-Cookie": sessionCookie(token, request, TTL),
  });
}
