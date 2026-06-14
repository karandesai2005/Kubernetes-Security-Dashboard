export function formatRelativeTime(iso: string): string {
  try {
    const date = new Date(iso)
    const now = new Date()
    const diff = (now.getTime() - date.getTime()) / 1000
    if (diff < 60) return `${Math.floor(diff)}s ago`
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
    return `${Math.floor(diff / 86400)}d ago`
  } catch {
    return iso
  }
}

export function truncate(str: string, len = 42): string {
  return str.length > len ? str.slice(0, len - 1) + '…' : str
}
