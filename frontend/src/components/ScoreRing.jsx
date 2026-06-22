import React from 'react'

const getScoreColor = (score) => {
  if (score >= 75) return { stroke: '#10B981', text: '#10B981', label: 'Excellent' }
  if (score >= 60) return { stroke: '#6366F1', text: '#818CF8', label: 'Good' }
  if (score >= 45) return { stroke: '#F59E0B', text: '#F59E0B', label: 'Fair' }
  return { stroke: '#EF4444', text: '#EF4444', label: 'Weak' }
}

export default function ScoreRing({ score = 0, size = 140, label = "Overall" }) {
  const r = 42
  const circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ
  const colors = getScoreColor(score)

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox="0 0 100 100">
          {/* Track */}
          <circle cx="50" cy="50" r={r} fill="none" stroke="#2E3447" strokeWidth="8" />
          {/* Progress */}
          <circle
            cx="50" cy="50" r={r}
            fill="none"
            stroke={colors.stroke}
            strokeWidth="8"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{
              transformOrigin: 'center',
              transform: 'rotate(-90deg)',
              transition: 'stroke-dashoffset 1.2s cubic-bezier(0.34,1.56,0.64,1)',
              filter: `drop-shadow(0 0 6px ${colors.stroke}60)`,
            }}
          />
          <text x="50" y="46" textAnchor="middle" dominantBaseline="middle"
            fontSize="20" fontWeight="700" fill={colors.text} fontFamily="Plus Jakarta Sans">
            {score}
          </text>
          <text x="50" y="62" textAnchor="middle" fontSize="8" fill="#64748B" fontFamily="Inter">
            / 100
          </text>
        </svg>
      </div>
      <div className="text-center">
        <div className="text-xs text-text-secondary">{label}</div>
        <div className="text-xs font-semibold mt-0.5" style={{ color: colors.text }}>
          {colors.label}
        </div>
      </div>
    </div>
  )
}
