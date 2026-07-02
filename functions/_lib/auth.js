/**
 * Общая логика аутентификации для Cloudflare Pages Functions.
 *
 * - Пароли: PBKDF2-HMAC-SHA256 (bcrypt на Workers недоступен — нативный модуль).
 *   Формат хранения: "pbkdf2$<iterations>$<saltB64>$<hashB64>".
 * - Сессия: самописный JWT (HS256) на Web Crypto, подпись секретом env.JWT_SECRET.
 * - Токен принимается из заголовка Authorization: Bearer <jwt> (для Capacitor,
 *   cross-origin) ИЛИ из HttpOnly-cookie "auth_token" (для веба).
 */

const COOKIE = "auth_token";
const PBKDF2_ITERATIONS = 100000;   // компромисс под лимит CPU у Workers
const TOKEN_TTL = 60 * 60 * 24 * 30; // 30 дней

const enc = new TextEncoder();
const dec = new TextDecoder();

// ---------- base64 / base64url ----------
function bufToB64(buf) {
  return btoa(String.fromCharCode(...new Uint8Array(buf)));
}
function b64ToBuf(b64) {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
function b64url(str) {
  return btoa(str).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function b64urlToStr(s) {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  return atob(s);
}

// ---------- пароли ----------
export async function hashPassword(password) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const key = await crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations: PBKDF2_ITERATIONS, hash: "SHA-256" },
    key, 256
  );
  return `pbkdf2$${PBKDF2_ITERATIONS}$${bufToB64(salt)}$${bufToB64(bits)}`;
}

export async function verifyPassword(password, stored) {
  try {
    const [scheme, iterStr, saltB64, hashB64] = String(stored).split("$");
    if (scheme !== "pbkdf2") return false;
    const salt = b64ToBuf(saltB64);
    const key = await crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2", false, ["deriveBits"]);
    const bits = await crypto.subtle.deriveBits(
      { name: "PBKDF2", salt, iterations: parseInt(iterStr, 10), hash: "SHA-256" },
      key, 256
    );
    return timingSafeEqual(bufToB64(bits), hashB64);
  } catch {
    return false;
  }
}

function timingSafeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

// ---------- JWT (HS256) ----------
async function hmacKey(secret) {
  return crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]);
}

export async function signToken(payload, secret, ttl = TOKEN_TTL) {
  const now = Math.floor(Date.now() / 1000);
  const body = { ...payload, iat: now, exp: now + ttl };
  const head = b64url(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const data = `${head}.${b64url(JSON.stringify(body))}`;
  const sig = await crypto.subtle.sign("HMAC", await hmacKey(secret), enc.encode(data));
  const sigB64 = bufToB64(sig).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  return `${data}.${sigB64}`;
}

export async function verifyToken(token, secret) {
  try {
    const [head, body, sig] = String(token).split(".");
    if (!head || !body || !sig) return null;
    const data = `${head}.${body}`;
    const expected = await crypto.subtle.sign("HMAC", await hmacKey(secret), enc.encode(data));
    const expB64 = bufToB64(expected).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    if (!timingSafeEqual(expB64, sig)) return null;
    const payload = JSON.parse(b64urlToStr(body));
    if (payload.exp && Math.floor(Date.now() / 1000) > payload.exp) return null;
    return payload;
  } catch {
    return null;
  }
}

// ---------- запрос → пользователь ----------
export function getToken(request) {
  const auth = request.headers.get("Authorization") || "";
  if (auth.startsWith("Bearer ")) return auth.slice(7).trim();
  const raw = request.headers.get("Cookie") || "";
  for (const part of raw.split(/;\s*/)) {
    const i = part.indexOf("=");
    if (i > -1 && part.slice(0, i) === COOKIE) return part.slice(i + 1);
  }
  return null;
}

// Возвращает payload JWT или null. secret = env.JWT_SECRET.
export async function getAuth(request, env) {
  if (!env.JWT_SECRET) return null;
  const token = getToken(request);
  if (!token) return null;
  return verifyToken(token, env.JWT_SECRET);
}

// ---------- cookie ----------
export function sessionCookie(token, request, ttl = TOKEN_TTL) {
  const secure = new URL(request.url).protocol === "https:";
  return `${COOKIE}=${token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${ttl}` + (secure ? "; Secure" : "");
}
export function clearCookie(request) {
  const secure = new URL(request.url).protocol === "https:";
  return `${COOKIE}=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0` + (secure ? "; Secure" : "");
}

// ---------- rate limiting (фиксированное окно, счётчик в D1) ----------
// Возвращает { ok } либо { ok:false, retryAfter } (секунды до сброса окна).
export async function rateLimit(env, key, limit, windowMs) {
  if (!env.DB) return { ok: true }; // без БД не ограничиваем (локальная подстраховка)
  const now = Date.now();
  const row = await env.DB.prepare("SELECT count, reset_at FROM auth_attempts WHERE key = ?").bind(key).first();

  if (!row || now > row.reset_at) {
    const resetAt = now + windowMs;
    await env.DB.prepare(
      "INSERT INTO auth_attempts (key, count, reset_at) VALUES (?, 1, ?) " +
      "ON CONFLICT(key) DO UPDATE SET count = 1, reset_at = excluded.reset_at"
    ).bind(key, resetAt).run();
    return { ok: true };
  }
  if (row.count >= limit) {
    return { ok: false, retryAfter: Math.ceil((row.reset_at - now) / 1000) };
  }
  await env.DB.prepare("UPDATE auth_attempts SET count = count + 1 WHERE key = ?").bind(key).run();
  return { ok: true };
}

// IP клиента (за прокси Cloudflare)
export function clientIp(request) {
  return request.headers.get("CF-Connecting-IP") || "unknown";
}

// ---------- ответы ----------
export function json(body, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...extraHeaders },
  });
}

export const TTL = TOKEN_TTL;
