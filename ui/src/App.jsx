import { useState, useEffect, useCallback } from 'react'
import { getStats, listNotes, searchNotes, queryRAG } from './api'
import './App.css'

const TABS = ['Ask', 'Search', 'Notes']

export default function App() {
  const [tab, setTab]   = useState('Ask')
  const [stats, setStats] = useState(null)
  const [dark, setDark] = useState(() => document.documentElement.classList.contains('dark'))

  const refreshStats = useCallback(async () => {
    try { setStats(await getStats()) } catch {}
  }, [])

  useEffect(() => { refreshStats() }, [refreshStats])

  function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark')
    localStorage.setItem('notes-theme', isDark ? 'dark' : 'light')
    setDark(isDark)
  }

  return (
    <>
      <nav className="nav">
        <span className="nav-logo">Notes</span>
        <div className="nav-right">
          {TABS.map(t => (
            <button key={t} className={`nav-link ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>
              {t}
            </button>
          ))}
          <button className="theme-btn" onClick={toggleTheme} title="Toggle light / dark">◐</button>
        </div>
      </nav>

      <main>
        {stats && (
          <div className="stats-row">
            <div className="stat-item">
              <span className="stat-n">{stats.files}</span>
              <span className="stat-label">Files</span>
            </div>
            <div className="stat-item">
              <span className="stat-n">{stats.chunks}</span>
              <span className="stat-label">Chunks</span>
            </div>
          </div>
        )}

        {tab === 'Ask'    && <AskTab />}
        {tab === 'Search' && <SearchTab />}
        {tab === 'Notes'  && <NotesTab />}
      </main>

      <footer>
        <span>Notes RAG</span>
        <span>Gemma · ChromaDB · Docker Model Runner</span>
      </footer>
    </>
  )
}

// ── Ask ───────────────────────────────────────────────────────────────────────

function AskTab() {
  const [question, setQuestion] = useState('')
  const [topK, setTopK]         = useState(5)
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)

  async function handleAsk(e) {
    e.preventDefault()
    if (!question.trim()) return
    setLoading(true); setError(null); setResult(null)
    try { setResult(await queryRAG(question, topK)) }
    catch (err) { setError(err.message) }
    finally { setLoading(false) }
  }

  return (
    <div className="panel">
      <p className="label">Ask</p>
      <p className="panel-subtitle">Gemma answers using your notes as context.</p>

      <form onSubmit={handleAsk}>
        <div className="field">
          <textarea
            rows={3}
            placeholder="What would you like to know about your notes?"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAsk(e) } }}
          />
        </div>
        <div className="field-row">
          <label className="field-label">
            Top-K sources
            <input type="number" min={1} max={20} value={topK} onChange={e => setTopK(+e.target.value)} />
          </label>
          <button className="btn btn-primary" disabled={loading || !question.trim()}>
            {loading ? 'Thinking…' : 'Ask →'}
          </button>
        </div>
      </form>

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <div className="answer-block">
          <p className="answer-kicker">Answer</p>
          <p className="answer-text">{result.answer}</p>

          {result.sources?.length > 0 && (
            <>
              <p className="sources-kicker">Sources ({result.sources.length})</p>
              {result.sources.map((s, i) => <SourceRow key={i} source={s} index={i} />)}
            </>
          )}
        </div>
      )}
    </div>
  )
}

// ── Search ────────────────────────────────────────────────────────────────────

function SearchTab() {
  const [query, setQuery]     = useState('')
  const [topK, setTopK]       = useState(5)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  async function handleSearch(e) {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true); setError(null)
    try { setResults((await searchNotes(query, topK)).results) }
    catch (err) { setError(err.message) }
    finally { setLoading(false) }
  }

  return (
    <div className="panel">
      <p className="label">Search</p>
      <p className="panel-subtitle">Semantic similarity — finds relevant passages without LLM generation.</p>

      <form onSubmit={handleSearch}>
        <div className="field">
          <input
            placeholder="Search your notes…"
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
        </div>
        <div className="field-row">
          <label className="field-label">
            Results
            <input type="number" min={1} max={20} value={topK} onChange={e => setTopK(+e.target.value)} />
          </label>
          <button className="btn btn-primary" disabled={loading || !query.trim()}>
            {loading ? 'Searching…' : 'Search →'}
          </button>
        </div>
      </form>

      {error && <div className="alert alert-error">{error}</div>}

      {results && (
        <div style={{ marginTop: 24 }}>
          <p className="sources-kicker">{results.length} result{results.length !== 1 ? 's' : ''}</p>
          {results.map((s, i) => <SourceRow key={i} source={s} index={i} showScore />)}
          {results.length === 0 && <p className="empty">No results found.</p>}
        </div>
      )}
    </div>
  )
}

// ── Notes ─────────────────────────────────────────────────────────────────────

function NotesTab() {
  const [notes, setNotes]     = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listNotes()
      .then(d => setNotes(d.notes))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="panel">
      <p className="label">Notes</p>
      <p className="panel-subtitle">All files currently indexed in ChromaDB.</p>

      {loading && <p className="empty">Loading…</p>}
      {!loading && notes.length === 0 && (
        <p className="empty">No notes indexed yet. Run: <code>python indexer.py</code></p>
      )}

      {notes.map((n, i) => (
        <div key={n} className="doc-row">
          <span className="doc-num">{String(i + 1).padStart(2, '0')}</span>
          <div className="doc-body">
            <p className="doc-name">{n.split(/[\\/]/).pop()}</p>
            <p className="doc-path">{n}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Source row ────────────────────────────────────────────────────────────────

function SourceRow({ source, index, showScore }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="source-row" onClick={() => setOpen(o => !o)}>
      <span className="source-num">{String(index + 1).padStart(2, '0')}</span>
      <div className="source-body">
        <p className="source-doc">{source.filename || source.source}</p>
        <p className="source-meta">{source.source}</p>
        <p className={`source-excerpt ${open ? 'open' : ''}`}>{source.text}</p>
      </div>
      <div className="source-right">
        {showScore && source.score != null && (
          <span className="source-score">{(source.score * 100).toFixed(1)}%</span>
        )}
        <span className="source-arrow">{open ? '↑' : '↗'}</span>
      </div>
    </div>
  )
}
