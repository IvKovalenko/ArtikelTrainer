/**
 * Cloudflare Pages Function: /api/progress  (многопользовательская версия)
 * GET  → прогресс текущего пользователя (JSON-блоб из D1)
 * POST → слить присланный прогресс с серверным и сохранить результат.
 *        С ?replace=1 — заменить целиком (только «Сбросить статистику»).
 *
 * Пользователь определяется по JWT (cookie или Authorization: Bearer).
 * Хранилище — таблица progress в D1 (binding DB). KV больше не используется.
 */
import { getAuth, json } from "../_lib/auth.js";

// Поэлементное слияние — зеркало клиентского mergeMax (public/app.js).
// Счётчики монотонно растут, поэтому максимум безопасен. Раньше POST слепо
// перезаписывал блоб, и клиент с устаревшей копией (вкладка, открытая до
// сессии на другом устройстве) стирал свежий прогресс — «кто последний
// записал, тот и прав». Теперь отставший клиент ничего разрушить не может.
const SETTING_FIELDS = ["masterPct", "wrongPause", "delayRight", "delayWrong"];
function mergeMax(a, b) {
  const out = {};
  for (const key of new Set([...Object.keys(a), ...Object.keys(b)])) {
    const x = (a[key] && typeof a[key] === "object") ? a[key] : {};
    const y = (b[key] && typeof b[key] === "object") ? b[key] : {};
    if (key === "__meta") {   // служебная запись: достигнутый уровень + настройки
      const m = { unlockedIdx: Math.max(x.unlockedIdx || 1, y.unlockedIdx || 1) };
      // у каждой настройки своя метка времени — побеждает более поздний выбор;
      // 0 — валидное значение, поэтому проверяем «поле есть», а не истинность
      for (const f of SETTING_FIELDS) {
        const at = f + "At";
        const newer = (x[at] || 0) >= (y[at] || 0) ? x : y;
        const other = newer === x ? y : x;
        const src = newer[f] !== undefined ? newer : (other[f] !== undefined ? other : null);
        if (src) { m[f] = src[f]; m[at] = src[at] || 0; }
      }
      out[key] = m;
      continue;
    }
    out[key] = {
      correct: Math.max(x.correct || 0, y.correct || 0),
      wrong: Math.max(x.wrong || 0, y.wrong || 0),
      seen: Math.max(x.seen || 0, y.seen || 0),
    };
    if ((x.m || 0) || (y.m || 0)) out[key].m = 1;   // «выучено» не отбирается
  }
  return out;
}

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

  // replace=1 — явная замена без слияния; шлёт только «Сбросить статистику»
  const replace = new URL(request.url).searchParams.get("replace") === "1";
  let data = body;
  if (!replace) {
    const row = await env.DB.prepare("SELECT data FROM progress WHERE user_id = ?")
      .bind(auth.sub).first();
    if (row) {
      let existing = null;
      try { existing = JSON.parse(row.data); } catch {}
      if (existing && typeof existing === "object" && !Array.isArray(existing)) {
        data = mergeMax(existing, body);
      }
    }
  }

  await env.DB.prepare(
    "INSERT INTO progress (user_id, data, updated_at) VALUES (?, ?, ?) " +
    "ON CONFLICT(user_id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at"
  ).bind(auth.sub, JSON.stringify(data), Date.now()).run();

  return json({ ok: true, words: Object.keys(data).length });
}
