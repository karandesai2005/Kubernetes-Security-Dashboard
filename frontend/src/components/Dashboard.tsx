import { RiskScore } from './RiskScore'
import { ThreatFeed } from './ThreatFeed'
import { VulnTable } from './VulnTable'
import { RBACViewer } from './RBACViewer'

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Kubernetes Security Posture</h1>
          <p className="text-gray-400 mt-1 text-sm">Unified view across Falco, Trivy, GuardDuty &amp; RBAC signals</p>
        </div>
        <a
          href="/seed"
          onClick={async (e) => {
            e.preventDefault()
            try {
              await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/api/v1/seed', { method: 'POST' })
              window.location.reload()
            } catch {}
          }}
          className="text-xs px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white"
        >
          SEED / REFRESH MOCK DATA
        </a>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
        <div className="lg:col-span-2">
          <RiskScore />
        </div>
        <div className="lg:col-span-3">
          <ThreatFeed compact />
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <VulnTable limit={9} />
        <RBACViewer />
      </div>

      <div className="text-[11px] text-gray-500 text-center pt-2">
        Data refreshes automatically. Use the top navigation for full-screen views. Backend at :8000
      </div>
    </div>
  )
}

