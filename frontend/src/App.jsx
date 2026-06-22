import React, { useState, useCallback, useRef } from 'react'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  Cell
} from 'recharts'

// ── Helpers ────────────────────────────────────────────────────────────────
const scoreColor = (s) =>
  s >= 75 ? '#10B981' : s >= 60 ? '#6366F1' : s >= 45 ? '#F59E0B' : '#EF4444'
const scoreLabel = (s) =>
  s >= 75 ? 'Excellent' : s >= 60 ? 'Good' : s >= 45 ? 'Fair' : 'Weak'
const priorityColor = { high: '#EF4444', medium: '#F59E0B', low: '#6366F1' }
const priorityBg = { high: '#7f1d1d22', medium: '#78350f22', low: '#312e8122' }

// ── Score Ring ─────────────────────────────────────────────────────────────
function ScoreRing({ score = 0, size = 140, label = 'Overall', animate = true }) {
  const r = 42
  const circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ
  const color = scoreColor(score)
  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={size} height={size} viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#2E3447" strokeWidth="8" />
        <circle cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
          style={{
            transformOrigin: 'center', transform: 'rotate(-90deg)',
            transition: animate ? 'stroke-dashoffset 1.2s cubic-bezier(0.34,1.56,0.64,1)' : 'none',
            filter: `drop-shadow(0 0 8px ${color}55)`
          }} />
        <text x="50" y="46" textAnchor="middle" fontSize="20" fontWeight="700"
          fill={color} fontFamily="Plus Jakarta Sans">{score}</text>
        <text x="50" y="62" textAnchor="middle" fontSize="8" fill="#64748B" fontFamily="Inter">/100</text>
      </svg>
      <div className="text-center">
        <div className="text-xs text-slate-400">{label}</div>
        <div className="text-xs font-semibold" style={{ color }}>{scoreLabel(score)}</div>
      </div>
    </div>
  )
}

// ── Mini Score Bar ─────────────────────────────────────────────────────────
function ScoreBar({ label, score, weight }) {
  const color = scoreColor(score)
  return (
    <div className="flex items-center gap-3">
      <div className="w-36 text-xs text-slate-400 shrink-0">{label}</div>
      <div className="flex-1 bg-slate-800 rounded-full h-1.5 overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700"
          style={{ width: `${score}%`, background: color, boxShadow: `0 0 6px ${color}55` }} />
      </div>
      <div className="w-8 text-right text-xs font-mono font-semibold" style={{ color }}>{score}</div>
      {weight && <div className="w-8 text-right text-xs text-slate-600">{weight}</div>}
    </div>
  )
}

// ── Skill Tag ──────────────────────────────────────────────────────────────
function Tag({ text, variant = 'default' }) {
  const styles = {
    default: 'bg-slate-800 text-slate-300 border border-slate-700',
    matched: 'bg-emerald-900/40 text-emerald-300 border border-emerald-700/50',
    missing: 'bg-red-900/30 text-red-300 border border-red-700/40',
    info: 'bg-indigo-900/40 text-indigo-300 border border-indigo-700/50',
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[variant]}`}>
      {text}
    </span>
  )
}

// ── Section Card ───────────────────────────────────────────────────────────
function Card({ title, icon, children, className = '' }) {
  return (
    <div className={`bg-[#1C202B] border border-[#2E3447] rounded-xl p-5 ${className}`}>
      {title && (
        <div className="flex items-center gap-2 mb-4">
          {icon && <span className="text-base">{icon}</span>}
          <h3 className="font-display text-sm font-semibold text-slate-100">{title}</h3>
        </div>
      )}
      {children}
    </div>
  )
}

// ── Upload Page ────────────────────────────────────────────────────────────
function UploadPage({ onSubmit, loading }) {
  const [resume, setResume] = useState(null)
  const [jd, setJd] = useState('')
  const [drag, setDrag] = useState(false)
  const fileRef = useRef()

  const handleDrop = (e) => {
    e.preventDefault(); setDrag(false)
    const f = e.dataTransfer.files[0]
    if (f && (f.name.endsWith('.pdf') || f.name.endsWith('.docx'))) setResume(f)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!resume || !jd.trim()) return
    onSubmit(resume, jd)
  }

  return (
    <div className="min-h-screen bg-[#0F1117] flex flex-col">
      {/* Header */}
      <header className="border-b border-[#2E3447] px-6 py-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-sm font-bold">IR</div>
        <div>
          <div className="font-display font-bold text-sm text-slate-100">Intelli_Resume</div>
          <div className="text-xs text-slate-500">Powered by semantic AI — not keyword counting</div>
        </div>
      </header>

      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-2xl">
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 bg-indigo-900/30 border border-indigo-700/40 rounded-full px-4 py-1.5 mb-4">
              <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-pulse" />
              <span className="text-xs text-indigo-300 font-medium">Semantic AI Analysis</span>
            </div>
            <h1 className="font-display text-3xl font-bold text-slate-100 mb-3">
              ATS Resume Intelligence
            </h1>
            <p className="text-slate-400 text-sm max-w-md mx-auto">
              Deep semantic analysis across 10 dimensions. Not a keyword counter.
              Understands context, relevance, and recruiter perspective.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Drop Zone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDrag(true) }}
              onDragLeave={() => setDrag(false)}
              onDrop={handleDrop}
              onClick={() => fileRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-200 ${
                drag ? 'border-indigo-500 bg-indigo-900/20' :
                resume ? 'border-emerald-500/60 bg-emerald-900/10' :
                'border-[#2E3447] hover:border-indigo-600/50 hover:bg-indigo-900/10'
              }`}
            >
              <input ref={fileRef} type="file" accept=".pdf,.docx" className="hidden"
                onChange={(e) => setResume(e.target.files[0])} />
              {resume ? (
                <div>
                  <div className="text-3xl mb-2">📄</div>
                  <div className="text-sm font-medium text-emerald-400">{resume.name}</div>
                  <div className="text-xs text-slate-500 mt-1">{(resume.size / 1024).toFixed(1)} KB · Click to change</div>
                </div>
              ) : (
                <div>
                  <div className="text-3xl mb-3">📁</div>
                  <div className="text-sm text-slate-300 font-medium">Drop your resume here</div>
                  <div className="text-xs text-slate-500 mt-1">PDF or DOCX · Max 10MB</div>
                </div>
              )}
            </div>

            {/* JD Input */}
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-2">
                Job Description <span className="text-red-400">*</span>
              </label>
              <textarea
                value={jd}
                onChange={(e) => setJd(e.target.value)}
                placeholder="Paste the full job description here..."
                rows={9}
                className="w-full bg-[#1C202B] border border-[#2E3447] rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 resize-none focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30 transition-all"
              />
              <div className="text-xs text-slate-600 mt-1 text-right">{jd.length} chars</div>
            </div>

            <button
              type="submit"
              disabled={!resume || !jd.trim() || loading}
              className="w-full py-3.5 rounded-xl font-display font-semibold text-sm transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-900/40"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="40" strokeDashoffset="10" />
                  </svg>
                  Analyzing Resume...
                </span>
              ) : 'Analyze Resume →'}
            </button>
          </form>

          {/* Feature pills */}
          <div className="flex flex-wrap gap-2 justify-center mt-8">
            {['Semantic Skill Matching','Experience Relevance','Project Scoring','ATS Compatibility','Career Fit Prediction','Recruiter Perspective','Benchmarking'].map(f => (
              <span key={f} className="text-xs text-slate-500 bg-[#1C202B] border border-[#2E3447] rounded-full px-3 py-1">{f}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Dashboard ──────────────────────────────────────────────────────────────
function Dashboard({ data, onReset }) {
  const [tab, setTab] = useState('overview')

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'skills', label: 'Skills' },
    { id: 'experience', label: 'Experience' },
    { id: 'quality', label: 'Quality' },
    { id: 'recruiter', label: 'Recruiter View' },
    { id: 'benchmark', label: 'Benchmarking' },
    { id: 'career', label: 'Career Fit' },
    { id: 'recommendations', label: 'Recommendations' },
  ]

  const d = data
  const total = d.total_score
  const skillScore = d.skill_analysis?.score ?? 0
  const expScore = d.experience_analysis?.score ?? 0
  const projScore = d.project_analysis?.score ?? 0
  const atsScore = d.ats_analysis?.score ?? 0
  const qualScore = d.quality_analysis?.score ?? 0
  const achScore = d.achievement_analysis?.score ?? 0

  return (
    <div className="min-h-screen bg-[#0F1117]">
      {/* Top Bar */}
      <header className="sticky top-0 z-20 border-b border-[#2E3447] bg-[#0F1117]/95 backdrop-blur px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-xs font-bold">IR</div>
          <span className="font-display font-bold text-sm text-slate-100 hidden sm:block">Resume Intelligence</span>
          <span className="text-xs text-slate-600 hidden md:block">· {d.resume_filename}</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 bg-[#1C202B] border border-[#2E3447] rounded-lg px-3 py-1.5">
            <div className="w-2 h-2 rounded-full" style={{ background: scoreColor(total) }} />
            <span className="text-xs font-semibold" style={{ color: scoreColor(total) }}>{total}/100</span>
          </div>
          <button onClick={onReset}
            className="text-xs text-slate-400 hover:text-slate-200 border border-[#2E3447] rounded-lg px-3 py-1.5 transition-colors">
            New Analysis
          </button>
        </div>
      </header>

      {/* Tab Nav */}
      <div className="border-b border-[#2E3447] px-6 overflow-x-auto">
        <div className="flex gap-0 min-w-max">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`px-4 py-3 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
                tab === t.id
                  ? 'border-indigo-500 text-indigo-400'
                  : 'border-transparent text-slate-500 hover:text-slate-300'
              }`}>{t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 space-y-6 animate-fadeIn">

        {/* ── OVERVIEW TAB ── */}
        {tab === 'overview' && (
          <>
            {/* Hero Score Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-4">
              <div className="col-span-2 sm:col-span-4 lg:col-span-2 bg-[#1C202B] border border-[#2E3447] rounded-xl p-5 flex items-center gap-5">
                <ScoreRing score={total} size={110} label="ATS Match" />
                <div>
                  <div className="text-xs text-slate-500 mb-1">Overall Score</div>
                  <div className="text-3xl font-display font-bold" style={{ color: scoreColor(total) }}>{total}</div>
                  <div className="text-xs text-slate-400 mt-0.5">{d.benchmark?.percentile}</div>
                  <div className="mt-2 text-xs">
                    <span className="bg-[#252A38] px-2 py-0.5 rounded text-slate-300">
                      Interview: {d.benchmark?.interview_probability}
                    </span>
                  </div>
                </div>
              </div>

              {[
                { label: 'Skills', score: skillScore },
                { label: 'Experience', score: expScore },
                { label: 'Projects', score: projScore },
                { label: 'ATS', score: atsScore },
                { label: 'Quality', score: qualScore },
              ].map(({ label, score }) => (
                <div key={label} className="bg-[#1C202B] border border-[#2E3447] rounded-xl p-4 flex flex-col items-center justify-center gap-2">
                  <ScoreRing score={score} size={72} label={label} />
                </div>
              ))}
            </div>

            {/* Score Breakdown */}
            <Card title="Score Breakdown" icon="📊">
              <div className="space-y-3">
                {(d.score_breakdown || []).map(row => (
                  <ScoreBar key={row.category} label={row.category} score={row.score} weight={row.weight} />
                ))}
              </div>
            </Card>

            {/* ATS Issues */}
            {(d.ats_analysis?.issues?.length > 0) && (
              <Card title="ATS Compatibility Issues" icon="⚠️">
                <div className="space-y-2">
                  {d.ats_analysis.issues.map((issue, i) => {
                    const styles = {
                      error: { bg: 'bg-red-900/20 border-red-700/40', dot: '#EF4444', text: 'text-red-300' },
                      warning: { bg: 'bg-amber-900/20 border-amber-700/40', dot: '#F59E0B', text: 'text-amber-300' },
                      info: { bg: 'bg-blue-900/20 border-blue-700/40', dot: '#6366F1', text: 'text-blue-300' },
                    }[issue.type] || { bg: 'bg-slate-800 border-slate-700', dot: '#64748B', text: 'text-slate-400' }
                    return (
                      <div key={i} className={`flex items-start gap-2.5 px-3 py-2 rounded-lg border ${styles.bg}`}>
                        <div className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" style={{ background: styles.dot }} />
                        <span className={`text-xs ${styles.text}`}>{issue.msg}</span>
                      </div>
                    )
                  })}
                </div>
              </Card>
            )}

            {/* Contact + Sections */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card title="Contact Detected" icon="👤">
                <div className="space-y-2">
                  {Object.entries(d.ats_analysis?.contact_completeness || {}).map(([k, v]) => (
                    <div key={k} className="flex items-center justify-between">
                      <span className="text-xs text-slate-400 capitalize">{k}</span>
                      <span className={`text-xs font-medium ${v ? 'text-emerald-400' : 'text-red-400'}`}>
                        {v ? '✓ Found' : '✗ Missing'}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
              <Card title="Resume Sections" icon="📋">
                <div className="flex flex-wrap gap-2">
                  {(d.ats_analysis?.sections_found || []).map(s => (
                    <Tag key={s} text={s} variant="matched" />
                  ))}
                </div>
              </Card>
            </div>
          </>
        )}

        {/* ── SKILLS TAB ── */}
        {tab === 'skills' && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="md:col-span-3" title="Skill Match Analysis" icon="🎯">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <div className="text-xs text-slate-500 mb-3 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
                      Semantically Matched ({d.skill_analysis?.matched?.length || 0})
                    </div>
                    <div className="space-y-2">
                      {(d.skill_analysis?.matched || []).map((m, i) => (
                        <div key={i} className="flex items-center justify-between bg-emerald-900/20 border border-emerald-700/30 rounded-lg px-3 py-1.5">
                          <div>
                            <div className="text-xs text-emerald-300 font-medium">{m.jd_skill}</div>
                            {m.jd_skill !== m.resume_match && (
                              <div className="text-xs text-slate-500">↳ {m.resume_match}</div>
                            )}
                          </div>
                          <div className="text-xs font-mono text-emerald-500">{Math.round(m.score * 100)}%</div>
                        </div>
                      ))}
                      {!d.skill_analysis?.matched?.length && <p className="text-xs text-slate-600">No matches found</p>}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-3 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />
                      Missing Skills ({d.skill_analysis?.missing?.length || 0})
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {(d.skill_analysis?.missing || []).map((s, i) => (
                        <Tag key={i} text={s} variant="missing" />
                      ))}
                      {!d.skill_analysis?.missing?.length && <p className="text-xs text-slate-600">No critical gaps!</p>}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-3 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-indigo-500 inline-block" />
                      Your Skills ({d.resume_skills?.length || 0})
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {(d.resume_skills || []).map((s, i) => (
                        <Tag key={i} text={s} variant="info" />
                      ))}
                    </div>
                  </div>
                </div>
              </Card>
            </div>

            {/* JD Parsed Skills */}
            <Card title="Job Description — Extracted Requirements" icon="📄">
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                {Object.entries(d.jd_parsed || {}).filter(([k, v]) => Array.isArray(v) && v.length > 0 && k !== 'responsibilities').map(([k, v]) => (
                  <div key={k}>
                    <div className="text-xs text-slate-500 capitalize mb-2">{k.replace(/_/g, ' ')}</div>
                    <div className="flex flex-wrap gap-1">
                      {v.map((s, i) => <Tag key={i} text={s} />)}
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Soft Skills */}
            {(d.skill_analysis?.soft_skills_match?.matched?.length > 0 || d.skill_analysis?.soft_skills_match?.missing?.length > 0) && (
              <Card title="Soft Skills" icon="🤝">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-slate-500 mb-2">Matched</div>
                    <div className="flex flex-wrap gap-1.5">
                      {(d.skill_analysis.soft_skills_match.matched || []).map((s, i) => (
                        <Tag key={i} text={s} variant="matched" />
                      ))}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-2">Missing</div>
                    <div className="flex flex-wrap gap-1.5">
                      {(d.skill_analysis.soft_skills_match.missing || []).map((s, i) => (
                        <Tag key={i} text={s} variant="missing" />
                      ))}
                    </div>
                  </div>
                </div>
              </Card>
            )}
          </>
        )}

        {/* ── EXPERIENCE TAB ── */}
        {tab === 'experience' && (
          <>
            <Card title="Experience Relevance" icon="💼">
              <div className="flex items-start gap-6 mb-5">
                <ScoreRing score={expScore} size={90} label="Relevance" />
                <div className="flex-1">
                  <p className="text-sm text-slate-300 mb-3">{d.experience_analysis?.explanation}</p>
                  <div className="space-y-2">
                    {(d.experience_analysis?.details || []).map((det, i) => (
                      <ScoreBar key={i} label={det.label} score={det.score} />
                    ))}
                  </div>
                </div>
              </div>
            </Card>

            {(d.experience || []).map((exp, i) => (
              <Card key={i} title={exp.role || 'Role'} icon="🏢">
                <div className="flex justify-between items-start mb-2">
                  <div className="text-xs text-slate-400">{exp.company}</div>
                  <div className="text-xs text-slate-600 font-mono">{exp.duration}</div>
                </div>
                <p className="text-xs text-slate-400 mb-3 leading-relaxed">{exp.description?.slice(0, 300)}</p>
                {exp.skills_used?.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {exp.skills_used.map((s, j) => <Tag key={j} text={s} variant="info" />)}
                  </div>
                )}
              </Card>
            ))}

            {/* Projects */}
            <Card title={`Projects (Score: ${projScore}/100)`} icon="🚀">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(d.project_analysis?.details || []).map((proj, i) => (
                  <div key={i} className="bg-[#252A38] rounded-lg p-4">
                    <div className="flex justify-between items-center mb-2">
                      <div className="text-sm font-medium text-slate-200">{proj.name}</div>
                      <div className="text-sm font-bold" style={{ color: scoreColor(proj.score) }}>{proj.score}</div>
                    </div>
                    <div className="space-y-1">
                      <ScoreBar label="Tech Relevance" score={proj.tech_relevance} />
                      <ScoreBar label="Complexity" score={proj.complexity} />
                      <ScoreBar label="Impact" score={proj.impact} />
                    </div>
                  </div>
                ))}
              </div>
              {(d.project_analysis?.details || []).length === 0 && (
                <p className="text-xs text-slate-600">No projects detected in resume</p>
              )}
            </Card>
          </>
        )}

        {/* ── QUALITY TAB ── */}
        {tab === 'quality' && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card title="Resume Quality Score" icon="✍️" className="md:col-span-1">
                <div className="flex flex-col items-center py-2">
                  <ScoreRing score={qualScore} size={100} label="Quality" />
                  <div className="mt-4 w-full space-y-2">
                    {Object.entries(d.quality_analysis?.components || {}).map(([k, v]) => (
                      <ScoreBar key={k} label={k.replace(/_/g, ' ')} score={v} />
                    ))}
                  </div>
                </div>
              </Card>

              <div className="md:col-span-2 space-y-4">
                <Card title="Action Verb Analysis" icon="💪">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-xs text-emerald-400 font-medium mb-2">
                        Strong Verbs ({d.quality_analysis?.strong_verbs?.length || 0})
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {(d.quality_analysis?.strong_verbs || []).map((v, i) => (
                          <Tag key={i} text={v} variant="matched" />
                        ))}
                        {!d.quality_analysis?.strong_verbs?.length && (
                          <p className="text-xs text-slate-600">None detected</p>
                        )}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-red-400 font-medium mb-2">
                        Weak Verbs ({d.quality_analysis?.weak_verbs?.length || 0})
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {(d.quality_analysis?.weak_verbs || []).map((v, i) => (
                          <Tag key={i} text={v} variant="missing" />
                        ))}
                        {!d.quality_analysis?.weak_verbs?.length && (
                          <p className="text-xs text-emerald-500">No weak verbs found ✓</p>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>

                <Card title="Achievement Quantification" icon="📈">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-xs text-emerald-400 font-medium mb-2">Quantified ✓</div>
                      {(d.quality_analysis?.quantified_achievements || []).map((a, i) => (
                        <div key={i} className="text-xs text-slate-300 bg-emerald-900/20 border border-emerald-700/30 rounded p-2 mb-2 leading-relaxed">
                          {a.slice(0, 160)}
                        </div>
                      ))}
                      {!d.quality_analysis?.quantified_achievements?.length && (
                        <p className="text-xs text-slate-600">No quantified achievements detected</p>
                      )}
                    </div>
                    <div>
                      <div className="text-xs text-amber-400 font-medium mb-2">Needs Metrics ⚠</div>
                      {(d.quality_analysis?.unquantified_examples || []).map((a, i) => (
                        <div key={i} className="text-xs text-slate-400 bg-amber-900/10 border border-amber-700/20 rounded p-2 mb-2 leading-relaxed">
                          {a.slice(0, 160)}
                        </div>
                      ))}
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          </>
        )}

        {/* ── RECRUITER VIEW TAB ── */}
        {tab === 'recruiter' && (
          <>
            <div className="bg-gradient-to-r from-indigo-900/30 to-purple-900/20 border border-indigo-700/30 rounded-xl p-5 mb-4">
              <div className="text-xs text-indigo-400 font-medium mb-2">6-Second First Impression</div>
              <p className="text-sm text-slate-200 font-medium">{d.recruiter_view?.first_impression}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card title="What Recruiters Will Notice — Strengths" icon="✅">
                <div className="space-y-2.5">
                  {(d.recruiter_view?.strengths || []).map((s, i) => (
                    <div key={i} className="flex items-start gap-2.5">
                      <div className="w-4 h-4 rounded-full bg-emerald-900/50 border border-emerald-500/40 flex items-center justify-center shrink-0 mt-0.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      </div>
                      <span className="text-xs text-slate-300 leading-relaxed">{s}</span>
                    </div>
                  ))}
                  {!d.recruiter_view?.strengths?.length && <p className="text-xs text-slate-600">No notable strengths detected</p>}
                </div>
              </Card>

              <Card title="What Recruiters Will Notice — Weaknesses" icon="⚠️">
                <div className="space-y-2.5">
                  {(d.recruiter_view?.weaknesses || []).map((s, i) => (
                    <div key={i} className="flex items-start gap-2.5">
                      <div className="w-4 h-4 rounded-full bg-red-900/50 border border-red-500/40 flex items-center justify-center shrink-0 mt-0.5">
                        <div className="w-1.5 h-1.5 rounded-full bg-red-400" />
                      </div>
                      <span className="text-xs text-slate-300 leading-relaxed">{s}</span>
                    </div>
                  ))}
                  {!d.recruiter_view?.weaknesses?.length && <p className="text-xs text-emerald-500 text-xs">No major weaknesses found!</p>}
                </div>
              </Card>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {[
                { label: 'Interview Readiness', val: d.recruiter_view?.interview_readiness },
                { label: 'Hiring Readiness', val: d.recruiter_view?.hiring_readiness },
                { label: 'Benchmark', val: d.benchmark?.percentile },
              ].map(({ label, val }) => {
                const color = val === 'High' || val === 'Strong' ? '#10B981'
                  : val === 'Medium' || val === 'Moderate' ? '#F59E0B' : '#EF4444'
                return (
                  <div key={label} className="bg-[#1C202B] border border-[#2E3447] rounded-xl p-4 text-center">
                    <div className="text-xs text-slate-500 mb-2">{label}</div>
                    <div className="text-lg font-display font-bold" style={{ color }}>{val || '—'}</div>
                  </div>
                )
              })}
            </div>
          </>
        )}

        {/* ── BENCHMARKING TAB ── */}
        {tab === 'benchmark' && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
              {[
                { label: 'Candidate Percentile', val: d.benchmark?.percentile, icon: '🏆' },
                { label: 'Interview Probability', val: d.benchmark?.interview_probability, icon: '📞' },
                { label: 'Overall Score', val: `${total}/100`, icon: '🎯' },
              ].map(({ label, val, icon }) => (
                <Card key={label}>
                  <div className="text-center py-2">
                    <div className="text-2xl mb-2">{icon}</div>
                    <div className="text-xs text-slate-500 mb-1">{label}</div>
                    <div className="text-xl font-display font-bold text-slate-100">{val}</div>
                  </div>
                </Card>
              ))}
            </div>

            <Card title="Candidate Radar — vs Ideal Applicant" icon="📡">
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={d.benchmark?.radar_data || []}>
                    <PolarGrid stroke="#2E3447" />
                    <PolarAngleAxis dataKey="metric" tick={{ fontSize: 10, fill: '#94A3B8' }} />
                    <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar name="You" dataKey="score" stroke="#6366F1" fill="#6366F1" fillOpacity={0.25}
                      dot={{ fill: '#818CF8', r: 3 }} />
                    <Tooltip
                      contentStyle={{ background: '#1C202B', border: '1px solid #2E3447', borderRadius: 8, fontSize: 12 }}
                      formatter={(v) => [`${v}/100`, 'Score']}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card title="Score Dimension Comparison" icon="📊">
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={d.benchmark?.radar_data || []} barSize={28} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
                    <XAxis dataKey="metric" tick={{ fontSize: 9, fill: '#64748B' }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#64748B' }} />
                    <Tooltip
                      contentStyle={{ background: '#1C202B', border: '1px solid #2E3447', borderRadius: 8, fontSize: 12 }}
                    />
                    <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                      {(d.benchmark?.radar_data || []).map((entry, i) => (
                        <Cell key={i} fill={scoreColor(entry.score)} fillOpacity={0.85} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </>
        )}

        {/* ── CAREER FIT TAB ── */}
        {tab === 'career' && (
          <Card title="Career Role Fit Prediction" icon="🧭">
            <p className="text-xs text-slate-500 mb-5">
              Predicted alignment with each career role based on your skill set. Based on semantic skill coverage analysis.
            </p>
            <div className="space-y-4">
              {(d.career_fit || []).map((role, i) => (
                <div key={i} className="flex items-center gap-4">
                  <div className="w-40 text-xs text-slate-300 font-medium shrink-0">{role.role}</div>
                  <div className="flex-1 bg-slate-800 rounded-full h-2.5 overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-700 delay-75"
                      style={{
                        width: `${role.fit}%`,
                        background: scoreColor(role.fit),
                        boxShadow: `0 0 8px ${scoreColor(role.fit)}55`
                      }} />
                  </div>
                  <div className="w-12 text-right text-sm font-bold font-mono" style={{ color: scoreColor(role.fit) }}>
                    {role.fit}%
                  </div>
                  {i === 0 && (
                    <span className="text-xs bg-indigo-900/40 border border-indigo-700/40 text-indigo-300 rounded-full px-2 py-0.5">
                      Best fit
                    </span>
                  )}
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* ── RECOMMENDATIONS TAB ── */}
        {tab === 'recommendations' && (
          <>
            <div className="text-xs text-slate-500 mb-4">
              {d.recommendations?.length || 0} actionable improvement recommendations ranked by priority
            </div>
            <div className="space-y-4">
              {(d.recommendations || []).map((rec, i) => (
                <div key={i}
                  className="border rounded-xl p-5 transition-all"
                  style={{
                    background: priorityBg[rec.priority] || '#1C202B22',
                    borderColor: `${priorityColor[rec.priority] || '#2E3447'}44`,
                  }}
                >
                  <div className="flex items-start gap-3">
                    <div className="shrink-0 mt-0.5">
                      <span className="text-xs font-semibold px-2 py-0.5 rounded-full border"
                        style={{
                          color: priorityColor[rec.priority],
                          borderColor: `${priorityColor[rec.priority]}44`,
                          background: `${priorityColor[rec.priority]}15`,
                        }}>
                        {rec.priority?.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className="text-xs font-mono text-slate-500">{rec.category}</span>
                      </div>
                      <div className="text-sm font-semibold text-slate-100 mb-2">{rec.title}</div>
                      <p className="text-xs text-slate-400 leading-relaxed">{rec.detail}</p>
                    </div>
                  </div>
                </div>
              ))}
              {!d.recommendations?.length && (
                <div className="text-center py-10 text-slate-600 text-sm">No recommendations generated</div>
              )}
            </div>
          </>
        )}

      </div>
    </div>
  )
}

// ── Error Banner ───────────────────────────────────────────────────────────
function ErrorBanner({ msg, onDismiss }) {
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 bg-red-900/90 border border-red-700 text-red-200 text-sm rounded-xl px-5 py-3 shadow-2xl backdrop-blur">
      <span>⚠ {msg}</span>
      <button onClick={onDismiss} className="text-red-400 hover:text-red-200">✕</button>
    </div>
  )
}

// ── Root App ───────────────────────────────────────────────────────────────
export default function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = useCallback(async (resumeFile, jdText) => {
    setLoading(true)
    setError(null)
    try {
      const form = new FormData()
      form.append('resume', resumeFile)
      form.append('job_description', jdText)

      const res = await fetch('/analyze', { method: 'POST', body: form })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Analysis failed' }))
        throw new Error(err.detail || `HTTP ${res.status}`)
      }
      const result = await res.json()
      setData(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  return (
    <>
      {!data
        ? <UploadPage onSubmit={handleSubmit} loading={loading} />
        : <Dashboard data={data} onReset={() => setData(null)} />
      }
      {error && <ErrorBanner msg={error} onDismiss={() => setError(null)} />}
      {loading && !data && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-[#1C202B] border border-[#2E3447] rounded-2xl px-10 py-8 text-center">
            <div className="flex justify-center mb-4">
              <svg className="animate-spin w-10 h-10 text-indigo-400" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" strokeDasharray="45" strokeDashoffset="10" />
              </svg>
            </div>
            <div className="font-display font-semibold text-slate-200 mb-1">Analyzing Resume</div>
            <div className="text-xs text-slate-500">Running semantic skill matching, experience analysis,<br/>project scoring and benchmarking…</div>
          </div>
        </div>
      )}
    </>
  )
}
