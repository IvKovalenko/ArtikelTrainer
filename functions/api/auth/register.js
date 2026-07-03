/**
 * POST /api/auth/register  { email, password }
 * Создаёт пользователя и шлёт письмо подтверждения email — вход возможен только
 * после подтверждения (ответ { ok, verify:true }).
 * Если почта не настроена (нет RESEND_API_KEY, локальная разработка) — аккаунт
 * создаётся сразу подтверждённым и логинится, как раньше.
 */
import { hashPassword, signToken, sessionCookie, json, TTL, rateLimit, clientIp } from "../../_lib/auth.js";
import { mailConfigured, sendEmail, createEmailToken, verifyEmail } from "../../_lib/mail.js";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const VERIFY_TTL = 48 * 60 * 60 * 1000; // 48 часов

export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ error: "D1 binding DB is missing" }, 500);
  if (!env.JWT_SECRET) return json({ error: "JWT_SECRET is not set" }, 500);

  // не более 5 регистраций с одного IP за час
  const rl = await rateLimit(env, "register:" + clientIp(request), 5, 60 * 60 * 1000);
  if (!rl.ok) return json({ error: "rate-limited", retryAfter: rl.retryAfter }, 429, { "Retry-After": String(rl.retryAfter) });

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
  const needVerify = mailConfigured(env);

  await env.DB.batch([
    env.DB.prepare("INSERT INTO users (id, email, password_hash, created_at, email_verified) VALUES (?, ?, ?, ?, ?)")
      .bind(id, email, password_hash, now, needVerify ? 0 : 1),
    env.DB.prepare("INSERT INTO progress (user_id, data, updated_at) VALUES (?, '{}', ?)")
      .bind(id, now),
  ]);

  if (needVerify) {
    const verifyToken = await createEmailToken(env, id, "verify", VERIFY_TTL);
    const link = new URL(request.url).origin + "/api/auth/verify?token=" + verifyToken;
    try {
      await sendEmail(env, { to: email, ...verifyEmail(link) });
    } catch (e) {
      // письмо не ушло → аккаунт был бы навсегда заблокирован; откатываем регистрацию
      console.error("register: send failed:", e.message);
      await env.DB.prepare("DELETE FROM users WHERE id = ?").bind(id).run(); // каскадом чистит progress и токены
      return json({ error: "mail-failed" }, 502);
    }
    return json({ ok: true, verify: true, user: { id, email } });
  }

  const token = await signToken({ sub: id, email }, env.JWT_SECRET);
  return json({ ok: true, token, user: { id, email } }, 200, {
    "Set-Cookie": sessionCookie(token, request, TTL),
  });
}
