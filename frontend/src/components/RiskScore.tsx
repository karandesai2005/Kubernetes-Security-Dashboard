import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../utils/api'
import { REFRESH_INTERVAL_MS, SEVERITY_COLORS } from '../utils/constants'
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

interface RiskData {
  score: number
  breakdown: Record<string, number>
  generated_at: string
  counts: Record<string, number>
}

function getColor(score: number) {
  if (score >= 80) return '#ef4444'
  if (score >= 55) return '#f97316'
  if (score >= 30) return '#eab308'
  return '#22c55e'
}

export function RiskScore() {
  const { data, isLoading } = useQuery({
    queryKey: ['risk-score'],
    queryFn: async () => {
      const { data } = await apiClient.get<RiskData>('/api/v1/risk-score')
      return data
    },
    refetchInterval: REFRESH_INTERVAL_MS,
  })

  const score = data?.score ?? 0
  const color = getColor(score)
  const breakdown = data?.breakdown ?? { falco: 0, trivy: 0, guardduty: 0, rbac: 0 }

  const pieData = Object.entries(breakdown).map(([k, v]) => ({ name: k, value: Math.max(1, v) }))

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm font-medium tracking-wider text-gray-400">CLUSTER RISK SCORE</div>
        <div className="text-xs text-gray-500">0–100</div>
      </div>

      <div className="flex items-end gap-6">
        {/* Gauge */}
        <div className="relative w-40 h-40 flex-shrink-0">
          <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
            <circle cx="60" cy="60" r="52" fill="none" stroke="#1f2937" strokeWidth="11" />
            <circle
              cx="60"
              cy="60"
              r="52"
              fill="none"
              stroke={color}
              strokeWidth="11"
              strokeDasharray={326}
              strokeDashoffset={326 - (326 * Math.min(score, 100)) / 100}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className="text-6xl font-semibold tabular-nums tracking-tighter" style={{ color }}>
              {Math.round(score)}
            </div>
            <div className="text-xs -mt-1 text-gray-400">RISK</div>
          </div>
        </div>

        {/* Breakdown */}
        <div className="flex-1 min-w-0 pt-1">
          <div className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
            {Object.entries(breakdown).map(([key, val]) => (
              <div key={key} className="flex justify-between items-center">
                <div className="capitalize text-gray-400">{key}</div>
                <div className="font-mono text-right">{Number(val).toFixed(1)}</div>
              </div>
            ))}
          </div>

          <div className="mt-4 h-2.5 w-full bg-gray-800 rounded overflow-hidden flex">
            {Object.entries(breakdown).map(([k, v], idx) => (
              <div
                key={idx}
                className="h-full transition-all"
                style={{
                  width: `${Math.max(2, (Number(v) / 100) * 100)}%`,
                  background: k === 'falco' ? '#3b82f6' : k === 'trivy' ? '#a78bfa' : k === 'guardduty' ? '#f472b6' : '#f59e0b',
                }}
              />
            ))}
          </div>
          <div className="text-[10px] text-gray-500 mt-1.5">Weighted by signal category</div>
        </div>
      </div>

      {data && (
        <div className="mt-4 text-xs text-gray-500">
          Signals: <span className="font-mono">{data.counts.falco}</span> Falco ·{' '}
          <span className="font-mono">{data.counts.trivy}</span> CVEs ·{' '}
          <span className="font-mono">{data.counts.guardduty}</span> GuardDuty ·{' '}
          <span className="font-mono">{data.counts.rbac}</span> RBAC
        </div>
      )}
    </div>
  )
}

