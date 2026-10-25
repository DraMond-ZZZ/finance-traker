const tok = () => localStorage.getItem('token');
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const rp = (n) => 'Rp ' + Number(n).toLocaleString('id-ID');
function logout() { localStorage.clear(); location.href = '/login'; }
async function api(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (tok()) headers.Authorization = 'Bearer ' + tok();
  const res = await fetch('/api' + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  const json = await res.json().catch(() => ({}));
  if (res.status === 401 && tok()) logout();
  if (!res.ok) throw new Error(json.error || 'Terjadi kesalahan');
  return json;
}
