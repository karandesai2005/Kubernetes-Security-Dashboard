import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { apiClient } from '../utils/api'
import { ThreatFeed } from '../components/ThreatFeed'
import { formatRelativeTime } from '../utils/formatters'

interface Threat {
  id: number
  source: string
  severity: string
  rule: string
  namespace: string | null
  pod: string | null
  message: string
  timestamp: string
  risk_score: number
}

export default function ThreatsPage() {
  const [severity, setSeverity] = useState('')
  const [source, setSource] = useState('')

  const { data } = useQuery({
    queryKey: ['threats', 'full', severity, source],
    queryFn: async () => {
      const params = new URLSearchParams({ limit: '120' })
      if (severity) params.set('severity', severity)
      if (source) params.set('source', source)
      const { data } = await apiClient.get<Threat[]>(`/api/v1/threats?${params}`)
      return data
    },
    refetchInterval: 15000,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Threat Events</h1>
        <p className="text-sm text-gray-400">Falco runtime detections + AWS GuardDuty EKS findings</p>
      </div>

      <div className="flex gap-3 text-sm">
        <select className="bg-gray-900 border border-gray-700 px-3 py-1 rounded" value={severity} onChange={e => setSeverity(e.target.value)}>
          <option value="">All severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
        </select>
        <select className="bg-gray-900 border border-gray-700 px-3 py-1 rounded" value={source} onChange={e => setSource(e.target.value)}>
          <option value="">All sources</option>
          <option value="falco">Falco</option>
          <option value="guardduty">GuardDuty</option>
        </select>
      </div>

      <ThreatFeed compact={false} />

      <div className="card p-5">
        <div className="text-sm font-medium mb-3 text-gray-400">ALL THREATS (DETAILED)</div>
        <table className="w-full text-sm">
          <thead><tr><th>Time</th><th>Source</th><th>Rule</th><th>Target</th><th>Severity</th><th>Risk</th></tr></thead>
          <tbody>
            {(data || []).map(t => (
              <tr key={t.id}>
                <td className="text-xs text-gray-400 tabular-nums">{formatRelativeTime(t.timestamp)}</td>
                <td><span className="uppercase text-xs px-1.5 py-px bg-gray-800 rounded">{t.source}</span></td>
                <td className="font-medium">{t.rule}</td>
                <td className="text-xs text-gray-400">{t.namespace ? `ns/${t.namespace}` : ''} {t.pod}</td>
                <td><span className={`badge sev-${t.severity}`}>{t.severity}</span></td>
                <td className="font-mono text-amber-400">+{t.risk_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
