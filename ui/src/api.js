const BASE = '/api'

async function request(path, opts = {}) {
  const r = await fetch(BASE + path, opts)
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(err.detail || `Request failed: ${r.status}`)
  }
  return r.json()
}

export const getStats  = () => request('/stats')
export const listNotes = () => request('/notes')

export function searchNotes(query, topK = 5) {
  return request('/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: topK }),
  })
}

export function queryRAG(question, topK = 5) {
  return request('/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK }),
  })
}
