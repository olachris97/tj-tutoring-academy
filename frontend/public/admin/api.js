const API_BASE = (window.TJ_API_BASE || 'https://tj-tutoring-api.onrender.com') + '/api/v1';

const TokenStore = {
  get access() { return localStorage.getItem('tj_access_token'); },
  set access(v) { v ? localStorage.setItem('tj_access_token', v) : localStorage.removeItem('tj_access_token'); },
  get refresh() { return localStorage.getItem('tj_refresh_token'); },
  set refresh(v) { v ? localStorage.setItem('tj_refresh_token', v) : localStorage.removeItem('tj_refresh_token'); },
  get admin() {
    try { return JSON.parse(localStorage.getItem('tj_admin') || 'null'); } catch (_) { return null; }
  },
  set admin(v) { v ? localStorage.setItem('tj_admin', JSON.stringify(v)) : localStorage.removeItem('tj_admin'); },
  clear() {
    this.access = null; this.refresh = null; this.admin = null;
  },
};

function goToLogin() {
  TokenStore.clear();
  if (!location.pathname.endsWith('login.html')) {
    location.href = 'login.html';
  }
}

async function refreshSession() {
  const refresh_token = TokenStore.refresh;
  if (!refresh_token) return false;
  try {
    const res = await fetch(API_BASE + '/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    TokenStore.access = data.access_token;
    TokenStore.refresh = data.refresh_token;
    TokenStore.admin = data.admin;
    return true;
  } catch (_) {
    return false;
  }
}

async function apiRequest(method, path, body) {
  const doFetch = () => fetch(API_BASE + path, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(TokenStore.access ? { Authorization: 'Bearer ' + TokenStore.access } : {}),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  let res = await doFetch();

  if (res.status === 401) {
    const refreshed = await refreshSession();
    if (!refreshed) { goToLogin(); throw new Error('Session expired.'); }
    res = await doFetch();
  }

  let data = null;
  try { data = await res.json(); } catch (_) { /* no body */ }

  if (!res.ok) {
    const message = (data && data.error && data.error.message) || 'Something went wrong.';
    const err = new Error(message);
    err.status = res.status;
    err.details = data && data.error && data.error.details;
    throw err;
  }
  return data;
}

const api = {
  get: (path) => apiRequest('GET', path),
  post: (path, body) => apiRequest('POST', path, body),
  patch: (path, body) => apiRequest('PATCH', path, body),
  delete: (path) => apiRequest('DELETE', path),
};

function requireAuth() {
  if (!TokenStore.access || !TokenStore.refresh) {
    goToLogin();
    return false;
  }
  return true;
}
