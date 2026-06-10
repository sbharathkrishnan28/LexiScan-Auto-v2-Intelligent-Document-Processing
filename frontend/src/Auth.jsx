import { useState } from 'react'

// ─── Auth Screen (Login / Sign-up) ────────────────────────────────────────────
// Calls /auth/login or /auth/register and hands the token + user back up.

function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === 'dark'
  return (
    <button className="theme-toggle auth-theme" onClick={onToggle} aria-label="Toggle color theme"
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}>
      <span className="tt-icon">{isDark ? '🌙' : '☀️'}</span>
      <span className="tt-label">{isDark ? 'Dark' : 'Light'}</span>
    </button>
  )
}

export default function Auth({ api, onAuthed, onBack, addToast, theme, onToggleTheme }) {
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async e => {
    e.preventDefault()
    if (busy) return
    setBusy(true)
    const path = mode === 'login' ? '/auth/login' : '/auth/register'
    const payload = mode === 'login' ? { email, password } : { name, email, password }
    try {
      const res = await fetch(`${api}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Authentication failed.')
      addToast(mode === 'login' ? `Welcome back, ${data.user.name}!` : `Account created — welcome, ${data.user.name}!`, 'success')
      onAuthed(data.access_token, data.user)
    } catch (err) {
      addToast(err.message || 'Could not authenticate. Is the backend running?', 'error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-screen">
      <button className="auth-back" onClick={onBack}>← Back to home</button>
      <ThemeToggle theme={theme} onToggle={onToggleTheme} />

      <div className="glass auth-card fade-in">
        <div className="brand auth-brand">
          <div className="brand-icon">⚡</div>
          <h1>LexiScan Auto</h1>
        </div>

        <div className="auth-tabs">
          <button
            className={`auth-tab ${mode === 'login' ? 'auth-tab-active' : ''}`}
            onClick={() => setMode('login')}
          >Log in</button>
          <button
            className={`auth-tab ${mode === 'register' ? 'auth-tab-active' : ''}`}
            onClick={() => setMode('register')}
          >Sign up</button>
        </div>

        <form onSubmit={submit} className="auth-form">
          {mode === 'register' && (
            <label className="auth-field">
              <span>Name</span>
              <input value={name} onChange={e => setName(e.target.value)} placeholder="Your name" autoComplete="name" />
            </label>
          )}
          <label className="auth-field">
            <span>Email</span>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" required autoComplete="email" />
          </label>
          <label className="auth-field">
            <span>Password</span>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required minLength={6} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} />
          </label>

          <button className="btn btn-primary btn-block" disabled={busy}>
            {busy ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Create account'}
          </button>
        </form>

        <p className="auth-switch">
          {mode === 'login' ? "Don't have an account? " : 'Already registered? '}
          <span className="accent-link" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
            {mode === 'login' ? 'Sign up' : 'Log in'}
          </span>
        </p>
      </div>
    </div>
  )
}
