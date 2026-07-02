/**
 * POST /api/auth/delete — полное удаление текущего аккаунта и его данных.
 * Требует валидный JWT. Удаляет прогресс и запись пользователя, чистит cookie.
 * (Требование Google Play: удаление аккаунта в приложении + по веб-ссылке.)
 */
import { getAuth, clearCookie, json } from "../../_lib/auth.js";

export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ error: "D1 binding DB is missing" }, 500);
  const auth = await getAuth(request, env);
  if (!auth) return json({ error: "unauthorized" }, 401);

  await env.DB.batch([
    env.DB.prepare("DELETE FROM progress WHERE user_id = ?").bind(auth.sub),
    env.DB.prepare("DELETE FROM users WHERE id = ?").bind(auth.sub),
  ]);

  return json({ ok: true }, 200, { "Set-Cookie": clearCookie(request) });
}
