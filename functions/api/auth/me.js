/**
 * GET /api/auth/me — данные текущего пользователя по JWT (cookie или Bearer).
 * 401, если токен отсутствует/невалиден.
 */
import { getAuth, json } from "../../_lib/auth.js";

export async function onRequestGet({ request, env }) {
  if (!env.DB) return json({ error: "D1 binding DB is missing" }, 500);
  const auth = await getAuth(request, env);
  if (!auth) return json({ error: "unauthorized" }, 401);

  const user = await env.DB.prepare("SELECT id, email, created_at, email_verified FROM users WHERE id = ?")
    .bind(auth.sub).first();
  if (!user) return json({ error: "unauthorized" }, 401);

  return json({ user });
}
