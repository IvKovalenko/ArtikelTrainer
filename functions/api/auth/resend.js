/**
 * POST /api/auth/resend  { email }
 * Повторно шлёт письмо подтверждения (если аккаунт существует и не подтверждён).
 * Ответ всегда { ok:true } — существование адреса не раскрываем.
 */
import { json, rateLimit, clientIp } from "../../_lib/auth.js";
import { mailConfigured, sendEmail, createEmailToken, verifyEmail } from "../../_lib/mail.js";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const TOKEN_TTL = 48 * 60 * 60 * 1000; // 48 часов

export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ error: "D1 binding DB is missing" }, 500);
  if (!mailConfigured(env)) return json({ error: "mail-not-configured" }, 500);

  const rl = await rateLimit(env, "resend:" + clientIp(request), 5, 60 * 60 * 1000);
  if (!rl.ok) return json({ error: "rate-limited", retryAfter: rl.retryAfter }, 429, { "Retry-After": String(rl.retryAfter) });

  let body;
  try { body = await request.json(); } catch { return json({ error: "invalid JSON" }, 400); }
  const email = String(body?.email || "").trim().toLowerCase();
  if (!EMAIL_RE.test(email)) return json({ error: "invalid-email" }, 400);

  const rlMail = await rateLimit(env, "resend-mail:" + email, 3, 60 * 60 * 1000);
  if (!rlMail.ok) return json({ error: "rate-limited", retryAfter: rlMail.retryAfter }, 429, { "Retry-After": String(rlMail.retryAfter) });

  const user = await env.DB.prepare("SELECT id, email_verified FROM users WHERE email = ?").bind(email).first();
  if (user && !user.email_verified) {
    const token = await createEmailToken(env, user.id, "verify", TOKEN_TTL);
    const link = new URL(request.url).origin + "/api/auth/verify?token=" + token;
    try {
      await sendEmail(env, { to: email, ...verifyEmail(link) });
    } catch (e) {
      console.error("resend: send failed:", e.message);
    }
  }
  return json({ ok: true });
}
