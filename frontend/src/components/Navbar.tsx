import Link from 'next/link'
import { useRouter } from 'next/router'
import { Shield, Activity, AlertTriangle, Users, Settings } from 'lucide-react'

const nav = [
  { href: '/', label: 'Dashboard', icon: Shield },
  { href: '/threats', label: 'Threats', icon: Activity },
  { href: '/vulnerabilities', label: 'Vulnerabilities', icon: AlertTriangle },
  { href: '/rbac', label: 'RBAC', icon: Users },
  { href: '/settings', label: 'Settings', icon: Settings },
]

export default function Navbar() {
  const router = useRouter()
  const current = router.pathname

  return (
    <nav className="border-b border-gray-800 bg-[#0b0f17]/95 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <div className="font-semibold tracking-tight">K8s Security</div>
            <div className="text-[10px] text-gray-500 -mt-1">Posture Dashboard</div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm">
          {nav.map((item) => {
            const Icon = item.icon
            const active = current === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg transition-colors hover:bg-gray-800/60 ${active ? 'bg-gray-800 text-white' : 'text-gray-400 hover:text-gray-200'}`}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </Link>
            )
          })}
        </div>

        <div className="flex items-center gap-2 text-xs">
          <div className="px-2 py-1 rounded bg-emerald-900/30 text-emerald-400 border border-emerald-800/60">MOCK MODE</div>
          <a href="http://localhost:8000/docs" target="_blank" className="text-gray-400 hover:text-gray-300">API</a>
        </div>
      </div>
    </nav>
  )
}
