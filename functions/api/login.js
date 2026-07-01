/**
 * Cloudflare Pages Function: /api/login
 * POST { password } → при верном пароле ставит сессионную HttpOnly-куку.
 *
 * Пароль сравнивается с секретом env.SITE_PASSWORD (задать:
 *   npx wrangler pages secret put SITE_PASSWORD).
 * Если секрет не задан — защита выключена, вход не требуется.
 */

const COOKIE = "artikel_auth";
const SESSION_MSG = "artikel-session-v1";
const MAX_AGE = 60 * 60 * 24 * 365; // 1 год

async function sessionToken(password) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(password),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(SESSION_MSG));
  return btoa(String.fromCharCode(...new Uint8Array(sig)));
}

function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function json(body, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      ...extraHeaders,
    },
  });
}

export async function onRequestPost({ request, env }) {
  const password = env.SITE_PASSWORD;
  if (!password) return json({ ok: true, disabled: true }); // защита выключена

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "invalid JSON" }, 400);
  }
  if (!body || typeof body.password !== "string" || !safeEqual(body.password, password)) {
    return json({ error: "wrong-password" }, 401);
  }

  const token = await sessionToken(password);
  const secure = new URL(request.url).protocol === "https:";
  const cookie =
    `${COOKIE}=${token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${MAX_AGE}` +
    (secure ? "; Secure" : "");
  return json({ ok: true }, 200, { "Set-Cookie": cookie });
}
