/**
 * Cloudflare Pages Function: /api/logout
 * POST → удаляет сессионную куку (выход).
 */

const COOKIE = "artikel_auth";

export async function onRequestPost({ request }) {
  const secure = new URL(request.url).protocol === "https:";
  const cookie =
    `${COOKIE}=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0` +
    (secure ? "; Secure" : "");
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "Set-Cookie": cookie,
    },
  });
}
