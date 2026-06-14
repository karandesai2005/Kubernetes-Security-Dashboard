import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { apiClient } from '../utils/api'
import { REFRESH_INTERVAL_MS } from '../utils/constants'
import { formatRelativeTime } from '../utils/formatters'

interface Vuln {
  id: number
  cve_id: string
  severity: string
  cvss_score: number | null
  image: string
  package: string | null
  fixed_version: string | null
  namespace: string | null
  resource_kind: string | null
  discovered_at: string
  risk_score: number
}

export function VulnTable({ limit = 12 }: { limit?: number }) {
  const [severityFilter, setSeverityFilter] = useState<string>('')
  const [nsFilter, setNsFilter] = useState<string>('')

  const { data, isLoading } = useQuery({
    queryKey: ['vulns', limit],
    queryFn: async () => {
      const { data } = await apiClient.get<Vuln[]>('/api/v1/vulns?limit=' + (limit * 2))
      return data
    },
    refetchInterval: REFRESH_INTERVAL_MS,
  })

  const filtered = useMemo(() => {
    let rows = data || []
    if (severityFilter) rows = rows.filter(r => r.severity === severityFilter)
    if (nsFilter) rows = rows.filter(r => (r.namespace || '') === nsFilter)
    return rows.slice(0, limit)
  }, [data, severityFilter, nsFilter, limit])

  const namespaces = Array.from(new Set((data || []).map(d => d.namespace).filter(Boolean)))

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="font-medium tracking-wider text-sm text-gray-400">VULNERABILITY FINDINGS (TRIVY)</div>
        <div className="flex gap-2 text-xs">
          <select
            className="bg-gray-900 border border-gray-700 rounded px-2 py-1"
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="">All severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select
            className="bg-gray-900 border border-gray-700 rounded px-2 py-1"
            value={nsFilter}
            onChange={(e) => setNsFilter(e.target.value)}
          >
            <option value="">All namespaces</option>
            {namespaces.map(n => <option key={n} value={n!}>{n}</option>)}
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr>
              <th>CVE</th>
              <th>Severity</th>
              <th>CVSS</th>
              <th>Image / Package</th>
              <th>Namespace</th>
              <th>Fixed In</th>
              <th>Found</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={7} className="py-8 text-center text-gray-500">No findings match filters</td></tr>
            )}
            {filtered.map(v => (
              <tr key={v.id}>
                <td className="font-mono text-xs text-rose-400">{v.cve_id}</td>
                <td>
                  <span className={`badge sev-${v.severity}`}>{v.severity}</span>
                </td>
                <td className="tabular-nums font-medium">{v.cvss_score ?? '—'}</td>
                <td className="max-w-[260px] truncate text-xs" title={v.image}>
                  {v.image.split('/').pop()}<br />
                  <span className="text-gray-500">{v.package}@{v.installed_version}</span>
                </td>
                <td className="text-xs text-blue-400">{v.namespace || '—'} {v.resource_kind && <span className="text-gray-500">({v.resource_kind})</span>}</td>
                <td className="text-xs font-mono text-emerald-400">{v.fixed_version || '—'}</td>
                <td className="text-xs text-gray-400 tabular-nums">{formatRelativeTime(v.discovered_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="text-[10px] text-gray-500 mt-2">Showing {filtered.length} of latest findings. Use /scan/trivy to simulate new results.</div>
    </div>
  )
}

