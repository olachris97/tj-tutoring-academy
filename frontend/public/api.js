const API_BASE = (window.TJ_API_BASE || 'https://tj-tutoring-api.onrender.com') + '/api/v1';

async function apiPost(path, body) {
  const res = await fetch(API_BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  let data = null;
  try { data = await res.json(); } catch (_) { /* no body */ }
  if (!res.ok) {
    const message = (data && data.error && data.error.message) || 'Something went wrong. Please try again.';
    const err = new Error(message);
    err.status = res.status;
    err.details = data && data.error && data.error.details;
    throw err;
  }
  return data;
}

function fieldErrors(details) {
  // marshmallow validation error shape: { field: ["message", ...] }
  if (!details) return '';
  const lines = Object.entries(details).map(([field, msgs]) => `${field}: ${[].concat(msgs).join(' ')}`);
  return lines.join(' ');
}
