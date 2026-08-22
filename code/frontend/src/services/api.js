const request = (path, options = {}) => fetch(`/api${path}`, options)

async function readResponse(response) {
  const raw = await response.text()
  let data = raw
  try { data = raw ? JSON.parse(raw) : null } catch { /* plain text response */ }
  if (!response.ok) throw new Error(typeof data === 'string' ? data : data?.detail || data?.message || '请求失败，请稍后重试')
  return data
}

export async function register(username, password) {
  const params = new URLSearchParams({ username, password })
  return readResponse(await request(`/register?${params}`, { method: 'POST' }))
}
export async function login(username, password) {
  const params = new URLSearchParams({ username, password })
  return readResponse(await request(`/login?${params}`, { method: 'POST' }))
}
export async function ragUpload(file) {
  const body = new FormData(); body.append('file', file)
  return readResponse(await request('/rag', { method: 'POST', body }))
}
export async function chat(question) {
  const params = new URLSearchParams({ question })
  return readResponse(await request(`/chat?${params}`))
}
export async function graphChat(question) {
  const params = new URLSearchParams({ question })
  return readResponse(await request(`/rag/chat?${params}`))
}
