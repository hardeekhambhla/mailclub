// POST /waitlist — stores emails in the WAITLIST KV namespace.
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

export async function onRequestPost({ request, env }) {
  let email = "";
  try {
    email = String((await request.json()).email ?? "").trim().toLowerCase();
  } catch {}
  if (email.length > 254 || !EMAIL_RE.test(email)) {
    return json({ ok: false, error: "Enter a valid email." }, 400);
  }
  const key = `email:${email}`;
  if (!(await env.WAITLIST.get(key))) {
    await env.WAITLIST.put(key, new Date().toISOString());
  }
  return json({ ok: true });
}
