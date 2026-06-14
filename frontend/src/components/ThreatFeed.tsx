import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../utils/api'
import { SEVERITY_COLORS, REFRESH_INTERVAL_MS } from '../utils/constants'
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

export function ThreatFeed({ compact = false }: { compact?: boolean }) {
  const [liveEvents, setLiveEvents] = useState<Threat[]>([])
  const [wsStatus, setWsStatus] = useState<'connecting' | 'open' | 'closed'>('connecting')

  const { data: initial } = useQuery({
    queryKey: ['threats', 40],
    queryFn: async () => {
      const { data } = await apiClient.get<Threat[]>('/api/v1/threats?limit=40')
      return data
    },
    refetchInterval: REFRESH_INTERVAL_MS,
  })

  // Merge initial + live
  const allEvents = [...liveEvents, ...(initial || [])]
    .sort((a, b) => (a.timestamp > b.timestamp ? -1 : 1))
    .slice(0, compact ? 8 : 18)

  // WebSocket for live push (best effort)
  useEffect(() => {
    let ws: WebSocket | null = null
    let retry: any

    function connect() {
      try {
        ws = new WebSocket((process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000') + '/ws/threats')
        setWsStatus('connecting')

        ws.onopen = () => setWsStatus('open')
        ws.onclose = () => {
          setWsStatus('closed')
          retry = setTimeout(connect, 4000)
        }
        ws.onerror = () => ws?.close()

        ws.onmessage = (ev) => {
          try {
            const msg = JSON.parse(ev.data)
            if (msg.type === 'threat' && msg.data) {
              setLiveEvents((prev) => [msg.data as Threat, ...prev].slice(0, 12))
            }
          } catch {}
        }
      } catch {
        setWsStatus('closed')
        retry = setTimeout(connect, 5000)
      }
    }

    connect()
    return () => {
      clearTimeout(retry)
      ws?.close()
    }
  }, [])

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="font-medium tracking-wider text-sm text-gray-400">LIVE THREAT FEED</div>
        <div className="text-[10px] px-2 py-0.5 rounded bg-gray-800 text-gray-400">
          {wsStatus === 'open' ? 'LIVE' : 'POLLING'}
        </div>
      </div>

      <div className={compact ? "max-h-[268px]" : "max-h-[420px]"} style={{ overflowY: 'auto' }}>
        {allEvents.length === 0 && (
          <div className="text-gray-500 text-sm py-8 text-center">No threats yet. Seed data or wait for events.</div>
        )}
        {allEvents.map((t, idx) => (
          <div key={`${t.id}-${idx}`} className="flex gap-3 py-2.5 border-b border-gray-800 last:border-0">
            <div className={`badge self-start mt-0.5 sev-${t.severity}`}>{t.severity}</div>
            <div className="min-w-0 flex-1">
              <div className="font-medium text-sm leading-tight">{t.rule}</div>
              <div className="text-xs text-gray-400 mt-0.5 line-clamp-1">{t.message}</div>
              <div className="flex items-center gap-2 mt-1 text-[11px] text-gray-500">
                <span className="uppercase tracking-widest">{t.source}</span>
                {t.namespace && <span className="text-blue-400">ns/{t.namespace}</span>}
                {t.pod && <span>pod/{t.pod}</span>}
                <span className="ml-auto tabular-nums">{formatRelativeTime(t.timestamp)}</span>
              </div>
            </div>
            <div className="text-right text-xs font-mono text-amber-400 self-start tabular-nums">
              +{t.risk_score.toFixed(0)}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

