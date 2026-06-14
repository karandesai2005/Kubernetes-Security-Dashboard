import { RBACViewer } from '../components/RBACViewer'

export default function RBACPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">RBAC Analysis</h1>
        <p className="text-sm text-gray-400">Audit events indicating privilege escalation or excessive permissions</p>
      </div>
      <RBACViewer />
      <div className="card p-5 text-sm text-gray-400">
        Planned: interactive graph of subjects → roles → resources with highlighted high-risk paths (cluster-admin, wildcard verbs, impersonate, cross-ns secret access).
      </div>
    </div>
  )
}
