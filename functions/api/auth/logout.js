/**
 * POST /api/auth/logout — очищает сессионную cookie.
 * Примечание: JWT stateless, поэтому уже выданный токен остаётся валиден до
 * истечения exp. Для мгновенного отзыва понадобится denylist (позже, при нужде).
 */
import { clearCookie, json } from "../../_lib/auth.js";

export async function onRequestPost({ request }) {
  return json({ ok: true }, 200, { "Set-Cookie": clearCookie(request) });
}
