/**
 * Письма (Resend) + одноразовые email-токены (таблица email_tokens в D1).
 *
 * env.RESEND_API_KEY — API-ключ Resend (secret).
 * env.MAIL_FROM      — отправитель, напр. "Artikeltrainer <noreply@mydomain.de>".
 *                      Без своего домена остаётся onboarding@resend.dev — Resend
 *                      тогда доставляет письма ТОЛЬКО владельцу аккаунта Resend.
 *
 * В базе хранится не сам токен, а его SHA-256 — утечка БД не даёт ссылок.
 */

export function mailConfigured(env) {
  return Boolean(env.RESEND_API_KEY);
}

export async function sendEmail(env, { to, subject, html }) {
  const from = env.MAIL_FROM || "Artikeltrainer <onboarding@resend.dev>";
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { "content-type": "application/json", Authorization: "Bearer " + env.RESEND_API_KEY },
    body: JSON.stringify({ from, to: [to], subject, html }),
  });
  if (!r.ok) throw new Error("Resend " + r.status + ": " + (await r.text()).slice(0, 300));
}

// ---------- одноразовые токены ----------
async function sha256hex(s) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// Создаёт токен (256 бит, base64url), кладёт его хэш в БД, попутно чистит просроченные.
export async function createEmailToken(env, userId, purpose, ttlMs) {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  const token = btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  const now = Date.now();
  await env.DB.batch([
    env.DB.prepare("DELETE FROM email_tokens WHERE expires_at < ?").bind(now),
    env.DB.prepare("INSERT INTO email_tokens (token_hash, user_id, purpose, expires_at) VALUES (?, ?, ?, ?)")
      .bind(await sha256hex(token), userId, purpose, now + ttlMs),
  ]);
  return token;
}

// Проверяет токен и сразу гасит (одноразовый). Возвращает user_id или null.
export async function consumeEmailToken(env, token, purpose) {
  if (!token || typeof token !== "string" || token.length > 200) return null;
  const hash = await sha256hex(token);
  const row = await env.DB.prepare(
    "SELECT user_id, expires_at FROM email_tokens WHERE token_hash = ? AND purpose = ?"
  ).bind(hash, purpose).first();
  if (!row) return null;
  await env.DB.prepare("DELETE FROM email_tokens WHERE token_hash = ?").bind(hash).run();
  if (Date.now() > row.expires_at) return null;
  return row.user_id;
}

// ---------- шаблоны писем (трёхъязычные, без внешних ресурсов) ----------
function layout(title, lines, link, button) {
  const rows = lines.map((l) => `<p style="margin:6px 0;color:#2b2b2b;font-size:15px">${l}</p>`).join("");
  return `<div style="font-family:system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px">
  <h2 style="margin:0 0 14px;color:#2b2b2b">${title}</h2>
  ${rows}
  <p style="margin:22px 0"><a href="${link}" style="background:#2b2b2b;color:#fff;text-decoration:none;padding:12px 22px;border-radius:10px;display:inline-block">${button}</a></p>
  <p style="margin:6px 0;color:#9a9a9a;font-size:13px">${link}</p>
</div>`;
}

export function resetEmail(link) {
  return {
    subject: "Passwort zurücksetzen / Reset password — Artikeltrainer",
    html: layout(
      "Artikeltrainer",
      [
        "Setze dein Passwort über den Button unten zurück. Der Link ist 30 Minuten gültig. Wenn du das nicht angefordert hast, ignoriere diese E-Mail.",
        "Reset your password using the button below. The link is valid for 30 minutes. If you didn't request this, ignore this email.",
        "Сбрось пароль по кнопке ниже. Ссылка действует 30 минут. Если ты этого не запрашивал — просто проигнорируй письмо.",
      ],
      link,
      "Passwort zurücksetzen / Reset password"
    ),
  };
}

export function verifyEmail(link) {
  return {
    subject: "E-Mail bestätigen / Confirm your email — Artikeltrainer",
    html: layout(
      "Artikeltrainer",
      [
        "Bestätige deine E-Mail-Adresse über den Button unten, um dein Konto zu aktivieren. Der Link ist 48 Stunden gültig.",
        "Confirm your email address using the button below to activate your account. The link is valid for 48 hours.",
        "Подтверди свой email по кнопке ниже, чтобы активировать аккаунт. Ссылка действует 48 часов.",
      ],
      link,
      "E-Mail bestätigen / Confirm email"
    ),
  };
}
