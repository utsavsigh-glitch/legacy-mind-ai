import React, { useState } from "react";
import LetterGlitch from "./LetterGlitch";

const stages = [
  ["01", "Upload", "Legacy code intake"],
  ["02", "Understand", "AI code mapping"],
  ["03", "Dependencies", "Architecture graph"],
  ["04", "Secure", "Threat discovery"],
  ["05", "Document", "Knowledge recovery"],
  ["06", "Modernize", "Migration plan"],
  ["07", "Verify", "Safety gate"],
  ["08", "Deploy", "Release ready"],
];

function Metric({ label, value, accent = "" }) {
  return (
    <div className={`metric ${accent}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? "https://legacy-mind-ai.onrender.com" : "");

export default function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyze() {
    if (!file) return;
    setLoading(true);
    setError("");
    setData(null);

    const form = new FormData();
    form.append("file", file);

    try {
      const response = await fetch(`${API_BASE}/api/analyze`, { method: "POST", body: form });
      const raw = await response.text();
      let json = {};
      try { json = raw ? JSON.parse(raw) : {}; } catch { json = {}; }
      if (!response.ok) throw new Error(json.detail || raw || `Analysis failed (${response.status})`);
      setData(json);
    } catch (err) {
      setError(err.message || "Unable to analyze this codebase.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <div className="glitch-background" aria-hidden="true">
        <LetterGlitch
          glitchSpeed={65}
          centerVignette={true}
          outerVignette={true}
          smooth={true}
          glitchColors={["#0d7ea5", "#18e0c1", "#356dff", "#0a3145"]}
        />
      </div>
      <div className="ambient-grid" aria-hidden="true" />

      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark">LM</div>
          <div>
            <div className="brand-name">LEGACY<span>MIND</span> <b>AI</b></div>
            <div className="brand-sub">LEGACY SOFTWARE INTELLIGENCE PLATFORM</div>
          </div>
        </div>
        <div className="top-actions">
          <span className="system-pill"><i /> SYSTEM ONLINE</span>
          <span className="version">MVP / 01</span>
        </div>
      </header>

      <main className="content">
        <section className="hero-panel">
          <div className="hero-copy">
            <div className="section-kicker">AUTONOMOUS MODERNIZATION ENGINE</div>
            <h1>Make legacy code<br /><em>understandable again.</em></h1>
            <p>
              Recover architecture, expose security risk, generate living documentation,
              and create a safer modernization path from code you already have.
            </p>
            <div className="hero-tags">
              <span>CODE INTELLIGENCE</span>
              <span>SECURITY</span>
              <span>MODERNIZATION</span>
            </div>
          </div>

          <div className="upload-console">
            <div className="console-head">
              <span>01 / CODE INTAKE</span>
              <span>READY</span>
            </div>
            <label className="dropzone">
              <input
                type="file"
                accept=".zip,.py,.js,.jsx,.ts,.tsx,.java,.c,.cpp,.h,.hpp,.cob,.cbl,.f,.f90,.for"
                onChange={(e) => { setFile(e.target.files[0] || null); setError(""); setData(null); }}
              />
              <div className="upload-orbit"><span>↑</span></div>
              <strong>{file ? file.name : "DROP LEGACY CODE HERE"}</strong>
              <small>{file ? "SOURCE CAPTURED · READY TO SCAN" : "ZIP / PYTHON / JAVA / COBOL / C / C++ / JS"}</small>
            </label>
            <button className="analyze-button" disabled={!file || loading} onClick={analyze}>
              <span>{loading ? "RUNNING ANALYSIS" : "START CODE ANALYSIS"}</span>
              <b>{loading ? "…" : "→"}</b>
            </button>
            {error && <div className="error-box"><b>ANALYSIS ERROR</b><span>{error}</span></div>}
          </div>
        </section>

        <section className="pipeline-panel">
          <div className="panel-heading">
            <div><span className="section-kicker">PIPELINE</span><h2>Modernization sequence</h2></div>
            <span className="pipeline-status">08 STAGES</span>
          </div>
          <div className="stages">
            {stages.map(([number, title, description]) => (
              <div className="stage" key={number}>
                <small>{number}</small>
                <strong>{title}</strong>
                <span>{description}</span>
              </div>
            ))}
          </div>
        </section>

        {data && (
          <div className="results-area">
            <section className="metrics">
              <Metric label="FILES ANALYZED" value={data.summary.files} />
              <Metric label="LINES OF CODE" value={data.summary.lines} />
              <Metric label="DEPENDENCIES" value={data.summary.dependencies} />
              <Metric label="SECURITY FINDINGS" value={data.summary.security_findings} />
              <Metric label="CRITICAL" value={data.summary.critical_findings} accent="critical" />
            </section>

            <section className="results-grid">
              <div className="result-panel">
                <div className="result-title"><span>SECURITY</span><b>THREAT SURFACE</b></div>
                {data.security_findings.length === 0 ? <p className="muted">No heuristic findings detected.</p> : data.security_findings.map((item, i) => (
                  <div className="finding" key={i}><div><strong>{item.type}</strong><span>{item.file}:{item.line}</span></div><b className={item.severity.toLowerCase()}>{item.severity}</b></div>
                ))}
              </div>
              <div className="result-panel">
                <div className="result-title"><span>DEPENDENCIES</span><b>CODE RELATIONSHIPS</b></div>
                {data.dependencies.length === 0 ? <p className="muted">No dependencies detected.</p> : data.dependencies.map((item, i) => (
                  <div className="dependency" key={i}><span>{item.file}</span><b>→ {item.dependency}</b></div>
                ))}
              </div>
              <div className="result-panel wide">
                <div className="result-title"><span>MODERNIZATION</span><b>RECOMMENDED TARGETS</b></div>
                {data.modernization.map((item, i) => <div className="recommendation" key={i}><strong>{item.file}</strong><span>→ {item.target}</span><p>{item.reason}</p></div>)}
              </div>
              <div className="result-panel wide">
                <div className="result-title"><span>DOCUMENTATION</span><b>RECOVERED KNOWLEDGE</b></div>
                <pre>{data.documentation}</pre>
              </div>
              {data.ai_analysis && data.ai_analysis.status === "success" && (
                <div className="result-panel wide">
                  <div className="result-title"><span>AI DEEP SCAN</span><b>{data.ai_analysis.model.toUpperCase()} INTELLIGENCE</b></div>
                  <pre>{data.ai_analysis.analysis}</pre>
                </div>
              )}
              <div className="result-panel wide verification-panel">
                <div className="result-title"><span>VERIFICATION GATE</span><b>RELEASE SAFETY</b></div>
                <div className={data.verification.status === "PASS" ? "pass" : "review"}>{data.verification.status}</div>
                <p>{data.verification.message}</p>
              </div>
            </section>
          </div>
        )}
      </main>

      <footer>LEGACYMIND AI · CODE UNDERSTANDING → SECURITY → MODERNIZATION</footer>
    </div>
  );
}
