/**
 * GET /api/auth/verify?token=...
 * Подтверждение email по ссылке из письма. Редиректит на страницу входа:
 * ?verified=1 — успех, ?verified=0 — токен невалиден/просрочен.
 */
import { consumeEmailToken } from "../../_lib/mail.js";

export async function onRequestGet({ request, env }) {
  const origin = new URL(request.url).origin;
  const back = (ok) => Response.redirect(origin + "/login.html?verified=" + (ok ? "1" : "0"), 302);
  if (!env.DB) return back(false);

  const token = new URL(request.url).searchParams.get("token");
  const userId = await consumeEmailToken(env, token, "verify");
  if (!userId) return back(false);

  await env.DB.prepare("UPDATE users SET email_verified = 1 WHERE id = ?").bind(userId).run();
  return back(true);
}
