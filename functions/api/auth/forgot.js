/**
 * POST /api/auth/forgot  { email }
 * Шлёт письмо со ссылкой на сброс пароля (ссылка действует 30 минут).
 * Ответ всегда { ok:true } — существование адреса не раскрываем.
 */
import { json, rateLimit, clientIp } from "../../_lib/auth.js";
import { mailConfigured, sendEmail, createEmailToken, resetEmail } from "../../_lib/mail.js";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const TOKEN_TTL = 30 * 60 * 1000; // 30 минут

export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ error: "D1 binding DB is missing" }, 500);
  if (!mailConfigured(env)) return json({ error: "mail-not-configured" }, 500);

  // не более 5 запросов с одного IP в час
  const rl = await rateLimit(env, "forgot:" + clientIp(request), 5, 60 * 60 * 1000);
  if (!rl.ok) return json({ error: "rate-limited", retryAfter: rl.retryAfter }, 429, { "Retry-After": String(rl.retryAfter) });

  let body;
  try { body = await request.json(); } catch { return json({ error: "invalid JSON" }, 400); }
  const email = String(body?.email || "").trim().toLowerCase();
  if (!EMAIL_RE.test(email)) return json({ error: "invalid-email" }, 400);

  // и не более 3 писем на один адрес в час (защита от заваливания чужой почты)
  const rlMail = await rateLimit(env, "forgot-mail:" + email, 3, 60 * 60 * 1000);
  if (!rlMail.ok) return json({ error: "rate-limited", retryAfter: rlMail.retryAfter }, 429, { "Retry-After": String(rlMail.retryAfter) });

  const user = await env.DB.prepare("SELECT id FROM users WHERE email = ?").bind(email).first();
  if (user) {
    const token = await createEmailToken(env, user.id, "reset", TOKEN_TTL);
    const link = new URL(request.url).origin + "/reset-password.html?token=" + token;
    try {
      await sendEmail(env, { to: email, ...resetEmail(link) });
    } catch (e) {
      console.error("forgot: send failed:", e.message); // виден в `wrangler pages deployment tail`
    }
  }
  return json({ ok: true });
}
