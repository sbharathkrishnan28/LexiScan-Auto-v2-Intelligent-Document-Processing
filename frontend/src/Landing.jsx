// ─── Landing Page ─────────────────────────────────────────────────────────────
// Marketing entry point shown to logged-out visitors.

function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === 'dark'
  return (
    <button className="theme-toggle" onClick={onToggle} aria-label="Toggle color theme"
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}>
      <span className="tt-icon">{isDark ? '🌙' : '☀️'}</span>
      <span className="tt-label">{isDark ? 'Dark' : 'Light'}</span>
    </button>
  )
}

export default function Landing({ onGetStarted, onLogin, theme, onToggleTheme }) {
  const features = [
    { icon: '🔍', title: 'Named Entity Recognition', body: 'Spacy NER pinpoints parties, dates, financial amounts, locations and termination clauses in seconds.' },
    { icon: '🤖', title: 'AI Type Prediction', body: 'An offline machine-learning model classifies each contract — NDA, Lease, Employment, Service, Sales or Loan.' },
    { icon: '🛡️', title: 'PII Redaction Engine', body: 'Automatically masks sensitive names and figures for GDPR-style compliance — fully on-device.' },
    { icon: '📊', title: 'Confidence & Risk Scoring', body: '0–100 confidence with LOW / MEDIUM / HIGH risk and automatic human-review flagging.' },
    { icon: '🗂', title: 'Per-User History', body: 'Every analysis is saved to your private, authenticated account with full search and delete.' },
    { icon: '⚡', title: 'Millisecond Processing', body: 'PyMuPDF text extraction with no OCR — most contracts analyse in well under a second.' },
  ]

  const steps = [
    { n: '01', title: 'Create your account', body: 'Sign up securely with email & password — JWT-protected.' },
    { n: '02', title: 'Upload a PDF contract', body: 'Drag & drop any legal PDF into the analyzer.' },
    { n: '03', title: 'Get instant intelligence', body: 'Entities, predicted type, risk score and a redacted copy.' },
  ]

  return (
    <div className="landing">
      {/* Nav */}
      <header className="landing-nav">
        <div className="brand">
          <div className="brand-icon">⚡</div>
          <div>
            <h1>LexiScan Auto</h1>
            <p className="brand-sub">AI Contract Intelligence</p>
          </div>
        </div>
        <div className="btn-row">
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
          <button className="btn btn-secondary" onClick={onLogin}>Log in</button>
          <button className="btn btn-primary" onClick={onGetStarted}>Get Started</button>
        </div>
      </header>

      {/* Hero */}
      <section className="hero">
        <div className="hero-badge">⚡ NLP · Machine Learning · PII Redaction</div>
        <h2 className="hero-title">
          Turn dense legal PDFs into<br />
          <span className="hero-accent">structured intelligence</span>
        </h2>
        <p className="hero-sub">
          LexiScan Auto reads your contracts the way an analyst would — extracting parties,
          amounts and clauses, predicting the contract type with an on-device ML model, scoring
          risk, and redacting sensitive data. No cloud AI, no API keys, fully private.
        </p>
        <div className="hero-cta">
          <button className="btn btn-primary btn-lg" onClick={onGetStarted}>Analyze a Contract →</button>
          <button className="btn btn-secondary btn-lg" onClick={onLogin}>I already have an account</button>
        </div>

        <div className="hero-stats">
          <div><span className="hero-stat-num">6</span><span className="hero-stat-lbl">Contract types</span></div>
          <div><span className="hero-stat-num">5+</span><span className="hero-stat-lbl">Entity classes</span></div>
          <div><span className="hero-stat-num">&lt;1s</span><span className="hero-stat-lbl">Avg analysis</span></div>
          <div><span className="hero-stat-num">100%</span><span className="hero-stat-lbl">On-device</span></div>
        </div>
      </section>

      {/* Features */}
      <section className="landing-section">
        <h3 className="section-title">Everything you need to triage contracts</h3>
        <p className="section-sub">A full NLP pipeline wrapped in a clean, authenticated dashboard.</p>
        <div className="feature-grid">
          {features.map(f => (
            <div key={f.title} className="glass feature-card">
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="landing-section">
        <h3 className="section-title">How it works</h3>
        <div className="steps-grid">
          {steps.map(s => (
            <div key={s.n} className="glass step-card">
              <span className="step-num">{s.n}</span>
              <h4>{s.title}</h4>
              <p>{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="landing-cta glass">
        <h3>Ready to scan your first contract?</h3>
        <p>Create a free account and analyze a PDF in under a minute.</p>
        <button className="btn btn-primary btn-lg" onClick={onGetStarted}>Get Started — it's free</button>
      </section>

      <footer className="landing-footer">
        <span>LexiScan Auto · Built with FastAPI · React · Spacy · scikit-learn</span>
        <span>Zaalima Intern Project — AI Document Processing</span>
      </footer>
    </div>
  )
}
