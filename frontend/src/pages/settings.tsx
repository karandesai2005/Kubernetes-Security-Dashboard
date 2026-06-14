import { useState } from 'react'

export default function SettingsPage() {
  const [seededMsg, setSeededMsg] = useState('')

  async function seed() {
    setSeededMsg('Seeding...')
    try {
      const res = await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/api/v1/seed', { method: 'POST' })
      const json = await res.json()
      setSeededMsg(JSON.stringify(json))
    } catch (e) {
      setSeededMsg('Failed to seed (is backend running?)')
    }
    setTimeout(() => setSeededMsg(''), 3200)
  }

  return (
    <div className="max-w-2xl space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-gray-400">Local development &amp; demo controls</p>
      </div>

      <div className="card p-6 space-y-4">
        <div>
          <div className="font-medium mb-1">Data</div>
          <button onClick={seed} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded text-sm">Seed / Refresh Mock Data</button>
          {seededMsg && <div className="text-xs mt-2 text-emerald-400">{seededMsg}</div>}
        </div>

        <div className="text-sm text-gray-400 pt-3 border-t border-gray-800">
          Feature flags and external integrations (GuardDuty, real Falco gRPC, Trivy Operator CRD watch) are controlled on the backend via environment variables.
          <br /><br />
          Current deployment uses in-memory + Postgres mock data with live WebSocket simulation for new Falco-style events.
        </div>
      </div>

      <div className="text-xs text-gray-500">
        Backend: <code>http://localhost:8000/docs</code> &nbsp;•&nbsp; Frontend hot-reloads via Docker volume.
      </div>
    </div>
  )
}
