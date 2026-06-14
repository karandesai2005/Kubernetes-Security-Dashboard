import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../utils/api'
import { REFRESH_INTERVAL_MS } from '../utils/constants'
import { formatRelativeTime } from '../utils/formatters'

interface RBACEvent {
  id: number
  subject: string
  verb: string
  resource: string
  namespace: string | null
  allowed: boolean
  reason: string | null
  timestamp: string
  risk_score: number
}

export function RBACViewer() {
  const { data } = useQuery({
    queryKey: ['rbac'],
    queryFn: async () => {
      const { data } = await apiClient.get<RBACEvent[]>('/api/v1/rbac?limit=60')
      return data
    },
    refetchInterval: REFRESH_INTERVAL_MS * 1.5,
  })

  const highRisk = (data || []).filter(e => e.risk_score >= 12).slice(0, 9)

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="font-medium tracking-wider text-sm text-gray-400">RBAC POSTURE — OVERPERMISSIONED BINDINGS</div>
        <div className="text-xs text-amber-400">{(data || []).length} events</div>
      </div>

      <div className="space-y-2">
        {(data || []).length === 0 && <div className="text-sm text-gray-500 py-6">No RBAC anomalies collected.</div>}

        {highRisk.length > 0 && (
          <div className="mb-2 text-xs uppercase tracking-widest text-amber-400/80">Highest risk subjects</div>
        )}
        {highRisk.map((e, idx) => (
          <div key={idx} className="flex items-center gap-3 text-sm p-2 bg-[#0b0f17] rounded border border-gray-800">
            <div className="font-mono text-xs text-red-400 w-8 text-right tabular-nums">+{e.risk_score}</div>
            <div className="flex-1 min-w-0">
              <div className="font-medium truncate">{e.subject}</div>
              <div className="text-xs text-gray-400">
                {e.verb} {e.resource} {e.namespace ? `in ${e.namespace}` : ''} · <span className="text-amber-400">{e.reason}</span>
              </div>
            </div>
            <div className="text-right text-xs text-gray-500">{formatRelativeTime(e.timestamp)}</div>
          </div>
        ))}

        {data && data.length > 0 && (
          <div className="pt-3 border-t border-gray-800 text-xs text-gray-500">
            Full RBAC graph visualisation + policy simulation planned. Current view highlights risky audit events.
          </div>
        )}
      </div>
    </div>
  )
}

