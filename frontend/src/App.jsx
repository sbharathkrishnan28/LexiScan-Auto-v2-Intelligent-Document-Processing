import { useState, useRef, useCallback, useEffect } from 'react'
import Landing from './Landing'
import Auth from './Auth'

const API = 'http://localhost:8001/api/v1'

// ─── Theme Toggle ─────────────────────────────────────────────────────────────
function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === 'dark'
  return (
    <button
      className="theme-toggle"
      onClick={onToggle}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-label="Toggle color theme"
    >
      <span className="tt-icon">{isDark ? '🌙' : '☀️'}</span>
      <span className="tt-label">{isDark ? 'Dark' : 'Light'}</span>
    </button>
  )
}

// ─── Toast ───────────────────────────────────────────────────────────────────
function Toast({ toasts, remove }) {
  return (
    <div className="toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`toast toast-${t.type}`}>
          <span>{t.message}</span>
          <button className="toast-close" onClick={() => remove(t.id)}>✕</button>
        </div>
      ))}
    </div>
  )
}

// ─── Confidence Meter ─────────────────────────────────────────────────────────
function ConfidenceMeter({ score }) {
  const color = score >= 70 ? '#4ade80' : score >= 40 ? '#fbbf24' : '#f87171'
  return (
    <div className="confidence-meter">
      <div className="confidence-label">
        <span>AI Confidence</span>
        <span style={{ color, fontWeight: 700 }}>{score}%</span>
      </div>
      <div className="confidence-track">
        <div className="confidence-fill" style={{ width: `${score}%`, background: color }} />
      </div>
    </div>
  )
}

// ─── Risk Badge ───────────────────────────────────────────────────────────────
function RiskBadge({ level }) {
  return (
    <span className={`risk-badge risk-${(level || 'medium').toLowerCase()}`}>
      {level} RISK
    </span>
  )
}

// ─── Prediction Panel (ML contract-type classifier) ──────────────────────────
function PredictionPanel({ prediction }) {
  if (!prediction || !prediction.ranked?.length) return null
  return (
    <div className="glass predict-panel">
      <h3 className="panel-title">🤖 AI Contract-Type Prediction</h3>
      <div className="predict-head">
        <span className="predict-type">{prediction.category}</span>
        <span className="predict-conf">{prediction.confidence}% confident</span>
      </div>
      <p className="predict-label">{prediction.category_label}</p>
      <div className="predict-bars">
        {prediction.ranked.map(r => (
          <div key={r.category} className="predict-row">
            <span className="predict-row-label">{r.category}</span>
            <div className="predict-track">
              <div className="predict-fill" style={{ width: `${r.probability}%` }} />
            </div>
            <span className="predict-row-val">{r.probability}%</span>
          </div>
        ))}
      </div>
      <p className="predict-note">Offline TF-IDF + Logistic Regression model · no external API</p>
    </div>
  )
}

// ─── Processing Steps ─────────────────────────────────────────────────────────
function ProcessingSteps({ step }) {
  const steps = [
    'Extracting PDF text…',
    'Running NLP pipeline…',
    'Detecting entities…',
    'Applying PII redaction…',
    'Finalizing results…',
  ]
  return (
    <div className="proc-steps">
      {steps.map((s, i) => (
        <div key={i} className={`proc-step ${i < step ? 'done' : i === step ? 'active' : ''}`}>
          <span className="proc-icon">{i < step ? '✓' : i === step ? '◉' : '○'}</span>
          <span>{s}</span>
        </div>
      ))}
    </div>
  )
}

// ─── Entity Tag ───────────────────────────────────────────────────────────────
function EntityTag({ text, type }) {
  return <span className={`tag tag-${type}`}>{text}</span>
}

// ─── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('lexiscan_token') || '')
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('lexiscan_user') || 'null') } catch { return null }
  })
  const [gate, setGate] = useState('landing') // 'landing' | 'auth' (only used when logged out)
  const [theme, setTheme] = useState(() => localStorage.getItem('lexiscan_theme') || 'dark')

  const [view, setView] = useState('upload')
  const [loading, setLoading] = useState(false)
  const [loadStep, setLoadStep] = useState(0)
  const [result, setResult] = useState(null)
  const [filename, setFilename] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [contracts, setContracts] = useState([])
  const [statsData, setStatsData] = useState(null)
  const [toasts, setToasts] = useState([])
  const fileInputRef = useRef(null)
  const toastId = useRef(0)

  const addToast = useCallback((message, type = 'info') => {
    const id = ++toastId.current
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4500)
  }, [])

  const removeToast = useCallback(id => setToasts(prev => prev.filter(t => t.id !== id)), [])

  // Apply theme to <html> and persist it.
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('lexiscan_theme', theme)
  }, [theme])

  const toggleTheme = useCallback(() => setTheme(t => (t === 'dark' ? 'light' : 'dark')), [])

  const logout = useCallback(() => {
    localStorage.removeItem('lexiscan_token')
    localStorage.removeItem('lexiscan_user')
    setToken('')
    setUser(null)
    setGate('landing')
    setView('upload')
    setResult(null)
    setContracts([])
    setStatsData(null)
  }, [])

  const onAuthed = useCallback((tok, usr) => {
    localStorage.setItem('lexiscan_token', tok)
    localStorage.setItem('lexiscan_user', JSON.stringify(usr))
    setToken(tok)
    setUser(usr)
    setView('upload')
  }, [])

  // Authenticated fetch — injects the bearer token and logs out on 401.
  const authedFetch = useCallback(async (path, opts = {}) => {
    const res = await fetch(`${API}${path}`, {
      ...opts,
      headers: { ...(opts.headers || {}), Authorization: `Bearer ${token}` },
    })
    if (res.status === 401) {
      logout()
      addToast('Session expired — please log in again.', 'error')
      throw new Error('Unauthorized')
    }
    return res
  }, [token, logout, addToast])

  const fetchHistory = useCallback(async () => {
    try {
      const res = await authedFetch('/contracts')
      const data = await res.json()
      setContracts(data.contracts || [])
    } catch (e) {
      if (e.message !== 'Unauthorized') addToast('Could not load history — is the backend running?', 'error')
    }
  }, [authedFetch, addToast])

  const fetchStats = useCallback(async () => {
    try {
      const res = await authedFetch('/stats')
      setStatsData(await res.json())
    } catch (e) {
      if (e.message !== 'Unauthorized') addToast('Could not load stats.', 'error')
    }
  }, [authedFetch, addToast])

  useEffect(() => {
    if (!token) return
    if (view === 'history') fetchHistory()
    if (view === 'stats') fetchStats()
  }, [view, token, fetchHistory, fetchStats])

  const processFile = async file => {
    if (!file?.name?.toLowerCase().endsWith('.pdf')) {
      addToast('Please upload a valid PDF file.', 'error')
      return
    }
    setFilename(file.name)
    setLoading(true)
    setLoadStep(0)
    setResult(null)

    const stepTimer = setInterval(() =>
      setLoadStep(prev => (prev < 4 ? prev + 1 : prev)), 420)

    const fd = new FormData()
    fd.append('file', file)

    try {
      const res = await authedFetch('/extract', { method: 'POST', body: fd })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Processing failed.')
      }
      const data = await res.json()
      clearInterval(stepTimer)
      setLoadStep(5)
      setTimeout(() => {
        setResult(data.analysis)
        setLoading(false)
        setView('results')
        addToast(
          `Analyzed in ${data.analysis.stats.processing_time_ms}ms — ${data.analysis.stats.entity_count} entities found`,
          'success'
        )
      }, 450)
    } catch (err) {
      clearInterval(stepTimer)
      setLoading(false)
      addToast(err.message || 'Failed to process. Is the backend running?', 'error')
    }
  }

  const handleDrop = e => {
    e.preventDefault()
    setDragOver(false)
    processFile(e.dataTransfer.files[0])
  }

  const exportRedacted = () => {
    if (!result) return
    const blob = new Blob([result.redacted_text], { type: 'text/plain' })
    const a = Object.assign(document.createElement('a'), {
      href: URL.createObjectURL(blob),
      download: `redacted_${filename.replace('.pdf', '.txt')}`,
    })
    a.click()
    URL.revokeObjectURL(a.href)
    addToast('Redacted document exported.', 'success')
  }

  const deleteContract = async id => {
    try {
      await authedFetch(`/contracts/${id}`, { method: 'DELETE' })
      setContracts(prev => prev.filter(c => c.id !== id))
      addToast('Contract removed from history.', 'info')
    } catch (e) {
      if (e.message !== 'Unauthorized') addToast('Failed to delete contract.', 'error')
    }
  }

  const highlightRedactions = text => {
    if (!text) return null
    return text.split(/(\[PARTY_REDACTED\]|\[AMOUNT_REDACTED\])/g).map((part, i) => {
      if (part === '[PARTY_REDACTED]')
        return <span key={i} className="redacted redacted-party">{part}</span>
      if (part === '[AMOUNT_REDACTED]')
        return <span key={i} className="redacted redacted-amount">{part}</span>
      return <span key={i}>{part}</span>
    })
  }

  const tabs = [
    { id: 'upload',  label: '⬆ Upload' },
    { id: 'results', label: '📊 Results', disabled: !result },
    { id: 'history', label: '🗂 History' },
    { id: 'stats',   label: '📈 Stats' },
  ]

  // ── Logged-out: landing / auth ─────────────────────────────────────────────
  if (!token) {
    return (
      <>
        <Toast toasts={toasts} remove={removeToast} />
        {gate === 'auth' ? (
          <Auth
            api={API}
            addToast={addToast}
            onAuthed={onAuthed}
            onBack={() => setGate('landing')}
            theme={theme}
            onToggleTheme={toggleTheme}
          />
        ) : (
          <Landing
            onGetStarted={() => setGate('auth')}
            onLogin={() => setGate('auth')}
            theme={theme}
            onToggleTheme={toggleTheme}
          />
        )}
      </>
    )
  }

  // ── Logged-in: dashboard ───────────────────────────────────────────────────
  return (
    <div className="app-root">
      <Toast toasts={toasts} remove={removeToast} />

      {/* Header */}
      <header className="app-header">
        <div className="brand">
          <div className="brand-icon">⚡</div>
          <div>
            <h1>LexiScan Auto</h1>
            <p className="brand-sub">Intelligent Document Processing &amp; PII Redaction</p>
          </div>
        </div>
        <nav className="tab-nav">
          {tabs.map(t => (
            <button
              key={t.id}
              className={`tab-btn ${view === t.id ? 'tab-active' : ''} ${t.disabled ? 'tab-disabled' : ''}`}
              onClick={() => !t.disabled && setView(t.id)}
            >
              {t.label}
            </button>
          ))}
          <div className="user-menu">
            <ThemeToggle theme={theme} onToggle={toggleTheme} />
            <span className="user-chip" title={user?.email}>
              <span className="user-avatar">{(user?.name || user?.email || '?')[0].toUpperCase()}</span>
              <span className="user-name">{user?.name}</span>
            </span>
            <button className="btn btn-secondary btn-sm" onClick={logout}>Log out</button>
          </div>
        </nav>
      </header>

      <main className="app-main">

        {/* ── UPLOAD VIEW ─────────────────────────────────────────── */}
        {view === 'upload' && !loading && (
          <div className="fade-in">
            <div
              className={`glass upload-zone ${dragOver ? 'drag-over' : ''}`}
              onDrop={handleDrop}
              onDragOver={e => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onClick={() => fileInputRef.current.click()}
            >
              <div className="upload-icon">
                <svg width="52" height="52" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="12" y1="18" x2="12" y2="12" />
                  <polyline points="9 15 12 12 15 15" />
                </svg>
              </div>
              <h2 className="upload-title">Drop PDF Contract Here</h2>
              <p className="upload-hint">Drag &amp; drop or <span className="accent-link">click to browse</span></p>
              <p className="upload-note">PDF only · Powered by Spacy NER + PyMuPDF</p>
              <input
                ref={fileInputRef} type="file" accept=".pdf"
                style={{ display: 'none' }} onChange={e => processFile(e.target.files[0])}
              />
            </div>

            <div className="feature-grid">
              {[
                { icon: '🔍', title: 'Named Entity Recognition', body: 'Identifies Parties, Dates, Amounts, Locations, and Termination Clauses with Spacy NER.' },
                { icon: '🛡️', title: 'PII Redaction Engine', body: 'Automatically masks sensitive names and financial figures for GDPR compliance.' },
                { icon: '📊', title: 'Confidence Scoring', body: 'AI-powered 0–100 confidence score with risk assessment and human-review flagging.' },
                { icon: '⚡', title: 'Real-Time Processing', body: 'PyMuPDF extracts and analyzes legal contracts in milliseconds — no OCR required.' },
              ].map(f => (
                <div key={f.title} className="glass feature-card">
                  <div className="feature-icon">{f.icon}</div>
                  <h3>{f.title}</h3>
                  <p>{f.body}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── LOADING VIEW ─────────────────────────────────────────── */}
        {loading && (
          <div className="glass loading-panel fade-in">
            <div className="spinner" />
            <h2>Analyzing <span className="accent-text">{filename}</span></h2>
            <p className="brand-sub">NLP pipeline running…</p>
            <ProcessingSteps step={loadStep} />
          </div>
        )}

        {/* ── RESULTS VIEW ─────────────────────────────────────────── */}
        {view === 'results' && result && (
          <div className="fade-in">
            <div className="results-bar">
              <div>
                <h2 className="page-title">Analysis Complete</h2>
                <p className="brand-sub">
                  {filename} &nbsp;·&nbsp;
                  {result.stats.word_count.toLocaleString()} words &nbsp;·&nbsp;
                  {result.stats.page_count} page(s) &nbsp;·&nbsp;
                  {result.stats.processing_time_ms} ms
                </p>
              </div>
              <div className="btn-row">
                <button className="btn btn-secondary" onClick={() => setView('upload')}>Analyze New</button>
                <button className="btn btn-primary" onClick={exportRedacted}>⬇ Export Redacted</button>
              </div>
            </div>

            {result.human_review_required && (
              <div className="alert-warning">
                <strong>⚠ Human Review Required</strong>
                <ul>{result.flags.map((f, i) => <li key={i}>{f}</li>)}</ul>
              </div>
            )}

            <div className="meta-strip glass">
              <ConfidenceMeter score={result.confidence_score} />
              <div className="meta-divider" />
              <div className="meta-kv">
                <span className="meta-label">Risk Level</span>
                <RiskBadge level={result.risk_level} />
              </div>
              <div className="meta-divider" />
              <div className="meta-kv">
                <span className="meta-label">Entities Found</span>
                <span className="meta-value">{result.stats.entity_count}</span>
              </div>
              <div className="meta-divider" />
              <div className="meta-kv">
                <span className="meta-label">Predicted Type</span>
                <span className="meta-value meta-type">{result.prediction?.category || '—'}</span>
              </div>
              <div className="meta-divider" />
              <div className="meta-kv">
                <span className="meta-label">Pages</span>
                <span className="meta-value">{result.stats.page_count}</span>
              </div>
            </div>

            <PredictionPanel prediction={result.prediction} />

            <div className="results-grid">
              {/* Entities panel */}
              <div className="glass entity-panel">
                <h3 className="panel-title">Extracted Intelligence</h3>

                {[
                  { key: 'parties',             label: 'Parties',             type: 'party',    dot: 'dot-party' },
                  { key: 'amounts',             label: 'Financial Amounts',   type: 'amount',   dot: 'dot-amount' },
                  { key: 'dates',               label: 'Dates',               type: 'date',     dot: 'dot-date' },
                  { key: 'locations',           label: 'Locations',           type: 'location', dot: 'dot-location' },
                  { key: 'termination_clauses', label: 'Termination Clauses', type: 'clause',   dot: 'dot-clause' },
                ].map(({ key, label, type, dot }) => (
                  <div key={key} className="entity-group">
                    <div className="entity-header">
                      <span className={`dot ${dot}`} />
                      <span>{label}</span>
                      <span className="entity-count">({result.entities[key].length})</span>
                    </div>
                    <div className="tag-cloud">
                      {result.entities[key].length
                        ? result.entities[key].map((v, i) => <EntityTag key={i} text={v} type={type} />)
                        : <span className="none-found">None found</span>}
                    </div>
                  </div>
                ))}
              </div>

              {/* Redacted text panel */}
              <div className="glass redact-panel">
                <h3 className="panel-title">PII-Redacted Document</h3>
                <div className="redact-legend">
                  <span className="redacted redacted-party">[PARTY_REDACTED]</span> Party &nbsp;
                  <span className="redacted redacted-amount">[AMOUNT_REDACTED]</span> Amount
                </div>
                <div className="text-preview">{highlightRedactions(result.redacted_text)}</div>
              </div>
            </div>
          </div>
        )}

        {/* ── HISTORY VIEW ─────────────────────────────────────────── */}
        {view === 'history' && (
          <div className="fade-in">
            <div className="page-bar">
              <h2 className="page-title">Document History</h2>
              <button className="btn btn-secondary" onClick={fetchHistory}>↻ Refresh</button>
            </div>

            {contracts.length === 0 ? (
              <div className="glass empty-state">
                <p>No documents processed yet. Upload a PDF to get started.</p>
              </div>
            ) : (
              <div className="glass table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>#</th><th>Filename</th><th>Type</th><th>Parties</th><th>Max Amount</th>
                      <th>Confidence</th><th>Risk</th><th>Words</th><th>Date</th><th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {contracts.map(c => (
                      <tr key={c.id}>
                        <td className="td-muted">#{c.id}</td>
                        <td className="td-name">{c.filename}</td>
                        <td>
                          {c.predicted_type
                            ? <span className="type-chip">{c.predicted_type}</span>
                            : <span className="td-muted">—</span>}
                        </td>
                        <td>
                          {c.parties.slice(0, 2).join(', ')}
                          {c.parties.length > 2 && <span className="td-more">+{c.parties.length - 2}</span>}
                        </td>
                        <td>{c.max_amount > 0 ? `$${c.max_amount.toLocaleString()}` : '—'}</td>
                        <td>
                          <span className="conf-chip" style={{
                            background: c.confidence_score >= 70 ? 'rgba(74,222,128,.15)' : c.confidence_score >= 40 ? 'rgba(251,191,36,.15)' : 'rgba(248,113,113,.15)',
                            color: c.confidence_score >= 70 ? '#4ade80' : c.confidence_score >= 40 ? '#fbbf24' : '#f87171',
                          }}>
                            {c.confidence_score}%
                          </span>
                        </td>
                        <td><RiskBadge level={c.risk_level} /></td>
                        <td className="td-muted">{c.word_count?.toLocaleString()}</td>
                        <td className="td-muted">
                          {c.created_at ? new Date(c.created_at).toLocaleDateString() : '—'}
                        </td>
                        <td>
                          <button className="del-btn" onClick={() => deleteContract(c.id)} title="Delete">✕</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ── STATS VIEW ───────────────────────────────────────────── */}
        {view === 'stats' && (
          <div className="fade-in">
            <h2 className="page-title" style={{ marginBottom: '1.5rem' }}>Analytics Dashboard</h2>

            {!statsData ? (
              <div className="glass empty-state"><p>Loading…</p></div>
            ) : (
              <>
                <div className="stats-grid">
                  {[
                    { label: 'Total Documents', value: statsData.total_contracts, color: '#818cf8' },
                    { label: 'Avg. Confidence',  value: `${statsData.avg_confidence}%`, color: '#c084fc' },
                    { label: 'Need Review',       value: statsData.needs_review, color: '#f87171' },
                    { label: 'Avg. Words',        value: statsData.avg_word_count?.toLocaleString(), color: '#4ade80' },
                    { label: 'Avg. Speed (ms)',   value: statsData.avg_processing_ms, color: '#38bdf8' },
                  ].map(s => (
                    <div key={s.label} className="glass stat-card">
                      <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
                      <div className="stat-label">{s.label}</div>
                    </div>
                  ))}
                </div>

                <div className="glass risk-chart">
                  <h3 className="panel-title">Risk Distribution</h3>
                  {[
                    { label: 'LOW',    value: statsData.risk_breakdown.low,    color: '#4ade80' },
                    { label: 'MEDIUM', value: statsData.risk_breakdown.medium, color: '#fbbf24' },
                    { label: 'HIGH',   value: statsData.risk_breakdown.high,   color: '#f87171' },
                  ].map(r => {
                    const pct = statsData.total_contracts
                      ? Math.round((r.value / statsData.total_contracts) * 100)
                      : 0
                    return (
                      <div key={r.label} className="risk-row">
                        <span className="risk-label">{r.label}</span>
                        <div className="risk-track">
                          <div className="risk-fill" style={{ width: `${pct}%`, background: r.color }} />
                        </div>
                        <span className="risk-count">{r.value}</span>
                      </div>
                    )
                  })}
                </div>

                {statsData.type_breakdown?.length > 0 && (
                  <div className="glass risk-chart" style={{ marginTop: '1.5rem' }}>
                    <h3 className="panel-title">🤖 Predicted Contract Types</h3>
                    {statsData.type_breakdown.map((t, i) => {
                      const palette = ['#818cf8', '#c084fc', '#38bdf8', '#4ade80', '#fbbf24', '#fb923c']
                      const pct = statsData.total_contracts
                        ? Math.round((t.count / statsData.total_contracts) * 100)
                        : 0
                      return (
                        <div key={t.type} className="risk-row">
                          <span className="risk-label" style={{ width: 92 }}>{t.type}</span>
                          <div className="risk-track">
                            <div className="risk-fill" style={{ width: `${pct}%`, background: palette[i % palette.length] }} />
                          </div>
                          <span className="risk-count">{t.count}</span>
                        </div>
                      )
                    })}
                  </div>
                )}
              </>
            )}
          </div>
        )}

      </main>
    </div>
  )
}
