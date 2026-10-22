if (!requireAuth()) {
  // requireAuth already redirected to login.html
  throw new Error('Not authenticated');
}

const state = {
  view: 'overview',
  messages: { status: '', page: 1 },
  applications: { status: '', page: 1 },
  detail: null, // { kind: 'message'|'application', id }
};

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) +
    ' · ' + d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
}

function timeAgo(iso) {
  if (!iso) return '—';
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.round(diffMs / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return mins + 'm ago';
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return hrs + 'h ago';
  return Math.round(hrs / 24) + 'd ago';
}

function badge(status) {
  return `<span class="badge badge-${status}">${status}</span>`;
}

// ---------------------------------------------------------------------------
// Nav / view switching
// ---------------------------------------------------------------------------
document.querySelectorAll('.nav-item[data-view]').forEach((btn) => {
  btn.addEventListener('click', () => switchView(btn.dataset.view));
});

function switchView(view) {
  state.view = view;
  document.querySelectorAll('.nav-item[data-view]').forEach((b) => b.classList.toggle('active', b.dataset.view === view));
  document.querySelectorAll('.view').forEach((v) => v.classList.toggle('active', v.id === 'view-' + view));

  if (view === 'overview') loadOverview();
  if (view === 'messages') loadMessages();
  if (view === 'applications') loadApplications();
}

// ---------------------------------------------------------------------------
// Overview
// ---------------------------------------------------------------------------
async function loadOverview() {
  try {
    const data = await api.get('/admin/dashboard/summary');
    document.getElementById('statMsgTotal').textContent = data.messages.total;
    document.getElementById('statMsgNew').textContent = data.messages.last_7_days + ' in the last 7 days';
    document.getElementById('statMsgNewCount').textContent = data.messages.new;
    document.getElementById('statAppTotal').textContent = data.applications.total;
    document.getElementById('statAppSubmitted').textContent = data.applications.submitted + ' awaiting review';
    document.getElementById('statAppShortlisted').textContent = data.applications.shortlisted;

    document.getElementById('navMsgCount').textContent = data.messages.new;
    document.getElementById('navAppCount').textContent = data.applications.submitted;

    const list = document.getElementById('activityList');
    if (!data.recent_activity.length) {
      list.innerHTML = '<div class="empty-state">No activity yet.</div>';
    } else {
      list.innerHTML = data.recent_activity.map((a) => `
        <div class="activity-row">
          <span class="action">${escapeHtml(a.action)}</span>
          <span class="when">${timeAgo(a.created_at)}</span>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error(err);
  }
}

// ---------------------------------------------------------------------------
// Messages
// ---------------------------------------------------------------------------
document.querySelectorAll('#msgStatusFilters .pill').forEach((pill) => {
  pill.addEventListener('click', () => {
    document.querySelectorAll('#msgStatusFilters .pill').forEach((p) => p.classList.remove('active'));
    pill.classList.add('active');
    state.messages.status = pill.dataset.status;
    state.messages.page = 1;
    loadMessages();
  });
});

async function loadMessages() {
  const wrap = document.getElementById('messagesTableWrap');
  wrap.innerHTML = '<div class="empty-state">Loading…</div>';
  const { status, page } = state.messages;
  const qs = new URLSearchParams({ page, per_page: 10, ...(status ? { status } : {}) });

  try {
    const data = await api.get('/admin/messages?' + qs.toString());
    if (!data.items.length) {
      wrap.innerHTML = `<div class="empty-state"><div class="icon">✉️</div>No messages${status ? ' with status "' + status + '"' : ''} yet.</div>`;
      document.getElementById('messagesPagination').innerHTML = '';
      return;
    }
    wrap.innerHTML = `
      <table class="data-table">
        <thead><tr><th>From</th><th>Topic</th><th>Message</th><th>Status</th><th>Received</th></tr></thead>
        <tbody>
          ${data.items.map((m) => `
            <tr class="clickable" data-id="${m.id}">
              <td>
                <div class="cell-name">${escapeHtml(m.name)}</div>
                <div class="cell-sub">${escapeHtml(m.email)}</div>
              </td>
              <td>${escapeHtml(m.topic || 'general')}</td>
              <td class="cell-msg">${escapeHtml(m.message)}</td>
              <td>${badge(m.status)}</td>
              <td class="cell-sub">${timeAgo(m.created_at)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
    wrap.querySelectorAll('tr[data-id]').forEach((row) => {
      row.addEventListener('click', () => openMessageDetail(row.dataset.id));
    });
    renderPagination('messagesPagination', data, (p) => { state.messages.page = p; loadMessages(); });
  } catch (err) {
    wrap.innerHTML = `<div class="empty-state">Couldn't load messages: ${escapeHtml(err.message)}</div>`;
  }
}

async function openMessageDetail(id) {
  state.detail = { kind: 'message', id };
  const panel = document.getElementById('detailPanel');
  panel.innerHTML = '<div class="empty-state">Loading…</div>';
  showOverlay();
  try {
    const m = await api.get('/admin/messages/' + id);
    panel.innerHTML = `
      <div class="detail-head">
        <h3>${escapeHtml(m.name)}</h3>
        <button class="detail-close" id="closeDetail">✕</button>
      </div>
      <div class="detail-meta">${escapeHtml(m.email)}${m.phone ? ' · ' + escapeHtml(m.phone) : ''} · ${formatDate(m.created_at)}</div>

      <div class="detail-section">
        <div class="k">Topic</div>
        <div class="v">${escapeHtml(m.topic || 'general')}</div>
      </div>
      <div class="detail-section">
        <div class="k">Message</div>
        <div class="v">${escapeHtml(m.message)}</div>
      </div>

      <div class="detail-section">
        <div class="k">Status</div>
        <select class="status-select" id="detailStatus">
          ${['new', 'read', 'responded', 'archived'].map((s) => `<option value="${s}" ${s === m.status ? 'selected' : ''}>${s}</option>`).join('')}
        </select>
      </div>
      <div class="detail-section">
        <div class="k">Admin notes (private)</div>
        <textarea id="detailNotes" placeholder="Notes for the team — not visible to the sender">${escapeHtml(m.admin_notes || '')}</textarea>
      </div>

      <div class="detail-actions">
        <button class="btn btn-primary" id="saveDetail">Save Changes</button>
        <a class="btn btn-secondary" href="mailto:${escapeHtml(m.email)}">Reply by Email</a>
      </div>
      <div id="detailAlert" class="form-alert" style="margin-top: 14px;"></div>
      <button class="detail-danger" id="deleteDetail">Delete this message</button>
    `;
    wireDetailActions('message', id);
  } catch (err) {
    panel.innerHTML = `<div class="empty-state">Couldn't load message: ${escapeHtml(err.message)}</div>`;
  }
  loadMessages(); // refresh list/badges since viewing marks "new" as "read"
  loadOverview();
}

// ---------------------------------------------------------------------------
// Applications
// ---------------------------------------------------------------------------
document.querySelectorAll('#appStatusFilters .pill').forEach((pill) => {
  pill.addEventListener('click', () => {
    document.querySelectorAll('#appStatusFilters .pill').forEach((p) => p.classList.remove('active'));
    pill.classList.add('active');
    state.applications.status = pill.dataset.status;
    state.applications.page = 1;
    loadApplications();
  });
});

async function loadApplications() {
  const wrap = document.getElementById('applicationsTableWrap');
  wrap.innerHTML = '<div class="empty-state">Loading…</div>';
  const { status, page } = state.applications;
  const qs = new URLSearchParams({ page, per_page: 10, ...(status ? { status } : {}) });

  try {
    const data = await api.get('/admin/applications?' + qs.toString());
    if (!data.items.length) {
      wrap.innerHTML = `<div class="empty-state"><div class="icon">📝</div>No applications${status ? ' with status "' + status + '"' : ''} yet.</div>`;
      document.getElementById('applicationsPagination').innerHTML = '';
      return;
    }
    wrap.innerHTML = `
      <table class="data-table">
        <thead><tr><th>Applicant</th><th>Subjects</th><th>Experience</th><th>Status</th><th>Submitted</th></tr></thead>
        <tbody>
          ${data.items.map((a) => `
            <tr class="clickable" data-id="${a.id}">
              <td>
                <div class="cell-name">${escapeHtml(a.full_name)}</div>
                <div class="cell-sub">${escapeHtml(a.location || a.email)}</div>
              </td>
              <td class="cell-msg">${escapeHtml(a.subjects)}</td>
              <td>${a.years_experience} yr${a.years_experience === 1 ? '' : 's'}</td>
              <td>${badge(a.status)}</td>
              <td class="cell-sub">${timeAgo(a.created_at)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
    wrap.querySelectorAll('tr[data-id]').forEach((row) => {
      row.addEventListener('click', () => openApplicationDetail(row.dataset.id));
    });
    renderPagination('applicationsPagination', data, (p) => { state.applications.page = p; loadApplications(); });
  } catch (err) {
    wrap.innerHTML = `<div class="empty-state">Couldn't load applications: ${escapeHtml(err.message)}</div>`;
  }
}

async function openApplicationDetail(id) {
  state.detail = { kind: 'application', id };
  const panel = document.getElementById('detailPanel');
  panel.innerHTML = '<div class="empty-state">Loading…</div>';
  showOverlay();
  try {
    const a = await api.get('/admin/applications/' + id);
    panel.innerHTML = `
      <div class="detail-head">
        <h3>${escapeHtml(a.full_name)}</h3>
        <button class="detail-close" id="closeDetail">✕</button>
      </div>
      <div class="detail-meta">${escapeHtml(a.email)} · ${escapeHtml(a.phone)} · ${formatDate(a.created_at)}</div>

      <div class="detail-grid">
        <div class="detail-section">
          <div class="k">Subjects</div>
          <div class="v">${escapeHtml(a.subjects)}</div>
        </div>
        <div class="detail-section">
          <div class="k">Levels</div>
          <div class="v">${escapeHtml(a.levels || '—')}</div>
        </div>
        <div class="detail-section">
          <div class="k">Experience</div>
          <div class="v">${a.years_experience} year${a.years_experience === 1 ? '' : 's'}</div>
        </div>
        <div class="detail-section">
          <div class="k">Location</div>
          <div class="v">${escapeHtml(a.location || '—')}</div>
        </div>
      </div>

      <div class="detail-section">
        <div class="k">Qualification</div>
        <div class="v">${escapeHtml(a.qualification)}</div>
      </div>
      <div class="detail-section">
        <div class="k">Availability</div>
        <div class="v">${escapeHtml(a.availability || '—')}</div>
      </div>
      ${a.resume_url ? `
      <div class="detail-section">
        <div class="k">CV / Portfolio</div>
        <a class="v" href="${escapeHtml(a.resume_url)}" target="_blank" rel="noopener">${escapeHtml(a.resume_url)}</a>
      </div>` : ''}
      ${a.cover_note ? `
      <div class="detail-section">
        <div class="k">Cover Note</div>
        <div class="v">${escapeHtml(a.cover_note)}</div>
      </div>` : ''}

      <div class="detail-section">
        <div class="k">Status</div>
        <select class="status-select" id="detailStatus">
          ${['submitted', 'reviewing', 'shortlisted', 'rejected', 'hired'].map((s) => `<option value="${s}" ${s === a.status ? 'selected' : ''}>${s}</option>`).join('')}
        </select>
      </div>
      <div class="detail-section">
        <div class="k">Admin notes (private)</div>
        <textarea id="detailNotes" placeholder="Interview notes, demo lesson feedback...">${escapeHtml(a.admin_notes || '')}</textarea>
      </div>

      <div class="detail-actions">
        <button class="btn btn-primary" id="saveDetail">Save Changes</button>
        <a class="btn btn-secondary" href="mailto:${escapeHtml(a.email)}">Email Applicant</a>
      </div>
      <div id="detailAlert" class="form-alert" style="margin-top: 14px;"></div>
      <button class="detail-danger" id="deleteDetail">Delete this application</button>
    `;
    wireDetailActions('application', id);
  } catch (err) {
    panel.innerHTML = `<div class="empty-state">Couldn't load application: ${escapeHtml(err.message)}</div>`;
  }
}

// ---------------------------------------------------------------------------
// Shared detail panel plumbing
// ---------------------------------------------------------------------------
function wireDetailActions(kind, id) {
  document.getElementById('closeDetail').addEventListener('click', hideOverlay);

  document.getElementById('saveDetail').addEventListener('click', async () => {
    const status = document.getElementById('detailStatus').value;
    const admin_notes = document.getElementById('detailNotes').value;
    const alertBox = document.getElementById('detailAlert');
    try {
      const path = kind === 'message' ? '/admin/messages/' + id : '/admin/applications/' + id;
      await api.patch(path, { status, admin_notes });
      alertBox.textContent = 'Saved.';
      alertBox.className = 'form-alert show success';
      if (kind === 'message') loadMessages(); else loadApplications();
      loadOverview();
    } catch (err) {
      alertBox.textContent = err.message;
      alertBox.className = 'form-alert show error';
    }
  });

  document.getElementById('deleteDetail').addEventListener('click', async () => {
    if (!confirm('Delete this ' + kind + ' permanently? This cannot be undone.')) return;
    try {
      const path = kind === 'message' ? '/admin/messages/' + id : '/admin/applications/' + id;
      await api.delete(path);
      hideOverlay();
      if (kind === 'message') loadMessages(); else loadApplications();
      loadOverview();
    } catch (err) {
      alert('Could not delete: ' + err.message);
    }
  });
}

function showOverlay() { document.getElementById('overlay').classList.add('show'); }
function hideOverlay() { document.getElementById('overlay').classList.remove('show'); state.detail = null; }
document.getElementById('overlay').addEventListener('click', (e) => {
  if (e.target.id === 'overlay') hideOverlay();
});

// ---------------------------------------------------------------------------
// Pagination
// ---------------------------------------------------------------------------
function renderPagination(elId, data, onPage) {
  const el = document.getElementById(elId);
  if (data.pages <= 1) { el.innerHTML = ''; return; }
  el.innerHTML = `
    <span>Page ${data.page} of ${data.pages} · ${data.total} total</span>
    <div class="btns">
      <button class="btn btn-secondary btn-sm" id="prevPage" ${data.page <= 1 ? 'disabled' : ''}>← Prev</button>
      <button class="btn btn-secondary btn-sm" id="nextPage" ${data.page >= data.pages ? 'disabled' : ''}>Next →</button>
    </div>
  `;
  document.getElementById('prevPage').addEventListener('click', () => onPage(data.page - 1));
  document.getElementById('nextPage').addEventListener('click', () => onPage(data.page + 1));
}

// ---------------------------------------------------------------------------
// Account / change password
// ---------------------------------------------------------------------------
document.getElementById('changePasswordForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const alertBox = document.getElementById('pwAlert');
  const btn = document.getElementById('pwSubmitBtn');
  const current_password = document.getElementById('currentPassword').value;
  const new_password = document.getElementById('newPassword').value;

  btn.disabled = true;
  btn.textContent = 'Updating...';
  try {
    await api.post('/auth/change-password', { current_password, new_password });
    alertBox.textContent = 'Password updated.';
    alertBox.className = 'form-alert show success';
    e.target.reset();
  } catch (err) {
    alertBox.textContent = err.message;
    alertBox.className = 'form-alert show error';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Update Password';
  }
});

// ---------------------------------------------------------------------------
// Logout
// ---------------------------------------------------------------------------
document.getElementById('logoutBtn').addEventListener('click', async () => {
  try { await api.post('/auth/logout', { refresh_token: TokenStore.refresh }); } catch (_) { /* ignore */ }
  TokenStore.clear();
  location.href = 'login.html';
});

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
const admin = TokenStore.admin;
if (admin) document.getElementById('sidebarAdminName').textContent = admin.full_name;
loadOverview();
