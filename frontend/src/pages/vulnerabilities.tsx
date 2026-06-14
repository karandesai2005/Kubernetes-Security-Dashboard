import { VulnTable } from '../components/VulnTable'

export default function VulnerabilitiesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Vulnerabilities</h1>
        <p className="text-sm text-gray-400">Findings from Trivy Operator across workloads and images</p>
      </div>
      <VulnTable limit={40} />
    </div>
  )
}
